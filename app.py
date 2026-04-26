import collections
import collections.abc
collections.Mapping = collections.abc.Mapping 

from flask import Flask, jsonify, render_template
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from experta import *

app = Flask(__name__)


harga = ctrl.Antecedent(np.arange(0, 701, 1), 'harga') 
durasi = ctrl.Antecedent(np.arange(0, 13, 0.1), 'durasi') 
tunggu = ctrl.Antecedent(np.arange(0, 7, 0.1), 'tunggu')
skor = ctrl.Consequent(np.arange(0, 101, 1), 'skor')

harga['murah'] = fuzz.trapmf(harga.universe, [0, 0, 150, 350])
harga['sedang'] = fuzz.trimf(harga.universe, [100, 280, 520])
harga['mahal'] = fuzz.trapmf(harga.universe, [380, 550, 700, 700])

durasi['cepat'] = fuzz.trapmf(durasi.universe, [0, 0, 5, 7])
durasi['sedang'] = fuzz.trimf(durasi.universe, [5, 6.5, 9])
durasi['lama'] = fuzz.trapmf(durasi.universe, [7.5, 9, 13, 13])

tunggu['singkat'] = fuzz.trapmf(tunggu.universe, [0, 0, 0.5, 1.5])
tunggu['sedang'] = fuzz.trimf(tunggu.universe, [0.5, 1.5, 3])
tunggu['lama'] = fuzz.trapmf(tunggu.universe, [2, 3.5, 7, 7])

skor['rendah'] = fuzz.trapmf(skor.universe, [0, 0, 40, 55])
skor['cukup'] = fuzz.trimf(skor.universe, [45, 65, 80])
skor['tinggi'] = fuzz.trapmf(skor.universe, [70, 85, 100, 100])

rule1 = ctrl.Rule(harga['murah'] & durasi['cepat'] & tunggu['singkat'], skor['tinggi'])
rule2 = ctrl.Rule(harga['mahal'] & durasi['lama'], skor['rendah'])
rule3 = ctrl.Rule(harga['sedang'] & durasi['sedang'], skor['cukup'])
rule4 = ctrl.Rule(harga['murah'] & durasi['lama'], skor['cukup'])
rule5 = ctrl.Rule(harga['mahal'] & durasi['cepat'], skor['cukup'])
rule_default = ctrl.Rule(harga['sedang'] | durasi['sedang'] | tunggu['sedang'], skor['cukup'])

skor_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule_default])
mesin_fuzzy = ctrl.ControlSystemSimulation(skor_ctrl)


class FaktaKereta(Fact):
    pass

class PakarKereta(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.saran = []

    @Rule(FaktaKereta(kelas='Ekonomi', durasi=P(lambda x: x > 7)))
    def rule_ekonomi(self):
        self.saran.append("💡 Perjalanan panjang di kelas Ekonomi. Disarankan bawa bantal leher & air minum ekstra.")

    @Rule(FaktaKereta(malam=True))
    def rule_malam(self):
        self.saran.append("🌙 Kereta Malam: Suhu AC biasanya lebih dingin, persiapkan jaket atau pakaian hangat.")

    @Rule(FaktaKereta(tunggu=P(lambda x: x < 1.0)))
    def rule_tunggu(self):
        self.saran.append("⚡ Waktu tunggu mepet! Pastikan tiba di stasiun min. 45 menit sebelum keberangkatan.")


# Data kereta statis (pengganti database MySQL)
STATIC_TRAINS = [
    {"id": 1, "nama": "Serayu Pagi",     "stasiun": "Pasar Senen", "dep": "06:00", "arr": "12:45", "kelas": "Ekonomi",   "harga": 69000,  "durasi": 6.75, "tunggu": 0.5,  "malam": False},
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
        import copy
        trains = copy.deepcopy(STATIC_TRAINS)

        mesin_pakar = PakarKereta()

        for t in trains:
            mesin_fuzzy.input['harga'] = t['harga'] / 1000
            mesin_fuzzy.input['durasi'] = float(t['durasi'])
            mesin_fuzzy.input['tunggu'] = float(t['tunggu'])

            try:
                mesin_fuzzy.compute()
                t['score_base'] = round(mesin_fuzzy.output['skor'])
            except:
                t['score_base'] = 50

            mesin_pakar.reset()
            mesin_pakar.saran = []
            mesin_pakar.declare(FaktaKereta(
                kelas=t['kelas'],
                durasi=float(t['durasi']),
                malam=bool(t['malam']),
                tunggu=float(t['tunggu'])
            ))
            mesin_pakar.run()

            if len(mesin_pakar.saran) == 0:
                t['advice'] = "✅ Jadwal sangat ideal. Pastikan dokumen perjalanan Anda sudah siap."
            else:
                t['advice'] = "<br>".join(mesin_pakar.saran)

        return jsonify(trains)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)