import sqlite3
from datetime import datetime
from .aktivitas import Berenang, Bersepeda, JalanKaki, Lari
from .catatan import (CatatanAktivitas, CatatanBerat, CatatanMakanan, CatatanTidur, CatatanVital)
from .pengguna import Pengguna

FORMAT_TANGGAL = "%Y-%m-%d"
FORMAT_JAM = "%H:%M"

SKEMA = """
CREATE TABLE IF NOT EXISTS pengguna (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    nama TEXT NOT NULL,
    usia INTEGER NOT NULL,
    tinggi REAL NOT NULL,
    berat REAL NOT NULL,
    jenis_kelamin TEXT NOT NULL,
    target_berat REAL NOT NULL,
    level_aktivitas INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS aktivitas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL UNIQUE,
    met REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS catatan_berat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT NOT NULL,
    berat REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS catatan_aktivitas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT NOT NULL,
    aktivitas_id INTEGER NOT NULL REFERENCES aktivitas(id),
    durasi_menit INTEGER NOT NULL,
    berat_badan REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS catatan_makanan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT NOT NULL,
    nama_makanan TEXT NOT NULL,
    kalori REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS catatan_tidur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT NOT NULL,
    jam_tidur TEXT NOT NULL,
    jam_bangun TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS catatan_vital (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT NOT NULL,
    sistolik INTEGER NOT NULL,
    diastolik INTEGER NOT NULL,
    detak_jantung INTEGER NOT NULL,
    status TEXT NOT NULL
);
"""

TABEL_CATATAN = {
    CatatanBerat: "catatan_berat",
    CatatanAktivitas: "catatan_aktivitas",
    CatatanMakanan: "catatan_makanan",
    CatatanTidur: "catatan_tidur",
    CatatanVital: "catatan_vital",
}


class Database:
    def __init__(self, path="kesehatan.db"):
        self.path = path
        self.koneksi = sqlite3.connect(path)
        self.koneksi.row_factory = sqlite3.Row
        self.koneksi.execute("PRAGMA foreign_keys = ON")
        self.koneksi.executescript(SKEMA)
        self._isi_aktivitas()

    def tutup(self):
        self.koneksi.close()

    def _isi_aktivitas(self):
        for a in (JalanKaki(), Lari(), Bersepeda(), Berenang()):
            self.koneksi.execute("INSERT OR IGNORE INTO aktivitas (nama, met) VALUES (?, ?)", (a.nama, a.met))
        self.koneksi.commit()

    def simpan_pengguna(self, p):
        self.koneksi.execute(
            "INSERT OR REPLACE INTO pengguna VALUES (1, ?, ?, ?, ?, ?, ?, ?)",
            (p.nama, p.usia, p.tinggi, p.berat, p.jenis_kelamin, p.target_berat, p.level_aktivitas))
        self.koneksi.commit()

    def muat_pengguna(self):
        r = self.koneksi.execute("SELECT * FROM pengguna WHERE id = 1").fetchone()
        if r is None:
            return None
        return Pengguna(r["nama"], r["usia"], r["tinggi"], r["berat"], r["jenis_kelamin"], r["target_berat"], r["level_aktivitas"])

    def daftar_aktivitas(self):
        kelas = {a.nama: a for a in (JalanKaki(), Lari(), Bersepeda(), Berenang())}
        rows = self.koneksi.execute("SELECT id, nama FROM aktivitas ORDER BY id").fetchall()
        return [(r["id"], kelas[r["nama"]]) for r in rows]

    def simpan_catatan(self, c):
        # Tiap jenis catatan punya tabel dan kolom sendiri, jadi dicek dulu objek ini termasuk jenis yang mana. Nilai selalu dikirim lewat tanda tanya (?), tidak digabung ke teks SQL, supaya aman dari SQL injection.
        if c.id is not None:
            raise ValueError("Catatan ini sudah tersimpan")
        tanggal = c.tanggal.strftime(FORMAT_TANGGAL)
        if isinstance(c, CatatanBerat):
            sql, nilai = "INSERT INTO catatan_berat (tanggal, berat) VALUES (?, ?)", (tanggal, c.berat)
        elif isinstance(c, CatatanAktivitas):
            baris = self.koneksi.execute("SELECT id FROM aktivitas WHERE nama = ?", (c.aktivitas.nama,)).fetchone()
            berat_badan = c.kalori_terbakar / (c.aktivitas.met * c.durasi_menit / 60)
            sql = ("INSERT INTO catatan_aktivitas (tanggal, aktivitas_id, durasi_menit, berat_badan) "
                   "VALUES (?, ?, ?, ?)")
            nilai = (tanggal, baris["id"], c.durasi_menit, berat_badan)
        elif isinstance(c, CatatanMakanan):
            sql = "INSERT INTO catatan_makanan (tanggal, nama_makanan, kalori) VALUES (?, ?, ?)"
            nilai = (tanggal, c.nama_makanan, c.kalori)
        elif isinstance(c, CatatanTidur):
            sql = "INSERT INTO catatan_tidur (tanggal, jam_tidur, jam_bangun) VALUES (?, ?, ?)"
            nilai = (tanggal, c.jam_tidur.strftime(FORMAT_JAM), c.jam_bangun.strftime(FORMAT_JAM))
        elif isinstance(c, CatatanVital):
            sql = ("INSERT INTO catatan_vital (tanggal, sistolik, diastolik, detak_jantung, status) "
                   "VALUES (?, ?, ?, ?, ?)")
            nilai = (tanggal, c.sistolik, c.diastolik, c.detak_jantung, c.status)
        else:
            raise ValueError("Jenis catatan tidak dikenal")
        cur = self.koneksi.execute(sql, nilai)
        self.koneksi.commit()
        c.id = cur.lastrowid

    def muat_catatan(self):
        # Baris dari tiap tabel dibuat lagi menjadi objek catatan, sehingga bagian lain program bekerja dengan objek yang sama seperti versi terminal.
        hasil = []
        aktivitas = dict(self.daftar_aktivitas())
        for r in self.koneksi.execute("SELECT * FROM catatan_berat"):
            hasil.append(self._beri_id(CatatanBerat(self._tgl(r), r["berat"]), r))
        for r in self.koneksi.execute("SELECT * FROM catatan_aktivitas"):
            c = CatatanAktivitas(self._tgl(r), aktivitas[r["aktivitas_id"]], r["durasi_menit"], r["berat_badan"])
            hasil.append(self._beri_id(c, r))
        for r in self.koneksi.execute("SELECT * FROM catatan_makanan"):
            hasil.append(self._beri_id(CatatanMakanan(self._tgl(r), r["nama_makanan"], r["kalori"]), r))
        for r in self.koneksi.execute("SELECT * FROM catatan_tidur"):
            jam_tidur = datetime.strptime(r["jam_tidur"], FORMAT_JAM).time()
            jam_bangun = datetime.strptime(r["jam_bangun"], FORMAT_JAM).time()
            hasil.append(self._beri_id(CatatanTidur(self._tgl(r), jam_tidur, jam_bangun), r))
        for r in self.koneksi.execute("SELECT * FROM catatan_vital"):
            c = CatatanVital(self._tgl(r), r["sistolik"], r["diastolik"], r["detak_jantung"])
            hasil.append(self._beri_id(c, r))
        return hasil

    def hapus_catatan(self, tabel, id_catatan):
        # Nama tabel tidak bisa dikirim lewat tanda tanya (?), jadi dicocokkan dulu dengan daftar tabel yang diizinkan sebelum dimasukkan ke query.
        if tabel not in TABEL_CATATAN.values():
            raise ValueError("Tabel tidak dikenal")
        cur = self.koneksi.execute(f"DELETE FROM {tabel} WHERE id = ?", (id_catatan,))
        self.koneksi.commit()
        if cur.rowcount == 0:
            raise ValueError("Catatan tidak ditemukan")

    def kosongkan(self):
        for tabel in TABEL_CATATAN.values():
            self.koneksi.execute(f"DELETE FROM {tabel}")
        self.koneksi.execute("DELETE FROM pengguna")
        self.koneksi.commit()

    def isi_tabel(self, tabel):
        if tabel not in list(TABEL_CATATAN.values()) + ["pengguna", "aktivitas"]:
            raise ValueError("Tabel tidak dikenal")
        cur = self.koneksi.execute(f"SELECT * FROM {tabel}")
        return [k[0] for k in cur.description], [tuple(r) for r in cur.fetchall()]

    def _tgl(self, row):
        return datetime.strptime(row["tanggal"], FORMAT_TANGGAL)

    def _beri_id(self, catatan, row):
        catatan.id = row["id"]
        return catatan
