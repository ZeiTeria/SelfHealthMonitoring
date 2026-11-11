from datetime import datetime, time

from .aktivitas import Berenang, Bersepeda, JalanKaki, Lari
from .catatan import (CatatanAktivitas, CatatanBerat, CatatanMakanan, CatatanTidur,
                      CatatanVital)
from .exceptions import AbnormalVitalException
from .input_util import input_float, input_int, input_jam, input_tanggal
from .iterasi import RiwayatCatatan, catatan_tanggal, pemantau_vital
from .pengguna import FAKTOR_AKTIVITAS, NAMA_LEVEL, Pengguna


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

    def buat_profil(self):
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

    def menu_bmi(self):
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
        r = p.rencana_target()
        if r["arah"] != "tetap":
            print(f"Target asupan harian: {r['kalori_harian']:.0f} kkal "
                  f"({r['penyesuaian']:.0f} kkal dari TDEE), perkiraan {r['perkiraan_minggu']:.0f} minggu")

    def menu_bmr_tdee(self):
        if not self.ada_profil():
            return
        p = self.pengguna
        print(f"BMR (Mifflin-St Jeor): {p.hitung_bmr():.0f} kkal/hari")
        tabel = {lv: p.hitung_tdee(lv) for lv in FAKTOR_AKTIVITAS}
        for lv, tdee in tabel.items():
            tanda = "  <- level kamu" if lv == p.level_aktivitas else ""
            print(f"  Level {lv} ({NAMA_LEVEL[lv]}): {tdee:.0f} kkal{tanda}")

    def log_berat(self):
        if not self.ada_profil():
            return
        catatan = CatatanBerat(input_tanggal(), input_float("Berat (kg): "))
        self.daftar_catatan.append(catatan)
        self.pengguna.berat = catatan.berat
        print("Berat tercatat, profil diperbarui.")

    def log_aktivitas(self):
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

    def log_makanan(self):
        if not self.ada_profil():
            return
        tanggal = input_tanggal()
        nama = input("Nama makanan: ")
        self.daftar_catatan.append(CatatanMakanan(tanggal, nama, input_float("Kalori (kkal): ")))
        print("Makanan tercatat.")

    def defisit_surplus(self):
        if not self.ada_profil():
            return
        tanggal = input_tanggal()
        hari_ini = list(catatan_tanggal(self.daftar_catatan, tanggal))
        total_masuk = sum([c.kalori_masuk() for c in hari_ini])
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

    def log_tidur(self):
        if not self.ada_profil():
            return
        tanggal = input_tanggal()
        catatan = CatatanTidur(tanggal, input_jam("Jam tidur (HH:MM): "), input_jam("Jam bangun (HH:MM): "))
        self.daftar_catatan.append(catatan)
        print(f"Durasi tidur: {catatan.durasi_jam():.1f} jam")

    def catat_vital(self):
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
        for catatan in RiwayatCatatan(self.daftar_catatan):
            catatan.tampilkan()
        pantau = pemantau_vital()
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
        self._pengguna = Pengguna("Budi", 20, 170, 72, "L", 65, 2)
        hari = datetime(2026, 10, 9)
        vital = CatatanVital(hari, 120, 80, 75)
        vital.cek_vital()
        self._daftar_catatan += [
            CatatanBerat(datetime(2026, 10, 8), 72.5),
            CatatanMakanan(hari, "Roti & susu", 400),
            CatatanMakanan(hari, "Ayam bakar", 550),
            CatatanAktivitas(hari, self.daftar_aktivitas[0], 45, 72),
            CatatanTidur(hari, time(23, 0), time(6, 0)),
            vital,
        ]
        print("Data contoh terisi (profil Budi + 6 catatan, 8-9 Oktober 2026).")

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
