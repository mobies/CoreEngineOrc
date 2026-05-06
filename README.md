# 🦾 Core Engine Orchestrator

Core Engine Orchestrator adalah sistem AI multi-agent portable yang dirancang untuk otomatisasi manajemen proyek, dekomposisi tugas, dan eksekusi kode secara mandiri.

## ✨ Fitur Utama
- **Multi-Agent Orchestration:** Memecah tugas kompleks menjadi modul-modul kecil yang dieksekusi oleh agen spesialis.
- **Cloud Sync & Portability:** Sinkronisasi file proyek secara real-time menggunakan Firebase Storage, memungkinkan pengerjaan lintas perangkat.
- **Provider Agnostic:** Mendukung Google Gemini, OpenAI, dan Anthropic secara dinamis.
- **Secure Control Center:** Dashboard interaktif (Streamlit) dengan perlindungan password untuk mengelola proyek dan memantau kerja agen.

## 🚀 Cara Menjalankan
1. **Instalasi:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Konfigurasi:**
   - Salin `.env.example` ke `.env` dan isi API Key Anda.
   - Letakkan `serviceAccountKey.json` dari Firebase di folder root.
3. **Jalankan Dashboard:**
   ```bash
   streamlit run dashboard.py
   ```

## 📂 Struktur Proyek
- `src/core/orchestrator.py`: Otak utama perencana.
- `src/core/agent.py`: Agen pelaksana tugas (Sub-Agents).
- `src/core/state.py`: Pengelola status dan Cloud Sync.
- `docs/brain/`: Cache lokal untuk status proyek.

## 🛡️ Keamanan & Integritas
Sistem ini mematuhi protokol ketat yang tertuang dalam `docs/brain/context.md` untuk menjaga integritas kode dan mencegah penghapusan file tanpa izin user.

---
*Developed by mobies - 2026*
