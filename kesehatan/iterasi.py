# Iterator buatan sendiri untuk menelusuri catatan dari tanggal paling lama ke paling baru.
# Karena punya __iter__ dan __next__, objek ini bisa langsung dipakai di for loop tanpa
# pemanggilnya perlu tahu bahwa isinya sebenarnya sebuah list.
class RiwayatCatatan:
    def __init__(self, daftar_catatan):
        self.data = sorted(daftar_catatan, key=lambda c: c.tanggal)
        self.indeks = 0

    def __iter__(self):
        self.indeks = 0
        return self

    def __next__(self):
        # StopIteration memberi tahu for loop bahwa semua catatan sudah dibaca.
        if self.indeks >= len(self.data):
            raise StopIteration
        catatan = self.data[self.indeks]
        self.indeks += 1
        return catatan


# Generator: memakai yield sehingga catatan diberikan satu per satu saat diminta, tanpa
# membuat list baru berisi hasil penyaringan.
def catatan_tanggal(daftar_catatan, tanggal):
    for c in daftar_catatan:
        if c.tanggal == tanggal:
            yield c


def pemantau_vital():
    # Coroutine: setiap kali diberi CatatanVital lewat send(), fungsi ini menambah hitungan
    # pemeriksaan dan hitungan yang abnormal, lalu mengembalikan keduanya. Panggil next() satu
    # kali dulu untuk memulainya.
    abnormal = diperiksa = 0
    while True:
        catatan = yield (abnormal, diperiksa)
        diperiksa += 1
        if catatan.status == "ABNORMAL":
            abnormal += 1
