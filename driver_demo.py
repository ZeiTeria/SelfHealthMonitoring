"""Driver code UTS: membuktikan polymorphism, encapsulation, exception, dan iterator.
Jalankan: python driver_demo.py   (tidak butuh input)
"""
from datetime import datetime, time

from kesehatan import (AbnormalVitalException, Berenang, CatatanAktivitas, CatatanBerat,
                       CatatanMakanan, CatatanTidur, CatatanVital, JalanKaki, Lari,
                       Pengguna, RiwayatCatatan, catatan_tanggal)

hari = datetime(2026, 10, 9)
kemarin = datetime(2026, 10, 8)

print("=== 1. Polymorphism (method overriding) ===")
semua = [
    CatatanBerat(hari, 70),
    CatatanAktivitas(hari, Lari(), 30, 70),
    CatatanMakanan(hari, "Nasi goreng", 600),
    CatatanTidur(hari, time(23, 30), time(6, 0)),
    CatatanVital(hari, 120, 80, 72),
]
for c in semua:  # satu pemanggilan, perilaku berbeda tiap kelas
    c.tampilkan()
    print(f"   {type(c).__name__}: kalori_masuk={c.kalori_masuk():.0f}, kalori_keluar={c.kalori_keluar():.0f}")

print("\n=== 2. Encapsulation (atribut privat + property) ===")
p = Pengguna("Budi", 20, 170, 70, "L", 65, 2)
print("berat lewat property :", p.berat)
p.berat = 68
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
for sis, dia, nadi in [(120, 80, 70), (150, 95, 110)]:
    cek = CatatanVital(hari, sis, dia, nadi)
    try:
        cek.cek_vital()
        print(f"{sis}/{dia}, {nadi} bpm -> normal")
    except AbnormalVitalException as e:
        print(f"{sis}/{dia}, {nadi} bpm -> PERINGATAN: {e}")

print("\n=== 4. Iterator (__iter__ dan __next__) di for loop ===")
data = [CatatanBerat(datetime(2026, 10, d), 70 + d / 10) for d in (3, 1, 2)]
for c in RiwayatCatatan(data):  # otomatis terurut tanggal
    c.tampilkan()

print("\n=== 5. Generator ===")
data.append(CatatanMakanan(kemarin, "Roti", 200))
for c in catatan_tanggal(data, kemarin):
    c.tampilkan()
