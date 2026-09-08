"""
fetch_inarisk_raster.py
==========================
Ganti pendekatan dari fetch_inarisk.py: layer InaRISK yang tadi dicoba
("layer_bahaya_banjir_30") ternyata bertipe Raster Layer, bukan Feature
Layer, jadi tidak bisa di-query pakai /query+outFields kayak data vektor
(itu sebabnya kena 503 - bukan server down, tapi salah jenis request).

Untuk raster, jalurnya: ImageServer exportImage (potong raster sesuai bbox,
download sebagai GeoTIFF), lalu zonal stats ke grid H3 - prinsipnya sama
persis dengan compute_worldpop_zonal.py.

Layer yang dipakai: inarisk/layer_bahaya_banjir (ImageServer), indeks
bahaya banjir kontinu skala nasional (F32, bukan kelas diskrit). Kalau
butuh versi lain, INDEKS_BAHAYA_BANJIR (ImageServer) juga ada di server
yang sama dengan struktur serupa - tinggal ganti LAYER_NAME.

CATATAN PENTING: skrip ini menghasilkan nilai INDEKS MENTAH (rata-rata
dan maksimum per heksagon), BUKAN kelas risiko (rendah/sedang/tinggi).
Kamus data (L03) minta "Kelas risiko banjir" - breakpoint pengelompokan
indeks jadi kelas itu keputusan tim (belum ada breakpoint resmi yang
saya temukan dari InaRISK untuk layer spesifik ini), jangan dikira
angka di sini sudah berupa kelas final.

Belum pernah dites langsung (sandbox tidak ada akses internet).
"""

import json
from pathlib import Path

import geopandas as gpd
import requests
from rasterstats import zonal_stats

LAYER_NAME = "layer_bahaya_banjir"  # ganti ke "INDEKS_BAHAYA_BANJIR" kalau perlu versi lain
IMAGESERVER_URL = f"https://gis.bnpb.go.id/server/rest/services/inarisk/{LAYER_NAME}/ImageServer/exportImage"

BBOX = {"lon_min": 106.55, "lat_min": -6.45, "lon_max": 107.25, "lat_max": -5.95}

OUT_DIR = Path("data_raw/inarisk")
OUT_DIR.mkdir(parents=True, exist_ok=True)
RASTER_OUT = OUT_DIR / f"{LAYER_NAME}.tif"
GRID_PATH = Path("data_raw/h3_grid_res9.geojson")
FINAL_OUT = OUT_DIR / "h3_grid_with_risiko_banjir.geojson"

# Resolusi 100m (sama dengan WorldPop) - hitung ukuran pixel dari bbox
# supaya potongannya proporsional, bukan asal angka.
DEG_TO_M = 111_000  # perkiraan kasar di lintang khatulistiwa, cukup untuk ukuran gambar
WIDTH_PX = int((BBOX["lon_max"] - BBOX["lon_min"]) * DEG_TO_M / 100)
HEIGHT_PX = int((BBOX["lat_max"] - BBOX["lat_min"]) * DEG_TO_M / 100)


def download_raster():
    params = {
        "bbox": f"{BBOX['lon_min']},{BBOX['lat_min']},{BBOX['lon_max']},{BBOX['lat_max']}",
        "bboxSR": 4326,
        "imageSR": 4326,
        "size": f"{WIDTH_PX},{HEIGHT_PX}",
        "format": "tiff",
        "pixelType": "F32",
        "noDataInterpretation": "esriNoDataMatchAny",
        "interpolation": "RSP_NearestNeighbor",
        "f": "image",
    }
    print(f"Mengunduh raster dari {IMAGESERVER_URL} (ukuran {WIDTH_PX}x{HEIGHT_PX} px)...")
    resp = requests.get(IMAGESERVER_URL, params=params, timeout=120)
    resp.raise_for_status()

    # Kalau server mengembalikan JSON (bukan gambar), berarti ada error -
    # exportImage yang sukses selalu balas bytes gambar mentah.
    content_type = resp.headers.get("Content-Type", "")
    if "json" in content_type.lower():
        raise RuntimeError(f"Server mengembalikan error, bukan gambar: {resp.text[:500]}")

    with open(RASTER_OUT, "wb") as f:
        f.write(resp.content)
    print(f"Raster disimpan -> {RASTER_OUT} ({len(resp.content):,} bytes)")


def main():
    if not RASTER_OUT.exists():
        download_raster()
    else:
        print(f"Raster sudah ada di {RASTER_OUT}, skip download. "
              f"Hapus file itu manual kalau mau download ulang.")

    if not GRID_PATH.exists():
        raise FileNotFoundError(f"'{GRID_PATH}' tidak ditemukan. Jalankan generate_h3_grid.py dulu.")

    print(f"Membaca grid H3 dari {GRID_PATH} ...")
    gdf = gpd.read_file(GRID_PATH)

    print("Menghitung zonal statistics (mean dan max per heksagon)...")
    stats = zonal_stats(gdf, str(RASTER_OUT), stats=["mean", "max"], nodata=-9999, all_touched=False)

    gdf["risiko_banjir_indeks_mean"] = [s["mean"] if s["mean"] is not None else None for s in stats]
    gdf["risiko_banjir_indeks_max"] = [s["max"] if s["max"] is not None else None for s in stats]

    n_null = sum(1 for s in stats if s["mean"] is None)
    print(f"Heksagon tanpa data raster (null/di luar cakupan): {n_null} dari {len(gdf)}")

    gdf.to_file(FINAL_OUT, driver="GeoJSON")
    print(f"\nDisimpan -> {FINAL_OUT}")
    print("PENTING: ini masih indeks mentah, belum dikelompokkan jadi kelas "
          "risiko (rendah/sedang/tinggi). Breakpoint pengelompokan perlu "
          "diputuskan tim - bisa pakai kuantil (mis. tersil/kuartil dari "
          "distribusi indeks di wilayah studi) kalau tidak ada skema resmi "
          "dari BNPB untuk layer spesifik ini.")
    print("Ingat: cantumkan atribusi BNPB/InaRISK di halaman Metodologi.")


if __name__ == "__main__":
    main()