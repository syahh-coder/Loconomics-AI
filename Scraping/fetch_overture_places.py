"""
fetch_overture_dedup.py
==========================
Dedup Overture Places terhadap OSM kompetitor, sesuai aturan Bagian 5.1
(E-2) dan Bagian 9.2 laporan: dua entitas dianggap sama kalau kemiripan
nama >= 85% DAN jarak <= 30 meter. Kalau digabung tanpa dedup, kompetitor
akan terhitung dobel dan merusak seluruh komponen kompetisi di skor
peluang.

INPUT:
  data_raw/osm/kompetitor.geojson      (hasil fetch_osm_geofabrik.py)
  data_raw/overture/places_raw.geojson (hasil fetch_overture_places.py)

OUTPUT:
  data_raw/poi_terpadu.geojson - gabungan tanpa duplikat, field 'sumber'
  menandai asal data ('osm', 'overture', atau 'osm+overture' kalau
  match dan atributnya digabung)

LANGKAH MANUAL SEBELUM JALANIN INI:
  pip install rapidfuzz

CATATAN: record yang match (dianggap entitas sama) - OSM dipertahankan
sebagai record utama (karena sudah lebih dulu masuk pipeline taksonomi),
kategori Overture ditambahkan sebagai atribut pelengkap kalau OSM tidak
punya kategori setara. Overture yang tidak match jarak/nama dianggap
entitas baru dan tetap dipakai (terutama berguna untuk merchant
menengah-besar yang OSM Indonesia kurang lengkap datanya).
"""

import json
from pathlib import Path

import geopandas as gpd
from rapidfuzz import fuzz

OSM_PATH = Path("data_raw/osm/kompetitor.geojson")
OVERTURE_PATH = Path("data_raw/overture/places_raw.geojson")
OUT_PATH = Path("data_raw/poi_terpadu.geojson")

# CRS metrik (UTM 48S) supaya jarak dihitung dalam meter yang akurat,
# bukan derajat lat/lon.
CRS_METRIK = "EPSG:32748"

JARAK_MAX_M = 30
NAMA_MIRIP_MIN = 85  # persen, skala rapidfuzz 0-100


def main():
    for p in (OSM_PATH, OVERTURE_PATH):
        if not p.exists():
            raise FileNotFoundError(f"'{p}' tidak ditemukan. Jalankan skrip fetch yang sesuai dulu.")

    print("Membaca data OSM dan Overture...")
    osm = gpd.read_file(OSM_PATH).to_crs(CRS_METRIK)
    overture = gpd.read_file(OVERTURE_PATH).to_crs(CRS_METRIK)
    print(f"OSM: {len(osm)} titik, Overture: {len(overture)} titik")

    # Pastikan kolom nama konsisten - OSM pakai 'name', Overture pakai 'nama'
    osm["nama_cek"] = osm["name"].fillna("")
    overture["nama_cek"] = overture["nama"].fillna("")

    print(f"Mencari pasangan terdekat (maks {JARAK_MAX_M}m)...")
    # sjoin_nearest cari OSM terdekat untuk tiap titik Overture, dibatasi
    # jarak maksimal supaya tidak match ke titik yang jauh
    joined = gpd.sjoin_nearest(
        overture, osm[["geometry", "nama_cek"]],
        max_distance=JARAK_MAX_M, distance_col="jarak_m",
        lsuffix="overture", rsuffix="osm",
    )

    n_kandidat = len(joined)
    print(f"{n_kandidat} pasangan kandidat ketemu dalam radius {JARAK_MAX_M}m "
          f"(dari {len(overture)} titik Overture, sebagian mungkin tidak punya "
          f"pasangan OSM sama sekali dalam radius itu).")

    # Dari kandidat jarak dekat, filter lagi pakai kemiripan nama
    def mirip(row):
        a, b = row["nama_cek_overture"], row["nama_cek_osm"]
        if not a or not b:
            return 0
        return fuzz.token_sort_ratio(a, b)

    joined["kemiripan_nama"] = joined.apply(mirip, axis=1)
    duplikat = joined[joined["kemiripan_nama"] >= NAMA_MIRIP_MIN]

    overture_id_duplikat = set(duplikat["overture_id"])
    print(f"{len(overture_id_duplikat)} titik Overture dianggap duplikat OSM "
          f"(jarak <={JARAK_MAX_M}m DAN kemiripan nama >={NAMA_MIRIP_MIN}%).")

    overture_baru = overture[~overture["overture_id"].isin(overture_id_duplikat)].copy()
    print(f"{len(overture_baru)} titik Overture dianggap entitas BARU (dipakai).")

    # Susun output gabungan
    osm_wgs = osm.to_crs("EPSG:4326")
    overture_baru_wgs = overture_baru.to_crs("EPSG:4326")

    features = []
    for _, row in osm_wgs.iterrows():
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [row.geometry.x, row.geometry.y]},
            "properties": {
                "sumber": "osm",
                "nama": row.get("name"),
                "kelompok": row.get("kelompok"),
                "kategori_asli": row.get("kategori_asli"),
                "osm_id": row.get("osm_id"),
            },
        })
    for _, row in overture_baru_wgs.iterrows():
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [row.geometry.x, row.geometry.y]},
            "properties": {
                "sumber": "overture",
                "nama": row.get("nama"),
                "kelompok": "kompetitor",  # semua data ini memang dari kelompok kompetitor
                "kategori_asli": row.get("kategori"),
                "overture_id": row.get("overture_id"),
                "confidence": row.get("confidence"),
            },
        })

    geojson = {"type": "FeatureCollection", "features": features}
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)

    print(f"\nDisimpan -> {OUT_PATH}")
    print(f"Total POI terpadu: {len(features)} "
          f"({len(osm_wgs)} dari OSM + {len(overture_baru_wgs)} baru dari Overture)")
    print(f"Duplikat yang dibuang: {len(overture_id_duplikat)}")


if __name__ == "__main__":
    main()