# STATIONOMICS — Data Acquisition Pipeline

Platform WebGIS Decision Support System untuk pemilihan lokasi UMKM di kawasan
transportasi massal darat. Repo ini berisi skrip akuisisi & pemrosesan data
mentah — **bukan** data hasil akuisisinya sendiri (lihat [Struktur Output](#struktur-output--tidak-di-push)
soal kenapa).

Dibuat untuk MAPID WebGIS Competition 2026 — *Maps That Think! Mass Transportation Edition*.

## Ruang Lingkup

| Aspek | Cakupan |
|---|---|
| Wilayah studi | DKI Jakarta + Kota/Kab Bekasi + sebagian Tangerang/Tangsel |
| Bbox (lon_min, lat_min, lon_max, lat_max) | `106.55, -6.45, 107.25, -5.95` |
| Moda transportasi | Darat saja: KRL, MRT, LRT, TransJakarta/BRT, terminal bus, titik transit travel. **Tidak termasuk** laut/udara |
| Unit analisis | Heksagon H3 resolusi 9 (±0.10 km², lebar ±350m) |

**Catatan bbox:** ini kotak persegi (rectangular), bukan potongan batas administratif presisi. Bisa nyerempet sedikit ke Depok/Bogor di sudut selatan, dan sengaja memotong ujung barat Kabupaten Tangerang (Balaraja, Kronjo, dst — di luar cakupan studi).

## Setup

```bash
conda create -n stationomics python=3.11
conda activate stationomics

# Paket yang butuh binary compiled - install lewat conda-forge, BUKAN pip
# (pip akan gagal build di Windows tanpa Visual C++ Build Tools)
conda install -c conda-forge pyrosm geopandas shapely rasterio rasterstats -y

pip install -r requirements.txt
```

## Struktur Pipeline

Skrip dijalankan berurutan — beberapa bergantung pada output skrip sebelumnya.

```
1. generate_h3_grid.py           -> grid heksagon (wadah semua variabel)
2. fetch_osm_geofabrik.py        -> kompetitor, simpul transit, generator keramaian
3. compute_worldpop_zonal.py     -> populasi total per heksagon (D01)
4. compute_worldpop_age.py       -> populasi usia produktif per heksagon (D02)
5. fetch_jakarta_satu.py         -> RDTR/zonasi (NJOP: lihat "Data yang Belum Lengkap")
6. fetch_inarisk_raster.py       -> indeks risiko banjir (L03, mentah)
7. fetch_overture_places.py      -> POI Overture Maps (raw)
8. fetch_overture_dedup.py       -> gabung + dedup Overture vs OSM
9. compute_open_buildings.py     -> morfologi bangunan (M01, M02)
```

### 1. Grid H3

```bash
python generate_h3_grid.py
```
Generate heksagon H3 res-9 untuk seluruh bbox. Kompatibel h3-py v3 maupun v4 (auto-detect). Output: `data_raw/h3_grid_res9.geojson`.

### 2. OSM — kompetitor, transit, keramaian

```bash
python fetch_osm_geofabrik.py
```
**Butuh file manual dulu:** download PBF Jawa dari
`https://download.geofabrik.de/asia/indonesia/java-latest.osm.pbf`
(nama file asli biasanya bertanggal, mis. `java-260830.osm.pbf` — sesuaikan `PBF_PATH` di skrip). Taruh di root repo. Diproses offline pakai `pyrosm`, tidak lewat Overpass API (lihat catatan di bawah).

> **Alternatif (tidak disarankan):** `fetch_osm_overpass.py` — versi awal yang pakai Overpass API publik langsung. Disertakan untuk referensi, tapi di jaringan tertentu gagal konsisten (406/403/500 di semua mirror publik yang dicoba). `fetch_osm_geofabrik.py` adalah jalur yang benar-benar dipakai.

Output: `data_raw/osm/{kompetitor,simpul_transit,generator_keramaian}.geojson`

### 3-4. WorldPop

```bash
python compute_worldpop_zonal.py   # D01 - populasi total
python compute_worldpop_age.py     # D02 - usia produktif (15-64)
```
Butuh raster manual dari `hub.worldpop.org/geodata/summary?id=55010` (D01: total population 2025/2026 constrained 100m) dan dataset age-sex structures (D02: 20 file, band umur 15-64 laki-laki+perempuan). Lihat komentar di masing-masing skrip untuk detail nama file yang perlu didownload.

Output: `data_raw/h3_grid_with_pop.geojson`, `data_raw/h3_grid_with_pop_age.geojson`

### 5. Jakarta Satu (RDTR)

```bash
python fetch_jakarta_satu.py search rdtr      # cari layer dulu
python fetch_jakarta_satu.py fetch rdtr       # tarik data
```
Query ArcGIS REST FeatureServer dengan paginasi + checkpoint (resume otomatis kalau koneksi putus di tengah). Layer yang dipakai: `Rencana_Pola_Ruang_RDTR_2022/FeatureServer/0`.

Output: `data_raw/jakarta_satu/rdtr.geojson`

### 6. InaRISK (risiko banjir)

```bash
python fetch_inarisk_raster.py
```
Layer InaRISK yang relevan (`layer_bahaya_banjir_30`) ternyata bertipe **Raster Layer**, bukan vektor — jadi tidak bisa di-query pakai endpoint `/query` biasa (`fetch_inarisk.py`, disertakan untuk referensi, akan selalu gagal 503 untuk layer ini). Skrip yang benar pakai jalur ImageServer `exportImage`.

Output: `data_raw/inarisk/h3_grid_with_risiko_banjir.geojson` — **indeks mentah** (mean/max), belum diklasifikasi jadi kelas risiko (rendah/sedang/tinggi). Breakpoint klasifikasi belum ditentukan tim.

### 7-8. Overture Maps Places

```bash
pip install duckdb rapidfuzz
python fetch_overture_places.py    # query S3 via DuckDB
python fetch_overture_dedup.py     # dedup vs OSM
```
Query langsung ke bucket S3 publik Overture (bukan download file). Cek `RELEASE_VERSION` di skrip — Overture rilis versi baru tiap bulan, update kalau sudah kadaluarsa.

Dedup pakai aturan laporan: jarak ≤30m DAN kemiripan nama ≥85% (rapidfuzz). **Keterbatasan yang diketahui:** banyak POI kompetitor (OSM maupun Overture) yang tidak punya field nama — dedup otomatis menganggapnya entitas beda kalau salah satu tidak bernama, sehingga sebagian duplikat tanpa nama berpotensi tidak terdeteksi.

Output: `data_raw/overture/places_raw.geojson`, `data_raw/poi_terpadu.geojson`

### 9. Google Open Buildings

```bash
pip install s2sphere
python compute_open_buildings.py
```
**Bukan** lewat Google Earth Engine (butuh akun+auth) — pakai jalur download publik langsung per sel S2 level-4 dari `storage.googleapis.com/open-buildings-data`. File per sel bisa sangat besar (contoh: 1 sel untuk area studi ini ~5.8GB, karena densitas bangunan Jakarta tinggi). Skrip resumable (HTTP Range) dan retry otomatis untuk koneksi tidak stabil.

Output: `data_raw/open_buildings/h3_grid_with_buildings.geojson`

## Data yang Belum Lengkap

### NJOP (P01, P02) — BLOCKED

Layer resmi Jakarta Satu (`Perhitungan_NJOP`) mengembalikan `{"error":{"code":499,"message":"Token Required"}}` — butuh autentikasi yang belum didapat. Sudah dicoba cari layer publik alternatif di portal yang sama, hasilnya cuma layer BMD/BMN (Barang Milik Daerah/Negara — aset pemerintah, bukan NJOP umum, tetap butuh token juga).

**Belum diputuskan:** apakah lanjut cari akses resmi, atau ganti sepenuhnya ke ZNT Bhumi ATR/BPN (`bhumi.atrbpn.go.id/peta`) — yang tidak ada API-nya sama sekali, murni tangkap manual per lokasi.

### Ridership KAI (pelengkap D05/D06)

Data cuma tersedia di press release berformat narasi (`kci.id`, `commuterline.id`), bukan tabel/API. Setelah dicek, **kebanyakan rilis cuma memuat angka total jaringan** (Jabodetabek keseluruhan), bukan breakdown per-stasiun bulanan. Angka per-stasiun cuma muncul sporadis (stasiun baru dibuka, musim Lebaran/Nataru, isu khusus).

Skrip pembantu (`fetch_ridership_kai.py`) bisa fetch teks artikel dan cari kandidat angka pakai regex, tapi **hasilnya wajib diverifikasi manual** ke teks asli sebelum dipakai — regex rawan salah tangkap angka yang bukan ridership.

### ZNT Bhumi ATR/BPN

Viewer manual saja (`bhumi.atrbpn.go.id/peta`), tidak ada endpoint API atau bulk download yang ditemukan. Perlu tangkap manual per titik.

### Sample CSV MAPID — cakupan geografis tidak representatif

4 file sample resmi (Menu Go, Struk Go, Properti Go, Community Maps Activity — 15 titik per dataset, 50 untuk Activity) **sudah didapat**, tapi lokasinya **bukan di wilayah studi** (DKI+Bekasi+Tangerang):
- Menu Go: sekitar **Depok**
- Struk Go, Properti Go, Activity Maps: sekitar **Bandung**

Ini sesuai ketentuan resmi kompetisi (data sample memang diambil nasional, bukan pelanggaran), tapi konsekuensinya: **sample ini tidak bisa dipakai sebagai ground truth wilayah studi**, hanya sebagai referensi format/struktur kolom (dan itu pun nama kolom di file asli sudah terbukti beda dari dokumen ketentuan resmi — verifikasi manual tetap wajib sebelum menulis skrip pembersihan data). Data mission yang benar-benar mewakili wilayah studi baru akan didapat dari survei lapangan tim sendiri (rencana: 12 kawasan, 360-600 titik).

## Struktur Output — Tidak di-Push

Seluruh folder `data_raw/` (GeoJSON, raster, CSV.gz hasil download) **tidak masuk repo** — ukurannya besar (beberapa file ratusan MB - GB), dan hasilnya reproducible dari skrip + langkah download manual yang didokumentasikan di atas. Tambahkan ke `.gitignore`:

```
data_raw/
*.pbf
*.tif
*.csv.gz
```

Yang di-push cuma skrip, `requirements.txt`, dan dokumentasi ini.

## Lisensi & Atribusi (wajib dicantumkan di halaman Metodologi produk akhir)

| Sumber | Lisensi | Kewajiban |
|---|---|---|
| OpenStreetMap | ODbL 1.0 | Atribusi + share-alike pada database turunan (publikasikan hasil agregat saja) |
| Overture Maps | CDLA Permissive 2.0 + Apache 2.0 | Atribusi, tanpa share-alike |
| WorldPop | CC BY 4.0 | Atribusi |
| Google Open Buildings | CC BY 4.0 | Atribusi |
| Jakarta Satu (RDTR) | Data publik Pemprov DKI | Atribusi sumber |
| InaRISK/BNPB | Data publik | Atribusi sumber |
| Data misi MAPID | Ketentuan kompetisi | **Dilarang** redistribusi data mentah — hanya hasil olahan/agregat |

## Belum Dikerjakan

- Feature engineering — menggabungkan seluruh `data_raw/*` mentah di atas jadi satu tabel `hex_features` (41 variabel + 3 penanda kualitas sesuai kamus data)
- Model imputasi spasial (ML) — nunggu fitur predictor lengkap + hasil survei lapangan
- A1/A2 OCR (harga sewa spanduk, nominal struk)
- Verifikasi manual nama kolom CSV sample vs dokumen ketentuan resmi