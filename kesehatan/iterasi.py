# Iterator
class RiwayatCatatan:
    def __init__(self, daftar_catatan):
        self.data = sorted(daftar_catatan, key=lambda c: c.tanggal)
        self.indeks = 0

    # Setiap for loop mendapat iterator baru, jadi loop bersarang tidak saling mengganggu.
    def __iter__(self):
        return RiwayatCatatan(self.data)

    def __next__(self):
        # StopIteration
        if self.indeks >= len(self.data):
            raise StopIteration
        catatan = self.data[self.indeks]
        self.indeks += 1
        return catatan

# Generator
def catatan_tanggal(daftar_catatan, tanggal):
    for c in daftar_catatan:
        if c.tanggal == tanggal:
            yield c

def pemantau_vital():
    # Coroutine
    abnormal = diperiksa = 0
    while True:
        catatan = yield (abnormal, diperiksa)
        diperiksa += 1
        if catatan.status == "ABNORMAL":
            abnormal += 1
