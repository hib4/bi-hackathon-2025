import json
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()


class IntentClassifier:
    """
    A dedicated class for classifying user intent and extracting relevant parameters
    for backend API calls.
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initializes the IntentClassifier with an LLM for classification.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.1, # Lower temperature for more deterministic responses
            api_key=SecretStr(api_key) if api_key else None,
        )
        # Define the exact list of themes for the LLM to choose from, to ensure consistency
        self.financial_themes_list = [
            "Menabung",
            "Berbagi",
            "Kebutuhan vs Keinginan",
            "Instrumen Keuangan",
            "Kejujuran",
            "Kerja Keras",
            "Tanggung Jawab",
            "Perencanaan Keuangan",
            "Nilai Uang",
            "Konsep Dasar Uang",
            "Donasi",
            "Berbelanja dengan Bijak",
            "Kewirausahaan",
            "Gotong Royong",
            "Amanah",
            "Investasi",
        ]

        self.PROMPT_TEMPLATE = """
        Anda adalah asisten AI yang membantu mengklasifikasikan pertanyaan pengguna terkait performa belajar anak dalam literasi finansial atau informasi umum.
        Tugas Anda adalah mengidentifikasi niat pengguna dan mengekstrak parameter yang relevan.

        Daftar tema literasi finansial yang mungkin:
        {financial_themes_list}
        
        Ada 3 niat utama yang perlu Anda identifikasi:
        1. general_query: Pertanyaan umum yang tidak spesifik tentang performa anak, seperti tips atau informasi umum yang masih berkaitan dengan literasi finansial.
        2. child_performance_data: Pertanyaan spesifik tentang performa anak dalam literasi finansial, yang bisa mencakup:
        - concept-performance: Untuk pertanyaan spesifik tentang performa anak di tema tertentu. (misalnya, "Bagaimana performa anak saya di konsep menabung?")
        - performance-timeline: Untuk pertanyaan tentang perkembangan anak dalam periode waktu tertentu (mingguan, bulanan)
        - overall-statistics: Untuk pertanyaan umum tentang statistik performa anak secara keseluruhan atau ringkasan umum.Pertanyaan tentang ringkasan umum atau statistik performa anak (misalnya, "Berikan ringkasan umum tentang progres belajar anak saya.")
        Untuk niat child_performance_data, Anda perlu mengekstrak parameter berikut:
        - api_type: Jenis API yang relevan untuk pertanyaan ini (bisa 'concept-performance', 'performance-timeline', 'overall-statistics', atau null jika tidak relevan).
        - themes: Daftar tema yang diminta (pilih dari daftar tema di atas, atau kosong jika tidak spesifik).
        - time_unit: Satuan waktu yang diminta (bisa 'week', 'month', 'day', atau null jika tidak relevan).
        - num_periods: Jumlah periode yang diminta (integer, atau null jika tidak relevan).
        - start_date: Tanggal mulai periode yang diminta (format YYYY-MM-DD, atau null jika tidak relevan).
        - end_date: Tanggal akhir periode yang diminta (format YYYY-MM-DD, atau null jika tidak relevan).    
        3. invalid_query: Pertanyaan yang tidak dapat dipahami atau tidak relevan dengan literasi finansial anak.
        
        Apabila niatnya adalah "general_query", Anda tidak perlu mengisi parameter API, cukup kembalikan nilai null atau array kosong untuk semua parameter API.

        Apabila query merupakan gabungan dari beberapa niat di child_performance_data, Anda harus mengembalikan semua niat tersebut dalam bentuk list array yang terpisah.
        Contoh:
        - Jika pengguna bertanya tentang performa anak di tema "Menabung" dan performa anak dalam 1 minggu terakhir, Anda harus mengembalikan dua entri dalam array:
        - Satu untuk 'concept-performance' dengan tema "Menabung" lalu juga kirim parameter waktu yang diperlukan (misalkan num_periods).
        - Satu untuk 'performance-timeline' dengan time_unit 'week' dan num_periods 1.
        
        Kembalikan respons dalam format JSON murni, tanpa teks atau markdown tambahan, dengan struktur berikut:
        ```json
        {{
            "intent": "string (bisa 'general_query' atau 'child_performance_data')",
            "api_call_details": [
                {{
                    "api_type": "string (bisa 'concept-performance', 'performance-timeline', 'overall-statistics', atau null jika general_query tanpa alasan spesifik)",
                    "themes": "array of string (tema yang diminta, pilih dari daftar tema yang mungkin di atas, atau kosong jika tidak spesifik)",
                    "time_unit": "string (bisa 'week', 'month', 'day', atau null)",
                    "num_periods": "integer (jumlah periode yang diminta dihitung dari hari ini, atau null)",
                    "start_date": "string (YYYY-MM-DD, atau null)",
                    "end_date": "string (YYYY-MM-DD, atau null)",
                }}
                <tambahkan api_call lain jika dbutuhkan, dalam bentuk list array, apabila user juga meminta lebih dari satu API atau jangka waktu berbeda>
            ]
        }}
        ```
        Catatan:
        - Jika niatnya 'general_query', field 'api_call_details' harus diisi dengan semua nilai null atau array kosong.
        - Jika niatnya 'child_performance_data', field 'api_type' harus diisi sesuai API yang relevan.
        - Jika niatnya 'invalid_query', kembalikan 'intent' sebagai 'invalid_query' dan 'api_call_details' dengan semua nilai null atau array kosong.
        - Pastikan nama tema yang diekstrak persis sama dengan yang ada di daftar 'financial_themes_list' jika relevan.
        - Jika Anda tidak dapat mengidentifikasi API yang relevan atau parameter yang tepat untuk niat 'child_performance_data', tetapkan 'api_type' ke null dan 'themes' ke array kosong, dll., tetapi pertahankan struktur JSON.

        ---
        Pertanyaan pengguna: {query}
        ---
        """

    def classify(self, query: str) -> dict:
        """
        Classifies the user's query and extracts parameters using the LLM.

        Args:
            query (str): The user's input query.

        Returns:
            dict: Parsed JSON response from the LLM indicating intent and API details.
        """
        prompt_template = ChatPromptTemplate.from_template(self.PROMPT_TEMPLATE)
        formatted_prompt = prompt_template.format_messages(
            query=query,
            financial_themes_list=", ".join(self.financial_themes_list)
        )
        # Attempt to invoke the LLM with the formatted prompt
        print(f"Classifying user query...")
        try:
            response = self.llm.invoke(formatted_prompt)
            intent_data = json.loads(response.content.strip()) # type: ignore
            # Print for debugging
            print(f"Intent classification result: {intent_data}")
            return intent_data
        except Exception as e:
            print(f"An unexpected error occurred during intent classification: {e}")
            # Fallback for other errors
            return {
                "intent": "general_query",
                "api_call_details": {
                    "api_type": None,
                    "themes": [],
                    "time_unit": None,
                    "num_periods": None,
                    "start_date": None,
                    "end_date": None,
                    "api_call_reason": "General error fallback.",
                },
            }
