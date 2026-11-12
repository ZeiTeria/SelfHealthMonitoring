from datetime import time

from .catatan_harian import CatatanHarian


class CatatanTidur(CatatanHarian):
    def __init__(self, tanggal, jam_tidur, jam_bangun):
        if not isinstance(jam_tidur, time) or not isinstance(jam_bangun, time):
            raise ValueError("Format jam salah, gunakan HH:MM")
        super().__init__(tanggal)
        self._jam_tidur = jam_tidur
        self._jam_bangun = jam_bangun
        self._menit_tidur = jam_tidur.hour * 60 + jam_tidur.minute
        self._menit_bangun = jam_bangun.hour * 60 + jam_bangun.minute

    @property
    def jam_tidur(self):
        return self._jam_tidur

    @property
    def jam_bangun(self):
        return self._jam_bangun

    @property
    def menit_tidur(self):
        return self._menit_tidur

    @property
    def menit_bangun(self):
        return self._menit_bangun

    def durasi_jam(self):
        selisih = self.menit_bangun - self.menit_tidur
        # Kalau jam bangun lebih kecil atau sama dengan jam tidur, berarti tidurnya melewati
        # tengah malam, jadi hasilnya ditambah 24 jam.
        if selisih <= 0:
            selisih += 24 * 60
        return selisih / 60

    def tampilkan(self):
        print(f"[{self.tgl()}] Tidur       : {self.jam_tidur:%H:%M} - {self.jam_bangun:%H:%M} "
              f"({self.durasi_jam():.1f} jam)")
