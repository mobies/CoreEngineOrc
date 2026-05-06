from src.core.adapter import AIAdapter

def test_engine():
    print("--- Core Engine Connection Test ---")
    try:
        # Inisialisasi adapter
        adapter = AIAdapter()
        
        print(f"Mencoba menghubungi {adapter.provider}...")
        
        # Test sederhana: Tanya identitas
        response = adapter.chat("Halo, siapa kamu dan apa kemampuan utamamu?")
        
        print("\n--- Jawaban dari AI ---")
        print(response.content)
        print("\n✅ Koneksi Berhasil!")
        
    except Exception as e:
        print(f"\n❌ Error Terjadi: {e}")
        print("\nTips: Pastikan GOOGLE_API_KEY di file .env sudah benar.")

if __name__ == "__main__":
    test_engine()
