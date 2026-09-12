"""
data_loader.py
=================
Baca semua file sumber data mentah. Setiap fungsi loader melakukan
validasi eksplisit (file ada, bisa dibaca, kolom yang diharapkan ada)
SEBELUM mengembalikan data - kalau ada yang salah, exception yang
dilempar harus menjelaskan persis apa yang salah dan langkah perbaikannya,
bukan cuma stack trace generik dari geopandas/pandas.

Tidak ada fungsi di sini yang mengisi nilai kosong dengan asumsi (mis.
isi 0 untuk NULL) - itu keputusan yang harus eksplisit di
feature_engineering.py, bukan disembunyikan di loader.
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd

from train_model import config
from train_model.utils.logging_setup import get_logger

logger = get_logger(__name__)


class DataLoadError(Exception):
    """Exception khusus untuk semua kegagalan loading data di modul ini -
    memudahkan pemanggil membedakan 'data belum siap' vs error teknis lain."""
    pass


def _require_file(path: Path, penjelasan: str) -> None:
    """Cek file ada sebelum dibaca, lempar pesan yang actionable kalau tidak."""
    if not path.exists():
        raise DataLoadError(
            f"File tidak ditemukan: '{path}'\n"
            f"Konteks: {penjelasan}\n"
            f"Cek Scraping/README.md untuk skrip yang harus dijalankan dulu "
            f"untuk menghasilkan file ini, atau DATA_SCHEMA.md untuk detail skema."
        )


def _require_columns(df, kolom_wajib: list, nama_file: str) -> None:
    """Cek kolom yang diharapkan benar-benar ada, sebelum kode lain
    mengasumsikan keberadaannya dan gagal dengan KeyError yang membingungkan."""
    hilang = [k for k in kolom_wajib if k not in df.columns]
    if hilang:
        raise DataLoadError(
            f"Kolom hilang di '{nama_file}': {hilang}\n"
            f"Kolom yang tersedia: {list(df.columns)}\n"
            f"Kemungkinan skema file sudah berubah sejak DATA_SCHEMA.md ditulis - "
            f"cek ulang dan update dokumentasi kalau memang berubah, jangan "
            f"paksa mapping lama."
        )


def load_grid_base() -> gpd.GeoDataFrame:
    """Grid H3 dasar - kerangka join semua fitur lain."""
    _require_file(config.GRID_BASE, "grid dasar dari generate_h3_grid.py")
    try:
        gdf = gpd.read_file(config.GRID_BASE)
    except Exception as e:
        raise DataLoadError(f"Gagal baca '{config.GRID_BASE}' sebagai GeoJSON: {e}") from e

    _require_columns(gdf, ["hex_id", "geometry"], config.GRID_BASE.name)
    logger.info(f"Grid dasar dimuat: {len(gdf)} heksagon")
    return gdf


def load_population() -> pd.DataFrame:
    """D01 (pop_100m) dan D02 (pop_usia_produktif). Dikembalikan sebagai
    DataFrame biasa (bukan GeoDataFrame) karena cuma dipakai untuk join
    atribut ke grid dasar, tidak perlu geometry dobel."""
    _require_file(config.POP_AGE_FILE, "populasi usia produktif dari compute_worldpop_age.py")

    gdf = gpd.read_file(config.POP_AGE_FILE)
    _require_columns(gdf, ["hex_id", "pop_usia_produktif"], config.POP_AGE_FILE.name)

    kolom_ambil = ["hex_id", "pop_usia_produktif"]
    if "pop_100m" in gdf.columns:
        kolom_ambil.append("pop_100m")
        logger.info(f"'pop_100m' ditemukan langsung di {config.POP_AGE_FILE.name}")
        df = pd.DataFrame(gdf[kolom_ambil])
        logger.info(f"Populasi dimuat: {len(df)} baris")
        return df

    logger.info(f"'pop_100m' tidak ada di {config.POP_AGE_FILE.name}, join terpisah dari {config.POP_FILE.name}")
    _require_file(config.POP_FILE, "populasi total dari compute_worldpop_zonal.py")
    gdf_pop = gpd.read_file(config.POP_FILE)
    _require_columns(gdf_pop, ["hex_id", "pop_100m"], config.POP_FILE.name)
    df_pop = pd.DataFrame(gdf_pop[["hex_id", "pop_100m"]])
    df = pd.DataFrame(gdf[kolom_ambil]).merge(df_pop, on="hex_id", how="left")
    logger.info(f"Populasi dimuat: {len(df)} baris")
    return df


def load_buildings() -> pd.DataFrame:
    """M01 (rasio_tutupan_bangunan), M02 (luas_bangunan_median)."""
    _require_file(config.BUILDINGS_FILE, "morfologi bangunan dari compute_open_buildings.py")
    gdf = gpd.read_file(config.BUILDINGS_FILE)
    _require_columns(
        gdf, ["hex_id", "rasio_tutupan_bangunan", "luas_bangunan_median", "jumlah_bangunan"],
        config.BUILDINGS_FILE.name,
    )
    df = pd.DataFrame(gdf[["hex_id", "rasio_tutupan_bangunan", "luas_bangunan_median", "jumlah_bangunan"]])
    logger.info(f"Data bangunan dimuat: {len(df)} baris")
    return df


def load_inarisk() -> pd.DataFrame:
    """Proksi L03 (indeks risiko banjir mentah, belum diklasifikasi)."""
    _require_file(config.INARISK_FILE, "indeks risiko banjir dari fetch_inarisk_raster.py")
    gdf = gpd.read_file(config.INARISK_FILE)
    _require_columns(
        gdf, ["hex_id", "risiko_banjir_indeks_mean", "risiko_banjir_indeks_max"],
        config.INARISK_FILE.name,
    )
    df = pd.DataFrame(gdf[["hex_id", "risiko_banjir_indeks_mean", "risiko_banjir_indeks_max"]])
    logger.info(f"Data risiko banjir dimuat: {len(df)} baris")
    return df


def load_rdtr() -> gpd.GeoDataFrame:
    """L01/L02 - poligon zona, BELUM di-spatial-join ke heksagon (itu
    tugas feature_engineering.py). Fungsi ini cuma baca mentahnya.
    Cakupan cuma DKI - ini normal, bukan bug."""
    _require_file(config.RDTR_FILE, "zonasi RDTR dari fetch_jakarta_satu.py")
    gdf = gpd.read_file(config.RDTR_FILE)
    if len(gdf) == 0:
        raise DataLoadError(
            f"'{config.RDTR_FILE}' berhasil dibaca tapi kosong (0 fitur). "
            f"Ini tidak normal - cek ulang proses fetch_jakarta_satu.py."
        )
    logger.info(f"RDTR dimuat: {len(gdf)} fitur poligon. "
                f"Kolom tersedia: {list(gdf.columns)} - "
                f"VERIFIKASI MANUAL kolom mana yang berisi kode zona sebelum dipakai.")
    return gdf


def load_osm_points(kelompok: str) -> gpd.GeoDataFrame:
    """kelompok: 'kompetitor', 'simpul_transit', atau 'generator_keramaian'."""
    mapping = {
        "kompetitor": config.OSM_KOMPETITOR,
        "simpul_transit": config.OSM_SIMPUL_TRANSIT,
        "generator_keramaian": config.OSM_GENERATOR_KERAMAIAN,
    }
    if kelompok not in mapping:
        raise ValueError(f"kelompok harus salah satu dari {list(mapping.keys())}, dapat '{kelompok}'")

    path = mapping[kelompok]
    _require_file(path, f"titik OSM kelompok '{kelompok}' dari fetch_osm_geofabrik.py")
    gdf = gpd.read_file(path)
    if len(gdf) == 0:
        raise DataLoadError(f"'{path}' kosong (0 fitur) - cek ulang proses ekstraksi OSM.")
    logger.info(f"OSM '{kelompok}' dimuat: {len(gdf)} titik")
    return gdf


def load_poi_terpadu() -> gpd.GeoDataFrame:
    _require_file(config.POI_TERPADU, "POI gabungan OSM+Overture dari fetch_overture_dedup.py")
    gdf = gpd.read_file(config.POI_TERPADU)
    _require_columns(gdf, ["sumber", "geometry"], config.POI_TERPADU.name)
    logger.info(f"POI terpadu dimuat: {len(gdf)} titik")
    return gdf


def load_survey_labels() -> pd.DataFrame:
    """Data label/target untuk training. Sumber file tergantung
    config.TRAINING_MODE (blended/dummy_only/real_only) - lihat config.py
    dan PRD.md Bagian 4a untuk detail strategi hybrid real+sintetis."""
    if not config.MENU_GO_FILE.parent.exists():
        raise DataLoadError(
            f"Folder '{config.MENU_GO_FILE.parent}' tidak ditemukan.\n"
            f"Mode training saat ini: '{config.TRAINING_MODE}'.\n"
            f"Kalau mode 'blended' (default): jalankan dulu berurutan:\n"
            f"    python -m train_model.process_real_survey\n"
            f"    python -m train_model.merge_training_data\n"
            f"Kalau mode 'dummy_only': jalankan python -m train_model.generate_dummy_survey\n"
            f"Kalau mode 'real_only': jalankan python -m train_model.process_real_survey"
        )

    if not config.MENU_GO_FILE.exists():
        raise DataLoadError(
            f"'{config.MENU_GO_FILE}' tidak ditemukan meski folder induknya ada.\n"
            f"Mode training saat ini: '{config.TRAINING_MODE}'. Jalankan skrip "
            f"prasyarat yang sesuai (lihat pesan di atas kalau mode berbeda) "
            f"sebelum training - lihat PRD.md Bagian 4a untuk alur lengkapnya."
        )

    df = pd.read_csv(config.MENU_GO_FILE)
    logger.info(f"'{config.MENU_GO_FILE.name}' dimuat dari '{config.MENU_GO_FILE.parent.name}/': "
                f"{len(df)} baris, kolom: {df.columns.tolist()}")

    if "is_dummy" in df.columns and df["is_dummy"].any():
        logger.warning(
            "PERINGATAN: kolom 'is_dummy' terdeteksi TRUE di data label ini. "
            "Ini DATA SINTETIS dari generate_dummy_survey.py, bukan survei "
            "asli. Pastikan ini memang disengaja (STATIONOMICS_USE_DUMMY=1) "
            "dan JANGAN sampai file hasil (_DUMMY_TEST) terkirim ke tim WebGIS."
        )

    if len(df) == 0:
        raise DataLoadError(
            f"'{config.MENU_GO_FILE}' ada tapi kosong (0 baris). Training tidak "
            f"bisa jalan dengan data label kosong."
        )

    if len(df) <= 15 and config.TRAINING_MODE == "blended" and "sumber_data" not in df.columns:
        logger.warning(
            f"PERINGATAN: cuma {len(df)} baris di mode 'blended', dan kolom "
            f"'sumber_data' tidak ada - ini mencurigakan karena file gabungan "
            f"seharusnya sudah diaugmentasi lebih dari 15 titik. Cek apakah "
            f"merge_training_data.py sudah dijalankan dengan benar, atau file "
            f"yang terbaca ini ternyata real_processed.csv yang belum digabung."
        )

    return df
