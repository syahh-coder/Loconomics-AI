"""
merge_training_data.py
=========================
Gabungkan data real (hasil process_real_survey.py, 15 titik Menu Go)
dengan augmentasi sintetis untuk mencapai volume minimum training
(lihat PRD.md Bagian 6: minimal 30 titik, 3 kawasan unik).

DATA REAL SELALU DIPERTAHANKAN - tidak pernah dibuang atau ditimpa oleh
augmentasi. Kolom 'sumber_data' ('real' atau 'sintetis') dipertahankan
di output supaya distribusinya bisa dicek kapan saja.

CARA PAKAI:
    python -m train_model.process_real_survey     # hasilkan real_processed.csv dulu
    python -m train_model.merge_training_data      # baru gabungkan
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from train_model import config
from train_model.data_loader import DataLoadError
from train_model.feature_engineering import build_hex_features
from train_model.generate_dummy_survey import buatkan_label_sintetis, RANDOM_SEED
from train_model.utils.logging_setup import get_logger

logger = get_logger(__name__)


def load_real_processed() -> pd.DataFrame:
    if not config.REAL_PROCESSED_FILE.exists():
        raise DataLoadError(
            f"'{config.REAL_PROCESSED_FILE}' tidak ditemukan. Jalankan dulu:\n"
            f"    python -m train_model.process_real_survey"
        )
    df = pd.read_csv(config.REAL_PROCESSED_FILE)
    if len(df) == 0:
        raise DataLoadError(f"'{config.REAL_PROCESSED_FILE}' kosong (0 baris).")
    logger.info(f"Data real dimuat: {len(df)} titik")
    return df


def buatkan_kawasan_untuk_semua(hex_features, n_kawasan: int) -> pd.Series:
    """Satu skema clustering dipakai untuk SEMUA heksagon (baik yang nanti
    kepakai data real maupun sintetis) - supaya pengelompokan kawasan
    konsisten, bukan real dan sintetis punya skema kawasan yang beda sendiri-sendiri."""
    koordinat = hex_features[["centroid_lat", "centroid_lon"]].values
    km = KMeans(n_clusters=n_kawasan, random_state=RANDOM_SEED, n_init=10)
    label = km.fit_predict(koordinat)
    return pd.Series([f"kawasan_{i:02d}" for i in label], index=hex_features.index)


def main():
    logger.info("=== Menggabungkan data real + augmentasi sintetis ===")

    df_real = load_real_processed()
    hex_features = build_hex_features()

    hex_features["kawasan"] = buatkan_kawasan_untuk_semua(hex_features, config.N_KAWASAN_DUMMY)

    kawasan_per_hex = hex_features.set_index("hex_id")["kawasan"]
    df_real[config.KOLOM_KAWASAN_SURVEI] = df_real["hex_id"].map(kawasan_per_hex)

    n_tanpa_kawasan = df_real[config.KOLOM_KAWASAN_SURVEI].isna().sum()
    if n_tanpa_kawasan > 0:
        logger.warning(
            f"{n_tanpa_kawasan} titik real punya hex_id yang TIDAK ADA di "
            f"hex_features (grid mungkin sudah berubah sejak real_processed.csv "
            f"dibuat) - baris ini dibuang."
        )
        df_real = df_real.dropna(subset=[config.KOLOM_KAWASAN_SURVEI])

    hex_id_terpakai_real = set(df_real["hex_id"])
    n_target_total = max(config.MIN_TITIK_BERLABEL, config.N_KAWASAN_DUMMY * config.TITIK_PER_KAWASAN_DUMMY)
    n_sintetis_dibutuhkan = max(0, n_target_total - len(df_real))

    logger.info(f"Data real: {len(df_real)} titik. Target total: {n_target_total}. "
                f"Augmentasi sintetis dibutuhkan: {n_sintetis_dibutuhkan} titik")

    if n_sintetis_dibutuhkan == 0:
        logger.info("Data real saja sudah cukup, tidak perlu augmentasi sintetis.")
        hasil = df_real
    else:
        kandidat = hex_features[~hex_features["hex_id"].isin(hex_id_terpakai_real)].copy()
        if len(kandidat) < n_sintetis_dibutuhkan:
            logger.warning(
                f"Heksagon kandidat augmentasi ({len(kandidat)}) lebih sedikit dari "
                f"kebutuhan ({n_sintetis_dibutuhkan}) - pakai semua yang tersedia."
            )
            n_sintetis_dibutuhkan = len(kandidat)

        sampel_sintetis = kandidat.sample(n=n_sintetis_dibutuhkan, random_state=RANDOM_SEED)
        label_sintetis = buatkan_label_sintetis(sampel_sintetis)
        label_sintetis[config.KOLOM_KAWASAN_SURVEI] = sampel_sintetis["kawasan"].values
        label_sintetis["sumber_data"] = "sintetis"
        label_sintetis["is_dummy"] = True

        hasil = pd.concat([df_real, label_sintetis], ignore_index=True)

    n_real = (hasil["sumber_data"] == "real").sum()
    n_sintetis = (hasil["sumber_data"] == "sintetis").sum()
    n_kawasan_final = hasil[config.KOLOM_KAWASAN_SURVEI].nunique()

    logger.info(f"\n{'='*70}")
    logger.info(f"HASIL GABUNGAN: {len(hasil)} titik total")
    logger.info(f"  - Real  : {n_real} ({100*n_real/len(hasil):.1f}%)")
    logger.info(f"  - Sintetis: {n_sintetis} ({100*n_sintetis/len(hasil):.1f}%)")
    logger.info(f"  - Kawasan unik: {n_kawasan_final}")
    logger.info(f"{'='*70}")
    logger.info(
        "INGAT: proporsi real vs sintetis di atas WAJIB disebutkan di pesan "
        "serah terima ke tim WebGIS dan di halaman Metodologi produk - "
        "lihat PRD.md Bagian 4a dan Bagian 7."
    )

    config.SURVEI_DIR.mkdir(parents=True, exist_ok=True)
    hasil.to_csv(config.TRAINING_DATA_GABUNGAN, index=False)
    logger.info(f"Disimpan -> {config.TRAINING_DATA_GABUNGAN}")


if __name__ == "__main__":
    main()
