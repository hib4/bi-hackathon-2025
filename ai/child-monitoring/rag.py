import os
import shutil
import json
import requests
from datetime import datetime, timedelta
from intent_classifier import IntentClassifier
from pydantic import SecretStr

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.prompt_values import PromptValue
from dotenv import load_dotenv

load_dotenv()


class ChildMonitoringRAG:
    def __init__(
        self,
        data_dir: str,
        persist_directory: str,
        embedding_model_name: str = "text-embedding-3-small",
        llm_model_name: str = "gpt-4o-mini",
        similarity_threshold: float = 0.25,
        top_k: int = 3,
        backend_api_base_url: str = os.getenv(
            "BACKEND_API_BASE_URL", "http://localhost:8000/api/v1/analytic"
        ),
    ):
        self.data_dir = data_dir
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model_name
        self.llm_model_name = llm_model_name  # For the main conversational LLM
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k
        self.backend_api_base_url = backend_api_base_url

        api_key = os.getenv("OPENAI_API_KEY")
        self.embeddings = OpenAIEmbeddings(
            model=self.embedding_model_name,
            api_key=SecretStr(api_key) if api_key else None,
        )

        self.vectorstore = None
        self.retriever = None

        self.intent_classifier = IntentClassifier(
            model_name="gpt-4o-mini",
        )

    def _load_documents(self) -> list[Document]:
        """
        Load documents from the data directory (PDF file).
        Returns a list of Document objects, where each document is typically a page.
        """
        loader = PyPDFLoader(self.data_dir)
        documents = loader.load()

        print(f"Loaded {len(documents)} documents (pages) from {self.data_dir}")
        return documents

    def _setup_vector_store(self, chunk_size: int = 1000):
        """
        Create vector store and set up retriever.
        """
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
        print("Loading documents for new vector store...")
        documents = self._load_documents()
        print("Setting up new vector database...")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=int(chunk_size * 0.1),
            separators=["\n\n", "\n", ".", "!", "?", ",", " "],
            length_function=len,
        )

        splits = text_splitter.split_documents(documents)
        print(f"Split documents into {len(splits)} chunks.")

        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,  # Use self.persist_directory
        )
        print(
            f"Vector store created at {self.persist_directory} with {len(splits)} chunks."
        )

    def initialize_rag(self, rebuild: bool = False):
        """
        Initialize the complete RAG system.
        Args:
            rebuild (bool): If True, forces a rebuild of the vector store
                            even if it already exists.
        """
        print("Initializing RAG system...")

        if os.path.exists(self.persist_directory) and not rebuild:
            print("Using existing vector store from:", self.persist_directory)
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
            )
            if self.vectorstore._collection.count() == 0:
                print("Existing vector store is empty, rebuilding...")
                self._setup_vector_store()
        else:
            print("Creating new vector store...")
            self._setup_vector_store()

        if self.vectorstore is not None:
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={
                    "k": self.top_k,
                    "score_threshold": self.similarity_threshold,
                },
            )
        else:
            print("Error: Vector store is not initialized.")
            return

        print(
            f"Retriever initialized with top_k={self.top_k} and similarity threshold={self.similarity_threshold}."
        )
        print("RAG system initialized successfully.")

    @staticmethod
    def build_output_format_template() -> str:
        """
        Build the output format template for chatbot response.
        Returns a conversational text format instead of JSON.
        """
        return """
            Berikan respons dalam format percakapan yang natural dan ramah untuk orang tua/guru tentang perkembangan literasi finansial anak. Apabila diperlukan juga gunakan emoji yang sesuai. Gunakan format berikut:

            Mulai dengan sapaan hangat dan ringkasan singkat tentang perkembangan anak.

            Apabila orang tua/guru meminta ringkasan perkembangan anak untuk setiap tema, gunakan format berikut:
                **Yang sudah dikuasai dengan baik:**
                - Sebutkan konsep-konsep yang success_rate >= 80'%' dengan bahasa yang positif

                **Yang sedang dipelajari:**
                - Sebutkan konsep-konsep yang success_rate 60-80'%' dengan nada mendukung

                **Yang masih butuh perhatian:**
                - Sebutkan konsep-konsep yang success_rate < 60'%' dengan nada yang tetap positif dan memberikan harapan
                Jika ada data yang tidak tersedia, jelaskan dengan sopan.
            
            Apabila orang tua/guru meminta ringkasan perkembangan anak dalam periode waktu tertentu, gunakan format berikut:
            **Perkembangan Anak dalam Periode Tersebut:**
            - Berikan ringkasan perkembangan anak dalam periode waktu yang diminta, dengan fokus pada perubahan positif dan area yang perlu perhatian.
            - Gunakan bahasa yang mudah dipahami dan tidak menggurui.
            - Jika ada referensi dari panduan, sertakan dengan jelas.
            
            Apabila orang tua/guru meminta ringkasan umum atau statistik performa anak, gunakan format berikut:
            **Ringkasan Umum Performa Anak:**
            - Berikan ringkasan umum tentang progres belajar anak, dengan fokus pada kekuatan dan area yang perlu peningkatan.
            - Gunakan bahasa yang mudah dipahami dan tidak menggurui.
            - Jika ada referensi dari panduan, sertakan dengan jelas.
            - Jika ada data yang tidak tersedia, jelaskan dengan sopan.
            
            Apabila orang tua/guru meminta saran atau tips, gunakan format berikut:
            **Saran untuk Orang Tua/Guru:**
            - Berikan saran yang relevan dengan perkembangan anak
            - Gunakan bahasa yang mudah dipahami dan tidak menggurui
            - Sertakan contoh konkret atau aktivitas yang bisa dilakukan bersama anak
            - Jika ada referensi dari panduan, sertakan dengan jelas
            

            Akhiri dengan kata-kata motivasi dan dukungan untuk orang tua/guru.

            Pastikan seluruh respons terasa seperti sedang berbicara langsung dengan orang tua/guru, bukan laporan formal.
        """

    def make_backend_api_call(self, api_details: dict) -> dict[str, str]:
        """
        Makes API calls to the backend based on the classified intent's details.
        Handles multiple API types if present in api_details['api_type'].
        Returns a dictionary mapping API type to its JSON response string.
        """

        results = []
        for api_detail in api_details:
            url = self.backend_api_base_url
            api_type = api_detail.get("api_type")
            url += f"/{api_type}"

            # Params
            params_str = ""

            # Themes
            if api_type == "concept-performance":
                themes = api_detail.get("themes")
                if len(themes) > 0:
                    themes_str = ",".join(themes)
                    params_str += f"themes={themes_str}&"

            # Time Unit
            time_unit = api_detail.get("time_unit")
            if time_unit:
                params_str += f"time_unit={time_unit}&"

            # Num Periods
            num_periods = api_detail.get("num_periods")
            if num_periods:
                params_str += f"num_periods={num_periods}&"

            # Start Date
            start_date = api_detail.get("start_date")
            if start_date:
                params_str += f"start_date={start_date}&"

            # Start Date
            end_date = api_detail.get("end_date")
            if end_date:
                params_str += f"end_date={end_date}&"

            if params_str != "":
                url += f"?{params_str}"
                url = url[:-1]

            print(f"Trying to call URL: {url}")

            response = requests.get(url=url)
            results.append(response)

        return response.json()

    def create_prompt(self, query: str, child_age: int) -> PromptValue:
        """
        Creates a formatted prompt for the LLM, combining children's data context and RAG context.
        """
        # Get children's data context
        print("Classifying intent and fetching children's data context...")
        intent_data = self.intent_classifier.classify(query)
        intent = intent_data.get("intent")
        api_details = intent_data.get("api_call_details", {})
        children_data_context = ""
        if intent == "child_performance_data":
            try:
                children_data_context = self.make_backend_api_call(api_details)
                print("Children's data context retrieved successfully.")
                print(f"Children's data context: {children_data_context}")
            except Exception as e:
                print(f"An exception occurred with details {e}")

        # Get RAG context documents
        print("Retrieving RAG context documents...")
        rag_context_docs = []
        if self.retriever:
            try:
                rag_context_docs = self.retriever.invoke(query)
                print(f"Retrieved {len(rag_context_docs)} relevant documents from RAG.")
            except Exception as e:
                print(f"Error retrieving RAG documents: {e}")
                rag_context_docs = []
        else:
            print("Retriever not initialized. Ensure initialize_rag() was called.")
            rag_context_docs = []

        rag_context_text = "\n\n".join([doc.page_content for doc in rag_context_docs])
        if not rag_context_text.strip():
            rag_context_text = (
                "Tidak ada informasi umum yang sangat relevan ditemukan dari panduan."
            )

        output_format = self.build_output_format_template()
        PROMPT_TEMPLATE = """
        Anda adalah seorang asisten AI ahli dalam pedagogi dan literasi finansial di Indonesia.
        Tugas utama Anda adalah membantu orang tua dan pendidik menganalisis pola belajar dan pemahaman literasi finansial anak, serta memberikan saran yang tepat.

        Tolong berikan respons dalam **Bahasa Indonesia**, dengan nada suportif, empatik, dan penjelasan yang mudah dimengerti oleh orang tua dan guru.

        Berikut adalah data performa dan pola belajar anak:
        {children_data_context}

        Anda juga dapat menggunakan informasi tambahan dari panduan resmi berikut untuk memberikan analisis dan saran:
        {rag_context_text}
        ```

        ---
        Pertanyaan dari Orang Tua:
        {query}

        ---
        Format Output yang Diinginkan:
        {output_format}

        (Catatan: Jangan sertakan tanda '`' *markdown* di sekitar output JSON Anda. Hasilkan JSON murni.)

        ---
        Instruksi Umum:
        1.  Analisis data anak dengan cermat. Identifikasi kekuatan dan area yang perlu peningkatan.
        2.  Berikan jawaban yang jelas, empatik, dan mudah dimengerti oleh orang tua. Hindari jargon yang rumit.
        3.  Sesuaikan respons dengan usia dari anak yaitu {child_age} tahun, dan pastikan saran yang diberikan sesuai dengan tahap perkembangan mereka.
        4.  Jika relevan, sertakan saran konkret dan aktivitas yang bisa dilakukan orang tua untuk membantu anak.
        5.  Selalu berikan saran yang sesuai dengan konteks budaya Indonesia.
        6.  Jika data yang diminta tidak tersedia atau relevan, jelaskan dengan sopan, lalu follow-up dengan pertanyaan klarifikasi.
        7.  Jika pertanyaan umum tidak berkaitan dengan data anak, fokus pada konteks RAG.
        8.  Prioritaskan informasi dari data anak dan konteks RAG dibandingkan pengetahuan umum Anda.
        """

        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        formatted_prompt = prompt.format_prompt(
            children_data_context=children_data_context,
            rag_context_text=rag_context_text,
            query=query,
            output_format=output_format,
            child_age=child_age,
        )

        return formatted_prompt