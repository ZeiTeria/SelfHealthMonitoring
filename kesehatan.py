"""Aplikasi Monitoring Kesehatan Pribadi - Kelompok 8 (UTS, fitur F1-F10).

Materi yang dipakai (sesuai modul praktikum):
  P01 Kelas & objek   : Pengguna, AplikasiKesehatan, semua kelas Catatan
                        + encapsulation: atribut _privat diakses lewat @property
  P02 Inheritance     : AktivitasFisik -> JalanKaki/Lari/..., CatatanHarian -> Catatan*
  P03 Polymorphism    : overriding tampilkan()/kalori_masuk()/kalori_keluar(),
                        overloading lewat default parameter hitung_tdee(level=0),
                        abstract class CatatanHarian (ABC)
  P04 Exception       : AbnormalVitalException, ValueError, try-except-finally
  P05 Iterator        : RiwayatCatatan (__iter__ dan __next__)
  P06 Comprehension   : list/dict comprehension, generator catatan_tanggal()
  P07 Coroutine       : pemantau_vital() dengan send()

Catatan: aplikasi ini alat bantu pencatatan, bukan alat diagnosis medis.
Jalankan: python kesehatan.py
"""
from abc import ABC, abstractmethod
from datetime import datetime, time


# ---------- P04: exception buatan sendiri (F10) ----------
class AbnormalVitalException(Exception):
    def __init__(self, pesan):
        super().__init__(pesan)


# ---------- P02: inheritance jenis aktivitas ----------
class AktivitasFisik:
    def __init__(self, nama, met):
        self._nama = nama
        self._met = met

    @property
    def nama(self):
        return self._nama

    @property
    def met(self):
        return self._met

    def hitung_kalori(self, berat, durasi_menit):
        # kalori = MET x berat (kg) x durasi (jam)
        return self.met * berat * (durasi_menit / 60)


class JalanKaki(AktivitasFisik):
    def __init__(self):
        super().__init__("Jalan Kaki", 3.5)


class Lari(AktivitasFisik):
    def __init__(self):
        super().__init__("Lari", 9.8)


class Bersepeda(AktivitasFisik):
    def __init__(self):
        super().__init__("Bersepeda", 7.5)


class Berenang(AktivitasFisik):
    def __init__(self):
        super().__init__("Berenang", 8.0)


# ---------- P01: profil pengguna (F1-F3) ----------
FAKTOR_AKTIVITAS = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9}
NAMA_LEVEL = {1: "Sedentari (jarang olahraga)", 2: "Ringan (1-3 hari/minggu)",
              3: "Sedang (3-5 hari/minggu)", 4: "Berat (6-7 hari/minggu)",
              5: "Sangat berat (fisik berat/2x sehari)"}


class Pengguna:
    def __init__(self, nama, usia, tinggi, berat, jenis_kelamin, target_berat, level_aktivitas):
        # semua validasi ada di setter, jadi constructor dan perubahan nilai aturannya sama
        self.nama = nama
        self.usia = usia
        self.tinggi = tinggi
        self.berat = berat
        self.jenis_kelamin = jenis_kelamin
        self.target_berat = target_berat
        self.level_aktivitas = level_aktivitas

    @property
    def nama(self):
        return self._nama

    @nama.setter
    def nama(self, nilai):
        if not nilai.strip():
            raise ValueError("Nama tidak boleh kosong")
        self._nama = nilai.strip()

    @property
    def usia(self):
        return self._usia

    @usia.setter
    def usia(self, nilai):
        if not 1 <= nilai <= 120:
            raise ValueError("Usia harus 1-120 tahun")
        self._usia = nilai

    @property
    def tinggi(self):
        return self._tinggi

    @tinggi.setter
    def tinggi(self, nilai):
        if not 50 <= nilai <= 250:
            raise ValueError("Tinggi harus 50-250 cm")
        self._tinggi = nilai

    @property
    def berat(self):
        return self._berat

    @berat.setter
    def berat(self, nilai):
        if not 10 <= nilai <= 500:
            raise ValueError("Berat harus 10-500 kg")
        self._berat = nilai

    @property
    def jenis_kelamin(self):
        return self._jenis_kelamin

    @jenis_kelamin.setter
    def jenis_kelamin(self, nilai):
        nilai = nilai.strip().upper()
        if nilai not in ("L", "P"):
            raise ValueError("Jenis kelamin harus L atau P")
        self._jenis_kelamin = nilai

    @property
    def target_berat(self):
        return self._target_berat

    @target_berat.setter
    def target_berat(self, nilai):
        if not 10 <= nilai <= 500:
            raise ValueError("Target berat harus 10-500 kg")
        self._target_berat = nilai

    @property
    def level_aktivitas(self):
        return self._level_aktivitas

    @level_aktivitas.setter
    def level_aktivitas(self, nilai):
        if nilai not in FAKTOR_AKTIVITAS:
            raise ValueError("Level aktivitas harus 1-5")
        self._level_aktivitas = nilai

    def tampil_profil(self):
        print(f"Nama           : {self.nama}")
        print(f"Usia           : {self.usia} tahun")
        print(f"Jenis kelamin  : {self.jenis_kelamin}")
        print(f"Tinggi         : {self.tinggi} cm")
        print(f"Berat          : {self.berat} kg (target {self.target_berat} kg)")
        print(f"Level aktivitas: {self.level_aktivitas} - {NAMA_LEVEL[self.level_aktivitas]}")

    def hitung_bmi(self):
        return self.berat / (self.tinggi / 100) ** 2

    def kategori_bmi(self):
        bmi = self.hitung_bmi()
        if bmi < 18.5:
            return "Kurus"
        if bmi <= 25:
            return "Normal"
        if bmi <= 27:
            return "Gemuk"
        return "Obesitas"

    def hitung_bmr(self):
        # rumus Mifflin-St Jeor
        bmr = 10 * self.berat + 6.25 * self.tinggi - 5 * self.usia
        return bmr + 5 if self.jenis_kelamin == "L" else bmr - 161

    # P03: overloading dengan default parameter (level 0 = pakai level pengguna)
    def hitung_tdee(self, level=0):
        if level == 0:
            level = self.level_aktivitas
        if level not in FAKTOR_AKTIVITAS:
            raise ValueError("Level aktivitas harus 1-5")
        return self.hitung_bmr() * FAKTOR_AKTIVITAS[level]


# ---------- P03: abstract class + polymorphism ----------
class CatatanHarian(ABC):
    def __init__(self, tanggal):
        self._tanggal = tanggal

    @property
    def tanggal(self):
        return self._tanggal

    @abstractmethod
    def tampilkan(self):
        pass

    def kalori_masuk(self):
        return 0

    def kalori_keluar(self):
        return 0

    def tgl(self):
        return self.tanggal.strftime("%Y-%m-%d")


class CatatanBerat(CatatanHarian):
    def __init__(self, tanggal, berat):
        if not 10 <= berat <= 500:
            raise ValueError("Berat harus 10-500 kg")
        super().__init__(tanggal)
        self._berat = berat

    @property
    def berat(self):
        return self._berat

    def tampilkan(self):
        print(f"[{self.tgl()}] Berat badan : {self.berat} kg")


class CatatanAktivitas(CatatanHarian):
    def __init__(self, tanggal, aktivitas, durasi_menit, berat):
        if durasi_menit <= 0:
            raise ValueError("Durasi harus lebih dari 0 menit")
        if durasi_menit > 1440:
            raise ValueError("Durasi maksimal 1440 menit (24 jam)")
        super().__init__(tanggal)
        self._aktivitas = aktivitas
        self._durasi_menit = durasi_menit
        self._kalori_terbakar = aktivitas.hitung_kalori(berat, durasi_menit)

    @property
    def aktivitas(self):
        return self._aktivitas

    @property
    def durasi_menit(self):
        return self._durasi_menit

    @property
    def kalori_terbakar(self):
        return self._kalori_terbakar

    def tampilkan(self):
        print(f"[{self.tgl()}] Aktivitas   : {self.aktivitas.nama} {self.durasi_menit} menit, "
              f"terbakar {self.kalori_terbakar:.0f} kkal")

    def kalori_keluar(self):
        return self.kalori_terbakar


class CatatanMakanan(CatatanHarian):
    def __init__(self, tanggal, nama_makanan, kalori):
        if not nama_makanan.strip():
            raise ValueError("Nama makanan tidak boleh kosong")
        if not 0 <= kalori <= 10000:
            raise ValueError("Kalori harus 0-10000 kkal")
        super().__init__(tanggal)
        self._nama_makanan = nama_makanan.strip()
        self._kalori = kalori

    @property
    def nama_makanan(self):
        return self._nama_makanan

    @property
    def kalori(self):
        return self._kalori

    def tampilkan(self):
        print(f"[{self.tgl()}] Makanan     : {self.nama_makanan}, {self.kalori:.0f} kkal")

    def kalori_masuk(self):
        return self.kalori


class CatatanTidur(CatatanHarian):
    def __init__(self, tanggal, jam_tidur, jam_bangun):
        if not isinstance(jam_tidur, time) or not isinstance(jam_bangun, time):
            raise ValueError("Format jam salah, gunakan HH:MM")
        super().__init__(tanggal)
        self._jam_tidur = jam_tidur
        self._jam_bangun = jam_bangun
        self._menit_tidur = jam_tidur.hour * 60 + jam_tidur.minute
        self._menit_bangun = jam_bangun.hour * 60 + jam_bangun.minute

    @property
    def jam_tidur(self):
        return self._jam_tidur

    @property
    def jam_bangun(self):
        return self._jam_bangun

    @property
    def menit_tidur(self):
        return self._menit_tidur

    @property
    def menit_bangun(self):
        return self._menit_bangun

    def durasi_jam(self):
        selisih = self.menit_bangun - self.menit_tidur
        if selisih <= 0:  # tidur melewati tengah malam
            selisih += 24 * 60
        return selisih / 60

    def tampilkan(self):
        print(f"[{self.tgl()}] Tidur       : {self.jam_tidur:%H:%M} - {self.jam_bangun:%H:%M} "
              f"({self.durasi_jam():.1f} jam)")


class CatatanVital(CatatanHarian):
    def __init__(self, tanggal, sistolik, diastolik, detak_jantung):
        if not (30 <= sistolik <= 300 and 20 <= diastolik <= 200 and 20 <= detak_jantung <= 300):
            raise ValueError("Nilai tanda vital tidak masuk akal, periksa lagi alat ukurnya")
        super().__init__(tanggal)
        self._sistolik = sistolik
        self._diastolik = diastolik
        self._detak_jantung = detak_jantung
        self._status = "Normal"

    @property
    def sistolik(self):
        return self._sistolik

    @property
    def diastolik(self):
        return self._diastolik

    @property
    def detak_jantung(self):
        return self._detak_jantung

    @property
    def status(self):
        return self._status

    def cek_vital(self):
        masalah = []
        if not 90 <= self.sistolik <= 140:
            masalah.append(f"sistolik {self.sistolik} (normal 90-140)")
        if not 60 <= self.diastolik <= 90:
            masalah.append(f"diastolik {self.diastolik} (normal 60-90)")
        if not 60 <= self.detak_jantung <= 100:
            masalah.append(f"detak jantung {self.detak_jantung} (normal 60-100)")
        if masalah:
            self._status = "ABNORMAL"
            raise AbnormalVitalException("Di luar batas normal: " + "; ".join(masalah))

    def tampilkan(self):
        print(f"[{self.tgl()}] Tanda vital : {self.sistolik}/{self.diastolik} mmHg, "
              f"{self.detak_jantung} bpm -> {self.status}")


# ---------- P05: iterator buatan sendiri ----------
class RiwayatCatatan:
    """Menelusuri catatan urut tanggal dengan __iter__ dan __next__."""

    def __init__(self, daftar_catatan):
        self.data = sorted(daftar_catatan, key=lambda c: c.tanggal)
        self.indeks = 0

    def __iter__(self):
        self.indeks = 0
        return self

    def __next__(self):
        if self.indeks >= len(self.data):
            raise StopIteration
        catatan = self.data[self.indeks]
        self.indeks += 1
        return catatan


# ---------- P06: generator ----------
def catatan_tanggal(daftar_catatan, tanggal):
    for c in daftar_catatan:
        if c.tanggal == tanggal:
            yield c


# ---------- P07: coroutine ----------
def pemantau_vital():
    """Kirim CatatanVital dengan send(); balasannya (jumlah abnormal, jumlah diperiksa)."""
    abnormal = diperiksa = 0
    while True:
        catatan = yield (abnormal, diperiksa)
        diperiksa += 1
        if catatan.status == "ABNORMAL":
            abnormal += 1


# ---------- Input helper ----------
def input_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Masukkan bilangan bulat!")


def input_float(prompt):
    while True:
        try:
            return float(input(prompt).replace(",", "."))
        except ValueError:
            print("Masukkan angka!")


def input_tanggal():
    while True:
        teks = input("Tanggal (YYYY-MM-DD, kosong = hari ini): ").strip()
        if not teks:
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        try:
            return datetime.strptime(teks, "%Y-%m-%d")
        except ValueError:
            print("Format tanggal salah!")


def input_jam(prompt):
    while True:
        try:
            return datetime.strptime(input(prompt).strip(), "%H:%M").time()
        except ValueError:
            print("Format jam salah, gunakan HH:MM")


# ---------- Aplikasi ----------
class AplikasiKesehatan:
    def __init__(self):
        self._pengguna = None
        self._daftar_catatan = []
        self._daftar_aktivitas = [JalanKaki(), Lari(), Bersepeda(), Berenang()]

    @property
    def pengguna(self):
        return self._pengguna

    @property
    def daftar_catatan(self):
        return self._daftar_catatan

    @property
    def daftar_aktivitas(self):
        return self._daftar_aktivitas

    def ada_profil(self):
        if self.pengguna is None:
            print("Buat profil pengguna terlebih dahulu (menu 1).")
            return False
        return True

    def buat_profil(self):  # F1
        nama = input("Nama: ")
        usia = input_int("Usia (tahun): ")
        tinggi = input_float("Tinggi (cm): ")
        berat = input_float("Berat (kg): ")
        jk = input("Jenis kelamin (L/P): ")
        target = input_float("Target berat (kg): ")
        for k, v in NAMA_LEVEL.items():
            print(f"  {k}. {v}")
        level = input_int("Level aktivitas (1-5): ")
        self._pengguna = Pengguna(nama, usia, tinggi, berat, jk, target, level)
        print("Profil tersimpan.")
        self.pengguna.tampil_profil()

    def menu_bmi(self):  # F2
        if not self.ada_profil():
            return
        p = self.pengguna
        print(f"BMI: {p.hitung_bmi():.1f} ({p.kategori_bmi()})")
        selisih = p.berat - p.target_berat
        if selisih > 0:
            print(f"Perlu turun {selisih:.1f} kg untuk mencapai target {p.target_berat} kg")
        elif selisih < 0:
            print(f"Perlu naik {-selisih:.1f} kg untuk mencapai target {p.target_berat} kg")
        else:
            print("Berat badan sudah sama dengan target.")

    def menu_bmr_tdee(self):  # F3
        if not self.ada_profil():
            return
        p = self.pengguna
        print(f"BMR (Mifflin-St Jeor): {p.hitung_bmr():.0f} kkal/hari")
        tabel = {lv: p.hitung_tdee(lv) for lv in FAKTOR_AKTIVITAS}  # dict comprehension
        for lv, tdee in tabel.items():
            tanda = "  <- level kamu" if lv == p.level_aktivitas else ""
            print(f"  Level {lv} ({NAMA_LEVEL[lv]}): {tdee:.0f} kkal{tanda}")

    def log_berat(self):  # F4
        if not self.ada_profil():
            return
        catatan = CatatanBerat(input_tanggal(), input_float("Berat (kg): "))
        self.daftar_catatan.append(catatan)
        self.pengguna.berat = catatan.berat
        print("Berat tercatat, profil diperbarui.")

    def log_aktivitas(self):  # F5
        if not self.ada_profil():
            return
        tanggal = input_tanggal()
        for i, a in enumerate(self.daftar_aktivitas, 1):
            print(f"  {i}. {a.nama} (MET {a.met})")
        nomor = input_int("Nomor aktivitas: ")
        if not 1 <= nomor <= len(self.daftar_aktivitas):
            print("Aktivitas tidak tersedia!")
            return
        durasi = input_int("Durasi (menit): ")
        catatan = CatatanAktivitas(tanggal, self.daftar_aktivitas[nomor - 1], durasi, self.pengguna.berat)
        self.daftar_catatan.append(catatan)
        print(f"Kalori terbakar: {catatan.kalori_terbakar:.0f} kkal")

    def log_makanan(self):  # F6
        if not self.ada_profil():
            return
        tanggal = input_tanggal()
        nama = input("Nama makanan: ")
        self.daftar_catatan.append(CatatanMakanan(tanggal, nama, input_float("Kalori (kkal): ")))
        print("Makanan tercatat.")

    def defisit_surplus(self):  # F7
        if not self.ada_profil():
            return
        tanggal = input_tanggal()
        hari_ini = list(catatan_tanggal(self.daftar_catatan, tanggal))  # generator
        total_masuk = sum([c.kalori_masuk() for c in hari_ini])  # polymorphism
        total_olahraga = sum([c.kalori_keluar() for c in hari_ini])
        kebutuhan = self.pengguna.hitung_tdee(1)
        selisih = total_masuk - (kebutuhan + total_olahraga)
        print(f"Kalori masuk     : {total_masuk:.0f} kkal")
        print(f"Kebutuhan dasar  : {kebutuhan:.0f} kkal")
        print(f"Dibakar olahraga : {total_olahraga:.0f} kkal")
        if selisih < 0:
            print(f"DEFISIT {-selisih:.0f} kkal")
        elif selisih > 0:
            print(f"SURPLUS {selisih:.0f} kkal")
        else:
            print("SEIMBANG")
        if total_masuk == 0:
            print("(Belum ada catatan makanan di tanggal ini, hasil belum menggambarkan kondisi sebenarnya)")

    def log_tidur(self):  # F8
        if not self.ada_profil():
            return
        tanggal = input_tanggal()
        catatan = CatatanTidur(tanggal, input_jam("Jam tidur (HH:MM): "), input_jam("Jam bangun (HH:MM): "))
        self.daftar_catatan.append(catatan)
        print(f"Durasi tidur: {catatan.durasi_jam():.1f} jam")

    def catat_vital(self):  # F9 dan F10
        if not self.ada_profil():
            return
        catatan = CatatanVital(input_tanggal(), input_int("Sistolik (mmHg): "),
                               input_int("Diastolik (mmHg): "), input_int("Detak jantung (bpm): "))
        try:
            catatan.cek_vital()
            print("Tanda vital normal.")
        except AbnormalVitalException as e:
            print(f"PERINGATAN: {e}")
            print("Saran: istirahat, ukur ulang, dan konsultasikan ke dokter bila berlanjut.")
        finally:
            self.daftar_catatan.append(catatan)

    def lihat_catatan(self):
        if not self.daftar_catatan:
            print("Belum ada catatan.")
            return
        for catatan in RiwayatCatatan(self.daftar_catatan):  # iterator
            catatan.tampilkan()  # polymorphism
        pantau = pemantau_vital()  # coroutine
        hasil = next(pantau)
        for c in self.daftar_catatan:
            if isinstance(c, CatatanVital):
                hasil = pantau.send(c)
        print(f"Ringkasan tanda vital: {hasil[0]} abnormal dari {hasil[1]} pemeriksaan")

    def isi_data_contoh(self):
        if self.pengguna is not None:
            jawab = input("Profil dan catatan yang ada akan diganti data contoh. Lanjut? (y/n): ")
            if jawab.strip().lower() != "y":
                print("Dibatalkan.")
                return
            self._daftar_catatan = []
        self._pengguna = Pengguna("Contoh", 20, 170, 70, "L", 65, 2)
        t = datetime(2026, 10, 9)
        vital = CatatanVital(t, 150, 95, 110)
        self._daftar_catatan += [
            CatatanBerat(t, 70),
            CatatanAktivitas(t, self.daftar_aktivitas[1], 30, 70),
            CatatanMakanan(t, "Nasi goreng", 600),
            CatatanMakanan(t, "Ayam bakar", 450),
            CatatanTidur(t, time(23, 30), time(6, 0)),
            vital,
        ]
        try:
            vital.cek_vital()
        except AbnormalVitalException:
            pass  # statusnya jadi ABNORMAL, tampil di menu 10
        print("Data contoh terisi (profil + 6 catatan, tanggal 2026-10-09).")

    def tampil_menu(self):
        print("\n=== MONITORING KESEHATAN PRIBADI ===")
        print(" 1. Buat Profil              7. Defisit/Surplus Kalori")
        print(" 2. BMI & Kategori           8. Log Pola Tidur")
        print(" 3. BMR & TDEE               9. Catat Tanda Vital")
        print(" 4. Log Berat Badan         10. Lihat Semua Catatan")
        print(" 5. Log Aktivitas Fisik     11. Isi Data Contoh")
        print(" 6. Log Makanan              0. Keluar")

    def jalankan(self):
        menu = {"1": self.buat_profil, "2": self.menu_bmi, "3": self.menu_bmr_tdee,
                "4": self.log_berat, "5": self.log_aktivitas, "6": self.log_makanan,
                "7": self.defisit_surplus, "8": self.log_tidur, "9": self.catat_vital,
                "10": self.lihat_catatan, "11": self.isi_data_contoh}
        while True:
            self.tampil_menu()
            pilih = input("Pilih: ").strip()
            if pilih == "0":
                print("Sampai jumpa!")
                break
            if pilih not in menu:
                print("Menu tidak tersedia!")
                continue
            try:
                menu[pilih]()
            except ValueError as e:
                print(f"Gagal: {e}")


if __name__ == "__main__":
    AplikasiKesehatan().jalankan()
