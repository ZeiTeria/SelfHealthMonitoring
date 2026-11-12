import sys


# Tanpa argumen, program berjalan sebagai web. Dengan --konsol, yang jalan adalah versi terminal.
def main():
    if "--konsol" in sys.argv:
        from kesehatan import AplikasiKesehatan
        AplikasiKesehatan().jalankan()
        return
    from web.app import buat_app
    print("Buka http://127.0.0.1:5000 di browser")
    buat_app().run(host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()
