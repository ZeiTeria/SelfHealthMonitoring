from .catatan_harian import CatatanHarian


# Di semua kelas catatan, atribut disimpan dengan awalan _ (privat) dan hanya bisa dibaca lewat
# @property. Jadi catatan yang sudah dibuat tidak berubah tanpa sengaja.
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
