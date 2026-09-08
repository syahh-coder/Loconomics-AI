"""
fetch_osm_geofabrik.py
========================
Alternatif fetch_osm_overpass.py — dipakai kalau Overpass API publik gagal
terus (406/403/500 di semua mirror, biasanya karena jaringan lokal/proxy
mengganggu content negotiation, atau server publik lagi sibuk/butuh
whitelist).

Cara kerja: download SEKALI file PBF area Jawa dari Geofabrik (mirror resmi
OSM, bukan API interaktif jadi tidak kena masalah 406/403/rate-limit di
atas), lalu filter offline pakai pyrosm sesuai bbox wilayah studi.

LANGKAH MANUAL SEBELUM JALANIN SKRIP INI:
  1. pip install pyrosm
  2. Download file PBF Jawa (mencakup DKI+Bekasi+Tangerang) dari:
     https://download.geofabrik.de/asia/indonesia/java-latest.osm.pbf
     Ukurannya beberapa ratus MB - download manual lewat browser lebih
     stabil daripada lewat skrip Python untuk file sebesar ini, apalagi
     kalau jaringan lokal memang bermasalah dengan koneksi Python.
  3. Taruh filenya di folder yang sama dengan skrip ini, atau ubah
     PBF_PATH di bawah sesuai lokasi filenya.

Kalau nanti ternyata dari Geofabrik pun gagal didownload (jaringan
benar-benar bermasalah untuk semua domain OSM), kemungkinan besar
masalahnya di jaringan/proxy lokal, bukan di server manapun - coba
dari jaringan lain (hotspot HP) untuk konfirmasi.
"""

import json
from pathlib import Path

from pyrosm import OSM
import geopandas as gpd

# ── Konfigurasi ──────────────────────────────────────────────────────
# Nama file PBF hasil download dari Geofabrik. Geofabrik menamai file
# pakai tanggal snapshot (mis. java-260830.osm.pbf), BUKAN "java-latest.osm.pbf"
# meski link download-nya pakai kata "latest" - sesuaikan kalau nama file
# hasil downloadmu beda tanggal.
PBF_PATH = "java-260830.osm.pbf"

# Bbox sama dengan fetch_osm_overpass.py dan generate_h3_grid.py - HARUS
# konsisten di ketiga skrip. Format pyrosm: [lon_min, lat_min, lon_max, lat_max]
BBOX = [106.55, -6.45, 107.25, -5.95]

OUT_DIR = Path("data_raw/osm")
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Filter per kelompok (persis sama isinya dengan versi Overpass) ──
FILTERS = {
    "kompetitor": {
        "shop": True,
        "amenity": ["restaurant", "cafe", "fast_food", "food_court", "bar",
                     "bank", "atm", "pharmacy", "marketplace", "fuel"],
        "office": True,
        "building": ["retail", "commercial"],
        "landuse": ["retail", "commercial"],
    },
    "simpul_transit": {
        "railway": ["station", "halt"],
        "public_transport": ["station", "stop_position"],
        "amenity": ["bus_station"],
        "highway": ["bus_stop"],
    },
    "generator_keramaian": {
        "amenity": ["school", "university", "hospital", "place_of_worship", "marketplace"],
        "leisure": ["park", "sports_centre"],
    },
}

TAG_KOLOM = ("shop", "amenity", "office", "building", "landuse",
             "railway", "public_transport", "highway", "leisure")


def to_point_geometry(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Way berbentuk polygon (mis. building=retail) diubah ke titik
    representative_point supaya formatnya konsisten dengan node (Point),
    setara 'out center' di versi Overpass."""
    gdf = gdf.copy()
    is_poly = gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])
    gdf.loc[is_poly, "geometry"] = gdf.loc[is_poly, "geometry"].representative_point()
    is_line = gdf.geometry.geom_type.isin(["LineString", "MultiLineString"])
    gdf.loc[is_line, "geometry"] = gdf.loc[is_line, "geometry"].centroid
    return gdf


def to_geojson_dict(gdf: gpd.GeoDataFrame, kategori: str) -> dict:
    features = []
    for _, row in gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        lon, lat = geom.x, geom.y

        # Kumpulkan semua tag relevan yang ada di baris ini
        tag_dict = {}
        for col in TAG_KOLOM:
            if col in row and row[col] not in (None, "", "nan"):
                tag_dict[col] = row[col]
        # pyrosm biasanya taruh tag tambahan di kolom 'tags' (dict/JSON string)
        extra = row.get("tags")
        if isinstance(extra, str):
            try:
                tag_dict.update(json.loads(extra))
            except (json.JSONDecodeError, TypeError):
                pass
        elif isinstance(extra, dict):
            tag_dict.update(extra)

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "osm_id": row.get("id"),
                "osm_type": "way" if geom.geom_type != "Point" else "node",
                "kelompok": kategori,
                "kategori_asli": json.dumps(tag_dict, ensure_ascii=False),
                "name": row.get("name"),
                **tag_dict,
            },
        })
    return {"type": "FeatureCollection", "features": features}


def main():
    pbf_file = Path(PBF_PATH)
    if not pbf_file.exists():
        raise FileNotFoundError(
            f"File PBF tidak ditemukan di '{PBF_PATH}'. Download manual dulu dari "
            f"https://download.geofabrik.de/asia/indonesia/java-latest.osm.pbf "
            f"lalu taruh di folder ini atau ubah PBF_PATH."
        )

    print(f"Membaca {PBF_PATH} dengan filter bbox {BBOX} ...")
    osm = OSM(str(pbf_file), bounding_box=BBOX)

    for nama, filt in FILTERS.items():
        print(f"[{nama}] mengekstrak dari PBF...")
        gdf = osm.get_data_by_custom_criteria(
            custom_filter=filt,
            filter_type="keep",
            keep_nodes=True,
            keep_ways=True,
            keep_relations=False,
        )
        if gdf is None or len(gdf) == 0:
            print(f"[{nama}] tidak ada data yang cocok di area ini.")
            continue

        gdf = to_point_geometry(gdf)
        geojson = to_geojson_dict(gdf, nama)

        out_path = OUT_DIR / f"{nama}.geojson"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(geojson, f, ensure_ascii=False, indent=2)
        print(f"[{nama}] disimpan -> {out_path} ({len(geojson['features'])} titik)\n")

    print("Selesai. Ingat: cantumkan atribusi '© OpenStreetMap contributors' "
          "di halaman Metodologi, dan jangan publikasikan file GeoJSON mentah "
          "ini kalau sudah digabung dengan sumber lain (ODbL share-alike).")


if __name__ == "__main__":
    main()