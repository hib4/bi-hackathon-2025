import os
import shutil
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
import json
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file


class FinancialLiteracyRAG:
    def __init__(
        self,
        data_dir: str,
        persist_directory: str,
        model: str = "text-embedding-3-small",
    ):
        self.data_dir = data_dir
        self.persist_directory = persist_directory
        self.model = model

        # Initialize components
        self.embeddings = OpenAIEmbeddings(
            model=model,
            openai_api_key=os.getenv("OPENAI_API_KEY", "your_openai_api_key_here"),
        )
        self.vectorstore = None
        self.retriever = None

    def add_metadata(self, documents):
        for doc in documents:
            # Extract metadata from file path
            file_path = doc.metadata.get("source", "")

            # Age range detection based on file name
            if "4_7.md" in file_path:
                doc.metadata["age_range"] = "4-7"
                doc.metadata["min_age"] = 4
                doc.metadata["max_age"] = 7
            elif "8_10.md" in file_path:
                doc.metadata["age_range"] = "8-10"
                doc.metadata["min_age"] = 8
                doc.metadata["max_age"] = 10
            elif "11_12.md" in file_path:
                doc.metadata["age_range"] = "11-12"
                doc.metadata["min_age"] = 11
                doc.metadata["max_age"] = 12

            # Content type detection
            if "cultural_elements" in file_path:
                doc.metadata["content_type"] = "cultural"
            elif "financial_concepts" in file_path:
                doc.metadata["content_type"] = "financial"
            elif "stories" in file_path:
                doc.metadata["content_type"] = "story"

    def setup_vector_store(self, documents, top_k: int = 10, chunk_size: int = 600):
        """
        Create vector store and set up retriever
        """
        # Add metadata to documents
        self.add_metadata(documents)

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
            documents=splits, embedding=self.embeddings, persist_directory="./chroma_db"
        )

        # Set up retriever
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": top_k, "score_threshold": 0.1},
        )

    @staticmethod
    def build_output_format_template(user_id, age_group):
        """
        Build the output format template for the story
        """
        print("Building output format template...")
        print(f"User ID: {user_id}, Age Group: {age_group}")
        return json.dumps(
            {
                "user_id": user_id,
                "title": "<judul cerita akan diisi oleh LLM>",
                "theme": [
                    """
                    Menabung, Berbagi, Kebutuhan vs Keinginan, Instrumen Keuangan, Kejujuran, 
                    Kerja Keras, Tanggung Jawab, Perencanaan Keuangan, Nilai Uang, Konsep Dasar Uang,
                    Donasi, Berbelanja dengan Bijak, Kewirausahaan, Gotong Royong, Amanah, Investasi,
                    """
                    "<pilih 1 - 3 tema yang sesuai dari pilihan tersebut, pastikan sama dan konsisten dengan pilihan tersebut, kembalikan dalam bentuk list>"
                ],
                "language": "indonesian",
                "status": "in_progress",
                "age_group": age_group,
                "current_scene": 1,
                "created_at": None,
                "finished_at": None,
                "maximum_point": "<jumlah poin maksimum akan diisi oleh LLM (integer)>",
                "story_flow": {"total_scene": 0, "decision_point": [], "ending": []},
                "cover_img_url": None,
                "cover_img_description": "<buat deskripsi gambar sampul dalam bahasa Inggris>",
                "description": "<buat deskripsi cerita dalam bahasa Inggris>",
                "estimated_reading_time": "<perkiraan waktu membaca dalam bahasa Indonesia (dalam detik (integer))>",
                "characters": [
                    {
                        "name": "<buat nama karakter dalam bahasa Indonesia>",
                        "description": "<buat deskripsi karakter dalam bahasa Inggris, masukkan ciri fisik, sifat, dan peran dalam cerita>",
                    }
                ],
                "scene": [
                    {
                        "scene_id": 1,
                        "type": "narrative",
                        "img_url": None,
                        "img_description": "<buat deskripsi gambar yang sesuai dengan scene dalam bahasa Inggris>",
                        "voice_url": None,
                        "content": "<isi konten cerita yang sesuai dengan scene dalam bahasa Indonesia>",
                        "next_scene": "<buat nomor scene selanjutnya yang sesuai dengan alur cerita (integer)>",
                    },
                    {
                        "scene_id": 2,
                        "type": "decision_point",
                        "img_url": None,
                        "img_description": "<buat deskripsi gambar yang sesuai dengan scene dalam bahasa Inggris>",
                        "voice_url": None,
                        "content": "<isi konten cerita yang sesuai dengan scene dalam bahasa Indonesia>",
                        "branch": [
                            {
                                "choice": "baik",
                                "content": "<buat teks pilihan yang sesuai dengan konteks cerita dalam bahasa Indonesia, pilihan ini bersifat positif atau negatif>",
                                "moral_value": "<buat nilai moral yang sesuai dengan pilihan dalam bahasa Indonesia>",
                                "point": "<buat poin yang sesuai dengan pilihan, bisa positif atau negatif (integer)>",
                                "next_scene": "<buat nomor scene selanjutnya yang sesuai dengan percabangan (integer)>",
                            },
                            {
                                "choice": "buruk",
                                "content": "<buat teks pilihan yang sesuai dengan konteks cerita dalam bahasa Indonesia, pilihan ini bersifat negatif atau positif>",
                                "moral_value": "<buat nilai moral yang sesuai dengan pilihan dalam bahasa Indonesia>",
                                "point": "<buat poin yang sesuai dengan pilihan, bisa positif atau negatif (integer)>",
                                "next_scene": "<buat nomor scene selanjutnya yang sesuai dengan percabangan (integer)>",
                            },
                        ],
                        "selected_choice": None,
                    },
                    {
                        "scene_id": 3,
                        "type": "ending",
                        "img_url": None,
                        "img_description": "<buat deskripsi gambar yang sesuai dengan scene dalam bahasa Inggris>",
                        "voice_url": None,
                        "content": "<isi konten cerita yang sesuai dengan scene dalam bahasa Indonesia>",
                        "lesson_learned": "<buat pelajaran yang didapat dari cerita ini dalam bahasa Indonesia>",
                    },
                    "<more scenes can be added here>",
                ],
                "user_story": {
                    "visited_scene": [],
                    "choices": [],
                    "total_point": 0,
                    "finished_time": 0,
                },
            },
            indent=4,
        )

    def load_documents(self):
        """
        Load documents from the data directory
        """
        if not os.path.exists(self.data_dir):
            print(f"Warning: Data directory {self.data_dir} does not exist!")
            return []

        # Load documents from directory
        loader = DirectoryLoader(self.data_dir, glob="**/*.md")
        documents = loader.load()

        print(f"Loaded {len(documents)} documents from {self.data_dir}")
        return documents

    def initialize_rag(self, rebuild: bool = False):
        """
        Initialize the complete RAG system
        """
        print("Initializing RAG system...")
        print(f"Data directory: {self.data_dir}")
        # Check if the persist directory
        if os.path.exists(self.persist_directory) and not rebuild:
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
            )
            self.retriever = self.retriever = self.vector_store.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={"k": 10, "score_threshold": 0.1},
            )
            print("Using existing vector store from:", self.persist_directory)
            return True
        else:
            # Setup fresh vector store
            documents = self.load_documents()
            self.setup_vector_store(documents)
            print("RAG system initialized successfully!")
            return True


    @staticmethod
    def build_story_structure_rules(age_group: int) -> str:
        if 4 <= age_group <= 5:
            return (
                "Buat cerita dengan total 5 scene:\n"
                "- Scene 1: naratif pembuka\n"
                "- Scene 2: pengembangan\n"
                "- Scene 3: decision point (anak memilih baik/buruk)\n"
                "- Scene 4 & 5: masing-masing adalah ending berdasarkan pilihan\n"
            )
        elif 6 <= age_group <= 12:
            return (
                "Buat cerita dengan total 10 scene:\n"
                "- Scene 1: naratif pembuka\n"
                "- Scene 2: decision point pertama\n"
                "   - Pilihan baik → scene 3 (berikan reward disini) → scene 4\n"
                "   - Pilihan buruk → scene 5 (berikan koreksi atau konsekuensi disini) → scene 6\n"
                "- Scene 4: decision point kedua untuk cabang baik\n"
                "   - Pilihan baik → scene 7 (ending terbaik)\n"
                "   - Pilihan buruk → scene 8 (ending cukup baik)\n"
                "- Scene 6: decision point kedua untuk cabang buruk\n"
                "   - Pilihan baik → scene 9 (ending cukup buruk)\n"
                "   - Pilihan buruk → scene 10 (ending terburuk)\n"
            )
        else:
            return "Gunakan struktur 10 scene default."

    def filter_retrieved_docs(self, docs, age, k=6):
        """
        Filter and prioritize documents, prioritizing matching age group and financial concepts before cultural elements and stories.
        """
        # Priority 1: Exact age match
        age_exact = [
            doc
            for doc in docs
            if doc.metadata.get("min_age", 0) <= age <= doc.metadata.get("max_age", 12)
            and doc.metadata.get("content_type") == "financial"
        ]

        # Priority 2: Financial core concepts
        financial_concepts = [
            doc
            for doc in docs
            if doc.metadata.get("content_type") == "financial"
            and "core_concepts" in doc.metadata.get("source")
        ]

        # Priority 3: Cultural elements and stories (universal content)
        cultural_story = [
            doc
            for doc in docs
            if doc.metadata.get("content_type") in ["cultural", "story"]
            and doc not in age_exact
        ]

        # Priority 4: Everything else
        other_content = [
            doc
            for doc in docs
            if doc not in age_exact
            and doc not in financial_concepts
            and doc not in cultural_story
        ]

        # Combine with limits to ensure balance
        prioritized_docs = (
            age_exact[:3]  # Max 3 from exact age
            + financial_concepts[:2]  # Max 2 from financial core concepts
            + cultural_story[:2]  # Max 2 cultural/story
            + other_content  # Fill remaining
        )[:k]

        print(f"Filtering for age {age}:")
        print(f"  Age-appropriate: {len(age_exact)}")
        print(
            f" Age-appropriate documents: {[doc.metadata.get('source', 'Unknown') for doc in age_exact]}"
        )

        print(f"  Adjacent financial: {len(financial_concepts)}")
        print(
            f"  Financial concepts documents: {[doc.metadata.get('source', 'Unknown') for doc in financial_concepts]}"
        )

        print(f"  Cultural/Story: {len(cultural_story)}")
        print(
            f"  Cultural/Story documents: {[doc.metadata.get('source', 'Unknown') for doc in cultural_story]}"
        )

        print(f"  Universal content: {len(other_content)}")
        print(f"  Other documents: {[doc.metadata.get('source', 'Unknown') for doc in other_content]}")
        
        print(f"  Final selection: {len(prioritized_docs)} documents")
        print(f"  Selected documents: {[doc.metadata.get('source', 'Unknown') for doc in prioritized_docs]}")
        return prioritized_docs

    def create_prompt(self, query, user_id, age: int):  # Change parameter to int
        PROMPT_TEMPLATE = """
        You are an expert Indonesian storyteller specializing in teaching financial literacy to children.

        Generate a JSON-formatted interactive story in **Bahasa Indonesia** for children aged {age}, with:
        - Indonesian character names and culturally relevant settings (e.g., warung, pasar)
        - Age-appropriate financial literacy lessons (saving, budgeting, honesty, etc.)
        - Two decision points (unless otherwise noted), each with two choices, that affect the story ending

        You can use the following context to inform your story, but you are not limited to it. Feel free to create engaging and educational content based on the query provided.
        ### Context:
        {context}
        
        ### Query:
        {query}

        ### Story Structure Instructions:
        {structure_rules}

        ### General Instructions:
        1. Use simple and engaging Indonesian suitable for age {age}
        2. Scene types must be: "narrative", "decision_point", or "ending"
        3. Choices should lead to consequences that are constructive but realistic
        4. Provide at least two different endings with different moral outcomes
        5. Do not include markdown or explanations—just clean JSON
        6. For higher age groups (11 - 12), the decision points can be more like a quiz to test their understanding for the said concept.
        For example: "Apa itu pegadaian ?"

        ### Format:
        {output_format}
        """

        # Get relevant context from retriever
        context_docs = []
        if self.retriever:
            try:
                context_docs = self.retriever.invoke(query)
                print(f"Retrieved {len(context_docs)} relevant documents")

                # Filter and prioritize documents based on age (now int)
                prioritized_docs = self.filter_retrieved_docs(context_docs, age)

                # Extract content from documents
                context = [doc.page_content for doc in prioritized_docs]
            except Exception as e:
                print(f"Error retrieving documents: {e}")
                context = ["Tidak ada konteks yang relevan ditemukan."]
        else:
            print(
                "Retriever not initialized. Make sure to call initialize_rag() first."
            )
            context = ["Tidak ada konteks yang relevan ditemukan."]

        if not context:
            context = ["Tidak ada konteks yang relevan ditemukan."]

        output_format = self.build_output_format_template(
            user_id=user_id, age_group=age  # Keep as int
        )
        # Use age directly for structure rules
        structure_rules = self.build_story_structure_rules(age)
        # Create and format the prompt
        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        formatted_prompt = prompt.format_prompt(
            context=context,
            query=query,
            age=age,
            output_format=output_format,
            structure_rules=structure_rules,
        )

        return formatted_prompt