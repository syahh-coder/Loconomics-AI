"""
compute_open_buildings.py
============================
Ekstraksi Google Open Buildings V3 -> M01 (rasio_tutupan_bangunan) dan
M02 (luas_bangunan_median) per heksagon.

BEDA DARI LAPORAN: laporan tim (Bagian 5.1, E-6) sebut aksesnya lewat
Google Earth Engine, yang butuh akun GEE + auth OAuth. Ternyata ada
jalur lebih simpel - Google menyediakan download publik langsung, tanpa
akun/auth sama sekali, dipecah per sel S2 level 4 (grid geografis milik
Google, bukan H3). Skrip ini pakai jalur itu.

CARA KERJA:
  1. Hitung sel S2 level-4 mana saja yang menutupi bbox wilayah studi
     (pakai library s2sphere)
  2. Download CSV.gz publik untuk tiap sel itu dari
     storage.googleapis.com/open-buildings-data/v3/polygons_s2_level_4_gzip/
  3. Baca cuma kolom latitude, longitude, area_in_meters, confidence -
     SENGAJA skip kolom geometry (WKT polygon penuh) karena ukurannya
     besar dan tidak kita butuh (kita cuma perlu titik pusat + luas per
     bangunan, bukan bentuk poligonnya)
  4. Potong presisi ke bbox (sel S2 biasanya jauh lebih besar dari bbox
     kita, jadi hasil download perlu difilter lagi)
  5. Spatial join ke grid H3, hitung total luas & median luas per heksagon

LANGKAH MANUAL SEBELUM JALANIN INI:
  pip install s2sphere pandas geopandas h3
"""

import gzip
import time
from pathlib import Path

import geopandas as gpd
import h3
import pandas as pd
import requests
import s2sphere
from shapely.geometry import Point

BBOX = {"lon_min": 106.55, "lat_min": -6.45, "lon_max": 107.25, "lat_max": -5.95}
GRID_PATH = Path("data_raw/h3_grid_res9.geojson")

OUT_DIR = Path("data_raw/open_buildings")
OUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR = OUT_DIR / "raw_s2_tiles"
RAW_DIR.mkdir(parents=True, exist_ok=True)
FINAL_OUT = OUT_DIR / "h3_grid_with_buildings.geojson"

BASE_URL = "https://storage.googleapis.com/open-buildings-data/v3/polygons_s2_level_4_gzip"

H3_V4 = hasattr(h3, "cell_area")


def hex_area_m2(hex_id: str) -> float:
    """Luas heksagon dalam meter persegi - dipakai untuk hitung rasio
    tutupan bangunan. Kompatibel h3-py v3 dan v4."""
    if H3_V4:
        return h3.cell_area(hex_id, unit="m^2")
    return h3.cell_area(hex_id, unit="m^2")  # v3 juga punya signature yang sama


def get_s2_tokens_for_bbox(bbox: dict) -> list:
    region = s2sphere.LatLngRect(
        s2sphere.LatLng.from_degrees(bbox["lat_min"], bbox["lon_min"]),
        s2sphere.LatLng.from_degrees(bbox["lat_max"], bbox["lon_max"]),
    )
    coverer = s2sphere.RegionCoverer()
    coverer.min_level = 4
    coverer.max_level = 4
    covering = coverer.get_covering(region)
    tokens = [cell_id.to_token() for cell_id in covering]
    return tokens


def download_tile(token: str, max_retry: int = 60) -> Path:
    out_path = RAW_DIR / f"{token}_buildings.csv.gz"
    url = f"{BASE_URL}/{token}_buildings.csv.gz"

    # Cek ukuran total file dulu via HEAD, biar tahu kapan resume selesai
    head = requests.head(url, timeout=30)
    if head.status_code == 404:
        print(f"  {token}: 404 - sel ini kemungkinan tidak ada bangunan terdeteksi, skip")
        return None
    head.raise_for_status()
    total_size = int(head.headers.get("Content-Length", 0))

    if out_path.exists() and out_path.stat().st_size >= total_size and total_size > 0:
        print(f"  {token}: sudah lengkap ({out_path.stat().st_size:,} bytes), skip download")
        return out_path

    for attempt in range(1, max_retry + 1):
        resume_byte = out_path.stat().st_size if out_path.exists() else 0
        headers = {"Range": f"bytes={resume_byte}-"} if resume_byte > 0 else {}
        mode = "ab" if resume_byte > 0 else "wb"

        print(f"  {token}: percobaan {attempt}/{max_retry}, resume dari byte "
              f"{resume_byte:,}/{total_size:,} ...")
        try:
            # timeout=(connect_timeout, read_timeout) - read timeout per chunk,
            # bukan untuk keseluruhan file (file ini bisa besar)
            resp = requests.get(url, headers=headers, timeout=(30, 60), stream=True)
            resp.raise_for_status()
            with open(out_path, mode) as f:
                for chunk in resp.iter_content(chunk_size=512 * 1024):
                    f.write(chunk)

            final_size = out_path.stat().st_size
            if total_size > 0 and final_size < total_size:
                print(f"  {token}: belum lengkap ({final_size:,}/{total_size:,}), lanjut retry...")
                continue
            print(f"  {token}: selesai ({final_size:,} bytes)")
            return out_path

        except requests.exceptions.RequestException as e:
            print(f"  {token}: gagal ({e}), akan resume di percobaan berikutnya")
            if attempt < max_retry:
                time.sleep(min(10, 3 * attempt))  # backoff dibatasi max 10 detik biar cepat coba lagi

    raise RuntimeError(
        f"'{token}' gagal didownload lengkap setelah {max_retry} percobaan. "
        f"File partial tersimpan di {out_path} - jalankan ulang skrip untuk "
        f"lanjut resume, tidak perlu mulai dari 0."
    )


def main():
    if not GRID_PATH.exists():
        raise FileNotFoundError(f"'{GRID_PATH}' tidak ditemukan. Jalankan generate_h3_grid.py dulu.")

    print("Menghitung sel S2 level-4 yang menutupi bbox wilayah studi...")
    tokens = get_s2_tokens_for_bbox(BBOX)
    print(f"Ditemukan {len(tokens)} sel S2: {tokens}")

    print("\nMengunduh tile CSV.gz...")
    tile_paths = []
    for token in tokens:
        p = download_tile(token)
        if p:
            tile_paths.append(p)

    if not tile_paths:
        raise RuntimeError("Tidak ada tile yang berhasil diunduh - cek bbox atau koneksi.")

    print(f"\nMembaca {len(tile_paths)} file CSV.gz (skip kolom geometry, cuma ambil "
          f"latitude/longitude/area_in_meters/confidence)...")
    dfs = []
    for p in tile_paths:
        print(f"  membaca {p.name} ...")
        with gzip.open(p, "rt") as f:
            df = pd.read_csv(f, usecols=["latitude", "longitude", "area_in_meters", "confidence"])
        dfs.append(df)
    all_buildings = pd.concat(dfs, ignore_index=True)
    print(f"Total baris sebelum filter bbox: {len(all_buildings):,}")

    # Sel S2 lebih besar dari bbox kita, potong presisi
    mask = (
        (all_buildings["longitude"] >= BBOX["lon_min"]) &
        (all_buildings["longitude"] <= BBOX["lon_max"]) &
        (all_buildings["latitude"] >= BBOX["lat_min"]) &
        (all_buildings["latitude"] <= BBOX["lat_max"])
    )
    all_buildings = all_buildings[mask].copy()
    print(f"Total baris setelah filter bbox: {len(all_buildings):,}")

    print("\nMembangun GeoDataFrame titik bangunan...")
    geometry = [Point(xy) for xy in zip(all_buildings["longitude"], all_buildings["latitude"])]
    buildings_gdf = gpd.GeoDataFrame(all_buildings, geometry=geometry, crs="EPSG:4326")

    print("Membaca grid H3...")
    grid = gpd.read_file(GRID_PATH)

    print("Spatial join bangunan ke heksagon (bisa beberapa menit)...")
    joined = gpd.sjoin(buildings_gdf, grid[["hex_id", "geometry"]], predicate="within")

    agg = joined.groupby("hex_id").agg(
        total_luas_bangunan_m2=("area_in_meters", "sum"),
        luas_bangunan_median=("area_in_meters", "median"),
        jumlah_bangunan=("area_in_meters", "count"),
    ).reset_index()

    grid = grid.merge(agg, on="hex_id", how="left")
    grid["total_luas_bangunan_m2"] = grid["total_luas_bangunan_m2"].fillna(0)
    grid["jumlah_bangunan"] = grid["jumlah_bangunan"].fillna(0)
    # luas_bangunan_median dibiarkan null (bukan 0) untuk heksagon tanpa
    # bangunan - median dari himpunan kosong tidak masuk akal diisi 0

    print("Menghitung rasio tutupan bangunan (M01)...")
    grid["hex_area_m2"] = grid["hex_id"].apply(hex_area_m2)
    grid["rasio_tutupan_bangunan"] = grid["total_luas_bangunan_m2"] / grid["hex_area_m2"]

    grid.to_file(FINAL_OUT, driver="GeoJSON")
    print(f"\nDisimpan -> {FINAL_OUT}")
    print(f"Heksagon dengan minimal 1 bangunan: {(grid['jumlah_bangunan'] > 0).sum()} dari {len(grid)}")
    print("Ingat: atribusi 'Google Open Buildings, CC BY 4.0' wajib di halaman Metodologi.")


if __name__ == "__main__":
    main()