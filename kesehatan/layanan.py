from datetime import datetime, time
from .catatan import (CatatanAktivitas, CatatanBerat, CatatanMakanan, CatatanTidur, CatatanVital)
from .exceptions import AbnormalVitalException
from .iterasi import RiwayatCatatan, catatan_tanggal, pemantau_vital
from .pengguna import FAKTOR_AKTIVITAS, NAMA_LEVEL, Pengguna


class LayananKesehatan:
    def __init__(self, database):
        self.database = database

    @property
    def pengguna(self):
        return self.database.muat_pengguna()

    def _wajib_profil(self):
        p = self.pengguna
        if p is None:
            raise ValueError("Buat profil pengguna terlebih dahulu")
        return p

    def buat_profil(self, nama, usia, tinggi, berat, jenis_kelamin, target_berat, level_aktivitas):
        p = Pengguna(nama, usia, tinggi, berat, jenis_kelamin, target_berat, level_aktivitas)
        self.database.simpan_pengguna(p)
        return p

    def ringkasan_tubuh(self):
        p = self._wajib_profil()
        selisih = p.berat - p.target_berat
        return {
            "pengguna": p,
            "bmi": p.hitung_bmi(),
            "kategori": p.kategori_bmi(),
            "bmr": p.hitung_bmr(),
            "tdee": {lv: (NAMA_LEVEL[lv], p.hitung_tdee(lv)) for lv in FAKTOR_AKTIVITAS},
            "selisih_target": selisih,
            "rencana": p.rencana_target(),
        }

    def catat_berat(self, tanggal, berat):
        p = self._wajib_profil()
        catatan = CatatanBerat(tanggal, berat)
        # Berat di profil hanya diganti kalau catatan ini yang paling baru, supaya mengisi catatan tanggal lama tidak menimpa berat terkini.
        terbaru = max([c.tanggal for c in self.database.muat_catatan() if isinstance(c, CatatanBerat)], default=None)
        mutakhir = terbaru is None or tanggal >= terbaru
        if mutakhir:
            p.berat = berat
        self.database.simpan_catatan(catatan)
        if mutakhir:
            self.database.simpan_pengguna(p)
        return catatan

    def catat_aktivitas(self, tanggal, id_aktivitas, durasi_menit):
        p = self._wajib_profil()
        pilihan = dict(self.database.daftar_aktivitas())
        if id_aktivitas not in pilihan:
            raise ValueError("Aktivitas tidak tersedia")
        catatan = CatatanAktivitas(tanggal, pilihan[id_aktivitas], durasi_menit, p.berat)
        self.database.simpan_catatan(catatan)
        return catatan

    def catat_makanan(self, tanggal, nama_makanan, kalori):
        self._wajib_profil()
        catatan = CatatanMakanan(tanggal, nama_makanan, kalori)
        self.database.simpan_catatan(catatan)
        return catatan

    def catat_tidur(self, tanggal, jam_tidur, jam_bangun):
        self._wajib_profil()
        catatan = CatatanTidur(tanggal, jam_tidur, jam_bangun)
        self.database.simpan_catatan(catatan)
        return catatan

    def catat_vital(self, tanggal, sistolik, diastolik, detak_jantung):
        self._wajib_profil()
        catatan = CatatanVital(tanggal, sistolik, diastolik, detak_jantung)
        # Exception hanya ditangkap di sini untuk diubah menjadi pesan peringatan. Penyimpanan ke database ada di finally supaya catatan abnormal tetap masuk.
        peringatan = None
        try:
            catatan.cek_vital()
        except AbnormalVitalException as e:
            peringatan = str(e)
        finally:
            self.database.simpan_catatan(catatan)
        return catatan, peringatan

    def defisit_surplus(self, tanggal):
        p = self._wajib_profil()
        hari_ini = list(catatan_tanggal(self.database.muat_catatan(), tanggal))
        masuk = sum([c.kalori_masuk() for c in hari_ini])
        olahraga = sum([c.kalori_keluar() for c in hari_ini])
        kebutuhan = p.hitung_tdee(1)
        selisih = masuk - (kebutuhan + olahraga)
        if selisih < 0:
            status = "DEFISIT"
        elif selisih > 0:
            status = "SURPLUS"
        else:
            status = "SEIMBANG"
        return {"masuk": masuk, "kebutuhan": kebutuhan, "olahraga": olahraga,
                "selisih": selisih, "status": status, "jumlah_catatan": len(hari_ini),
                "rencana": p.rencana_target()}

    def riwayat(self):
        return RiwayatCatatan(self.database.muat_catatan())

    def ringkasan_vital(self):
        pantau = pemantau_vital()
        hasil = next(pantau)
        for c in self.database.muat_catatan():
            if isinstance(c, CatatanVital):
                hasil = pantau.send(c)
        return hasil

    def isi_data_contoh(self):
        # Isinya sama dengan data contoh di laporan, supaya angka di layar bisa dicocokkan.
        self.database.kosongkan()
        self.buat_profil("Nicholas", 19, 175, 81, "L", 75, 2)
        jalan_kaki = self.database.daftar_aktivitas()[0][0]
        hari = datetime(2026, 10, 9)
        self.database.simpan_catatan(CatatanBerat(datetime(2026, 10, 8), 81.5))
        self.catat_makanan(hari, "Roti & susu", 400)
        self.catat_makanan(hari, "Ayam bakar", 550)
        self.catat_aktivitas(hari, jalan_kaki, 45)
        self.catat_tidur(hari, time(23, 0), time(6, 0))
        self.catat_vital(hari, 120, 80, 75)

    def kosongkan(self):
        self.database.kosongkan()
