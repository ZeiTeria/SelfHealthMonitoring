# Pengali BMR untuk tiap level aktivitas, dari jarang olahraga (1,2) sampai sangat aktif (1,9).
FAKTOR_AKTIVITAS = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9}
# Satu kilogram lemak tubuh kira-kira setara dengan 7700 kkal. Untuk rencana target berat,
# kami memakai selisih 500 kkal per hari supaya berat turun atau naik sekitar 0,5 kg per minggu.
KKAL_PER_KG = 7700
PENYESUAIAN_HARIAN = 500
NAMA_LEVEL = {1: "Sedentari (jarang olahraga)", 2: "Ringan (1-3 hari/minggu)",
              3: "Sedang (3-5 hari/minggu)", 4: "Berat (6-7 hari/minggu)",
              5: "Sangat berat (fisik berat/2x sehari)"}


class Pengguna:
    def __init__(self, nama, usia, tinggi, berat, jenis_kelamin, target_berat, level_aktivitas):
        # Semua nilai diisi lewat setter di bawah. Dengan begitu aturan validasinya cukup ditulis
        # satu kali dan tetap berlaku ketika nilainya diubah belakangan, misalnya berat badan.
        self.nama = nama
        self.usia = usia
        self.tinggi = tinggi
        self.berat = berat
        self.jenis_kelamin = jenis_kelamin
        self.target_berat = target_berat
        self.level_aktivitas = level_aktivitas

    @property
    def nama(self):
        return self._nama

    @nama.setter
    def nama(self, nilai):
        if not nilai.strip():
            raise ValueError("Nama tidak boleh kosong")
        self._nama = nilai.strip()

    @property
    def usia(self):
        return self._usia

    @usia.setter
    def usia(self, nilai):
        if not 1 <= nilai <= 120:
            raise ValueError("Usia harus 1-120 tahun")
        self._usia = nilai

    @property
    def tinggi(self):
        return self._tinggi

    @tinggi.setter
    def tinggi(self, nilai):
        if not 50 <= nilai <= 250:
            raise ValueError("Tinggi harus 50-250 cm")
        self._tinggi = nilai

    @property
    def berat(self):
        return self._berat

    @berat.setter
    def berat(self, nilai):
        if not 10 <= nilai <= 500:
            raise ValueError("Berat harus 10-500 kg")
        self._berat = nilai

    @property
    def jenis_kelamin(self):
        return self._jenis_kelamin

    @jenis_kelamin.setter
    def jenis_kelamin(self, nilai):
        nilai = nilai.strip().upper()
        if nilai not in ("L", "P"):
            raise ValueError("Jenis kelamin harus L atau P")
        self._jenis_kelamin = nilai

    @property
    def target_berat(self):
        return self._target_berat

    @target_berat.setter
    def target_berat(self, nilai):
        if not 10 <= nilai <= 500:
            raise ValueError("Target berat harus 10-500 kg")
        self._target_berat = nilai

    @property
    def level_aktivitas(self):
        return self._level_aktivitas

    @level_aktivitas.setter
    def level_aktivitas(self, nilai):
        if nilai not in FAKTOR_AKTIVITAS:
            raise ValueError("Level aktivitas harus 1-5")
        self._level_aktivitas = nilai

    def tampil_profil(self):
        print(f"Nama           : {self.nama}")
        print(f"Usia           : {self.usia} tahun")
        print(f"Jenis kelamin  : {self.jenis_kelamin}")
        print(f"Tinggi         : {self.tinggi} cm")
        print(f"Berat          : {self.berat} kg (target {self.target_berat} kg)")
        print(f"Level aktivitas: {self.level_aktivitas} - {NAMA_LEVEL[self.level_aktivitas]}")

    def hitung_bmi(self):
        return self.berat / (self.tinggi / 100) ** 2

    def kategori_bmi(self):
        # Batas kategori mengikuti Kemenkes: di bawah 18,5 kurus, sampai 25 normal,
        # lebih dari 25 sampai 27 gemuk, dan di atas 27 obesitas.
        bmi = self.hitung_bmi()
        if bmi < 18.5:
            return "Kurus"
        if bmi <= 25:
            return "Normal"
        if bmi <= 27:
            return "Gemuk"
        return "Obesitas"

    def hitung_bmr(self):
        # Rumus Mifflin-St Jeor. Perbedaan laki-laki dan perempuan hanya di angka terakhir:
        # ditambah 5 untuk laki-laki dan dikurangi 161 untuk perempuan.
        bmr = 10 * self.berat + 6.25 * self.tinggi - 5 * self.usia
        return bmr + 5 if self.jenis_kelamin == "L" else bmr - 161

    # Parameter level diberi nilai awal 0. Kalau tidak diisi, dipakai level aktivitas milik
    # pengguna; kalau diisi 1 sampai 5, dipakai level itu. Jadi satu method bisa dipanggil dengan
    # dua cara tanpa menulis dua method yang berbeda.
    def hitung_tdee(self, level=0):
        if level == 0:
            level = self.level_aktivitas
        if level not in FAKTOR_AKTIVITAS:
            raise ValueError("Level aktivitas harus 1-5")
        return self.hitung_bmr() * FAKTOR_AKTIVITAS[level]

    def rencana_target(self):
        # Mengubah selisih berat badan menjadi saran kalori harian. Untuk menurunkan berat,
        # asupan dikurangi 500 kkal dari TDEE, tetapi tidak boleh lebih rendah dari BMR supaya
        # tidak terlalu ekstrem. Untuk menaikkan berat, asupan ditambah 500 kkal.
        selisih = self.berat - self.target_berat
        tdee = self.hitung_tdee()
        if abs(selisih) < 0.1:
            return {"arah": "tetap", "kalori_harian": tdee, "penyesuaian": 0, "perkiraan_minggu": 0}
        if selisih > 0:
            arah = "turun"
            kalori = max(tdee - PENYESUAIAN_HARIAN, self.hitung_bmr())
        else:
            arah = "naik"
            kalori = tdee + PENYESUAIAN_HARIAN
        penyesuaian = abs(kalori - tdee)
        # Total kalori yang harus dikumpulkan (selisih kg x 7700) dibagi penyesuaian per hari
        # menghasilkan jumlah hari, lalu dibagi 7 menjadi minggu.
        hari = abs(selisih) * KKAL_PER_KG / penyesuaian
        return {"arah": arah, "kalori_harian": kalori, "penyesuaian": penyesuaian,
                "perkiraan_minggu": hari / 7}
