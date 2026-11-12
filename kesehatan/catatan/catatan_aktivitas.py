from .catatan_harian import CatatanHarian


class CatatanAktivitas(CatatanHarian):
    def __init__(self, tanggal, aktivitas, durasi_menit, berat):
        if durasi_menit <= 0:
            raise ValueError("Durasi harus lebih dari 0 menit")
        if durasi_menit > 1440:
            raise ValueError("Durasi maksimal 1440 menit (24 jam)")
        super().__init__(tanggal)
        self._aktivitas = aktivitas
        self._durasi_menit = durasi_menit
        self._kalori_terbakar = aktivitas.hitung_kalori(berat, durasi_menit)

    @property
    def aktivitas(self):
        return self._aktivitas

    @property
    def durasi_menit(self):
        return self._durasi_menit

    @property
    def kalori_terbakar(self):
        return self._kalori_terbakar

    def tampilkan(self):
        print(f"[{self.tgl()}] Aktivitas   : {self.aktivitas.nama} {self.durasi_menit} menit "
              f"(MET {self.aktivitas.met}) = {self.kalori_terbakar:.0f} kkal terbakar")

    def kalori_keluar(self):
        return self.kalori_terbakar
