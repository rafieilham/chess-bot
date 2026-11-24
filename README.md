# Chess Bot

Bot catur berbasis Python dengan pemindaian layar real-time (*screen capture*), pengenalan posisi papan (*board detection*), dan kalkulasi langkah terbaik menggunakan engine catur **Stockfish**.

---

## Fitur Utama

- 🔍 **Deteksi Papan Otomatis & Manual**: Menemukan area papan catur di layar secara presisi.
- ♟️ **Analisis Posisi Catur**: Evaluasi posisi bidak catur secara *real-time*.
- ⚙️ **Integrasi Engine Stockfish**: Mendukung engine Stockfish eksternal untuk analisis mendalam dan saran langkah terbaik.
- 🖥️ **Antarmuka Grafis (GUI)**: GUI interaktif berbasis Tkinter untuk kontrol bot, pengaturan kedalaman analisis (*depth*), dan mode permainan.

---

## Kebutuhan Sistem & Instalasi

### 1. Kloning Repositori
```bash
git clone https://github.com/rafieilham/chess-bot.git
cd chess-bot
```

### 2. Buat & Aktifkan Virtual Environment (Opsional tapi Direkomendasikan)
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### 3. Pasang Dependensi
```bash
pip install -r requirements.txt
```

---

## Pengaturan Stockfish Engine

Bot ini membutuhkan file binary Stockfish untuk menganalisis langkah catur:

1. Unduh binary Stockfish resmi untuk sistem operasi Anda dari [Stockfish Official Website](https://stockfishchess.org/download/).
2. Ekstrak file executable Stockfish (misalnya `stockfish-windows-x86-64-universal.exe`).
3. Anda dapat:
   - Menaruh executable tersebut di dalam folder project, atau
   - Memilih file executable langsung melalui tombol **"Pilih File Stockfish (.exe)"** di tampilan GUI saat bot dijalankan.

---

## Cara Menjalankan

Jalankan skrip utama:
```bash
python chess_bot.py
```

1. Buka situs catur pilihan Anda di browser (seperti Chess.com atau Lichess).
2. Sesuaikan area deteksi papan jika diperlukan melalui GUI bot.
3. Pilih mode dan jalankan bot sesuai kebutuhan Anda.

---

## Catatan & Lisensi
Proyek ini dibuat untuk tujuan edukasi dan eksplorasi *computer vision* serta integrasi engine catur AI.
