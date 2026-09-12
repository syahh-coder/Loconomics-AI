# PRD — Model Imputasi Spasial (A6) STATIONOMICS

## 1. Latar Belakang & Masalah

Data misi MAPID (Menu Go, Struk Go) cuma nutupin sedikit heksagon lewat
survei lapangan. Dua variabel paling penting di seluruh proyek —
**skor keramaian terkoreksi (D10)** dan **harga rata-rata menu (B07)** —
cuma ada nilainya di heksagon yang disurvei langsung. Di luar itu, kosong.

Model ini (fitur A6 di laporan, prioritas WAJIB) belajar hubungan antara
kedua variabel itu dengan fitur yang tersedia **di semua heksagon**
(populasi, kepadatan POI, jarak ke simpul transit, dst), lalu dipakai
memprediksi nilai D10 dan B07 di heksagon yang tidak pernah disurvei.
Tanpa ini, ~99% peta akan kosong.

## 2. STATUS DATA SAAT INI — BACA DULU SEBELUM MULAI CODING

**Update (setelah cross-check koordinat presisi terhadap bbox):** temuan awal
kalau "semua sample MAPID di luar wilayah studi" **TERNYATA CUMA BENAR
UNTUK 3 DARI 4 DATASET**. Sudah diverifikasi manual koordinat tiap titik:

| Dataset | Titik dalam bbox studi | Lokasi |
|---|---|---|
| **Menu Go** | **15/15** ✅ MASUK | lat -6.40 s.d -6.42, lon 106.82-106.85 |
| Struk Go | 0/15 | Bandung, lon ~107.53-107.62 |
| Properti Go | 0/15 | Bandung, lon ~107.58-107.72 |
| Activity | 0/50 | Bandung, lon ~107.43-107.62 |

**Ini penting karena D10 (skor_ramai_terkoreksi) dan B07 (harga_median_porsi)
KEDUANYA diturunkan dari Menu Go** — bukan dari Struk Go/Properti Go/Activity.
Artinya kita punya **15 titik label ASLI yang valid secara geografis**
untuk target variabel yang dibutuhkan model ini.

### Strategi yang disepakati (hasil mentoring): data hybrid real + sintetis

15 titik real tetap **terlalu sedikit** untuk spatial k-fold yang layak
(minimum 30 titik, 3 kawasan unik — lihat Bagian 6). Sesuai arahan mentor
saat sesi mentoring: **boleh menggabungkan augmentasi data sintetis
dengan data asli, SELAMA data asli tetap dipertahankan dan bukan
dibuang/diganti**. Fokus penilaian lomba ke solusi produk WebGIS, bukan
kemurnian metodologi data science.

**Konsekuensi untuk implementasi:**
- 15 titik Menu Go asli **WAJIB selalu ikut** dalam dataset training, ditandai `sumber_data = "real"`
- Titik sintetis augmentasi ditandai `sumber_data = "sintetis"` — kolom ini **tidak boleh hilang** di data gabungan, supaya bisa dibedakan kapan pun diperlukan
- **WAJIB disebutkan di halaman Metodologi produk akhir** bahwa sebagian data training adalah augmentasi sintetis sambil survei lapangan 12 kawasan berjalan — konsisten dengan prinsip proyek ini yang selalu menyatakan keterbatasan secara terbuka (lihat pola yang sama di seluruh laporan pendataan: batasan OSM, batasan cakupan NJOP, dst)
- Skor R²/MAE hasil validasi **tetap dilaporkan apa adanya**, dan di pesan serah terima ke tim WebGIS wajib disebutkan proporsi data real vs sintetis yang dipakai

Detail teknis strategi ini ada di Bagian 4a (baru) dan skrip
`process_real_survey.py` + `merge_training_data.py`.

### 3 dataset lain (Struk Go, Properti Go, Activity) — tetap berguna meski di luar bbox

Tidak dipakai sebagai ground truth spasial (lokasinya di luar wilayah
studi), tapi tetap berguna sebagai:
- Referensi skema/format kolom asli (lihat DATA_SCHEMA.md — beberapa nama
  kolom terpotong/beda dari dokumen ketentuan resmi, ini contoh konkretnya)
- Kalau nanti scope diperluas ke variabel lain (B09 nominal struk, P05
  harga sewa), pola pemrosesannya bisa dicontoh dari sini

## 3. Input yang Harus Dibaca Agent

Agent (dijalankan di Antigravity) harus baca semua file berikut sebelum
mulai coding. Jangan asumsikan skema dari dokumentasi ini saja — buka file
aslinya, karena beberapa nama kolom bisa beda dari yang didokumentasikan
(pola ini sudah terjadi berkali-kali sepanjang proyek: nama kolom CSV asli
vs dokumen ketentuan sering beda).

### 3.1 Fitur prediktor (tersedia di semua heksagon — sudah lengkap)

| File | Variabel kamus data | Keterangan |
|---|---|---|
| `Scraping/data_raw/h3_grid_with_pop.geojson` | D01 (`pop_100m`) | |
| `Scraping/data_raw/h3_grid_with_pop_age.geojson` | D02 (`pop_usia_produktif`) | |
| `Scraping/data_raw/open_buildings/h3_grid_with_buildings.geojson` | M01, M02 (`rasio_tutupan_bangunan`, `luas_bangunan_median`) | |
| `Scraping/data_raw/inarisk/h3_grid_with_risiko_banjir.geojson` | proksi L03 (`risiko_banjir_indeks_mean`, `risiko_banjir_indeks_max`) | Ini indeks mentah, belum kelas |
| `Scraping/data_raw/osm/kompetitor.geojson` | untuk turunan C01-C08 | Titik, perlu spatial join + agregasi per heksagon (belum dilakukan) |
| `Scraping/data_raw/osm/simpul_transit.geojson` | untuk turunan D03-D06 | Titik, perlu hitung jarak ke heksagon (belum dilakukan) |
| `Scraping/data_raw/osm/generator_keramaian.geojson` | D09 | Titik, perlu agregasi per heksagon (belum dilakukan) |
| `Scraping/data_raw/poi_terpadu.geojson` | dasar C01-C08 versi gabungan OSM+Overture | Titik |
| `Scraping/data_raw/jakarta_satu/rdtr.geojson` | L01, L02 | Poligon zona, perlu spatial join |
| `Scraping/data_raw/h3_grid_res9.geojson` | geometri dasar | Grid kosong, dipakai sebagai kerangka join semua fitur di atas |

**PENTING:** file-file di atas itu OUTPUT MENTAH per-sumber, BELUM digabung
jadi satu tabel `hex_features`. Menggabungkan semua ini ke satu tabel per
`hex_id` adalah bagian dari task ini (lihat `feature_engineering.py` di
Bagian 5) — bukan sesuatu yang sudah beres.

### 3.2 Data label / target (BELUM LENGKAP — cek dulu sebelum lanjut)

| File yang DIHARAPKAN ada | Variabel target | Status per hari ini |
|---|---|---|
| `Scraping/data_raw/survei/menu_go.csv` | D10 (`skor_ramai_terkoreksi`), B07 (`harga_median_porsi`) | **Kemungkinan besar belum ada / masih kosong** |
| `Scraping/data_raw/survei/struk_go.csv` | B09 (`nominal_median_struk`) | **Kemungkinan besar belum ada / masih kosong** |

Kalau file-file ini tidak ada atau isinya kosong/placeholder, skrip
**WAJIB berhenti dengan pesan error yang jelas** menyebutkan bahwa data
survei lapangan diperlukan sebelum training bisa dijalankan — TIDAK BOLEH
lanjut training pakai data yang tidak valid (mis. sample Depok/Bandung
yang di luar wilayah studi, atau nilai kosong yang diisi 0 secara diam-diam).

### 3.3 File referensi tambahan yang perlu dibaca

- `Scraping/README.md` — konteks pipeline akuisisi data, ruang lingkup, keterbatasan
- `scoring/metodologi.json` — skema kamus data & bobot yang dipakai tim scoring, termasuk `resolusi_data: 9` dan `resolusi_skor: 8` (**penting**: tim scoring bekerja di H3 res-8, sedangkan seluruh data kita res-9 — resolusi hasil prediksi harus tetap res-9, tapi field `hex_induk` di `scoring/kerangka_peta.geojson` dipakai untuk agregasi ke res-8 nanti oleh tim scoring, BUKAN oleh pipeline ini)
- `scoring/laporan_cakupan.csv` — status pengisian variabel di sisi tim scoring, dipakai untuk cross-check nama variabel target yang mereka harapkan

## 4. Model & Metodologi (mengikuti laporan Bagian 7 langkah 2)

- **Algoritma:** Gradient Boosting Regressor (scikit-learn `GradientBoostingRegressor`) sebagai default; sertakan Random Forest sebagai pembanding.
- **Dua model terpisah** (bukan multi-output tunggal): satu untuk D10, satu untuk B07 — keduanya punya pola missingness dan skala berbeda.
- **Validasi WAJIB pakai spatial k-fold, BUKAN random k-fold.** Split berdasarkan `kawasan`/kelompok kawasan survei, bukan per baris. Validasi acak akan bocor spasial dan menghasilkan skor yang terlihat bagus padahal cuma menghafal karakteristik kawasan (lihat penjelasan di laporan Bagian 7.1 Langkah 2).
- Minimal 12 kawasan survei diperlukan supaya spatial k-fold punya cukup grup untuk dibagi train/test (lihat Bagian 6 kriteria penerimaan).
- Laporkan R² dan MAE **apa adanya**, termasuk kalau hasilnya jelek — jangan disembunyikan atau di-cherry-pick.

## 4a. Strategi Data Hybrid (Real + Sintetis) — WAJIB DIBACA

Berdasarkan arahan mentoring: dataset training final adalah **gabungan**
15 titik Menu Go asli (dalam bbox, lihat Bagian 2) + augmentasi sintetis
untuk mencapai volume minimum. Ini BUKAN mengganti data asli dengan
sintetis — data asli SELALU jadi bagian dari dataset final, tidak pernah
dibuang.

**Alur pemrosesan:**

1. `process_real_survey.py` — baca sample Menu Go asli, filter ke titik
   yang jatuh dalam bbox studi (harus 15/15 lolos, kalau tidak berarti ada
   yang berubah dari data upload awal — investigasi), hitung kolom canonical:
   - `skor_ramai_terkoreksi` (D10): mapping "Kondisi Pembeli" ke skala 1-3.
     **Koreksi bias jam kunjungan (per laporan Bagian 6.1) TIDAK dilakukan
     penuh di sini** — dengan cuma 15 titik, baseline rata-rata per jam
     tidak cukup robust dihitung. Dipakai skor mentah (belum terkoreksi),
     dan ini **WAJIB dicatat sebagai simplifikasi** di halaman Metodologi,
     bukan diklaim sebagai D10 penuh sesuai definisi resmi.
   - `harga_median_porsi` (B07): langsung dari kolom harga per baris (tiap
     baris satu lokasi, jadi ini harga tunggal per lokasi bukan median
     dari banyak titik — istilah "median" di sini menjadi kurang tepat
     untuk N=1 per titik, catat ini juga sebagai simplifikasi)
   - Spatial join ke `hex_id` grid asli
   - Tandai `sumber_data = "real"`
2. `merge_training_data.py` — generate augmentasi sintetis (pakai ulang
   logika `generate_dummy_survey.py`) untuk heksagon LAIN yang belum
   dicakup 15 titik real, gabungkan jadi satu dataset, kolom `sumber_data`
   dipertahankan (`"real"` atau `"sintetis"`), simpan ke
   `data_raw/survei/training_data_gabungan.csv`
3. Pipeline training (`train_model.py`) baca file gabungan ini secara
   default — bukan lagi pilihan biner "semua asli" vs "semua dummy" seperti
   desain awal sebelum ditemukan Menu Go valid secara geografis.

## 5. Struktur Kode yang Diharapkan (modular)

```
train_model/
├── config.py                  # semua path file, konstanta (bbox, resolusi H3, ambang keyakinan)
├── data_loader.py              # baca semua file mentah, validasi keberadaan & skema tiap file
├── feature_engineering.py      # gabungkan semua raw jadi 1 tabel hex_features per hex_id
├── train_model.py              # spatial k-fold, training, evaluasi, simpan model (.pkl/.joblib)
├── predict.py                  # load model, prediksi ke heksagon tanpa data survei, tempel badge keyakinan
├── run_pipeline.py             # entrypoint orkestrasi seluruh langkah di atas
└── utils/
    └── logging_setup.py        # logging terpusat, dipakai semua modul di atas
```

Tiap modul harus:
- Punya docstring di awal file menjelaskan tanggung jawabnya
- Validasi input di awal fungsi (file ada/tidak, kolom yang diharapkan ada/tidak) sebelum proses berat dijalankan
- **Error message harus menyebutkan: file/kolom apa yang bermasalah, kenapa itu masalah, dan langkah konkret apa yang harus dilakukan user** — bukan cuma stack trace generik. Contoh gaya yang benar (dipakai konsisten di seluruh skrip akuisisi data proyek ini):
  ```
  FileNotFoundError: 'data_raw/survei/menu_go.csv' tidak ditemukan.
  Ini file hasil unduhan survei lapangan MAPID Apps (12 kawasan).
  Training TIDAK BISA jalan tanpa ini - lihat Bagian 2 PRD.md soal
  status data label yang belum lengkap.
  ```
- Tidak ada `except: pass` atau silent failure di manapun — setiap exception ditangkap spesifik jenisnya, dilog, dan diteruskan (raise ulang atau exit jelas) kecuali memang ada fallback yang secara eksplisit masuk akal (dan itu pun harus di-log sebagai warning, bukan diam-diam).

## 6. Kriteria Penerimaan (Definition of Done)

- [ ] `feature_engineering.py` berhasil menggabungkan seluruh sumber di Bagian 3.1 jadi satu tabel `hex_features` per `hex_id`, disimpan ke `data_raw/hex_features.geojson`
- [ ] Pipeline **menolak untuk training** (exit dengan pesan jelas, bukan crash acak) kalau:
  - Jumlah heksagon berlabel (survei asli) < 30 titik total, ATAU
  - Jumlah kawasan survei unik < 3 (spatial k-fold minimal butuh beberapa grup untuk dipisah train/test)
  - Kalau kedua syarat di atas terpenuhi, baru lanjut ke training
- [ ] Hasil validasi spatial k-fold (R², MAE per fold) dicetak ke log DAN disimpan ke file (`train_model/hasil_validasi.json`) — bukan cuma print ke terminal
- [ ] Model tersimpan dalam format yang bisa dimuat ulang (`.joblib`)
- [ ] `predict.py` menghasilkan kolom prediksi + kolom `tingkat_keyakinan` (TINGGI/SEDANG/RENDAH berdasarkan `n_titik_misi`, ambang sesuai `scoring/metodologi.json` kalau ada, atau default laporan: TINGGI ≥30, SEDANG 10-29, RENDAH <10) untuk SETIAP heksagon, termasuk yang datanya observasi asli (badge TINGGI otomatis untuk titik survei asli, bukan hasil model)
- [ ] Tidak ada nilai hasil prediksi yang menimpa nilai observasi asli — heksagon dengan data survei asli tetap pakai nilai aslinya, prediksi model cuma untuk yang kosong

## 7. Output & Yang Dikirim ke Tim WebGIS

### Output pipeline (internal)
- `data_raw/hex_features.geojson` — tabel gabungan lengkap (fitur + label + prediksi + badge)
- `train_model/model_skor_ramai.joblib`, `train_model/model_harga.joblib` — model terlatih
- `train_model/hasil_validasi.json` — metrik R²/MAE per fold, supaya bisa direview sebelum dipercaya

### File final yang dikirim ke Tim WebGIS
Satu file: **`data_raw/hex_features_final.geojson`**

Kolom minimum yang WAJIB ada (nama kolom persis, karena tim WebGIS/scoring
sudah punya skema sendiri di `scoring/kerangka_peta.geojson` — cocokkan
`hex_id` sebagai kunci join):

| Kolom | Isi |
|---|---|
| `hex_id` | kunci join ke `scoring/kerangka_peta.geojson` |
| `skor_ramai_terkoreksi` (D10) | nilai asli kalau ada, prediksi kalau tidak |
| `harga_median_porsi` (B07) | nilai asli kalau ada, prediksi kalau tidak |
| `tingkat_keyakinan` | TINGGI/SEDANG/RENDAH |
| `data_source` | `"observed"` atau `"predicted"` per variabel (bisa dua kolom terpisah kalau D10 dan B07 statusnya beda) |
| Semua fitur prediktor lain dari Bagian 3.1 | supaya tim WebGIS bisa pakai untuk komponen IAE/Kompetisi/Biaya_Risiko yang saat ini kosong di `scoring/metodologi.json` |

**Catatan penting untuk pesan serah terima ke tim:** sebutkan eksplisit R²
dan MAE dari `hasil_validasi.json` di pesan pengiriman — jangan cuma kirim
file tanpa konteks seberapa reliable prediksinya. Tim scoring perlu tahu
ini untuk memutuskan apakah badge RENDAH perlu ditampilkan lebih mencolok
di UI.

## 8. Yang TIDAK Termasuk Task Ini

- Klasifikasi `risiko_banjir_indeks_mean` jadi kelas (L03 final) — breakpoint belum diputuskan tim, keluar dari scope ini
- Resolusi NJOP yang masih blocked — model jalan tanpa variabel biaya NJOP untuk saat ini, IBR akan tetap parsial
- Integrasi ke WebGIS interface (B1-B4 di laporan) — itu task terpisah untuk tim frontend/produk
