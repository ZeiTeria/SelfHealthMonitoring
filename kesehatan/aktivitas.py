from abc import ABC, abstractmethod


# Kelas induk (abstract) untuk semua jenis olahraga, jadi tidak bisa dibuat objeknya langsung. Setiap olahraga wajib menulis intensitas() sendiri.
class AktivitasFisik(ABC):
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
        # Kalori terbakar = MET x berat badan (kg) x lama olahraga (jam).
        return self.met * berat * (durasi_menit / 60)

    @abstractmethod
    def intensitas(self):
        pass


# Inheritence
class JalanKaki(AktivitasFisik):
    def __init__(self):
        super().__init__("Jalan Kaki", 3.5)

    def intensitas(self):
        return "Ringan"


class Lari(AktivitasFisik):
    def __init__(self):
        super().__init__("Lari", 9.8)

    def intensitas(self):
        return "Berat"


class Bersepeda(AktivitasFisik):
    def __init__(self):
        super().__init__("Bersepeda", 7.5)

    def intensitas(self):
        return "Sedang"


class Berenang(AktivitasFisik):
    def __init__(self):
        super().__init__("Berenang", 8.0)

    def intensitas(self):
        return "Berat"