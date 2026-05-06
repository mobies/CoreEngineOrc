# Core Engine Orchestrator - Project Roadmap

This document tracks the progress of building the Core Engine Orchestrator, designed for project automation with flexible AI provider integration and a multi-agent evaluation loop.

---

### 🟢 Fase 1: Fondasi & Portabilitas (Setup Awal)
*Langkah ini memastikan proyek bisa berjalan di laptop mana pun.*
- [x] **Inisialisasi Repositori Git:** Buat repo di GitHub/GitLab (Private).
- [x] **Struktur Folder "Project Brain":** Buat folder `docs/brain` untuk menyimpan status proyek (agar saya tidak lupa konteks).
- [x] **Setup Lingkungan Kerja:** 
    - [x] Install Python 3.10+ (Direkomendasikan untuk AI).
    - [x] Buat Virtual Environment (`venv`).
- [x] **Konfigurasi Keamanan:** 
    - [x] Buat file `.env.example` sebagai template API Key.
    - [x] Buat file `.gitignore` (Pastikan `.env` dan `venv/` tidak ter-upload).
- [x] **Instalasi Dependency Dasar:** (LangChain/LangGraph, Pydantic, Python-dotenv).

---

### 🟡 Fase 2: Arsitektur API Gateway (Fleksibilitas LLM)
*Langkah ini agar Anda bisa berganti-ganti model AI (Gemini, GPT, Claude, dll).*
- [ ] **Desain Model Adapter:** Membuat class abstraksi agar Core Engine tidak tergantung pada satu provider saja.
- [ ] **Integrasi API Multi-Provider:** Menambahkan modul untuk membaca API Key dari `.env` secara dinamis.
- [ ] **Uji Coba Koneksi:** Skrip sederhana untuk memastikan Core Engine bisa memanggil berbagai AI yang berbeda.

---

### 🟠 Fase 3: Core Engine - The Orchestrator (Otak Utama)
*Langkah ini membangun kemampuan AI untuk merencana dan menerjemahkan keinginan Anda.*
- [ ] **System Prompt Engineering:** Membuat instruksi "Master" untuk Core Engine sebagai Orchestrator.
- [ ] **Modul Planning (Task Decomposition):** AI harus bisa memecah perintah user menjadi daftar tugas JSON.
- [ ] **State Management:** Membangun sistem memori agar Orchestrator ingat apa yang sedang dikerjakan Sub-Agent.

---

### 🔵 Fase 4: Sub-Agent & Execution (Pelaksana)
*Langkah ini membuat "pekerja" yang akan menjalankan perintah dari Orchestrator.*
- [ ] **Pembuatan Template Sub-Agent:** Agen spesialis (Penulis Kode, Riset, Dokumentasi).
- [ ] **Protokol Komunikasi:** Menentukan cara Orchestrator mengirim "Prompt Perintah" ke Sub-Agent.
- [ ] **Execution Sandbox:** Tempat di mana Sub-Agent menjalankan tugasnya (file creation, command run).

---

### 🔴 Fase 5: Evaluation Loop (Quality Control)
*Langkah ini adalah fitur "Judge" untuk mengevaluasi hasil kerja agen.*
- [ ] **Implementasi Critic/Judge Agent:** Agen khusus yang tugasnya hanya memeriksa apakah hasil kerja agen lain sudah sesuai standar.
- [ ] **Feedback Loop Logic:** Jika hasil buruk, Orchestrator otomatis mengirim revisi ke Sub-Agent.
- [ ] **Final Approval System:** Mekanisme di mana sistem meminta persetujuan akhir dari Anda.

---

### 🟣 Fase 6: Antarmuka & Monitoring (User Control)
*Langkah ini agar Anda bisa mengontrol dan melihat prosesnya dengan mudah.*
- [ ] **Logging & Tracing:** Dashboard sederhana (CLI atau Web) untuk melihat "isi pikiran" setiap agen.
- [ ] **Manual Override:** Fitur agar Anda bisa menghentikan atau mengubah rencana di tengah jalan.
