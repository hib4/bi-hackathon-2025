from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import ChatPromptTemplate
import os
import shutil
import json


class ChildMonitoringRAG:
    def __init__(
        self,
        data_dir: str,
        persist_directory: str,
        model: str = "text-embedding-3-small",
    ):
        self.data_dir = data_dir
        self.persist_directory = persist_directory
        self.model = model

        # Initialize RAG components
        self.embeddings = OpenAIEmbeddings(model=model)
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

    def setup_vector_store(self, documents, top_k: int = 4, chunk_size: int = 800):
        """
        Create vector store and set up retriever
        """

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=100,
            separators=["\n\n", "\n", "### ", "## ", "- ", ".", "!", "?", ",", " "],
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
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": top_k, "score_threshold": 0.4}
        )

    def initialize_rag(self):
        "Initialize RAG system"
        print("Initializing RAG system...")

        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)

        print("Loading documents...")
        documents = self.load_documents()

        print("Setting vector database...")
        self.setup_vector_store(documents)

        print("RAG system initialized successfully!")
        return True

    @staticmethod
    def build_output_format_template() -> str:
        """
        Build the output format template (JSON schema) for the LLM response.
        Returns a string representing the desired JSON schema.
        """
        # FIXED: Corrected JSON structure and added clearer type/description for LLM
        return json.dumps(
            {
                "analysis": "string (Ringkasan analisis pola belajar dan pemahaman anak berdasarkan data yang diberikan. Jelaskan kekuatan dan area yang butuh perhatian. Sampaikan dalam bentuk narasi yang interaktif dan mudah dipahami oleh orang tua atau guru, seolah-olah Anda sedang berkomunikasi langsung dengan mereka.)",
                "key_concepts_status": {
                    "mastered": "array of string (Daftar konsep literasi finansial yang telah dikuasai anak, contoh: 'Menabung')",
                    "learning": "array of string (Daftar konsep yang sedang dalam proses dipelajari, contoh: 'Berbelanja')",
                    "struggling": "array of string (Daftar konsep yang masih menjadi tantangan bagi anak, contoh: 'Berbagi')",
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
            indent=2,  # Use indent for readability in the prompt
        )

    def create_prompt(
        self, query: str, children_data_context: str
    ) -> ChatPromptTemplate:  # FIXED: Added children_data_context
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
        PROMPT_TEMPLATE = f"""
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
        3.  Jika relevan, sertakan saran konkret dan aktivitas yang bisa dilakukan orang tua untuk membantu anak.
        4.  Selalu berikan saran yang sesuai dengan usia anak dan konteks budaya Indonesia.
        5.  Jika data yang diminta tidak tersedia atau relevan, jelaskan dengan sopan.
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
        )

        return formatted_prompt
