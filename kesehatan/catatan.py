"""P03: abstract class CatatanHarian dan lima kelas turunannya (polymorphism)."""
from abc import ABC, abstractmethod
from datetime import time

from .exceptions import AbnormalVitalException


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
        print(f"[{self.tgl()}] Aktivitas   : {self.aktivitas.nama} {self.durasi_menit} menit, "
              f"terbakar {self.kalori_terbakar:.0f} kkal")

    def kalori_keluar(self):
        return self.kalori_terbakar


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
        print(f"[{self.tgl()}] Makanan     : {self.nama_makanan}, {self.kalori:.0f} kkal")

    def kalori_masuk(self):
        return self.kalori


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
        if selisih <= 0:  # tidur melewati tengah malam
            selisih += 24 * 60
        return selisih / 60

    def tampilkan(self):
        print(f"[{self.tgl()}] Tidur       : {self.jam_tidur:%H:%M} - {self.jam_bangun:%H:%M} "
              f"({self.durasi_jam():.1f} jam)")


class CatatanVital(CatatanHarian):
    def __init__(self, tanggal, sistolik, diastolik, detak_jantung):
        if not (30 <= sistolik <= 300 and 20 <= diastolik <= 200 and 20 <= detak_jantung <= 300):
            raise ValueError("Nilai tanda vital tidak masuk akal, periksa lagi alat ukurnya")
        super().__init__(tanggal)
        self._sistolik = sistolik
        self._diastolik = diastolik
        self._detak_jantung = detak_jantung
        self._status = "Normal"

    @property
    def sistolik(self):
        return self._sistolik

    @property
    def diastolik(self):
        return self._diastolik

    @property
    def detak_jantung(self):
        return self._detak_jantung

    @property
    def status(self):
        return self._status

    def cek_vital(self):
        masalah = []
        if not 90 <= self.sistolik <= 140:
            masalah.append(f"sistolik {self.sistolik} (normal 90-140)")
        if not 60 <= self.diastolik <= 90:
            masalah.append(f"diastolik {self.diastolik} (normal 60-90)")
        if not 60 <= self.detak_jantung <= 100:
            masalah.append(f"detak jantung {self.detak_jantung} (normal 60-100)")
        if masalah:
            self._status = "ABNORMAL"
            raise AbnormalVitalException("Di luar batas normal: " + "; ".join(masalah))

    def tampilkan(self):
        print(f"[{self.tgl()}] Tanda vital : {self.sistolik}/{self.diastolik} mmHg, "
              f"{self.detak_jantung} bpm -> {self.status}")
