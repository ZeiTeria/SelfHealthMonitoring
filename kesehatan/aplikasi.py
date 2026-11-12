from datetime import datetime, time
import os
from .aktivitas import Berenang, Bersepeda, JalanKaki, Lari
from .catatan import (CatatanAktivitas, CatatanBerat, CatatanMakanan, CatatanTidur, CatatanVital)
from .exceptions import AbnormalVitalException
from .input_util import input_float, input_int, input_jam, input_tanggal, minta
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
        # Profil sementara dipakai supaya tiap isian bisa dicek oleh setter Pengguna saat itu juga. Profil lama baru diganti setelah semua isian benar.
        p = Pengguna("-", 20, 170, 60, "L", 60, 1)
        minta(input, "Nama: ", lambda v: setattr(p, "nama", v))
        minta(input_int, "Usia (tahun): ", lambda v: setattr(p, "usia", v))
        minta(input_float, "Tinggi (cm): ", lambda v: setattr(p, "tinggi", v))
        minta(input_float, "Berat (kg): ", lambda v: setattr(p, "berat", v))
        minta(input, "Jenis kelamin (L/P): ", lambda v: setattr(p, "jenis_kelamin", v))
        minta(input_float, "Target berat (kg): ", lambda v: setattr(p, "target_berat", v))
        for k, v in NAMA_LEVEL.items():
            print(f"  {k}. {v}")
        minta(input_int, "Level aktivitas (1-5): ", lambda v: setattr(p, "level_aktivitas", v))
        self._pengguna = p
        print("Profil tersimpan.")
        p.tampil_profil()

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
        tanggal = input_tanggal()
        berat = minta(input_float, "Berat (kg): ", lambda v: CatatanBerat(tanggal, v))
        catatan = CatatanBerat(tanggal, berat)
        terbaru = max([c.tanggal for c in self.daftar_catatan if isinstance(c, CatatanBerat)], default=None)
        self.daftar_catatan.append(catatan)
        # Berat di profil hanya diganti kalau catatan ini yang paling baru.
        if terbaru is None or tanggal >= terbaru:
            self.pengguna.berat = catatan.berat
            print("Berat tercatat, profil diperbarui.")
        else:
            print("Berat tercatat. Profil tidak berubah karena sudah ada catatan yang lebih baru.")

    def log_aktivitas(self):
        if not self.ada_profil():
            return
        tanggal = input_tanggal()
        for i, a in enumerate(self.daftar_aktivitas, 1):
            print(f"  {i}. {a.nama} (MET {a.met})")
        def cek_nomor(n):
            if not 1 <= n <= len(self.daftar_aktivitas):
                raise ValueError("Aktivitas tidak tersedia")
        nomor = minta(input_int, "Nomor aktivitas: ", cek_nomor)
        aktivitas = self.daftar_aktivitas[nomor - 1]
        berat = self.pengguna.berat
        durasi = minta(input_int, "Durasi (menit): ", lambda v: CatatanAktivitas(tanggal, aktivitas, v, berat))
        catatan = CatatanAktivitas(tanggal, aktivitas, durasi, berat)
        self.daftar_catatan.append(catatan)
        print(f"Kalori terbakar: {catatan.kalori_terbakar:.0f} kkal")

    def log_makanan(self):
        if not self.ada_profil():
            return
        tanggal = input_tanggal()
        nama = minta(input, "Nama makanan: ", lambda v: CatatanMakanan(tanggal, v, 0))
        kalori = minta(input_float, "Kalori (kkal): ", lambda v: CatatanMakanan(tanggal, nama, v))
        self.daftar_catatan.append(CatatanMakanan(tanggal, nama, kalori))
        print("Makanan tercatat.")

    def defisit_surplus(self):
        if not self.ada_profil():
            return
        tanggal = input_tanggal()
        hari_ini = list(catatan_tanggal(self.daftar_catatan, tanggal))
        total_masuk = sum([c.kalori_masuk() for c in hari_ini])
        total_olahraga = sum([c.kalori_keluar() for c in hari_ini])
        # Kebutuhan memakai TDEE level 1 (tanpa olahraga), karena kalori olahraga dijumlahkan terpisah dari catatan aktivitas.
        kebutuhan = self.pengguna.hitung_tdee(1)
        selisih = total_masuk - (kebutuhan + total_olahraga)
        print(f"Kalori masuk     : {total_masuk:.0f} kkal")
        print(f"Kebutuhan (lv 1) : {kebutuhan:.0f} kkal")
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
        tanggal = input_tanggal()
        sistolik = minta(input_int, "Sistolik (mmHg): ", lambda v: CatatanVital(tanggal, v, 20, 70))
        diastolik = minta(input_int, "Diastolik (mmHg): ", lambda v: CatatanVital(tanggal, sistolik, v, 70))
        detak = minta(input_int, "Detak jantung (bpm): ", lambda v: CatatanVital(tanggal, sistolik, diastolik, v))
        catatan = CatatanVital(tanggal, sistolik, diastolik, detak)
        try:
            catatan.cek_vital()
            print("Tanda vital normal.")
        except AbnormalVitalException as e:
            print(f"PERINGATAN: {e}")
            print("Saran: istirahat, ukur ulang, dan konsultasikan ke dokter bila berlanjut.")
        finally:
            # finally selalu dijalankan, jadi catatan tersimpan baik nilainya normal maupun abnormal.
            self.daftar_catatan.append(catatan)

    def lihat_catatan(self):
        if not self.daftar_catatan:
            print("Belum ada catatan.")
            return
        # Setiap catatan dipanggil dengan tampilkan() yang sama, tetapi hasilnya berbeda karena tiap kelas menulis ulang method itu (polymorphism).
        for catatan in RiwayatCatatan(self.daftar_catatan):
            catatan.tampilkan()
        pantau = pemantau_vital()
        hasil = next(pantau)
        for c in self.daftar_catatan:
            if isinstance(c, CatatanVital):
                hasil = pantau.send(c)
        print(f"Ringkasan tanda vital: {hasil[0]} abnormal dari {hasil[1]} pemeriksaan")

    def isi_data_contoh(self):
        # Data contoh sama dengan yang dipakai di laporan (Nicholas, 8-9 Oktober 2026), supaya hasil di layar bisa dicocokkan dengan angka di laporan.
        if self.pengguna is not None:
            jawab = input("Profil dan catatan yang ada akan diganti data contoh. Lanjut? (y/n): ")
            if jawab.strip().lower() != "y":
                print("Dibatalkan.")
                return
            self._daftar_catatan = []
        self._pengguna = Pengguna("Nicholas", 19, 175, 81, "L", 75, 2)
        hari = datetime(2026, 10, 9)
        vital = CatatanVital(hari, 120, 80, 75)
        self._daftar_catatan += [
            CatatanBerat(datetime(2026, 10, 8), 81.5),
            CatatanMakanan(hari, "Roti & susu", 400),
            CatatanMakanan(hari, "Ayam bakar", 550),
            CatatanAktivitas(hari, self.daftar_aktivitas[0], 45, 81),
            CatatanTidur(hari, time(23, 0), time(6, 0)),
            vital,
        ]
        print("Data contoh terisi (profil Nicholas + 6 catatan, 8-9 Oktober 2026).")

    def tampil_menu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
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
            try:
                pilih = input("Pilih: ").strip()
                if pilih == "0":
                    print("Sampai jumpa!")
                    break
                if pilih not in menu:
                    print("Menu tidak tersedia!")
                    continue
                menu[pilih]()
            except ValueError as e:
                print(f"Gagal: {e}")
            except (EOFError, KeyboardInterrupt):
                # Ctrl+D atau Ctrl+C di mana saja menutup program dengan rapi, tanpa pesan error.
                print("\nInput berakhir, program ditutup.")
                break
