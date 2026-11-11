import io
import secrets
from contextlib import redirect_stdout
from datetime import datetime

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for

from kesehatan import (CatatanAktivitas, CatatanBerat, CatatanMakanan, CatatanTidur,
                       CatatanVital, Database, LayananKesehatan, NAMA_LEVEL)
from kesehatan.database import TABEL_CATATAN

JENIS = {CatatanBerat: "Berat badan", CatatanAktivitas: "Aktivitas", CatatanMakanan: "Makanan",
         CatatanTidur: "Tidur", CatatanVital: "Tanda vital"}
NAMA_TABEL = ["pengguna", "aktivitas"] + list(TABEL_CATATAN.values())


def buat_app(path_db="kesehatan.db"):
    app = Flask(__name__)
    app.secret_key = "kesehatan-kelompok-8"
    app.config["PATH_DB"] = path_db

    def layanan():
        if "layanan" not in g:
            g.layanan = LayananKesehatan(Database(app.config["PATH_DB"]))
        return g.layanan

    @app.before_request
    def periksa_token():
        if request.method == "POST":
            token = session.get("csrf", "")
            if not token or not secrets.compare_digest(token, request.form.get("csrf", "")):
                abort(400, "Token keamanan tidak cocok, muat ulang halaman lalu coba lagi")

    @app.context_processor
    def sisipkan_token():
        if "csrf" not in session:
            session["csrf"] = secrets.token_hex(16)
        return {"csrf_token": session["csrf"]}

    @app.teardown_appcontext
    def tutup_database(_):
        l = g.pop("layanan", None)
        if l is not None:
            l.database.tutup()

    def angka(nama, tipe=float):
        teks = request.form.get(nama, "").strip().replace(",", ".")
        try:
            return tipe(teks)
        except ValueError:
            raise ValueError(f"Isian '{nama.replace('_', ' ')}' harus berupa angka")

    def tanggal_form():
        teks = request.form.get("tanggal", "")
        try:
            return datetime.strptime(teks, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Format tanggal salah")

    def jam_form(nama):
        try:
            return datetime.strptime(request.form.get(nama, ""), "%H:%M").time()
        except ValueError:
            raise ValueError("Format jam salah, gunakan HH:MM")

    def baris(c):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            c.tampilkan()
        isi = buffer.getvalue().strip().split(" : ", 1)[1]
        return {"id": c.id, "tanggal": c.tanggal.strftime("%Y-%m-%d"), "jenis": JENIS[type(c)],
                "isi": isi, "tabel": TABEL_CATATAN[type(c)], "abnormal": getattr(c, "status", "") == "ABNORMAL"}

    def catatan_jenis(jenis, batas=8):
        data = [baris(c) for c in layanan().riwayat() if isinstance(c, jenis)]
        return data[::-1][:batas]

    def hari_ini():
        return datetime.now().strftime("%Y-%m-%d")

    def aman(fungsi, sukses):
        try:
            fungsi()
            flash(sukses, "ok")
            return True
        except ValueError as e:
            flash(str(e), "error")
            return False

    @app.route("/")
    def beranda():
        l = layanan()
        if l.pengguna is None:
            return render_template("beranda.html", tubuh=None)
        catatan = list(l.riwayat())
        terakhir = catatan[-1].tanggal if catatan else None
        kalori = l.defisit_surplus(terakhir) if terakhir else None
        return render_template("beranda.html", tubuh=l.ringkasan_tubuh(), kalori=kalori,
                               terakhir=terakhir, jumlah=len(catatan), vital=l.ringkasan_vital())

    @app.route("/profil", methods=["GET", "POST"])
    def profil():
        l = layanan()
        if request.method == "POST":
            ok = aman(lambda: l.buat_profil(request.form.get("nama", ""), angka("usia", int), angka("tinggi"),
                                            angka("berat"), request.form.get("jenis_kelamin", ""),
                                            angka("target_berat"), angka("level_aktivitas", int)),
                      "Profil tersimpan")
            if ok:
                return redirect(url_for("hitung"))
        return render_template("profil.html", p=l.pengguna, level=NAMA_LEVEL)

    @app.route("/hitung")
    def hitung():
        try:
            return render_template("hitung.html", t=layanan().ringkasan_tubuh())
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for("profil"))

    @app.route("/berat", methods=["GET", "POST"])
    def berat():
        l = layanan()
        if request.method == "POST":
            if aman(lambda: l.catat_berat(tanggal_form(), angka("berat")), "Berat badan tercatat, profil diperbarui"):
                return redirect(url_for("berat"))
        return render_template("berat.html", daftar=catatan_jenis(CatatanBerat), hari=hari_ini())

    @app.route("/aktivitas", methods=["GET", "POST"])
    def aktivitas():
        l = layanan()
        if request.method == "POST":
            if aman(lambda: l.catat_aktivitas(tanggal_form(), angka("aktivitas", int), angka("durasi", int)),
                    "Aktivitas tercatat"):
                return redirect(url_for("aktivitas"))
        pilihan = [(i, a.nama, a.met) for i, a in l.database.daftar_aktivitas()]
        return render_template("aktivitas.html", daftar=catatan_jenis(CatatanAktivitas), hari=hari_ini(), pilihan=pilihan)

    @app.route("/makanan", methods=["GET", "POST"])
    def makanan():
        l = layanan()
        if request.method == "POST":
            if aman(lambda: l.catat_makanan(tanggal_form(), request.form.get("nama_makanan", ""), angka("kalori")),
                    "Makanan tercatat"):
                return redirect(url_for("makanan"))
        return render_template("makanan.html", daftar=catatan_jenis(CatatanMakanan), hari=hari_ini())

    @app.route("/tidur", methods=["GET", "POST"])
    def tidur():
        l = layanan()
        if request.method == "POST":
            if aman(lambda: l.catat_tidur(tanggal_form(), jam_form("jam_tidur"), jam_form("jam_bangun")),
                    "Pola tidur tercatat"):
                return redirect(url_for("tidur"))
        return render_template("tidur.html", daftar=catatan_jenis(CatatanTidur), hari=hari_ini())

    @app.route("/vital", methods=["GET", "POST"])
    def vital():
        l = layanan()
        if request.method == "POST":
            try:
                catatan, peringatan = l.catat_vital(tanggal_form(), angka("sistolik", int), angka("diastolik", int),
                                                    angka("detak_jantung", int))
                if peringatan:
                    flash(f"PERINGATAN: {peringatan}. Saran: istirahat, ukur ulang, dan konsultasikan ke dokter "
                          "bila berlanjut.", "warning")
                else:
                    flash("Tanda vital normal", "ok")
                return redirect(url_for("vital"))
            except ValueError as e:
                flash(str(e), "error")
        return render_template("vital.html", daftar=catatan_jenis(CatatanVital), hari=hari_ini())

    @app.route("/defisit")
    def defisit():
        l = layanan()
        tanggal = request.args.get("tanggal", hari_ini())
        hasil = None
        try:
            hasil = l.defisit_surplus(datetime.strptime(tanggal, "%Y-%m-%d"))
        except ValueError as e:
            flash(str(e) if l.pengguna is None else "Format tanggal salah", "error")
        return render_template("defisit.html", tanggal=tanggal, h=hasil)

    @app.route("/catatan")
    def catatan():
        l = layanan()
        daftar = [baris(c) for c in l.riwayat()]
        masuk, diperiksa = l.ringkasan_vital()
        return render_template("catatan.html", daftar=daftar, abnormal=masuk, diperiksa=diperiksa)

    @app.route("/hapus/<tabel>/<int:id_catatan>", methods=["POST"])
    def hapus(tabel, id_catatan):
        try:
            layanan().database.hapus_catatan(tabel, id_catatan)
            flash("Catatan dihapus", "ok")
        except ValueError as e:
            flash(str(e), "error")
        return redirect(request.referrer or url_for("catatan"))

    @app.route("/data-contoh", methods=["POST"])
    def data_contoh():
        layanan().isi_data_contoh()
        flash("Data contoh terisi: profil Budi dan 6 catatan (8-9 Oktober 2026)", "ok")
        return redirect(url_for("beranda"))

    @app.route("/database")
    def database():
        l = layanan()
        tabel = []
        for nama in NAMA_TABEL:
            kolom, isi = l.database.isi_tabel(nama)
            tabel.append({"nama": nama, "kolom": kolom, "isi": isi})
        return render_template("database.html", tabel=tabel, path=app.config["PATH_DB"])

    return app
