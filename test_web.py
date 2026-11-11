from datetime import datetime

import pytest

from kesehatan import CatatanBerat, CatatanVital, Database, LayananKesehatan
from web.app import buat_app

PROFIL = {"nama": "A", "usia": "20", "tinggi": "170", "berat": "70", "jenis_kelamin": "L",
          "target_berat": "65", "level_aktivitas": "2"}


@pytest.fixture
def layanan():
    return LayananKesehatan(Database(":memory:"))


@pytest.fixture
def web(tmp_path):
    app = buat_app(str(tmp_path / "uji.db"))
    klien = app.test_client()
    klien.get("/")

    def kirim(alamat, data=None, **opsi):
        with klien.session_transaction() as sesi:
            token = sesi["csrf"]
        return klien.post(alamat, data={**(data or {}), "csrf": token}, **opsi)

    klien.kirim = kirim
    return klien


def teks(respon):
    return respon.get_data(as_text=True)


def test_profil_wajib_sebelum_ringkasan(layanan):
    with pytest.raises(ValueError):
        layanan.ringkasan_tubuh()


def test_data_contoh_dan_defisit(layanan):
    layanan.isi_data_contoh()
    assert layanan.pengguna.nama == "Budi" and len(layanan.database.muat_catatan()) == 6
    hasil = layanan.defisit_surplus(datetime(2026, 10, 9))
    assert (hasil["masuk"], hasil["olahraga"], hasil["kebutuhan"]) == (950, 189, 2025)
    assert hasil["status"] == "DEFISIT" and hasil["selisih"] == -1264


def test_riwayat_urut_tanggal_dan_ringkasan_vital(layanan):
    layanan.isi_data_contoh()
    assert [c.tanggal.day for c in layanan.riwayat()] == [8, 9, 9, 9, 9, 9]
    assert layanan.ringkasan_vital() == (0, 1)


def test_catat_vital_abnormal_tetap_tersimpan(layanan):
    layanan.isi_data_contoh()
    catatan, peringatan = layanan.catat_vital(datetime(2026, 10, 10), 150, 95, 110)
    assert peringatan and catatan.status == "ABNORMAL"
    assert layanan.ringkasan_vital() == (1, 2)
    status = [c.status for c in layanan.database.muat_catatan() if isinstance(c, CatatanVital)]
    assert status == ["Normal", "ABNORMAL"]


def test_catat_berat_memperbarui_profil_dan_hapus(layanan):
    layanan.isi_data_contoh()
    layanan.catat_berat(datetime(2026, 10, 11), 70)
    assert layanan.pengguna.berat == 70
    berat = [c for c in layanan.database.muat_catatan() if isinstance(c, CatatanBerat)]
    assert len(berat) == 2
    layanan.database.hapus_catatan("catatan_berat", berat[0].id)
    assert len([c for c in layanan.database.muat_catatan() if isinstance(c, CatatanBerat)]) == 1


def test_database_menolak_nama_tabel_tidak_valid(layanan):
    with pytest.raises(ValueError):
        layanan.database.hapus_catatan("pengguna; DROP TABLE pengguna", 1)
    with pytest.raises(ValueError):
        layanan.database.isi_tabel("sqlite_master")


def test_aktivitas_tidak_tersedia_ditolak(layanan):
    layanan.isi_data_contoh()
    with pytest.raises(ValueError):
        layanan.catat_aktivitas(datetime(2026, 10, 11), 99, 30)


def test_kosongkan_menghapus_semua(layanan):
    layanan.isi_data_contoh()
    layanan.kosongkan()
    assert layanan.pengguna is None and layanan.database.muat_catatan() == []


@pytest.mark.parametrize("alamat", ["/", "/profil", "/berat", "/aktivitas", "/makanan", "/tidur", "/vital",
                                    "/defisit", "/catatan", "/database"])
def test_semua_halaman_terbuka(web, alamat):
    assert web.get(alamat, follow_redirects=True).status_code == 200


def test_beranda_awal_mengajak_membuat_profil(web):
    assert "Buat profil" in teks(web.get("/"))


def test_profil_tidak_valid_menampilkan_pesan(web):
    assert "Usia harus 1-120 tahun" in teks(web.kirim("/profil", {**PROFIL, "usia": "0"}))
    assert "harus berupa angka" in teks(web.kirim("/profil", {**PROFIL, "usia": "abc"}))


def test_halaman_berisi_hasil_data_contoh(web):
    web.kirim("/data-contoh")
    beranda = teks(web.get("/"))
    assert "Budi" in beranda and "DEFISIT 1264 kkal" in beranda and "1820 kkal" in beranda
    hitung = teks(web.get("/hitung"))
    assert "24.91" in hitung and "2320" in hitung and "Target asupan harian" in hitung


def test_vital_abnormal_dan_normal(web):
    web.kirim("/data-contoh")
    data = {"tanggal": "2026-10-10", "sistolik": "150", "diastolik": "95", "detak_jantung": "110"}
    halaman = teks(web.kirim("/vital", data, follow_redirects=True))
    assert "PERINGATAN" in halaman and "ABNORMAL" in halaman
    data = {"tanggal": "2026-10-11", "sistolik": "118", "diastolik": "78", "detak_jantung": "70"}
    assert "Tanda vital normal" in teks(web.kirim("/vital", data, follow_redirects=True))


def test_durasi_nol_ditolak(web):
    web.kirim("/data-contoh")
    halaman = teks(web.kirim("/aktivitas", {"tanggal": "2026-10-11", "aktivitas": "1", "durasi": "0"}))
    assert "Durasi harus lebih dari 0 menit" in halaman


def test_halaman_database_dan_hapus(web):
    web.kirim("/data-contoh")
    assert "catatan_vital" in teks(web.get("/database")) and "Roti &amp; susu" in teks(web.get("/database"))
    web.kirim("/hapus/catatan_makanan/1")
    assert "Roti &amp; susu" not in teks(web.get("/catatan"))
    assert web.kirim("/hapus/pengguna/1").status_code == 302
    assert "Budi" in teks(web.get("/"))


def test_post_tanpa_token_ditolak(tmp_path):
    klien = buat_app(str(tmp_path / "x.db")).test_client()
    klien.get("/")
    assert klien.post("/data-contoh", data={}).status_code == 400
    assert klien.post("/data-contoh", data={"csrf": "salah"}).status_code == 400
