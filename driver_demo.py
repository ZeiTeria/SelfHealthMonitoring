from datetime import datetime, time

from kesehatan import (AbnormalVitalException, Bersepeda, Berenang, CatatanAktivitas, CatatanBerat, CatatanMakanan, CatatanTidur, CatatanVital, JalanKaki, Lari, Pengguna, RiwayatCatatan, catatan_tanggal)

hari = datetime(2026, 11, 12)
kemarin = datetime(2026, 11, 11)

print("=== 1. Polymorphism (method overriding) ===")
semua = [
    CatatanBerat(hari, 70),
    CatatanAktivitas(hari, Lari(), 30, 70),
    CatatanMakanan(hari, "Nasi goreng", 600),
    CatatanTidur(hari, time(23, 30), time(6, 0)),
    CatatanVital(hari, 120, 80, 72),
]

for c in semua:
    c.tampilkan()
    print(f"   {type(c).__name__}: kalori_masuk={c.kalori_masuk():.0f}, kalori_keluar={c.kalori_keluar():.0f}")

print("\n=== 1b. Polymorphism pada aktivitas (intensitas) ===")
for a in (JalanKaki(), Lari(), Bersepeda(), Berenang()):
    print(f"   {a.nama:<10} MET {a.met:<4} intensitas {a.intensitas()}")

print("\n=== 2. Encapsulation (atribut privat + property) ===")
p = Pengguna("Nicholas", 19, 175, 81, "L", 75, 2)
print("berat lewat property :", p.berat)
p.berat = 80
print("berat setelah setter :", p.berat)
for percobaan in ("p.berat = -5", "p.usia = 0", "p.jenis_kelamin = 'X'"):
    try:
        exec(percobaan)
    except ValueError as e:
        print(f"{percobaan:<24} -> ditolak: {e}")
try:
    CatatanBerat(hari, 70).berat = 99
except AttributeError:
    print("CatatanBerat.berat baca-saja -> AttributeError")

print("\n=== 3. Exception (custom + try-except) ===")
# Nilai di luar batas membuat cek_vital() melempar AbnormalVitalException. Exception itu ditangkap di sini supaya program tidak berhenti, lalu pesannya ditampilkan.
for sis, dia, nadi in [(120, 80, 70), (150, 95, 110)]:
    cek = CatatanVital(hari, sis, dia, nadi)
    try:
        cek.cek_vital()
        print(f"{sis}/{dia}, {nadi} bpm -> normal")
    except AbnormalVitalException as e:
        print(f"{sis}/{dia}, {nadi} bpm -> PERINGATAN: {e}")

print("\n=== 4. Iterator (__iter__ dan __next__) di for loop ===")
data = [CatatanBerat(datetime(2026, 10, d), 70 + d / 10) for d in (3, 1, 2)]
# Data sengaja dimasukkan tidak urut (3, 1, 2). Iterator menampilkannya urut dari tanggal terlama.
for c in RiwayatCatatan(data):
    c.tampilkan()

print("\n=== 5. Generator ===")
data.append(CatatanMakanan(kemarin, "Roti", 200))
data.append(CatatanMakanan(hari, "Nasi", 300))
# Generator hanya memberikan catatan pada tanggal yang diminta.
for c in catatan_tanggal(data, kemarin):
    c.tampilkan()
