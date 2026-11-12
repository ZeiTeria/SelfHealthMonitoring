# SelfHealthMonitoring

Aplikasi Monitoring Kesehatan Pribadi berbasis Python, dengan tampilan web (Flask) dan database SQLite.
Proyek UTS Perancangan dan Pemrograman Berorientasi Objek, Kelompok 8, IF-A Sore, Universitas Mikroskil.

## Fitur (F1-F10)
1. Profil pengguna (usia, tinggi, berat, target)
2. BMI dan kategori (batas Kemenkes: Kurus < 18,5; Normal 18,5-25; Gemuk > 25-27; Obesitas > 27)
3. BMR (Mifflin-St Jeor) dan TDEE untuk 5 level aktivitas
4. Log berat badan harian
5. Log aktivitas fisik dan kalori terbakar (MET)
6. Log makanan dan kalori masuk
7. Defisit/surplus kalori per tanggal
8. Log pola tidur (termasuk tidur melewati tengah malam)
9. Catat tanda vital (sistolik, diastolik, detak jantung)
10. `AbnormalVitalException` jika tanda vital di luar batas normal

Tambahan: rencana mencapai target berat (target asupan kalori harian, TDEE dikurangi atau ditambah 500 kkal tanpa turun di bawah BMR, dan perkiraan lama dalam minggu).

Pada versi web, semua data disimpan di database SQLite (`kesehatan.db`, dibuat otomatis) dan halaman "Database" menampilkan isi tabelnya. Versi terminal (`--konsol`) menyimpan data di memori saja, jadi hilang saat program ditutup.

## Konsep OOP
- Kelas dan objek, encapsulation (atribut privat dengan `@property`)
- Inheritance dan abstract class (`CatatanHarian`, `AktivitasFisik`)
- Polymorphism (overriding `tampilkan()`, `kalori_masuk()`, `kalori_keluar()`)
- Exception handling (`AbnormalVitalException`, `ValueError`)
- Iterator (`RiwayatCatatan` dengan `__iter__` dan `__next__`), generator, dan coroutine

## Struktur proyek
    main.py                  titik masuk: web (default) atau terminal (--konsol)
    driver_demo.py           demo polymorphism, encapsulation, exception, iterator
    test_kesehatan.py        pytest: kelas-kelas model
    test_web.py              pytest: database, layanan, dan halaman web
    requirements.txt         daftar library (Flask)
    kesehatan/
        exceptions.py        AbnormalVitalException
        aktivitas.py         AktivitasFisik dan turunannya (MET)
        pengguna.py          Pengguna: BMI, BMR, TDEE, rencana target
        catatan/             satu berkas per kelas catatan:
            catatan_harian.py    CatatanHarian (abstract)
            catatan_berat.py, catatan_aktivitas.py, catatan_makanan.py,
            catatan_tidur.py, catatan_vital.py
        iterasi.py           RiwayatCatatan (iterator), generator, coroutine
        database.py          Database: penyimpanan SQLite
        layanan.py           LayananKesehatan: logika yang dipakai halaman web
        input_util.py        fungsi bantu input (versi terminal)
        aplikasi.py          AplikasiKesehatan: menu terminal
    web/
        app.py               rute Flask (dengan perlindungan CSRF)
        templates/           halaman HTML (Jinja)
        static/              style.css dan logo

## Cara menjalankan
Butuh Python 3.8 ke atas.

    pip install -r requirements.txt
    python main.py             # buka http://127.0.0.1:5000 di browser
    python main.py --konsol    # versi terminal (tanpa Flask dan tanpa database)
    python driver_demo.py      # demo polymorphism, encapsulation, exception, iterator

Pengujian (butuh pytest):

    pip install pytest
    python -m pytest

Tombol "Isi data contoh" ada di halaman Beranda (saat belum ada profil) dan di halaman Profil. Tombol ini mengisi profil dan catatan contoh supaya semua fitur bisa langsung dicoba.

## Catatan
Aplikasi ini alat bantu pencatatan, bukan alat diagnosis medis.
