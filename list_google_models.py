import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def list_my_models():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY tidak ditemukan di .env")
        return

    genai.configure(api_key=api_key)
    
    print("--- Daftar Model Gemini yang Tersedia untuk API Key Anda ---")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
        print("\nJika daftar di atas kosong, berarti API Key Anda belum memiliki izin untuk model generatif.")
    except Exception as e:
        print(f"\n[ERROR] Gagal mengambil daftar model: {e}")

if __name__ == "__main__":
    list_my_models()
