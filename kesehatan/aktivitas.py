"""P02: inheritance jenis aktivitas fisik dan nilai MET."""


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
