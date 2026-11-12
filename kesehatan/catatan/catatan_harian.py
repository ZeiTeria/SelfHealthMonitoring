from abc import ABC, abstractmethod


# Abstract class: induk dari semua catatan harian dan tidak bisa dibuat objeknya langsung.
# Setiap catatan wajib menulis tampilkan() sendiri. Sedangkan kalori_masuk() dan kalori_keluar()
# bernilai 0 kecuali di-override oleh catatan yang memang punya kalori.
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
