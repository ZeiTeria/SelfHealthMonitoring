from abc import ABC, abstractmethod
from datetime import datetime


# Abstract class: induk dari semua catatan harian dan tidak bisa dibuat objeknya langsung. Setiap catatan wajib menulis tampilkan() sendiri. Sedangkan kalori_masuk() dan kalori_keluar() bernilai 0 kecuali di-override oleh catatan yang memang punya kalori.
class CatatanHarian(ABC):
    def __init__(self, tanggal):
        if not isinstance(tanggal, datetime) or not 1900 <= tanggal.year <= 2100:
            raise ValueError("Tanggal harus berada di antara tahun 1900 dan 2100")
        self._tanggal = tanggal
        self._id = None

    @property
    def tanggal(self):
        return self._tanggal

    # Nomor baris di database. Nilainya None sampai catatan disimpan, dan hanya boleh diisi satu kali.
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, nilai):
        if self._id is not None:
            raise ValueError("Nomor catatan sudah terisi dan tidak bisa diganti")
        self._id = nilai

    @abstractmethod
    def tampilkan(self):
        pass

    def kalori_masuk(self):
        return 0

    def kalori_keluar(self):
        return 0

    def tgl(self):
        return self.tanggal.strftime("%Y-%m-%d")
