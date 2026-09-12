"""
feature_engineering.py
=========================
Gabungkan semua sumber data mentah (lihat data_loader.py) jadi satu tabel
hex_features per hex_id. Ini langkah yang BELUM PERNAH dilakukan di
skrip manapun sebelumnya di proyek ini - seluruh skrip akuisisi data
menghasilkan file terpisah per sumber.

PENTING: fungsi-fungsi agregasi spasial (jarak ke simpul, hitung POI per
heksagon) di sini adalah IMPLEMENTASI PERTAMA untuk kebutuhan ini di
proyek - belum divalidasi terhadap definisi resmi di kamus data (mis.
jarak Euclidean di sini BUKAN isochrone jaringan jalan asli yang diminta
laporan Bagian 2.3). Ini keterbatasan yang harus didokumentasikan di
metodologi produk akhir, bukan disembunyikan.
"""

import geopandas as gpd
import numpy as np
import pandas as pd

from train_model import config, data_loader
from train_model.utils.logging_setup import get_logger

logger = get_logger(__name__)


def _to_metric_crs(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if gdf.crs is None:
        logger.warning(f"GeoDataFrame tidak punya CRS terdefinisi, asumsikan EPSG:4326")
        gdf = gdf.set_crs("EPSG:4326")
    return gdf.to_crs(config.CRS_METRIK)


def hitung_jarak_simpul_terdekat(grid: gpd.GeoDataFrame, simpul: gpd.GeoDataFrame) -> pd.Series:
    """D03 (jarak_simpul_m) - proksi Euclidean, BUKAN isochrone jaringan
    jalan asli. Dicatat sebagai keterbatasan di PRD.md Bagian 8 pengganti."""
    grid_m = _to_metric_crs(grid)
    simpul_m = _to_metric_crs(simpul)

    try:
        joined = gpd.sjoin_nearest(grid_m, simpul_m[["geometry"]], distance_col="jarak_simpul_m")
    except Exception as e:
        raise RuntimeError(
            f"Gagal hitung jarak ke simpul transit terdekat: {e}\n"
            f"Kemungkinan CRS tidak konsisten atau geometry invalid di salah satu "
            f"GeoDataFrame - cek gdf.is_valid.all() pada grid dan simpul sebelum panggil fungsi ini."
        ) from e

    # sjoin_nearest bisa hasilkan duplikat baris kalau ada >1 titik simpul
    # berjarak sama persis - ambil yang pertama per hex_id
    joined = joined.drop_duplicates(subset="hex_id", keep="first")
    return joined.set_index("hex_id")["jarak_simpul_m"]


def hitung_jumlah_poi_per_hex(grid: gpd.GeoDataFrame, poi: gpd.GeoDataFrame, nama_kolom: str) -> pd.Series:
    """Hitung berapa banyak titik POI (kompetitor/keramaian/dst) jatuh di
    tiap heksagon - dasar untuk C02, D09, dst."""
    grid_m = _to_metric_crs(grid)
    poi_m = _to_metric_crs(poi)

    try:
        joined = gpd.sjoin(poi_m, grid_m[["hex_id", "geometry"]], predicate="within")
    except Exception as e:
        raise RuntimeError(f"Gagal spatial join POI ke grid untuk '{nama_kolom}': {e}") from e

    hitung = joined.groupby("hex_id").size()
    hitung.name = nama_kolom
    return hitung


def build_hex_features() -> gpd.GeoDataFrame:
    """Fungsi utama - orkestrasi penggabungan semua sumber. Mengembalikan
    GeoDataFrame lengkap siap dipakai training maupun prediksi.

    Setiap langkah join dibungkus try/except yang menyebutkan LANGKAH MANA
    yang gagal, supaya kalau ada masalah di tengah pipeline panjang ini,
    tidak perlu menebak dari traceback generik.
    """
    logger.info("=== Mulai membangun hex_features ===")

    grid = data_loader.load_grid_base()
    hasil = grid.copy()

    langkah_selesai = []

    try:
        pop = data_loader.load_population()
        hasil = hasil.merge(pop, on="hex_id", how="left")
        langkah_selesai.append("populasi (D01, D02)")
    except data_loader.DataLoadError:
        raise  # biarkan pesan asli dari loader naik apa adanya, sudah jelas
    except Exception as e:
        raise RuntimeError(f"Gagal join data populasi ke grid: {e}") from e

    try:
        bangunan = data_loader.load_buildings()
        hasil = hasil.merge(bangunan, on="hex_id", how="left")
        langkah_selesai.append("bangunan (M01, M02)")
    except data_loader.DataLoadError:
        raise
    except Exception as e:
        raise RuntimeError(f"Gagal join data bangunan ke grid: {e}") from e

    try:
        risiko = data_loader.load_inarisk()
        hasil = hasil.merge(risiko, on="hex_id", how="left")
        langkah_selesai.append("risiko banjir (proksi L03)")
    except data_loader.DataLoadError:
        raise
    except Exception as e:
        raise RuntimeError(f"Gagal join data risiko banjir ke grid: {e}") from e

    try:
        simpul = data_loader.load_osm_points("simpul_transit")
        jarak = hitung_jarak_simpul_terdekat(hasil, simpul)
        hasil = hasil.merge(jarak.rename("jarak_simpul_m"), on="hex_id", how="left")
        langkah_selesai.append("jarak ke simpul transit (proksi D03)")
    except data_loader.DataLoadError:
        raise
    except Exception as e:
        raise RuntimeError(f"Gagal hitung fitur jarak simpul transit: {e}") from e

    try:
        kompetitor = data_loader.load_osm_points("kompetitor")
        jumlah_kompetitor = hitung_jumlah_poi_per_hex(hasil, kompetitor, "n_kompetitor")
        hasil = hasil.merge(jumlah_kompetitor, on="hex_id", how="left")
        hasil["n_kompetitor"] = hasil["n_kompetitor"].fillna(0)  # eksplisit: heksagon tanpa kompetitor = 0, ini valid (bukan missing data)
        langkah_selesai.append("jumlah kompetitor (dasar C01-C08)")
    except data_loader.DataLoadError:
        raise
    except Exception as e:
        raise RuntimeError(f"Gagal hitung fitur jumlah kompetitor: {e}") from e

    try:
        keramaian = data_loader.load_osm_points("generator_keramaian")
        jumlah_keramaian = hitung_jumlah_poi_per_hex(hasil, keramaian, "n_generator_keramaian")
        hasil = hasil.merge(jumlah_keramaian, on="hex_id", how="left")
        hasil["n_generator_keramaian"] = hasil["n_generator_keramaian"].fillna(0)
        langkah_selesai.append("jumlah generator keramaian (D09)")
    except data_loader.DataLoadError:
        raise
    except Exception as e:
        raise RuntimeError(f"Gagal hitung fitur generator keramaian: {e}") from e

    logger.info(f"hex_features selesai dibangun. Langkah berhasil: {langkah_selesai}")
    logger.info(f"Total kolom: {list(hasil.columns)}")
    logger.info(f"Total baris: {len(hasil)}")

    # RDTR dan POI terpadu SENGAJA belum di-join di sini - butuh taksonomi
    # 8 kelas induk (POI) dan identifikasi field kode zona (RDTR) yang
    # belum diverifikasi manual. Lihat DATA_SCHEMA.md. Panggil
    # data_loader.load_rdtr() dan load_poi_terpadu() secara terpisah kalau
    # sudah siap, jangan paksa masuk pipeline ini sebelum divalidasi.
    logger.warning(
        "RDTR (L01/L02) dan taksonomi POI terpadu (C03-C05) BELUM di-join "
        "ke hex_features - butuh langkah verifikasi manual tambahan yang "
        "belum dikerjakan (lihat DATA_SCHEMA.md). Model saat ini training "
        "TANPA kedua fitur ini."
    )

    return hasil


def save_hex_features(gdf: gpd.GeoDataFrame) -> None:
    config.HEX_FEATURES_PATH.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(config.HEX_FEATURES_PATH, driver="GeoJSON")
    logger.info(f"hex_features disimpan -> {config.HEX_FEATURES_PATH}")


if __name__ == "__main__":
    features = build_hex_features()
    save_hex_features(features)
