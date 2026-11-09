# SelfHealthMonitoring

Aplikasi Monitoring Kesehatan Pribadi berbasis Python (konsol).
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

## Konsep OOP
- Kelas dan objek, encapsulation (atribut privat dengan `@property`)
- Inheritance dan abstract class (`CatatanHarian`, `AktivitasFisik`)
- Polymorphism (overriding `tampilkan()`, `kalori_masuk()`, `kalori_keluar()`)
- Exception handling (`AbnormalVitalException`, `ValueError`)
- Iterator (`RiwayatCatatan` dengan `__iter__` dan `__next__`), generator, dan coroutine

## Cara menjalankan
Butuh Python 3.8 ke atas, tanpa library tambahan.

    python kesehatan.py        # aplikasi dengan menu
    python driver_demo.py      # demo polymorphism, encapsulation, exception, iterator
    python test_kesehatan.py   # pengujian otomatis, hasilnya OK

Menu 11 (Isi Data Contoh) mengisi profil dan catatan contoh supaya fitur bisa langsung dicoba.

## Catatan
Data disimpan di memori selama program berjalan. Aplikasi ini alat bantu pencatatan, bukan alat diagnosis medis.
