from flask import Flask, jsonify, render_template

app = Flask(__name__)


def trapmf(x, abcd):
    a, b, c, d = abcd
    if x <= a or x >= d:
        return 0.0
    if b <= x <= c:
        return 1.0
    if a < x < b:
        return (x - a) / (b - a)
    if c < x < d:
        return (d - x) / (d - c)
    return 0.0

def trimf(x, abc):
    a, b, c = abc
    if x <= a or x >= c:
        return 0.0
    if x == b:
        return 1.0
    if a < x < b:
        return (x - a) / (b - a)
    if b < x < c:
        return (c - x) / (c - b)
    return 0.0

def fuzzy_score(harga_ribu, durasi, tunggu):
    h = harga_ribu
    d = durasi
    w = tunggu

    mu_harga_murah  = trapmf(h, [0, 0, 150, 350])
    mu_harga_sedang = trimf(h,  [100, 280, 520])
    mu_harga_mahal  = trapmf(h, [380, 550, 700, 700])

    mu_dur_cepat  = trapmf(d, [0, 0, 5, 7])
    mu_dur_sedang = trimf(d,  [5, 6.5, 9])
    mu_dur_lama   = trapmf(d, [7.5, 9, 13, 13])

    mu_tun_singkat = trapmf(w, [0, 0, 0.5, 1.5])
    mu_tun_sedang  = trimf(w,  [0.5, 1.5, 3])

    r_tinggi = min(mu_harga_murah, mu_dur_cepat, mu_tun_singkat)
    r_rendah = min(mu_harga_mahal, mu_dur_lama)
    r_cukup  = max(
        min(mu_harga_sedang, mu_dur_sedang),
        min(mu_harga_murah,  mu_dur_lama),
        min(mu_harga_mahal,  mu_dur_cepat),
        max(mu_harga_sedang, mu_dur_sedang, mu_tun_sedang),
    )

    numerator   = 0.0
    denominator = 0.0
    for z in range(0, 101):
        mu_r = min(trapmf(z, [0, 0, 40, 55]), r_rendah)
        mu_c = min(trimf(z,  [45, 65, 80]),   r_cukup)
        mu_t = min(trapmf(z, [70, 85, 100, 100]), r_tinggi)
        mu   = max(mu_r, mu_c, mu_t)
        numerator   += z * mu
        denominator += mu

    if denominator == 0:
        return 50
    return round(numerator / denominator)


def expert_advice(kelas, durasi, malam, tunggu):
    saran = []

    if kelas == 'Ekonomi' and durasi > 7:
        saran.append("💡 Perjalanan panjang di kelas Ekonomi. "
                     "Disarankan bawa bantal leher & air minum ekstra.")

    if malam:
        saran.append("🌙 Kereta Malam: Suhu AC biasanya lebih dingin, "
                     "persiapkan jaket atau pakaian hangat.")

    if tunggu < 1.0:
        saran.append("⚡ Waktu tunggu mepet! "
                     "Pastikan tiba di stasiun min. 45 menit sebelum keberangkatan.")

    return saran


STATIC_TRAINS = [
    {"id": 1, "nama": "Serayu Pagi",      "stasiun": "Pasar Senen", "dep": "06:00", "arr": "12:45", "kelas": "Ekonomi",   "harga": 69000,  "durasi": 6.75, "tunggu": 0.5,  "malam": False},
    {"id": 2, "nama": "Sawunggalih Utama","stasiun": "Gambir",      "dep": "07:30", "arr": "12:50", "kelas": "Eksekutif", "harga": 280000, "durasi": 5.33, "tunggu": 1.0,  "malam": False},
    {"id": 3, "nama": "Logawa",           "stasiun": "Pasar Senen", "dep": "08:15", "arr": "15:30", "kelas": "Ekonomi",   "harga": 79000,  "durasi": 7.25, "tunggu": 1.5,  "malam": False},
    {"id": 4, "nama": "Purwojaya",        "stasiun": "Gambir",      "dep": "09:00", "arr": "14:10", "kelas": "Eksekutif", "harga": 310000, "durasi": 5.17, "tunggu": 0.75, "malam": False},
    {"id": 5, "nama": "Wijayakusuma",     "stasiun": "Gambir",      "dep": "15:00", "arr": "20:15", "kelas": "Bisnis",    "harga": 175000, "durasi": 5.25, "tunggu": 1.25, "malam": False},
    {"id": 6, "nama": "Serayu Malam",     "stasiun": "Pasar Senen", "dep": "21:00", "arr": "04:30", "kelas": "Ekonomi",   "harga": 69000,  "durasi": 7.5,  "tunggu": 0.5,  "malam": True },
    {"id": 7, "nama": "Bima",             "stasiun": "Gambir",      "dep": "17:00", "arr": "23:20", "kelas": "Eksekutif", "harga": 480000, "durasi": 6.33, "tunggu": 2.0,  "malam": False},
    {"id": 8, "nama": "Fajar Utama",      "stasiun": "Pasar Senen", "dep": "05:30", "arr": "11:00", "kelas": "Bisnis",    "harga": 145000, "durasi": 5.5,  "tunggu": 0.5,  "malam": False},
]


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/trains', methods=['GET'])
def get_trains():
    try:
        result = []
        for t in STATIC_TRAINS:
            train = dict(t)

            train['score_base'] = fuzzy_score(
                harga_ribu=train['harga'] / 1000,
                durasi=train['durasi'],
                tunggu=train['tunggu'],
            )

            saran = expert_advice(
                kelas=train['kelas'],
                durasi=train['durasi'],
                malam=train['malam'],
                tunggu=train['tunggu'],
            )
            train['advice'] = (
                "<br>".join(saran) if saran
                else "✅ Jadwal sangat ideal. Pastikan dokumen perjalanan Anda sudah siap."
            )

            result.append(train)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)