from datetime import datetime, time

import pytest

from kesehatan import (AbnormalVitalException, Berenang, CatatanAktivitas, CatatanBerat,
                       CatatanHarian, CatatanMakanan, CatatanTidur, CatatanVital, Lari,
                       Pengguna, RiwayatCatatan, catatan_tanggal, pemantau_vital)

HARI = datetime(2026, 10, 9)


@pytest.fixture
def nicholas():
    return Pengguna("Nicholas", 19, 175, 81, "L", 75, 2)


def test_bmi_dan_kategori(nicholas):
    assert round(nicholas.hitung_bmi(), 2) == 26.45
    assert nicholas.kategori_bmi() == "Gemuk"


@pytest.mark.parametrize("berat, kategori", [(45, "Kurus"), (60, "Normal"), (75, "Gemuk"), (95, "Obesitas")])
def test_kategori_bmi_kemenkes(berat, kategori):
    assert Pengguna("C", 20, 170, berat, "L", 60, 1).kategori_bmi() == kategori


@pytest.mark.parametrize("bmi, kategori", [(18.4, "Kurus"), (18.5, "Normal"), (25, "Normal"), (26, "Gemuk"),
                                           (27, "Gemuk"), (28, "Obesitas")])
def test_batas_bmi(bmi, kategori):
    assert Pengguna("X", 20, 100, bmi, "L", 20, 1).kategori_bmi() == kategori


def test_bmr_mifflin_st_jeor(nicholas):
    assert nicholas.hitung_bmr() == 1813.75
    assert Pengguna("B", 20, 160, 50, "P", 50, 1).hitung_bmr() == 500 + 1000 - 100 - 161


def test_tdee_default_dan_level(nicholas):
    assert nicholas.hitung_tdee() == 1813.75 * 1.375
    assert nicholas.hitung_tdee(1) == 2176.5
    with pytest.raises(ValueError):
        nicholas.hitung_tdee(9)


@pytest.mark.parametrize("data", [
    ("", 20, 170, 70, "L", 65, 2), ("A", 0, 170, 70, "L", 65, 2), ("A", 20, 17, 70, "L", 65, 2),
    ("A", 20, 170, -1, "L", 65, 2), ("A", 20, 170, 70, "X", 65, 2), ("A", 20, 170, 70, "L", 65, 6)])
def test_profil_tidak_valid_ditolak(data):
    with pytest.raises(ValueError):
        Pengguna(*data)


def test_encapsulation_setter_dan_readonly(nicholas):
    nicholas.berat = 68
    assert nicholas.berat == 68 and nicholas._berat == 68
    with pytest.raises(ValueError):
        nicholas.berat = -5
    assert nicholas.berat == 68
    with pytest.raises(AttributeError):
        CatatanBerat(HARI, 70).berat = 99


def test_kalori_aktivitas_met():
    assert Lari().hitung_kalori(70, 30) == 9.8 * 70 * 0.5
    assert CatatanAktivitas(HARI, Berenang(), 60, 70).kalori_keluar() == 560
    with pytest.raises(ValueError):
        CatatanAktivitas(HARI, Lari(), 0, 70)


def test_polymorphism_kalori_masuk_keluar():
    makanan = CatatanMakanan(HARI, "Nasi", 500)
    assert makanan.kalori_masuk() == 500 and makanan.kalori_keluar() == 0
    with pytest.raises(ValueError):
        CatatanMakanan(HARI, "x", -5)


def test_durasi_tidur_lewat_tengah_malam():
    assert CatatanTidur(HARI, time(23, 30), time(6, 0)).durasi_jam() == 6.5
    assert CatatanTidur(HARI, time(22, 0), time(23, 0)).durasi_jam() == 1


@pytest.mark.parametrize("nilai", [(150, 80, 70), (120, 95, 70), (120, 80, 110), (85, 55, 70)])
def test_tanda_vital_abnormal(nilai):
    catatan = CatatanVital(HARI, *nilai)
    with pytest.raises(AbnormalVitalException):
        catatan.cek_vital()
    assert catatan.status == "ABNORMAL"


def test_tanda_vital_normal():
    catatan = CatatanVital(HARI, 120, 80, 70)
    catatan.cek_vital()
    assert catatan.status == "Normal"


def test_abstract_class_tidak_bisa_dibuat():
    with pytest.raises(TypeError):
        CatatanHarian(HARI)


def test_iterator_terurut_tanggal():
    data = [CatatanBerat(datetime(2026, 10, d), 70) for d in (3, 1, 2)]
    assert [c.tanggal.day for c in RiwayatCatatan(data)] == [1, 2, 3]


def test_generator_per_tanggal():
    data = [CatatanBerat(datetime(2026, 10, d), 70) for d in (1, 2, 2)]
    assert len(list(catatan_tanggal(data, datetime(2026, 10, 2)))) == 2


def test_coroutine_ringkasan_vital():
    pantau = pemantau_vital()
    assert next(pantau) == (0, 0)
    abnormal = CatatanVital(HARI, 150, 80, 70)
    with pytest.raises(AbnormalVitalException):
        abnormal.cek_vital()
    assert pantau.send(abnormal) == (1, 1)
    assert pantau.send(CatatanVital(HARI, 120, 80, 70)) == (1, 2)


def test_rencana_target_turun(nicholas):
    r = nicholas.rencana_target()
    assert r["arah"] == "turun" and round(r["kalori_harian"]) == 1994 and r["penyesuaian"] == 500
    assert round(r["perkiraan_minggu"], 1) == 13.2


def test_rencana_target_naik_tetap_dan_batas_bmr():
    assert Pengguna("A", 20, 170, 60, "L", 65, 2).rencana_target()["arah"] == "naik"
    sama = Pengguna("A", 20, 170, 65, "L", 65, 1)
    assert sama.rencana_target()["arah"] == "tetap" and sama.rencana_target()["kalori_harian"] == sama.hitung_tdee()
    rendah = Pengguna("A", 60, 150, 95, "P", 50, 1)
    assert rendah.rencana_target()["kalori_harian"] >= rendah.hitung_bmr()


def test_iterator_bersarang_tidak_saling_mengganggu():
    riwayat = RiwayatCatatan([CatatanBerat(datetime(2026, 10, d), 70) for d in (1, 2, 3)])
    pasangan = [(a, b) for a in riwayat for b in riwayat]
    assert len(pasangan) == 9


def test_tanggal_di_luar_rentang_ditolak():
    with pytest.raises(ValueError):
        CatatanBerat(datetime(999, 1, 1), 70)


def test_id_catatan_hanya_bisa_diisi_sekali():
    c = CatatanBerat(HARI, 70)
    assert c.id is None
    c.id = 5
    with pytest.raises(ValueError):
        c.id = 6


def test_vital_sistolik_harus_lebih_besar_dari_diastolik():
    with pytest.raises(ValueError):
        CatatanVital(HARI, 80, 120, 70)


def test_status_vital_dihitung_dari_nilai_tanpa_cek_vital():
    assert CatatanVital(HARI, 150, 95, 70).status == "ABNORMAL"
    assert CatatanVital(HARI, 120, 80, 70).status == "Normal"


def test_validasi_tambahan():
    with pytest.raises(ValueError):
        Pengguna("A", 20.5, 175, 81, "L", 75, 2)
    with pytest.raises(ValueError):
        Pengguna("A", 20, 175, 81, None, 75, 2)
    with pytest.raises(ValueError):
        Pengguna("A" * 51, 20, 175, 81, "L", 75, 2)
    with pytest.raises(ValueError):
        CatatanTidur(HARI, time(7, 0), time(7, 0))
    with pytest.raises(ValueError):
        CatatanAktivitas(HARI, Lari(), 30, 0)
    with pytest.raises(ValueError):
        Pengguna("A", 20, 175, 81, "L", 75, 2).hitung_tdee(True)
    with pytest.raises(ValueError):
        Pengguna("A", 20, 175, 81, "L", 75, 2).hitung_tdee(False)


def test_aktivitas_fisik_abstract_dan_intensitas():
    from kesehatan import AktivitasFisik
    with pytest.raises(TypeError):
        AktivitasFisik("X", 1.0)
    assert Lari().intensitas() == "Berat"
