from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import ChatPromptTemplate
import os
import shutil
import json
from dotenv import load_dotenv
load_dotenv() 


class ChildMonitoringRAG:
    def __init__(
        self,
        data_dir: str,
        persist_directory: str,
        model: str = "text-embedding-3-small",
        similarity_threshold: float = 0.25,
        top_k: int = 3,
    ):
        self.data_dir = data_dir
        self.persist_directory = persist_directory
        self.model = model
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k

        # Initialize RAG components
        self.embeddings = OpenAIEmbeddings(
            model=model,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.vectorstore = None
        self.retriever = None

    def load_documents(self):
        """
        Load documents from the data directory
        """

        loader = PyPDFLoader(self.data_dir)
        pages = []
        for page in loader.lazy_load():
            pages.append(page)

        print(f"Loaded {len(pages)} documents from {self.data_dir}")
        return pages

    def setup_vector_store(self, documents, chunk_size: int = 1000):
        """
        Create vector store and set up retriever
        """
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", "!", "?", ",", " "],
            length_function=len,
        )

        splits = text_splitter.split_documents(documents)

        # Create vector store
        self.vector_store = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
        )

        # Set up retriever
        
    def initialize_rag(self, rebuild: bool = False):
        """
        Initialize the complete RAG system
        """
        print("Initializing RAG system...")

        # Check if the persist directory
        if os.path.exists(self.persist_directory) and not rebuild:
            print("Using existing vector store from:", self.persist_directory)
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
            )
            self.retriever = self.retriever = self.vector_store.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={"k": 3, "score_threshold": self.similarity_threshold},
            )
        else:
            # Setup fresh vector store
            print("Creating new vector store...")
            # Delete existing directory if rebuilding
            if os.path.exists(self.persist_directory):
                shutil.rmtree(self.persist_directory)
            documents = self.load_documents()
            self.setup_vector_store(documents)
            print(f"Vector store initialized with {len(documents)} documents.")
        
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": self.top_k, "score_threshold": self.similarity_threshold},
        )
        print(f"Retriever initialized with self.top_k={self.top_k} and similarity threshold={self.similarity_threshold}.")
        
        print("RAG system initialized successfully.")


    @staticmethod
    def build_output_format_template() -> str:
        """
        Build the output format template (JSON schema) for the LLM response.
        Returns a string representing the desired JSON schema.
        """
        return json.dumps(
            {
                "analysis": "string (Ringkasan analisis pola belajar dan pemahaman anak berdasarkan data yang diberikan. Jelaskan kekuatan dan area yang butuh perhatian. Sampaikan dalam bentuk narasi yang interaktif dan mudah dipahami oleh orang tua atau guru, seolah-olah Anda sedang berkomunikasi langsung dengan mereka.)",
                "key_concepts_status": {
                    "mastered": "array of string (Daftar konsep literasi finansial yang telah dikuasai anak, contoh: 'Menabung')",
                    "learning": "array of string (Daftar konsep yang sedang dalam proses dipelajari, contoh: 'Berbelanja')",
                    "struggling": "array of string (Daftar konsep yang masih menjadi tantangan bagi anak, contoh: 'Berbagi')",
                    "<bagian ini dapat dikosongkan apabila tidak relevan dengan query>": "array of string (Bagian ini dapat dikosongkan jika tidak ada konsep yang relevan.)",
                },
                "suggestions": [
                    {
                        "category": "string (Kategori saran, contoh: 'Aktivitas di Rumah', 'Diskusi Orang Tua-Anak', 'Penggunaan Aplikasi')",
                        "description": "string (Saran konkret dan kegiatan praktis yang bisa dilakukan orang tua atau guru untuk membantu anak meningkatkan pemahaman konsep ini.)",
                        "related_concepts": "array of string (Konsep literasi finansial yang relevan dengan saran ini, contoh: ['Menabung', 'Perencanaan Keuangan'])",
                    }
                ],
                "general_notes": "string (Informasi tambahan singkat, disclaimer, atau catatan umum jika ada.)",
            },
            indent=2,
        )

    def create_prompt(
        self, query: str, children_data_context: str
    ) -> ChatPromptTemplate:
        """
        Creates a formatted prompt for the LLM, combining children's data context and RAG context.

        Args:
            query (str): The user's original question.
            children_data_context (str): JSON string or formatted text of the child's performance data.

        Returns:
            ChatPromptTemplate: A formatted prompt ready for the LLM.
        """

        # --- RAG Context Retrieval ---
        rag_context_docs = []
        if self.retriever:
            try:
                # Retrieve relevant documents from the vector store based on the query
                rag_context_docs = self.retriever.invoke(query)
                print(f"Retrieved {len(rag_context_docs)} relevant documents from RAG.")
            except Exception as e:
                print(f"Error retrieving RAG documents: {e}")
                # If error, ensure empty list for rag_context_docs
                rag_context_docs = []
        else:
            print("Retriever not initialized. Ensure initialize_rag() was called.")
            rag_context_docs = []

        rag_context_text = "\n\n".join([doc.page_content for doc in rag_context_docs])
        if not rag_context_text.strip():
            rag_context_text = (
                "Tidak ada informasi umum yang sangat relevan ditemukan dari panduan."
            )

        # Get the structured output format
        # FIXED: Call static method correctly, no user_id needed
        output_format = self.build_output_format_template()

        # --- PROMPT TEMPLATE ---
        PROMPT_TEMPLATE = """
        Anda adalah seorang asisten AI ahli dalam pedagogi dan literasi finansial di Indonesia.
        Tugas utama Anda adalah membantu orang tua dan pendidik menganalisis pola belajar dan pemahaman literasi finansial anak, serta memberikan saran yang tepat.

        Tolong berikan respons dalam **Bahasa Indonesia**, dengan nada suportif, empatik, dan penjelasan yang mudah dimengerti oleh orang tua dan guru.

        Berikut adalah data performa dan pola belajar anak:
        ```json
        {children_data_context}
        ```

        Anda juga dapat menggunakan informasi tambahan dari panduan resmi berikut untuk memberikan analisis dan saran:
        ```text
        {rag_context_text}
        ```

        ---
        Pertanyaan dari Orang Tua:
        {query}

        ---
        Format Output yang Diinginkan:
        Harap berikan respons Anda dalam format JSON murni, tanpa teks atau *markdown* tambahan di luar blok JSON.
        Berikut adalah struktur JSON yang diharapkan:
        ```json
        {output_format}
        ```
        (Catatan: Jangan sertakan tanda '`' *markdown* di sekitar output JSON Anda. Hasilkan JSON murni.)

        ---
        Instruksi Umum:
        1.  Analisis data anak dengan cermat. Identifikasi kekuatan dan area yang perlu peningkatan.
        2.  Berikan jawaban yang jelas, empatik, dan mudah dimengerti oleh orang tua. Hindari jargon yang rumit.
        3.  Sesuaikan respons dengan usia dari anak yaitu {age} tahun, dan pastikan saran yang diberikan sesuai dengan tahap perkembangan mereka.
        4.  Jika relevan, sertakan saran konkret dan aktivitas yang bisa dilakukan orang tua untuk membantu anak.
        5.  Selalu berikan saran yang sesuai dengan konteks budaya Indonesia.
        5.  Jika data yang diminta tidak tersedia atau relevan, jelaskan dengan sopan, lalu follow-up dengan pertanyaan klarifikasi.
        6.  Jika pertanyaan umum tidak berkaitan dengan data anak, fokus pada konteks RAG.
        7.  Prioritaskan informasi dari data anak dan konteks RAG dibandingkan pengetahuan umum Anda.
        """

        # Create and format the prompt
        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        formatted_prompt = prompt.format_messages(
            children_data_context=children_data_context,
            rag_context_text=rag_context_text,
            query=query,
            output_format=output_format,
            age="11",  # Example age, can be parameterized if needed
        )

        return formatted_prompt