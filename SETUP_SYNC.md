# Panduan Sinkronisasi Proyek (Multi-Device Setup)

Gunakan panduan ini setiap kali Anda berpindah ke laptop/komputer baru agar pengerjaan **Core Engine Orchestrator** tetap berlanjut dengan mulus.

---

## 1. Langkah di Komputer Baru (Pertama Kali)

1.  **Clone Repositori:**
    ```powershell
    git clone https://github.com/mobies/CoreEngineOrc.git
    cd CoreEngineOrc
    ```

2.  **Setup Environment:**
    *   Pastikan Python 3.10+ sudah terinstall.
    *   Buat Virtual Environment: `python -m venv venv`
    *   Aktifkan venv: `.\venv\Scripts\activate` (Windows)
    *   Install Dependency: `pip install -r requirements.txt` (Jika file sudah ada).

3.  **Setup API Keys:**
    *   Copy file `.env.example` menjadi `.env`.
    *   Isi API Key Anda di dalam file `.env`. **(Jangan pernah push file .env ke GitHub!)**

---

## 2. Alur Kerja Harian (Agar Tetap Sync)

Selalu lakukan urutan ini setiap kali mulai dan selesai coding:

### Sebelum Mulai (Start):
```powershell
git pull origin main
```
*Tujuannya: Mengambil update terbaru dari cloud, termasuk "ingatan" saya di folder `docs/brain`.*

### Setelah Selesai (Finish):
```powershell
git add .
git commit -m "Catatan progres Anda"
git push origin main
```
*Tujuannya: Menyimpan progres dan memastikan "ingatan" saya di `docs/brain/context.md` terupdate ke cloud.*

---

## 3. Catatan untuk Antigravity (AI Assistant)
Saat pertama kali membuka proyek ini di komputer baru, cukup katakan:
> *"Buka file `docs/brain/context.md` dan `ROADMAP.md` untuk sinkronisasi konteks."*

Saya akan langsung memahami posisi terakhir proyek dan siap melanjutkan tugas.
