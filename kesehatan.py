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


