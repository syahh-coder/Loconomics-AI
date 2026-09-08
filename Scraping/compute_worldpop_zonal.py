"""
compute_worldpop_zonal.py
============================
Zonal statistics WorldPop -> isi variabel D01 (pop_100m) per heksagon H3.

LANGKAH MANUAL SEBELUM JALANIN INI:
  1. pip install rasterio rasterstats
  2. Download raster WorldPop Indonesia 2025 constrained, resolusi 100m,
     dari: https://hub.worldpop.org/geodata/summary?id=55010
     Format file .tif. Taruh di folder yang sama, atau ubah RASTER_PATH.
  3. Pastikan data_raw/h3_grid_res9.geojson sudah ada (hasil generate_h3_grid.py)

CATATAN:
  - Raster WorldPop Indonesia itu file nasional (cakupan seluruh negara),
    jadi ukurannya besar. rasterstats akan otomatis crop ke bbox grid H3
    saat proses, tapi baca file awal tetap makan waktu.
  - Ini baru D01 (pop_100m, total populasi). D02 (pop_usia_produktif,
    umur 15-64) butuh raster terpisah dari koleksi age-sex WorldPop
    (pop_age_sex_cons_unadj) - beda file, beda proses, dikerjakan
    menyusul kalau D01 sudah beres.
  - Lisensi CC BY 4.0 -> wajib atribusi WorldPop di halaman Metodologi.
"""

import json
from pathlib import Path

import geopandas as gpd
from rasterstats import zonal_stats

# ── Konfigurasi ──────────────────────────────────────────────────────
RASTER_PATH = "worldpop_2025.tif"  # ganti sesuai nama file hasil download
GRID_PATH = "data_raw/h3_grid_res9.geojson"
OUT_PATH = Path("data_raw/h3_grid_with_pop.geojson")


def main():
    raster_file = Path(RASTER_PATH)
    grid_file = Path(GRID_PATH)

    if not raster_file.exists():
        raise FileNotFoundError(
            f"Raster WorldPop tidak ditemukan di '{RASTER_PATH}'. Download dulu dari "
            f"https://hub.worldpop.org/geodata/summary?id=55010 (2025, constrained, 100m), "
            f"taruh di folder ini atau ubah RASTER_PATH."
        )
    if not grid_file.exists():
        raise FileNotFoundError(
            f"Grid H3 tidak ditemukan di '{GRID_PATH}'. Jalankan generate_h3_grid.py dulu."
        )

    print(f"Membaca grid H3 dari {GRID_PATH} ...")
    gdf = gpd.read_file(grid_file)
    print(f"Jumlah heksagon: {len(gdf)}")

    print(f"Menghitung zonal statistics dari {RASTER_PATH} (bisa beberapa menit)...")
    # stats='sum' -> D01 pop_100m = total populasi dalam satu heksagon,
    # sesuai definisi di kamus data (Bagian 6.1): "Zonal sum dari raster
    # populasi WorldPop 2025"
    stats = zonal_stats(
        gdf,
        str(raster_file),
        stats=["sum"],
        nodata=-99999,  # nilai nodata standar WorldPop, sesuaikan kalau beda
        all_touched=False,
    )

    gdf["pop_100m"] = [s["sum"] if s["sum"] is not None else 0 for s in stats]

    n_kosong = (gdf["pop_100m"] == 0).sum()
    print(f"Heksagon dengan populasi 0 atau di luar cakupan raster: {n_kosong} dari {len(gdf)}")

    gdf.to_file(OUT_PATH, driver="GeoJSON")
    print(f"Disimpan -> {OUT_PATH}")
    print("\nIngat: cantumkan atribusi 'WorldPop (www.worldpop.org), CC BY 4.0' "
          "di halaman Metodologi.")
    print("D02 (pop_usia_produktif) belum dihitung - butuh raster age-sex terpisah.")


if __name__ == "__main__":
    main()