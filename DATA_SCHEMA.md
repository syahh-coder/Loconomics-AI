# DATA_SCHEMA.md — Kamus Kolom untuk Pipeline Training

Dokumen ini memetakan nama kolom ASLI di tiap file mentah ke nama
CANONICAL yang dipakai di tabel `hex_features` gabungan. Agent WAJIB
verifikasi nama kolom asli langsung dari file (`geopandas.read_file(...).columns`)
sebelum coding — dokumen ini adalah referensi per hari dibuat, bisa basi
kalau skrip akuisisi data diubah setelah ini ditulis.

## Grid dasar

**File:** `Scraping/data_raw/h3_grid_res9.geojson`

| Kolom asli | Tipe | Keterangan |
|---|---|---|
| `hex_id` | string | Primary key seluruh pipeline |
| `centroid_lat`, `centroid_lon` | float | |
| `resolusi` | int | Selalu 9 |
| `n_titik_misi` | int | Diisi ulang oleh pipeline ini setelah join data survei — JANGAN andalkan nilai default (0) dari file grid awal |
| `tingkat_keyakinan` | string | Idem — akan di-overwrite oleh `predict.py` |
| `data_source` | string | Idem |

## Populasi (WorldPop)

**File:** `Scraping/data_raw/h3_grid_with_pop.geojson` -> canonical `D01 = pop_100m`
**File:** `Scraping/data_raw/h3_grid_with_pop_age.geojson` -> canonical `D02 = pop_usia_produktif`

Kedua file ini punya SEMUA kolom grid dasar plus satu kolom tambahan
masing-masing. Join ke grid via `hex_id`. Perhatian: kedua file adalah
hasil overwrite berurutan dari grid yang sama (`h3_grid_with_pop_age.geojson`
dibuat dari `h3_grid_with_pop.geojson`) - kemungkinan besar
`h3_grid_with_pop_age.geojson` SUDAH memuat kolom `pop_100m` juga. Cek dulu,
jangan join dua kali kolom yang sama.

## Bangunan (Google Open Buildings)

**File:** `Scraping/data_raw/open_buildings/h3_grid_with_buildings.geojson`

| Kolom asli | Canonical | Keterangan |
|---|---|---|
| `total_luas_bangunan_m2` | - | Intermediate, tidak perlu dibawa ke hex_features final |
| `luas_bangunan_median` | M02 | Bisa NULL untuk heksagon tanpa bangunan - JANGAN diisi 0 |
| `jumlah_bangunan` | - | Berguna sebagai fitur tambahan meski bukan kode resmi |
| `hex_area_m2` | - | Intermediate |
| `rasio_tutupan_bangunan` | M01 | |

## Risiko Banjir (InaRISK)

**File:** `Scraping/data_raw/inarisk/h3_grid_with_risiko_banjir.geojson`

| Kolom asli | Canonical | Keterangan |
|---|---|---|
| `risiko_banjir_indeks_mean` | proksi L03 | INDEKS MENTAH, bukan kelas. Pakai sebagai fitur numerik langsung, JANGAN dikira kategorikal |
| `risiko_banjir_indeks_max` | proksi L03 (varian) | |

## Titik OSM (perlu agregasi spasial - belum dilakukan di skrip manapun)

**File:** `Scraping/data_raw/osm/kompetitor.geojson`, `simpul_transit.geojson`, `generator_keramaian.geojson`

Semua bertipe Point, kolom: `osm_id`, `osm_type`, `kelompok`, `kategori_asli`
(JSON string), `name`, plus kolom tag spesifik (`shop`, `amenity`, dst -
TIDAK semua baris punya semua kolom ini terisi, banyak NULL).

Perlu dibuat di `feature_engineering.py` (belum ada kode ini di manapun):
- `C02_kepadatan_poi_total` = jumlah titik `kompetitor.geojson` per heksagon, dibagi luas heksagon
- `D09_generator_keramaian` = jumlah titik `generator_keramaian.geojson` per heksagon
- `D03_jarak_simpul_m`, `D04_waktu_jalan_menit` = jarak dari centroid heksagon ke titik `simpul_transit.geojson` terdekat (pakai jarak Euclidean projected dulu sebagai proksi; isochrone OSRM asli belum dibuat di proyek ini - CATAT INI SEBAGAI KETERBATASAN kalau dipakai, jangan diklaim sebagai isochrone jaringan jalan asli)

## POI terpadu (OSM + Overture, sudah dedup)

**File:** `Scraping/data_raw/poi_terpadu.geojson`

Kolom: `sumber` (`"osm"` atau `"overture"`), `nama`, `kelompok`,
`kategori_asli`, plus `osm_id` atau `overture_id`/`confidence` tergantung
sumber (kolom TIDAK seragam antar baris - cek `sumber` dulu sebelum baca
kolom spesifik sumber).

Belum ada pemetaan ke taksonomi 8 kelas induk (Bagian 4 laporan) - kolom
`kategori_asli` masih mentah per-sumber. Kalau task ini butuh
`C03_keragaman_usaha` (entropi Shannon dari kelas induk), taksonomi ini
harus dibuat dulu - bukan pekerjaan trivial, pertimbangkan apakah masuk
scope task ini atau didokumentasikan sebagai task terpisah.

## RDTR/Zonasi

**File:** `Scraping/data_raw/jakarta_satu/rdtr.geojson`

Poligon, atribut ArcGIS mentah (field asli belum didokumentasikan di
proyek ini - agent WAJIB cek `gdf.columns` dan `gdf.head()` dulu untuk
cari field kode zona sebelum bikin `L01_zona_izin_komersial` dan
`L02_kelas_zona`). Cakupan cuma DKI - heksagon di Bekasi/Tangerang akan
NULL untuk kolom ini, ini kondisi yang diketahui dan diterima (bukan bug).

## Data Survei — SUDAH TERVERIFIKASI dari sample resmi yang diupload

**PENTING:** dari 4 dataset sample, cuma **Menu Go** yang titiknya jatuh
di dalam bbox studi (15/15 titik, lat -6.40 s.d -6.42, lon 106.82-106.85).
Struk Go, Properti Go, dan Activity semuanya di Bandung (0/50-15 titik
dalam bbox) — dipakai cuma sebagai referensi skema, bukan ground truth
spasial. Lihat PRD.md Bagian 2 untuk strategi lengkapnya.

### Menu Go (VERIFIED — bisa dipakai sebagai data label asli)

**File asli:** `Sample_MenuGo_WebGIS2026.csv` (taruh di `Scraping/data_raw/survei_asli_sample/menu_go_sample.csv`)

Kolom persis (sudah dicek langsung, BUKAN dari dokumen ketentuan):
```
['Nama Tempat Makan', 'Jenis Tempat Makan', 'Tanggal', 'Waktu',
 'Foto Tempat', 'Foto Menu 1 (Foto Menu Utama)', 'Foto Menu 2 (Foto Menu Lainnya)',
 'Menu Dalam Bentuk Link Digital', 'Apa Menu Utama/Andalan Yang Dijual?',
 'Berapa Harga Rata-rata Menu Tersebut (Per porsi)?',
 'Bagaimana Kondisi Pembeli Saat Kunjungan Dilakukan?',
 'Apakah Berjualan Dengan Berkeliling (Mobilitas)?', 'Latitude', 'Longitude']
```

Nama kolom di sini TIDAK terpotong (beda dari Properti Go di bawah) —
persis sama dengan dokumen ketentuan resmi.

| Kolom asli | Canonical | Catatan |
|---|---|---|
| `Bagaimana Kondisi Pembeli Saat Kunjungan Dilakukan?` | dasar D10 | 3 nilai unik: `"Sepi (...)"`, `"Sedang (...)"`, `"Ramai (...)"` — map ke 1/2/3. Teksnya panjang (ada penjelasan dalam kurung), match pakai `.str.startswith()` atau `.str.contains()`, JANGAN exact match string penuh |
| `Berapa Harga Rata-rata Menu Tersebut (Per porsi)?` | B07 (harga_median_porsi) | Numerik langsung, tidak perlu parsing. Range di 15 sample: Rp5.000 - Rp35.000, median Rp20.000 |
| `Latitude`, `Longitude` | lokasi | Float, tidak ada masalah format (beda dari Struk Go yang Latitude/Longitude-nya bertipe Text) |

### Struk Go, Properti Go, Activity — VERIFIED tapi di luar bbox

**Properti Go** — konfirmasi kolom terpotong PERSIS seperti dugaan awal:
```
['Kategori P', 'Jenis Prop', ' Tanggal', 'Alamat', 'Foto Tampa', 'Foto Spand', 'Latitude', 'Longitude']
```
Perhatikan `' Tanggal'` ada leading space, `'Kategori P'`/`'Jenis Prop'`/`'Foto Tampa'`/`'Foto Spand'` semuanya terpotong dari nama aslinya di dokumen ketentuan.

**Struk Go** — kolom lebih banyak dari dokumen resmi:
```
['Nama Tempat/Merchant', 'Kategori Tempat', 'Tanggal Transaksi', 'Waktu Transaksi',
 'Metode Pembayaran', 'Foto Struk/Bukti bayar', 'Kontributor', 'Pengecekan',
 'Latitude', 'Longitude', 'ID data', 'Total Pengeluaran per Orang (Lama)',
 'Catatan Kesalahan', 'Jenis Kategori (Lama)', 'Alamat (Lama)', 'Tujuan makan (Lama)',
 'Foto menu (Lama)', 'Rating kepuasan tempat (Lama)', 'Jumlah orang yang makan (Lama)',
 'Total Pengeluaran (Tanpa PPN) (Lama)']
```
9 kolom `(Lama)` kosong semua (legacy, sesuai dugaan laporan awal) + kolom
`Kontributor`, `Pengecekan`, `ID data` yang tidak disebut dokumen ketentuan.

**Activity** — 8 kolom (bukan 7 seperti dokumen ketentuan):
```
['title', 'description', 'latitude', 'longitude', 'medias_all', 'images', 'videos', 'medias']
```
Kolom `medias_all` adalah tambahan yang tidak disebut dokumen.

## Ringkasan Prioritas Baca untuk Agent

Urutan file yang harus dibaca dulu sebelum menulis kode apapun:
1. `PRD.md` (Bagian 2 - status data, WAJIB paham dulu)
2. Dokumen ini (`DATA_SCHEMA.md`)
3. `Scraping/README.md`
4. Buka LANGSUNG tiap file di atas pakai `geopandas.read_file(...).columns` / `pandas.read_csv(...).columns` - dokumen ini bisa salah/basi, file asli adalah kebenaran final
