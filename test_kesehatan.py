from datetime import datetime, time

from kesehatan import (AbnormalVitalException, Berenang, CatatanAktivitas, CatatanBerat,
                       CatatanHarian, CatatanMakanan, CatatanTidur, CatatanVital, Lari,
                       Pengguna, RiwayatCatatan, catatan_tanggal, pemantau_vital)


def harus_error(kelas, *args):
    try:
        kelas(*args)
    except ValueError:
        return
    raise SystemExit(f"harusnya ValueError: {kelas.__name__}{args}")


p = Pengguna("A", 20, 170, 70, "L", 65, 2)
assert round(p.hitung_bmi(), 1) == 24.2 and p.kategori_bmi() == "Normal"
assert p.hitung_bmr() == 1667.5
assert p.hitung_tdee() == 1667.5 * 1.375 and round(p.hitung_tdee(1), 1) == 2001.0
assert Pengguna("B", 20, 160, 50, "P", 50, 1).hitung_bmr() == 500 + 1000 - 100 - 161
assert [Pengguna("C", 20, 170, b, "L", 60, 1).kategori_bmi() for b in (45, 60, 75, 95)] == \
    ["Kurus", "Normal", "Gemuk", "Obesitas"]
for bad in [("", 20, 170, 70, "L", 65, 2), ("A", 0, 170, 70, "L", 65, 2),
            ("A", 20, 170, 70, "X", 65, 2), ("A", 20, 170, 70, "L", 65, 6),
            ("A", 20, 17, 70, "L", 65, 2), ("A", 20, 170, -1, "L", 65, 2)]:
    harus_error(Pengguna, *bad)
harus_error(p.hitung_tdee, 9)

t = datetime(2026, 10, 9)
assert Lari().hitung_kalori(70, 30) == 9.8 * 70 * 0.5
assert CatatanAktivitas(t, Berenang(), 60, 70).kalori_keluar() == 560
harus_error(CatatanAktivitas, t, Lari(), 0, 70)
harus_error(CatatanBerat, t, 0)
harus_error(CatatanMakanan, t, "x", -5)
assert CatatanMakanan(t, "x", 500).kalori_masuk() == 500
assert CatatanMakanan(t, "x", 500).kalori_keluar() == 0
assert CatatanTidur(t, time(23, 30), time(6, 0)).durasi_jam() == 6.5
assert CatatanTidur(t, time(22, 0), time(23, 0)).durasi_jam() == 1
harus_error(CatatanTidur, t, "23:00", time(6, 0))

CatatanVital(t, 120, 80, 70).cek_vital()
for v in [(150, 80, 70), (120, 95, 70), (120, 80, 110), (80, 80, 70)]:
    c = CatatanVital(t, *v)
    try:
        c.cek_vital()
        raise SystemExit(f"harusnya abnormal: {v}")
    except AbnormalVitalException:
        assert c.status == "ABNORMAL"
harus_error(CatatanVital, t, 0, 80, 70)

try:
    CatatanHarian(t)
    raise SystemExit("ABC tidak boleh diinstansiasi")
except TypeError:
    pass

def bmi_kategori(bmi):
    return Pengguna("X", 20, 100, bmi, "L", 20, 1).kategori_bmi()
assert [bmi_kategori(b) for b in (18.4, 18.5, 25, 26, 27, 28)] == \
    ["Kurus", "Normal", "Normal", "Gemuk", "Gemuk", "Obesitas"]

p.berat = 68
assert p.berat == 68 and p._berat == 68
harus_error(setattr, p, "berat", -5)
assert p.berat == 68
try:
    CatatanBerat(t, 70).berat = 99
    raise SystemExit("berat catatan harusnya baca-saja")
except AttributeError:
    pass

b = [CatatanBerat(datetime(2026, 10, d), 70) for d in (3, 1, 2)]
assert [c.tanggal.day for c in RiwayatCatatan(b)] == [1, 2, 3]
assert len(list(catatan_tanggal(b, datetime(2026, 10, 2)))) == 1
pantau = pemantau_vital()
assert next(pantau) == (0, 0)
bad = CatatanVital(t, 150, 80, 70)
try:
    bad.cek_vital()
except AbnormalVitalException:
    pass
assert pantau.send(bad) == (1, 1) and pantau.send(CatatanVital(t, 120, 80, 70)) == (1, 2)
print("OK")
