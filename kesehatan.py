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


