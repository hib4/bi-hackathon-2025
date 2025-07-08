import os
import shutil
import json
import requests
from datetime import datetime, timedelta

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from dotenv import load_dotenv

# Import the new IntentClassifier module
from intent_classifier import IntentClassifier 

load_dotenv()


class ChildMonitoringRAG:
    def __init__(
        self,
        data_dir: str,
        persist_directory: str,
        embedding_model_name: str = "text-embedding-3-small",
        llm_model_name: str = "gpt-3.5-turbo", # Main LLM for response generation
        similarity_threshold: float = 0.25,
        top_k: int = 3,
        backend_api_base_url: str = "http://localhost:8000/api",
    ):
        self.data_dir = data_dir
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model_name
        self.llm_model_name = llm_model_name # For the main conversational LLM
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k
        self.backend_api_base_url = backend_api_base_url

        # Initialize RAG components
        self.embeddings = OpenAIEmbeddings(
            model=self.embedding_model_name,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.vectorstore = None
        self.retriever = None

        # Initialize the IntentClassifier
        self.intent_classifier = IntentClassifier(llm_model_name="gpt-4o-mini") # Use a specific model for classification if desired
        
        # Main LLM for generating detailed responses
        self.main_llm = ChatOpenAI( 
            model=self.llm_model_name, 
            temperature=0.7, 
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

    def load_documents(self) -> list[Document]:
        """
        Load documents from the data directory (PDF file).
        Returns a list of Document objects, where each document is typically a page.
        """
        loader = PyPDFLoader(self.data_dir)
        documents = loader.load()

        print(f"Loaded {len(documents)} documents (pages) from {self.data_dir}")
        return documents

    def add_metadata(self, documents: list[Document]):
        """
        Adds relevant metadata to each document/page.
        Implement specific logic here based on your PDF's structure.
        """
        print("Adding metadata to documents (if any specific logic implemented)...")
        for i, doc in enumerate(documents):
            doc.metadata["source"] = os.path.basename(self.data_dir)
            doc.metadata["page"] = doc.metadata.get("page", i) + 1
        print("Metadata addition complete.")


    def setup_vector_store(self, documents: list[Document], chunk_size: int = 1000):
        """
        Create vector store and set up retriever.
        """
        self.add_metadata(documents) # Call the implemented method

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
            persist_directory=self.persist_directory, # Use self.persist_directory
        )
        print(f"Vector store created at {self.persist_directory}.")

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
                self._rebuild_vector_store()
        else:
            print("Creating new vector store...")
            self._rebuild_vector_store()

        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": self.top_k, "score_threshold": self.similarity_threshold},
        )
        print(
            f"Retriever initialized with top_k={self.top_k} and similarity threshold={self.similarity_threshold}."
        )
        print("RAG system initialized successfully.")

    def _rebuild_vector_store(self):
        """Helper method to rebuild the vector store."""
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
        print("Loading documents for new vector store...")
        documents = self.load_documents()
        print("Setting up new vector database...")
        self.setup_vector_store(documents)
        print(f"Vector store initialized with {self.vectorstore._collection.count()} documents.")


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
                    "unencountered": "array of string (Daftar konsep yang belum pernah ditemui anak dalam cerita, jika relevan)",
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
        
    def make_backend_api_call(self, api_details: dict) -> dict[str, str]:
        """
        Makes API calls to the backend based on the classified intent's details.
        Handles multiple API types if present in api_details['api_type'].
        Returns a dictionary mapping API type to its JSON response string.
        """
        child_id = api_details.get("child_id")
        api_types = api_details.get("api_type") # This is now a list

        if not child_id:
            return {"error": json.dumps({"error": "Child ID missing for API call."})}

        if not isinstance(api_types, list): # Ensure it's a list for iteration
            api_types = [api_types] if api_types is not None else []

        results = {}
        for api_type in api_types:
            url = f"{self.backend_api_base_url}/child/{child_id}"
            params = {}
            current_api_data_key = api_type # Key to store result in dictionary

            if api_type == "concept-performance":
                url += "/concept-performance"
                themes = api_details.get("themes")
                if themes:
                    params["themes"] = ",".join(themes)
            elif api_type == "performance-timeline":
                url += "/performance-timeline"
                if api_details.get("time_unit"):
                    params["time_unit"] = api_details["time_unit"]
                if api_details.get("num_periods") is not None:
                    params["num_periods"] = api_details["num_periods"]
                if api_details.get("start_date"):
                    params["start_date"] = api_details["start_date"]
                if api_details.get("end_date"):
                    params["end_date"] = api_details["end_date"]
            elif api_type == "overall-statistics":
                url += "/overall-statistics"
            else:
                print(f"Skipping unknown API type: {api_type}. Child ID: {child_id}")
                results[f"{api_type}_error"] = json.dumps({"error": f"Unknown API type requested: {api_type}"})
                continue # Skip to next api_type in the list

            print(f"Attempting API call to: {url} with params: {params} for type: {api_type}")
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                print(f"API call successful for {api_type}. Status: {response.status_code}")
                results[api_type] = json.dumps(response.json(), indent=2)
            except requests.exceptions.RequestException as e:
                print(f"API call failed for {api_type} at {url} with params {params}: {e}")
                results[f"{api_type}_error"] = json.dumps({"error": f"Gagal mengambil data untuk {api_type}: {e}"})

        # If no specific API types were identified or called, and it's not general_query,
        # return a default status if needed.
        if not results and (api_details.get("intent") == "child_performance_data" and not api_types):
            return {"status": json.dumps({"status": "no_specific_api_call_needed_for_child_performance_intent"})}

        return results


    def create_prompt(
        self, query: str, children_data_context: str, child_age: int
    ) -> ChatPromptTemplate:
        """
        Creates a formatted prompt for the LLM, combining children's data context and RAG context.
        """
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
            rag_context_text = "Tidak ada informasi umum yang sangat relevan ditemukan dari panduan."

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
        Harap berikan respons Anda dalam format JSON murni, tanpa teks atau *markdown* tambahan di luar blok JSON.
        Berikut adalah struktur JSON yang diharapkan:
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

    # Modify get_chat_response to handle combined data
    def get_chat_response(self, query: str, child_id: str, child_age: int) -> str:
        """
        Main function to get a chat response from the RAG system.
        Orchestrates intent classification, data fetching, and response generation.
        """
        intent_data = self.intent_classifier.classify(query, child_id)
        intent = intent_data.get("intent")
        api_details = intent_data.get("api_call_details", {})

        children_data_context = "" # Initialize as empty string

        if intent == "child_performance_data":
            # make_backend_api_call now returns a dict of results
            backend_results = self.make_backend_api_call(api_details)
            print(f"Backend results: {backend_results}")

            if backend_results and not backend_results.get("error"): # Check if actual data was returned
                # Combine all fetched data into a single JSON string for the LLM
                combined_data = {}
                for api_type, data_str in backend_results.items():
                    try:
                        combined_data[api_type] = json.loads(data_str)
                    except json.JSONDecodeError:
                        combined_data[api_type] = data_str # Keep as string if not valid JSON

                children_data_context = json.dumps(combined_data, indent=2)
                print(f"Combined children data context for LLM:\n{children_data_context}")
            else:
                children_data_context = json.dumps({"status": "failed_to_fetch_child_data", "details": backend_results})
                print(f"Failed to fetch child data: {children_data_context}")
        else:
            children_data_context = json.dumps({"status": "no_child_data_requested", "query_type": "general"})
            print("Intent classified as general_query. No child-specific data needed from backend.")

        # Create the main prompt
        final_prompt = self.create_prompt(query, children_data_context, child_age)

        # Invoke the main LLM
        try:
            response = self.main_llm.invoke(final_prompt)
            return response.content.strip()
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return json.dumps({"error": "Maaf, terjadi kesalahan saat memproses permintaan Anda."})


if __name__ == "__main__":
    # Ensure OPENAI_API_KEY is set in your .env file
    # Example usage:
    rag_system = ChildMonitoringRAG(
        data_dir="knowledge_base/pendidikan_literasi_finansial.pdf", # Make sure this path is correct
        persist_directory="chroma_db",
        llm_model_name="gpt-4o-mini", # Using gpt-4o-mini for main LLM as well for consistency in test
    )
    
    # Initialize RAG system (builds or loads vector store)
    rag_system.initialize_rag(rebuild=False) # Set to True for first run or when PDF content changes

    # --- Test Case 1: Child performance query ---
    print("\n--- Test 1: Child Performance Query ---")
    query_child_performance = "Bagaimana performa Adi di konsep menabung dan kejujuran?"
    child_id_test = "child_12345" # Replace with an actual child ID from your backend
    child_age_test = 8 # Example age for testing

    # Simulate backend responses for testing
    # You'd replace these with actual calls to your running backend
    def mock_make_backend_api_call(api_details):
        api_type = api_details.get("api_type")
        themes = api_details.get("themes", [])
        
        if api_type == "concept-performance":
            mock_data = {
                "user_id": child_id_test,
                "concept_performance": {}
            }
            if "Menabung" in themes or not themes:
                mock_data["concept_performance"]["Menabung"] = {
                    "total_decisions": 15, "correct_decisions": 12, "success_rate": 80.0,
                    "first_encounter": "2025-01-01T09:00:00Z", "last_encounter": "2025-01-20T10:30:00Z"
                }
            if "Kejujuran" in themes or not themes:
                mock_data["concept_performance"]["Kejujuran"] = {
                    "total_decisions": 10, "correct_decisions": 9, "success_rate": 90.0,
                    "first_encounter": "2025-01-05T11:00:00Z", "last_encounter": "2025-01-18T15:20:00Z"
                }
            if "Berbelanja dengan Bijak" in themes or not themes:
                mock_data["concept_performance"]["Berbelanja dengan Bijak"] = {
                    "total_decisions": 7, "correct_decisions": 3, "success_rate": 42.8,
                    "first_encounter": "2025-01-10T13:30:00Z", "last_encounter": "2025-01-19T14:00:00Z"
                }
            return json.dumps(mock_data, indent=2)
        elif api_type == "performance-timeline":
            return json.dumps({
                "user_id": child_id_test,
                "time_unit": "week",
                "timeline_data": [
                    {"period": "2025-01-20", "metrics": {"total_minutes_played": 60, "stories_completed": 4, "success_rate": 85}},
                    {"period": "2025-01-13", "metrics": {"total_minutes_played": 45, "stories_completed": 3, "success_rate": 70}}
                ]
            }, indent=2)
        elif api_type == "overall-statistics":
            return json.dumps({
                "user_id": child_id_test,
                "overall_stats": {
                    "total_stories_completed": 15, "total_learning_time_hours": 4.5,
                    "overall_success_rate": 78, "concepts_mastered": ["Menabung"],
                    "concepts_learning": ["Kejujuran"], "concepts_struggling": ["Berbelanja dengan Bijak"],
                    "account_created": "2025-01-01T09:00:00Z"
                }
            }, indent=2)
        return json.dumps({"error": "Mock API call not implemented for this type."})

    # Temporarily replace the actual API call method with the mock for testing
    rag_system.make_backend_api_call = mock_make_backend_api_call

    response_child_performance = rag_system.get_chat_response(query_child_performance, child_id_test, child_age_test)
    print("\n--- Response for Child Performance Query ---")
    print(response_child_performance)

    # --- Test Case 2: General query ---
    print("\n--- Test 2: General Query ---")
    query_general = "Bagaimana cara mengajarkan anak tentang pentingnya berbagi?"
    response_general = rag_system.get_chat_response(query_general, child_id_test, child_age_test) # child_id might not be used, but good to pass consistently
    print("\n--- Response for General Query ---")
    print(response_general)

    # --- Test Case 3: Mixed Query (e.g., struggling concept + advice) ---
    print("\n--- Test 3: Mixed Query ---")
    query_mixed = "Adi sepertinya kesulitan di konsep berbelanja dengan bijak. Apa saran Anda untuk saya?"
    response_mixed = rag_system.get_chat_response(query_mixed, child_id_test, child_age_test)
    print("\n--- Response for Mixed Query ---")
    print(response_mixed)