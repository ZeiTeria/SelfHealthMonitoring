from ..exceptions import AbnormalVitalException
from .catatan_harian import CatatanHarian


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
        # Semua nilai yang keluar batas dikumpulkan dulu supaya pesan peringatannya menyebut
        # semuanya sekaligus, bukan hanya yang pertama ketemu.
        masalah = []
        if not 90 <= self.sistolik <= 140:
            masalah.append(f"sistolik {self.sistolik} (normal 90-140)")
        if not 60 <= self.diastolik <= 90:
            masalah.append(f"diastolik {self.diastolik} (normal 60-90)")
        if not 60 <= self.detak_jantung <= 100:
            masalah.append(f"detak jantung {self.detak_jantung} (normal 60-100)")
        if masalah:
            # Status diubah sebelum exception dilempar, supaya catatan tetap tercatat sebagai
            # ABNORMAL walaupun pemanggilnya menangkap exception lalu melanjutkan program.
            self._status = "ABNORMAL"
            raise AbnormalVitalException("Di luar batas normal: " + "; ".join(masalah))

    def tampilkan(self):
        print(f"[{self.tgl()}] Tanda Vital : {self.sistolik}/{self.diastolik} mmHg, "
              f"nadi {self.detak_jantung} bpm ({self.status})")
