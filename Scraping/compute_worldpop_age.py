"""
compute_worldpop_age.py
==========================
Hitung D02 (pop_usia_produktif, umur 15-64) dari raster age-sex WorldPop.

BEDA DENGAN D01: WorldPop total population (yang sudah dipakai di
compute_worldpop_zonal.py) itu satu file raster. Untuk breakdown umur,
WorldPop menyediakan raster TERPISAH per kombinasi umur x jenis kelamin
(mis. perempuan umur 15-19, laki-laki umur 20-24, dst - band 5 tahunan).
D02 = jumlah populasi pada band umur 15-19 sampai 60-64, laki-laki DAN
perempuan digabung, per heksagon.

LANGKAH MANUAL SEBELUM JALANIN INI:
  1. Buka https://hub.worldpop.org/geodata/summary?id=55010 (atau cari
     "Indonesia age sex structures" di hub.worldpop.org kalau id beda) -
     cari dataset "Age and sex structures" 2025 constrained, resolusi 100m.
  2. Download raster untuk umur 15-64, laki-laki (m) DAN perempuan (f).
     Band umur 5 tahunan yang perlu didownload untuk cakupan 15-64:
       15, 20, 25, 30, 35, 40, 45, 50, 55, 60
     (band "15" = umur 15-19, "20" = umur 20-24, dst - band terakhir yang
     perlu adalah "60" untuk umur 60-64)
     Total 10 band x 2 jenis kelamin = 20 file .tif.
  3. Taruh SEMUA file itu di satu folder, mis. worldpop_age_sex/
     Nama file WorldPop biasanya berpola: idn_f_15_2025_constrained.tif,
     idn_m_20_2025_constrained.tif, dst - skrip ini otomatis mendeteksi
     angka umur dari nama file, jadi nama file tidak perlu diubah manual.
  4. Ubah RASTER_DIR di bawah kalau nama foldernya beda.

Kalau sebagian file belum sempat didownload, skrip tetap jalan dengan
file yang ada - tapi HASILNYA AKAN KURANG (undercount). Cek jumlah file
yang terdeteksi di output sebelum percaya hasilnya (harusnya 20).
"""

import re
from pathlib import Path

import geopandas as gpd
from rasterstats import zonal_stats

# ── Konfigurasi ──────────────────────────────────────────────────────
RASTER_DIR = Path("worldpop_age_sex")
GRID_PATH = Path("data_raw/h3_grid_with_pop.geojson")  # output D01, dilanjutkan di sini
OUT_PATH = Path("data_raw/h3_grid_with_pop_age.geojson")

# Umur produktif = 15-64. Band 5-tahunan WorldPop yang termasuk rentang ini.
AGE_BANDS_PRODUKTIF = {15, 20, 25, 30, 35, 40, 45, 50, 55, 60}


def extract_age_band(filename: str) -> int | None:
    """Cari angka umur dari nama file WorldPop age-sex. Pola nama file
    biasanya <negara>_<f|m>_<umur>_<tahun>*.tif, mis. idn_f_15_2025.tif."""
    match = re.search(r"_[fm]_(\d{1,2})_", filename.lower())
    if match:
        return int(match.group(1))
    return None


def main():
    if not GRID_PATH.exists():
        raise FileNotFoundError(
            f"'{GRID_PATH}' tidak ditemukan. Jalankan compute_worldpop_zonal.py "
            f"(D01) dulu sebelum ini - skrip ini melanjutkan dari output-nya."
        )
    if not RASTER_DIR.exists():
        raise FileNotFoundError(
            f"Folder '{RASTER_DIR}' tidak ditemukan. Download raster age-sex "
            f"WorldPop dulu sesuai instruksi di docstring skrip ini."
        )

    tif_files = list(RASTER_DIR.glob("*.tif"))
    relevan = []
    for f in tif_files:
        umur = extract_age_band(f.name)
        if umur in AGE_BANDS_PRODUKTIF:
            relevan.append(f)

    print(f"Ditemukan {len(tif_files)} file .tif di '{RASTER_DIR}', "
          f"{len(relevan)} di antaranya masuk rentang umur produktif (15-64).")
    if len(relevan) < 20:
        print(f"PERINGATAN: harusnya ada 20 file (10 band umur x 2 jenis "
              f"kelamin). Cuma ketemu {len(relevan)} - hasil D02 akan "
              f"UNDERCOUNT kalau lanjut dengan file yang ada sekarang. "
              f"Cek lagi folder downloadnya, atau lanjut kalau memang sengaja "
              f"pakai subset (mis. cuma mau estimasi kasar dulu).")

    print(f"Membaca grid dari {GRID_PATH} ...")
    gdf = gpd.read_file(GRID_PATH)

    # Akumulasi sum tiap file ke kolom sementara, lalu dijumlah semua di akhir
    total_produktif = [0.0] * len(gdf)
    for f in relevan:
        print(f"  zonal stats: {f.name}")
        stats = zonal_stats(gdf, str(f), stats=["sum"], nodata=-99999, all_touched=False)
        for i, s in enumerate(stats):
            total_produktif[i] += s["sum"] if s["sum"] is not None else 0

    gdf["pop_usia_produktif"] = total_produktif

    gdf.to_file(OUT_PATH, driver="GeoJSON")
    print(f"\nDisimpan -> {OUT_PATH}")
    print(f"File age-sex yang dipakai: {len(relevan)}/20")
    print("Ingat: atribusi WorldPop (CC BY 4.0) sudah dicatat di langkah D01, "
          "tidak perlu ditambah terpisah.")


if __name__ == "__main__":
    main()
