from datetime import datetime


# Fungsi-fungsi input di bawah mengulang pertanyaan sampai pengguna mengisi nilai yang benar,
# jadi program tidak langsung error kalau yang diketik ternyata huruf.
def input_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Masukkan bilangan bulat!")


def input_float(prompt):
    while True:
        try:
            return float(input(prompt).replace(",", "."))
        except ValueError:
            print("Masukkan angka!")


def input_tanggal():
    while True:
        teks = input("Tanggal (YYYY-MM-DD, kosong = hari ini): ").strip()
        if not teks:
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        try:
            return datetime.strptime(teks, "%Y-%m-%d")
        except ValueError:
            print("Format tanggal salah!")


def input_jam(prompt):
    while True:
        try:
            return datetime.strptime(input(prompt).strip(), "%H:%M").time()
        except ValueError:
            print("Format jam salah, gunakan HH:MM")
