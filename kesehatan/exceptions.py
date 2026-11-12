# Aktif kalau hasil pengukuran tanda vital  berada di luar batas normal, supaya program bisa menampilkan peringatan ke pengguna.
class AbnormalVitalException(Exception):
    def __init__(self, pesan):
        super().__init__(pesan)
