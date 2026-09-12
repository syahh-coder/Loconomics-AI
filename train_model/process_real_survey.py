"""
process_real_survey.py
=========================
Proses sample Menu Go RESMI (bukan sintetis) jadi format canonical siap
training. Cuma Menu Go yang dipakai - Struk Go/Properti Go/Activity
lokasinya di luar bbox studi (sudah diverifikasi, lihat DATA_SCHEMA.md).

SIMPLIFIKASI YANG DISENGAJA (harus disebut di halaman Metodologi produk):
1. skor_ramai_terkoreksi (D10) TIDAK dikoreksi bias jam kunjungan penuh
   sesuai formula resmi (Bagian 6.1 laporan) - dengan cuma 15 titik,
   baseline rata-rata per jam tidak robust dihitung. Dipakai skor mentah.
2. harga_median_porsi (B07) di sini adalah harga PER LOKASI (satu angka
   per baris), bukan median dari banyak sampel per heksagon - istilah
   "median" jadi kurang presisi untuk kasus 1 titik per heksagon.

CARA PAKAI:
    python -m train_model.process_real_survey

INPUT YANG DIHARAPKAN: taruh file sample asli di
    Scraping/data_raw/survei_asli_sample/menu_go_sample.csv
(salin dari Sample_MenuGo_WebGIS2026.csv yang didapat dari panitia/tim)
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from train_model import config
from train_model.data_loader import DataLoadError, load_grid_base
from train_model.utils.logging_setup import get_logger

logger = get_logger(__name__)

KOLOM_KONDISI = "Bagaimana Kondisi Pembeli Saat Kunjungan Dilakukan?"
KOLOM_HARGA = "Berapa Harga Rata-rata Menu Tersebut (Per porsi)?"
KOLOM_LAT = "Latitude"
KOLOM_LON = "Longitude"

MAPPING_KONDISI = {
    "sepi": 1,
    "sedang": 2,
    "ramai": 3,
}


def _map_kondisi_ke_skor(teks: str):
    """Teks aslinya panjang, mis. 'Ramai (Terdapat antrean lebih dari 3
    orang ...)' - cocokkan berdasarkan kata kunci di awal, JANGAN exact match."""
    if not isinstance(teks, str):
        return None
    teks_lower = teks.strip().lower()
    for kata_kunci, skor in MAPPING_KONDISI.items():
        if teks_lower.startswith(kata_kunci):
            return skor
    logger.warning(f"Tidak bisa mapping teks kondisi pembeli: '{teks}' - hasil None")
    return None


def _validasi_bbox(df: pd.DataFrame) -> pd.DataFrame:
    """Filter cuma baris yang jatuh dalam bbox studi. Cetak berapa yang
    lolos - kalau tidak 15/15 (sesuai temuan verifikasi awal), ada yang
    berubah dari file yang sudah diverifikasi manual, WAJIB diinvestigasi."""
    b = config.BBOX
    mask = (
        (df[KOLOM_LAT] >= b["lat_min"]) & (df[KOLOM_LAT] <= b["lat_max"]) &
        (df[KOLOM_LON] >= b["lon_min"]) & (df[KOLOM_LON] <= b["lon_max"])
    )
    n_lolos = mask.sum()
    n_total = len(df)
    logger.info(f"Filter bbox: {n_lolos}/{n_total} titik lolos")

    if n_lolos < n_total:
        logger.warning(
            f"{n_total - n_lolos} titik DIBUANG karena di luar bbox studi. "
            f"Verifikasi terakhir (saat DATA_SCHEMA.md ditulis) menyatakan "
            f"15/15 titik Menu Go lolos - kalau sekarang berbeda, kemungkinan "
            f"file sample sudah diganti/diupdate. Cek ulang koordinat manual."
        )
    if n_lolos == 0:
        raise DataLoadError(
            f"0 titik lolos filter bbox dari '{config.MENU_GO_SAMPLE_ASLI}'. "
            f"Tidak ada data real yang bisa dipakai. Cek apakah file yang "
            f"ditaruh di sini benar Menu Go (bukan Struk Go/Properti Go/Activity "
            f"yang memang di luar bbox)."
        )
    return df[mask].copy()


def process() -> pd.DataFrame:
    if not config.MENU_GO_SAMPLE_ASLI.exists():
        raise DataLoadError(
            f"File tidak ditemukan: '{config.MENU_GO_SAMPLE_ASLI}'\n"
            f"Salin Sample_MenuGo_WebGIS2026.csv ke path ini dulu "
            f"(folder '{config.SURVEI_ASLI_SAMPLE_DIR}' mungkin perlu dibuat manual)."
        )

    df = pd.read_csv(config.MENU_GO_SAMPLE_ASLI)
    logger.info(f"Menu Go sample dimuat: {len(df)} baris")

    kolom_wajib = [KOLOM_KONDISI, KOLOM_HARGA, KOLOM_LAT, KOLOM_LON]
    hilang = [k for k in kolom_wajib if k not in df.columns]
    if hilang:
        raise DataLoadError(
            f"Kolom yang diharapkan tidak ditemukan: {hilang}\n"
            f"Kolom yang tersedia: {df.columns.tolist()}\n"
            f"Kemungkinan file yang ditaruh bukan Menu Go, atau skema berubah "
            f"dari yang didokumentasikan di DATA_SCHEMA.md."
        )

    df = _validasi_bbox(df)

    df[config.TARGET_SKOR_RAMAI] = df[KOLOM_KONDISI].apply(_map_kondisi_ke_skor)
    df[config.TARGET_HARGA] = df[KOLOM_HARGA]

    n_gagal_map = df[config.TARGET_SKOR_RAMAI].isna().sum()
    if n_gagal_map > 0:
        logger.warning(f"{n_gagal_map} baris gagal di-mapping ke skor kondisi - jadi NaN")

    grid = load_grid_base()
    geometry = [Point(lon, lat) for lon, lat in zip(df[KOLOM_LON], df[KOLOM_LAT])]
    gdf_points = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    try:
        joined = gpd.sjoin(gdf_points, grid[["hex_id", "geometry"]], predicate="within")
    except Exception as e:
        raise RuntimeError(f"Gagal spatial join Menu Go ke grid hex_id: {e}") from e

    if len(joined) < len(df):
        logger.warning(
            f"{len(df) - len(joined)} titik tidak jatuh di heksagon manapun "
            f"(kemungkinan di luar cakupan grid meski dalam bbox kotak - bisa "
            f"terjadi di tepi wilayah). Titik ini dibuang dari hasil."
        )

    hasil_per_titik = pd.DataFrame({
        "hex_id": joined["hex_id"],
        config.TARGET_SKOR_RAMAI: joined[config.TARGET_SKOR_RAMAI],
        config.TARGET_HARGA: joined[config.TARGET_HARGA],
    })

    n_hex_unik = hasil_per_titik["hex_id"].nunique()
    if n_hex_unik < len(hasil_per_titik):
        logger.warning(
            f"{len(hasil_per_titik)} titik cuma jatuh ke {n_hex_unik} heksagon "
            f"unik - ada heksagon yang menampung >1 titik survei (wajar untuk "
            f"titik yang berdekatan, heksagon res-9 cuma ~350m lebar). "
            f"Diagregasi jadi 1 baris per heksagon pakai MEDIAN, sesuai formula "
            f"resmi kamus data (Bagian 6.1 laporan: harga_rata_area = "
            f"median per heksagon)."
        )

    # WAJIB agregasi per heksagon, BUKAN 1 baris per titik mentah - kalau
    # tidak, hex_id akan duplikat di dataset training dan bikin merge/update
    # di modul lain gagal (ValueError: cannot reindex on axis dengan duplicate labels)
    hasil = hasil_per_titik.groupby("hex_id", as_index=False).agg({
        config.TARGET_SKOR_RAMAI: "median",
        config.TARGET_HARGA: "median",
    })
    n_titik_per_hex = hasil_per_titik.groupby("hex_id").size().rename("n_titik_real")
    hasil = hasil.merge(n_titik_per_hex, on="hex_id")
    hasil["sumber_data"] = "real"
    hasil["is_dummy"] = False

    logger.info(f"Hasil akhir: {len(hasil)} heksagon unik dari {len(hasil_per_titik)} "
                f"titik survei real (setelah agregasi median per heksagon)")
    return hasil


def main():
    hasil = process()
    config.SURVEI_DIR.mkdir(parents=True, exist_ok=True)
    hasil.to_csv(config.REAL_PROCESSED_FILE, index=False)
    logger.info(f"Disimpan -> {config.REAL_PROCESSED_FILE}")
    logger.info(
        "INGAT: simplifikasi D10 (tanpa koreksi bias jam) dan B07 (per lokasi, "
        "bukan median banyak titik) WAJIB disebutkan di halaman Metodologi "
        "produk akhir - lihat PRD.md Bagian 4a."
    )


if __name__ == "__main__":
    main()