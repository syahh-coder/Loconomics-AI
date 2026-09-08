# Akuisisi Data STATIONOMICS — P0

## Cara pakai

```bash
pip install -r requirements.txt

# 1. Tarik OSM (kompetitor, simpul transit, generator keramaian)
python fetch_osm_overpass.py

# 2. Generate grid H3 res-9 untuk wilayah studi
python generate_h3_grid.py
```

Hasil masuk ke `data_raw/osm/*.geojson` dan `data_raw/h3_grid_res9.geojson`.

## Sebelum menjalankan — cek dulu

1. **Wilayah studi belum final** (lihat briefing Bagian 5). BBOX di kedua
   skrip masih pakai asumsi Jabodetabek penuh dari draft laporan awal.
   Kalau tim putuskan DKI saja atau area lain, ganti `BBOX` di
   `fetch_osm_overpass.py` DAN `generate_h3_grid.py` sekaligus (biar bbox
   OSM dan grid H3 nyambung).
2. **Overpass API publik bisa timeout** untuk bbox seluas Jabodetabek.
   Kalau `fetch_osm_overpass.py` gagal berulang, pindah ke jalur bulk:
   download PBF dari Geofabrik lalu filter offline pakai `pyrosm` atau
   `osmium` — saya bisa siapkan skrip itu kalau dibutuhkan.
3. **Jangan publikasikan file di `data_raw/` mentah-mentah.** OSM berlisensi
   ODbL (share-alike kalau digabung), dan data misi MAPID dilarang keras
   diredistribusi mentah sesuai ketentuan lomba. Yang boleh dipublikasikan
   cuma hasil agregat per heksagon.

## Belum dikerjakan di tahap ini (menyusul)

- Overture Maps Places (DuckDB query) — P2, nunggu wilayah studi final dulu
  biar bbox query-nya pas
- WorldPop zonal statistics — butuh grid H3 sudah jadi dulu
- NJOP/RDTR Jakarta Satu — cakupan cuma DKI, tunggu keputusan wilayah studi
- Isochrone OSRM/Valhalla — butuh setup Docker terpisah

Bilang aja mana yang mau digarap duluan.
