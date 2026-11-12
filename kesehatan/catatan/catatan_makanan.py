from .catatan_harian import CatatanHarian


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
        print(f"[{self.tgl()}] Makanan     : {self.nama_makanan} = {self.kalori:.0f} kkal")

    def kalori_masuk(self):
        return self.kalori
