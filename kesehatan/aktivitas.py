# Kelas induk untuk semua jenis olahraga. Tiap olahraga punya nilai MET sendiri, yaitu
# ukuran seberapa berat olahraga itu dibandingkan dengan duduk diam.
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
        # Kalori terbakar = MET x berat badan (kg) x lama olahraga (jam). Durasi dari pengguna
        # dalam menit, jadi dibagi 60 dulu supaya menjadi jam.
        return self.met * berat * (durasi_menit / 60)


# Empat kelas di bawah ini tidak punya logika baru. Mereka hanya mengisi nama dan nilai MET
# lewat super().__init__(), sisanya diwarisi dari AktivitasFisik.
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
