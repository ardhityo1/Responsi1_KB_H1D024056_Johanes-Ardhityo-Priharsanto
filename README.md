Aplikasi ini menggunakan **Logika Fuzzy** dan **Sistem Pakar** untuk memberikan rekomendasi tiket kereta api terbaik berdasarkan harga, durasi perjalanan, dan waktu tunggu.

## Letak Logika AI di Kode (`app.py`)

Rincian letak bagian logika fuzzy dan logika sistem pakar

### 1. Logika Fuzzy
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

