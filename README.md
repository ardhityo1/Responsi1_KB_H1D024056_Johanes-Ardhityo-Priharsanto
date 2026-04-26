# SmartRail — Asisten Efisiensi Perjalanan Kereta

Aplikasi ini menggunakan **Logika Fuzzy** dan **Sistem Pakar** untuk memberikan rekomendasi tiket kereta api terbaik berdasarkan harga, durasi perjalanan, dan waktu tunggu.

Untuk memastikan aplikasi ini bisa di-deploy dengan lancar di **Vercel** (serverless environment), kami telah menghapus library berat (`scikit-fuzzy` dan `experta`) beserta koneksi database MySQL, dan menggantinya dengan implementasi **Pure Python**.

## 📌 Letak Logika AI di Kode (`app.py`)

Seluruh algoritma AI telah ditulis ulang ke dalam fungsi dasar Python di file `app.py`. Berikut adalah rinciannya:

### 1. Logika Fuzzy (Mamdani)
Logika Fuzzy digunakan untuk menghitung **Skor Efisiensi (0-100)** dari setiap tiket kereta.
- **Letak Fungsi:** `fuzzy_score(harga_ribu, durasi, tunggu)` (Baris ke-33 di `app.py`)
- **Fungsi Keanggotaan (Membership):** Menggunakan fungsi kustom `trapmf()` (Trapesium) dan `trimf()` (Segitiga) untuk variabel Harga, Durasi, dan Waktu Tunggu.
- **Fuzzy Rules:** Berada di dalam fungsi `fuzzy_score`. Aturan ini menggabungkan variabel-variabel menggunakan operator `min()` untuk logika AND dan `max()` untuk logika OR.
- **Defuzzifikasi:** Menggunakan metode **Centroid** (titik berat) menggunakan perulangan integral diskrit `for z in range(0, 101):`.

### 2. Sistem Pakar (Rule-Based)
Sistem Pakar digunakan untuk memberikan **Saran/Advice Spesifik** kepada pengguna berdasarkan karakteristik jadwal kereta.
- **Letak Fungsi:** `expert_advice(kelas, durasi, malam, tunggu)` (Baris ke-85 di `app.py`)
- **Aturan (Rules):** Ditulis dalam bentuk `if` statement murni. Contoh:
  - *JIKA kelas Ekonomi DAN durasi > 7 jam MAKA sarankan bawa bantal leher.*
  - *JIKA kereta malam MAKA sarankan bawa jaket.*

### 3. Basis Pengetahuan (Database)
Karena MySQL tidak bisa diakses dari Vercel tanpa cloud hosting tambahan, data kereta diubah menjadi data array statis.
- **Letak Data:** Variabel `STATIC_TRAINS` (Baris ke-110 di `app.py`)

---

## 🚀 Cara Menjalankan Secara Lokal

1. Pastikan Anda memiliki Python yang sudah ter-install.
2. Install framework web (Flask):
   ```bash
   pip install Flask
   ```
3. Jalankan aplikasi:
   ```bash
   python app.py
   ```
4. Buka browser dan pergi ke `http://localhost:5000`
