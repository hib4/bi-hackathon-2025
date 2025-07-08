import json
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

class IntentClassifier:
    """
    A dedicated class for classifying user intent and extracting relevant parameters
    for backend API calls.
    """
    def __init__(self, llm_model_name: str = "gpt-4o-mini"):
        """
        Initializes the IntentClassifier with an LLM for classification.
        """
        self.llm = ChatOpenAI(
            model=llm_model_name,
            temperature=0.1, # Low temperature for deterministic classification
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )
        # Define the exact list of themes for the LLM to choose from, to ensure consistency
        self.financial_themes_list = [
            "Menabung", "Berbagi", "Kebutuhan vs Keinginan", "Instrumen Keuangan", "Kejujuran",
            "Kerja Keras", "Tanggung Jawab", "Perencanaan Keuangan", "Nilai Uang", "Konsep Dasar Uang",
            "Donasi", "Berbelanja dengan Bijak", "Kewirausahaan", "Gotong Royong", "Amanah", "Investasi"
        ]

        self.PROMPT_TEMPLATE = """
        Anda adalah asisten AI yang membantu mengklasifikasikan pertanyaan pengguna terkait performa belajar anak dalam literasi finansial atau informasi umum.
        Tugas Anda adalah mengidentifikasi niat pengguna dan mengekstrak parameter yang relevan.

        Daftar tema literasi finansial yang mungkin:
        [
            "Menabung", "Berbagi", "Kebutuhan vs Keinginan", "Instrumen Keuangan", "Kejujuran",
            "Kerja Keras", "Tanggung Jawab", "Perencanaan Keuangan", "Nilai Uang", "Konsep Dasar Uang",
            "Donasi", "Berbelanja dengan Bijak", "Kewirausahaan", "Gotong Royong", "Amanah", "Investasi"
        ]

        Kembalikan respons dalam format JSON murni, tanpa teks atau markdown tambahan, dengan struktur berikut:
        ```json
        {{
          "intent": "string (bisa 'general_query' atau 'child_performance_data')",
          "api_call_details": {{
            "api_type": "string (bisa 'concept-performance', 'performance-timeline', 'overall-statistics', atau null jika general_query)",
            "themes": "array of string (tema yang diminta, pilih dari daftar tema yang mungkin di atas, atau kosong jika tidak spesifik)",
            "time_unit": "string (bisa 'week', 'month', 'day', atau null)",
            "num_periods": "integer (jumlah periode yang diminta, atau null)",
            "start_date": "string (YYYY-MM-DD, atau null)",
            "end_date": "string (YYYY-MM-DD, atau null)",
            "child_id": "string (ID anak, selalu ambil dari input)",
            "api_call_reason": "string (Penjelasan singkat mengapa API ini harus dipanggil, jika intent adalah child_performance_data)"
          }}
        }}
        ```
        Catatan:
        - Jika niatnya 'general_query', field 'api_call_details' harus diisi dengan semua nilai null atau array kosong, kecuali 'child_id' yang tetap diisi.
        - Jika niatnya 'child_performance_data', field 'api_type' harus diisi sesuai API yang relevan.
        - Pastikan nama tema yang diekstrak persis sama dengan yang ada di daftar 'financial_themes_list' jika relevan.
        - Jika Anda tidak dapat mengidentifikasi API yang relevan atau parameter yang tepat untuk niat 'child_performance_data', tetapkan 'api_type' ke null dan 'themes' ke array kosong, dll., tetapi pertahankan struktur JSON.

        ---
        Pertanyaan pengguna: {query}
        ---
        ID Anak: {child_id}
        """

    def classify(self, query: str, child_id: str) -> dict:
        """
        Classifies the user's query and extracts parameters using the LLM.

        Args:
            query (str): The user's input query.
            child_id (str): The ID of the child for context.

        Returns:
            dict: Parsed JSON response from the LLM indicating intent and API details.
        """
        prompt_template = ChatPromptTemplate.from_template(self.PROMPT_TEMPLATE)
        formatted_prompt = prompt_template.format_messages(
            query=query,
            child_id=child_id
        )
        
        try:
            response = self.llm.invoke(formatted_prompt)
            print(f"Raw intent classification response: {response.content}")
            intent_data = json.loads(response.content.strip())
            
            # Ensure child_id is correctly set in api_call_details even if LLM misses it
            if "api_call_details" in intent_data:
                intent_data["api_call_details"]["child_id"] = child_id
            else: # If LLM completely failed to output api_call_details, add a default
                intent_data["api_call_details"] = {"child_id": child_id, "api_type": None, "themes": [], "time_unit": None, "num_periods": None, "start_date": None, "end_date": None, "api_call_reason": "Default fallback."}

            return intent_data
        except json.JSONDecodeError as e:
            print(f"Error parsing intent classification JSON: {e}")
            print(f"Raw response was: {response.content}")
            # Fallback for parsing errors: treat as general query
            return {"intent": "general_query", "api_call_details": {"child_id": child_id, "api_type": None, "themes": [], "time_unit": None, "num_periods": None, "start_date": None, "end_date": None, "api_call_reason": "JSON parsing error fallback."}}
        except Exception as e:
            print(f"An unexpected error occurred during intent classification: {e}")
            # Fallback for other errors
            return {"intent": "general_query", "api_call_details": {"child_id": child_id, "api_type": None, "themes": [], "time_unit": None, "num_periods": None, "start_date": None, "end_date": None, "api_call_reason": "General error fallback."}}

if __name__ == '__main__':
    # Simple test for the IntentClassifier
    classifier = IntentClassifier()

    print("--- Test 1: Child Performance Query (specific themes) ---")
    query_1 = "Bagaimana performa Adi di konsep menabung dan kejujuran?"
    child_id_1 = "adi_123"
    result_1 = classifier.classify(query_1, child_id_1)
    print(f"Result 1: {json.dumps(result_1, indent=2)}")

    print("\n--- Test 2: Child Performance Query (timeline) ---")
    query_2 = "Tolong tunjukkan perkembangan anak saya bulan lalu."
    child_id_2 = "budi_456"
    result_2 = classifier.classify(query_2, child_id_2)
    print(f"Result 2: {json.dumps(result_2, indent=2)}")

    print("\n--- Test 3: General Query ---")
    query_3 = "Apa saja tips untuk mengajarkan literasi finansial kepada anak usia 7 tahun?"
    child_id_3 = "sari_789" # Still pass child_id even if it's a general query
    result_3 = classifier.classify(query_3, child_id_3)
    print(f"Result 3: {json.dumps(result_3, indent=2)}")

    print("\n--- Test 4: Child Overall Statistics Query ---")
    query_4 = "Berikan ringkasan umum tentang progres belajar anak saya."
    child_id_4 = "dodi_101"
    result_4 = classifier.classify(query_4, child_id_4)
    print(f"Result 4: {json.dumps(result_4, indent=2)}")

    print("\n--- Test 5: Ambiguous/Unclear Query ---")
    query_5 = "Bagaimana ya?"
    child_id_5 = "eko_202"
    result_5 = classifier.classify(query_5, child_id_5)
    print(f"Result 5: {json.dumps(result_5, indent=2)}")