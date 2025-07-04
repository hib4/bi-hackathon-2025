import os
import shutil
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
import json


class FinancialLiteracyRAG:
    def __init__(
        self, data_dir: str, persist_directory: str, model: str = "gpt-4o-mini"
    ):
        self.data_dir = data_dir
        self.persist_directory = persist_directory
        self.model = model

        # Initialize components
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None

    def setup_vector_store(self, documents, top_k: int = 5):
        """
        Create vector store and set up retriever
        """
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", "", "-"],
        )

        splits = text_splitter.split_documents(documents)

        # Create vector store
        self.vector_store = Chroma.from_documents(
            documents=splits, embedding=self.embeddings, persist_directory="./chroma_db"
        )

        # Set up retriever
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": top_k}
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
                "tema": [],
                "language": "indonesian",
                "status": "in_progress",
                "age_group": age_group,
                "current_scene": 1,
                "created_at": None,
                "finished_at": None,
                "maximum_point": "<jumlah poin maksimum akan diisi oleh LLM (integer)>",
                "story_flow": {"total_scene": 0, "decision_point": [], "ending": []},
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
                        "content": "Di warung, Pak Budi sedang sibuk melayani banyak pembeli. Saat memberikan kembalian, Pak Budi terburu-buru dan salah menghitung. Dia memberikan kembalian Rp 10.000 padahal seharusnya hanya Rp 5.000. Sari menyadari kesalahan ini. Apa yang sebaiknya Sari lakukan?",
                        "branch": [
                            {
                                "choice": "baik",
                                "teks": "<buat teks pilihan yang sesuai dengan konteks cerita dalam bahasa Indonesia, pilihan ini bersifat positif atau negatif>",
                                "moral_value": "<buat nilai moral yang sesuai dengan pilihan dalam bahasa Indonesia>",
                                "point": "<buat poin yang sesuai dengan pilihan, bisa positif atau negatif (integer)>",
                                "next_scene": "<buat nomor scene selanjutnya yang sesuai dengan percabangan (integer)>",
                            },
                            {
                                "choice": "buruk",
                                "teks": "<buat teks pilihan yang sesuai dengan konteks cerita dalam bahasa Indonesia, pilihan ini bersifat negatif atau positif>",
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

    def initialize_rag(self):
        """
        Initialize the complete RAG system
        """
        print("Initializing RAG system...")
        
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)

        # Load documents
        documents = self.load_documents()

        if not documents:
            print("No documents found! RAG system will work without context.")
            return False

        # Setup vector store and retriever
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
            return "Gunakan struktur 5 scene default."

    def create_prompt(self, query, user_id, age_group):
        output_format = self.build_output_format_template(
            user_id=user_id, age_group=age_group
        )

        # Add rule-based structure guidance
        if isinstance(age_group, str) and "-" in age_group:
            age_num = int(age_group.split("-")[0])
        else:
            age_num = int(age_group)

        structure_rules = self.build_story_structure_rules(age_num)

        PROMPT_TEMPLATE = """
        You are an expert Indonesian storyteller specializing in teaching financial literacy to children.

        Generate a JSON-formatted interactive story in **Bahasa Indonesia** for children aged {age_group}, with:
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
        1. Use simple and engaging Indonesian suitable for age {age_group}
        2. Scene types must be: "narrative", "decision_point", or "ending"
        3. Choices should lead to consequences that are constructive but realistic
        4. Provide at least two different endings with different moral outcomes
        5. Do not include markdown or explanations—just clean JSON

        ### Format:
        {output_format}
        """

        # Get relevant context from retriever
        context_docs = []
        if self.retriever:
            try:
                context_docs = self.retriever.invoke(query)
                print(f"Retrieved {len(context_docs)} relevant documents")
                # Extract content from documents
                context = [doc.page_content for doc in context_docs]
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

        # Create and format the prompt
        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        formatted_prompt = prompt.format_prompt(
            context=context,
            query=query,
            output_format=output_format,
            age_group=age_group,
            structure_rules=structure_rules,
        )

        return formatted_prompt
