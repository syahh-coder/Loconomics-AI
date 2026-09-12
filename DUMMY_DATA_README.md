# DUMMY_DATA_README.md — Mode Data Sintetis untuk Uji Pipeline

## Kenapa ini ada

Survei lapangan 12 kawasan (sumber data label asli untuk D10/B07) belum
dikerjakan. Supaya pipeline training-nya sudah teruji berfungsi begitu
data asli masuk (bukan baru ketahuan ada bug pas deadline mepet), modul
ini generate data survei SINTETIS untuk uji end-to-end.

**Data ini BUKAN data asli. Jangan pernah dikirim ke tim WebGIS atau
dipakai sebagai dasar keputusan produk.**

## Cara Pakai

### 1. Generate data dummy

```bash
python -m train_model.generate_dummy_survey
```

Ini membuat file di `Scraping/data_raw/survei_dummy/` - folder TERPISAH
dari `data_raw/survei/` (tempat data asli seharusnya ada). Tidak akan
tertukar karena lokasinya beda.

### 2. Aktifkan mode dummy

Pipeline TIDAK OTOMATIS memakai data dummy meski filenya sudah ada.
Harus eksplisit diaktifkan lewat environment variable:

**Command Prompt:**
```cmd
set STATIONOMICS_USE_DUMMY=1
python -m train_model.run_pipeline
```

**PowerShell:**
```powershell
$env:STATIONOMICS_USE_DUMMY="1"
python -m train_model.run_pipeline
```

Environment variable ini cuma berlaku di sesi terminal itu. Kalau buka
terminal baru, defaultnya balik ke mode data asli (aman by default).

### 3. Cek hasilnya

Output pipeline mode dummy dikasih akhiran `_DUMMY_TEST`:
- `output/model_skor_ramai_DUMMY_TEST.joblib`
- `output/model_harga_DUMMY_TEST.joblib`
- `output/hasil_validasi_DUMMY_TEST.json`
- `data_raw/hex_features_final_DUMMY_TEST.geojson`

File-file ini tidak akan pernah menimpa file hasil asli (yang tanpa
akhiran `_DUMMY_TEST`), jadi aman dijalankan kapan saja tanpa merusak
hasil training asli kalau nanti sudah ada.

## Apa yang Divalidasi dari Uji Dummy Ini

Kalau `run_pipeline.py` jalan sampai selesai dengan data dummy tanpa
error, itu artinya:
- Semua path file dan skema kolom di `data_loader.py` benar
- `feature_engineering.py` berhasil gabung semua sumber data
- Spatial k-fold di `train_model.py` jalan tanpa crash
- `predict.py` berhasil terapkan model ke seluruh heksagon

YANG TIDAK DIVALIDASI: apakah model beneran akurat untuk dunia nyata.
R2/MAE dari data dummy TIDAK ADA ARTINYA untuk kualitas model asli -
labelnya cuma formula sintetis (populasi + jarak simpul + noise acak),
bukan hubungan ekonomi nyata.

## Kapan Berhenti Pakai Mode Dummy

Begitu `Scraping/data_raw/survei/menu_go.csv` (data asli) sudah ada dan
lolos validasi di `data_loader.py`, hapus environment variable
`STATIONOMICS_USE_DUMMY` (atau jangan di-set lagi di terminal baru), lalu
jalankan pipeline normal. Jangan hapus folder `survei_dummy/` - biarkan
untuk uji regresi di masa depan kalau pipeline diubah lagi.
