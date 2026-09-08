"""
generate_h3_grid.py
=====================
Generate grid heksagon H3 resolusi 9 untuk wilayah studi (unit analisis utama
proyek, Bagian 2.3 laporan). Dijalankan SETELAH bbox/wilayah studi final
disepakati tim (lihat briefing: ini masih keputusan menggantung).

Output: GeoJSON polygon per heksagon + kolom hex_id, siap dipakai sebagai
target spatial join untuk semua variabel (D01-M03).
"""

import json
from pathlib import Path
import h3
from shapely.geometry import Polygon, mapping, box

# Bbox sama dengan fetch_osm_overpass.py - GANTI BARENGAN kalau wilayah berubah
# DKI Jakarta + Bekasi (kota & kab) + sebagian Tangerang/Tangsel
BBOX = {"lon_min": 106.55, "lat_min": -6.45, "lon_max": 107.25, "lat_max": -5.95}
RESOLUSI = 9  # ±0.10 km2, ±350m lebar - sesuai keputusan Bagian 2.3

OUT_PATH = Path("data_raw/h3_grid_res9.geojson")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# h3-py v4 mengganti total API-nya dari v3 (polyfill -> polygon_to_cells,
# h3_to_geo_boundary -> cell_to_boundary, h3_to_geo -> cell_to_latlng).
# Deteksi versi yang terinstall biar skrip jalan di keduanya tanpa perlu
# pin versi tertentu.
H3_V4 = hasattr(h3, "polygon_to_cells")


def bbox_to_h3_cells(bbox: dict, res: int) -> set:
    """Isi bbox dengan H3 cells, kompatibel h3-py v3 dan v4."""
    poly_coords = [
        (bbox["lat_min"], bbox["lon_min"]),
        (bbox["lat_min"], bbox["lon_max"]),
        (bbox["lat_max"], bbox["lon_max"]),
        (bbox["lat_max"], bbox["lon_min"]),
    ]
    if H3_V4:
        latlng_poly = h3.LatLngPoly(poly_coords)  # v4 pakai urutan (lat, lon)
        return set(h3.polygon_to_cells(latlng_poly, res))
    else:
        geojson_poly = {"type": "Polygon", "coordinates": [[[lon, lat] for lat, lon in poly_coords]]}
        return h3.polyfill(geojson_poly, res, geo_json_conformant=True)


def cell_boundary(hex_id):
    """Ambil boundary [[lon, lat], ...] - kompatibel v3 dan v4."""
    if H3_V4:
        return [[lon, lat] for lat, lon in h3.cell_to_boundary(hex_id)]
    return h3.h3_to_geo_boundary(hex_id, geo_json=True)


def cell_center(hex_id):
    """Ambil (lat, lon) centroid - kompatibel v3 dan v4."""
    if H3_V4:
        return h3.cell_to_latlng(hex_id)
    return h3.h3_to_geo(hex_id)


def main():
    cells = bbox_to_h3_cells(BBOX, RESOLUSI)
    print(f"Jumlah heksagon H3 res-{RESOLUSI} dalam bbox: {len(cells)}")

    features = []
    for hex_id in cells:
        boundary = cell_boundary(hex_id)  # [[lon, lat], ...]
        poly = Polygon(boundary)
        lat, lon = cell_center(hex_id)
        features.append({
            "type": "Feature",
            "geometry": mapping(poly),
            "properties": {
                "hex_id": hex_id,
                "centroid_lat": lat,
                "centroid_lon": lon,
                "resolusi": RESOLUSI,
                # kolom kualitas data (Bagian 6.7) - diisi belakangan
                "n_titik_misi": 0,
                "tingkat_keyakinan": "RENDAH",
                "data_source": "predicted",
            },
        })

    geojson = {"type": "FeatureCollection", "features": features}
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)

    print(f"Disimpan -> {OUT_PATH}")
    print("Catatan: ratusan ribu heksagon untuk Jabodetabek penuh - file bisa besar. "
          "Kalau cuma butuh area dekat simpul transit, potong dulu pakai isochrone "
          "catchment sebelum generate grid (lebih efisien daripada generate semua "
          "lalu filter belakangan).")


if __name__ == "__main__":
    main()