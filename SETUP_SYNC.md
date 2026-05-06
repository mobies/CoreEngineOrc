# Panduan Sinkronisasi Antar Perangkat

Dokumen ini menjelaskan cara melanjutkan pengerjaan **Core Engine Orc** di komputer baru.

## 1. Persiapan di Komputer Baru
1.  **Clone Repositori:**
    ```bash
    git clone https://github.com/mobies/CoreEngineOrc.git
    cd CoreEngineOrc
    ```
2.  **Setup Virtual Environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

## 2. Pemindahan Kunci Rahasia (Manual)
Karena alasan keamanan, file berikut tidak ada di GitHub. Anda harus menyalinnya dari komputer lama atau membuatnya ulang:
1.  **`.env`**: Salin dari komputer lama atau gunakan `.env.example` sebagai referensi.
2.  **`serviceAccountKey.json`**: Letakkan di folder root proyek.

## 3. Sinkronisasi Proyek (Otomatis)
Setelah Anda menjalankan dashboard:
```bash
streamlit run dashboard.py
```
Sistem akan otomatis:
*   Mendeteksi koneksi Firebase Storage.
*   Mendownload semua file rencana proyek (`plan_*.json`) yang ada di Cloud ke folder lokal `docs/brain/`.
*   Anda bisa langsung melanjutkan proyek yang tertunda tanpa kehilangan data.

## 4. Tips Pengerjaan
*   Selalu lakukan `git pull` sebelum memulai pengerjaan di komputer baru.
*   Selalu lakukan `git add .`, `git commit`, dan `git push` setelah selesai pengerjaan agar perubahan kode tersimpan.
*   Data proyek (JSON) tidak perlu di-push ke Git, karena sudah ditangani oleh Firebase Cloud Sync secara otomatis.
