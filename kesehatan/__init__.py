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
Jalankan: python main.py
"""
from .aktivitas import AktivitasFisik, Berenang, Bersepeda, JalanKaki, Lari
from .aplikasi import AplikasiKesehatan, RiwayatCatatan, catatan_tanggal, pemantau_vital
from .catatan import (CatatanAktivitas, CatatanBerat, CatatanHarian, CatatanMakanan,
                      CatatanTidur, CatatanVital)
from .exceptions import AbnormalVitalException
from .pengguna import FAKTOR_AKTIVITAS, NAMA_LEVEL, Pengguna
