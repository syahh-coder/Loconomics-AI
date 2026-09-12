"""
train_model.py
=================
Training model Gradient Boosting untuk memprediksi D10 (skor_ramai_terkoreksi)
dan B07 (harga_median_porsi) di heksagon yang tidak disurvei.

VALIDASI KETERSEDIAAN DATA DIJALANKAN DI AWAL, SEBELUM TRAINING APAPUN.
Kalau data tidak cukup, skrip BERHENTI dengan pesan jelas (lihat
_validasi_kecukupan_data) - TIDAK training dengan hasil yang tidak bisa
dipercaya. Ini bukan opsional, lihat PRD.md Bagian 2 dan Bagian 6.

Validasi pakai spatial k-fold (group by kawasan survei), BUKAN random
k-fold - lihat PRD.md Bagian 4 untuk alasannya.
"""

import json

import geopandas as gpd
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold

from train_model import config, data_loader
from train_model.feature_engineering import build_hex_features
from train_model.utils.logging_setup import get_logger

logger = get_logger(__name__)


class InsufficientDataError(Exception):
    """Dilempar kalau data label tidak cukup untuk training yang bisa
    dipercaya. Ini BUKAN bug - ini pipeline bekerja sesuai desain dengan
    menolak training yang tidak valid. Lihat PRD.md Bagian 2 dan 6."""
    pass


def _validasi_kecukupan_data(df_label: pd.DataFrame) -> None:
    n_titik = len(df_label)
    if n_titik < config.MIN_TITIK_BERLABEL:
        raise InsufficientDataError(
            f"Cuma {n_titik} titik berlabel ditemukan, minimum yang "
            f"disyaratkan adalah {config.MIN_TITIK_BERLABEL} (lihat PRD.md "
            f"Bagian 6).\n"
            f"Training DIBATALKAN. Ini bukan error teknis - datanya memang "
            f"belum cukup untuk hasil yang bisa dipercaya. Lanjutkan survei "
            f"lapangan 12 kawasan (rencana: 360-600 titik) sebelum training "
            f"ulang."
        )

    if config.KOLOM_KAWASAN_SURVEI not in df_label.columns:
        raise InsufficientDataError(
            f"Kolom '{config.KOLOM_KAWASAN_SURVEI}' tidak ada di data label. "
            f"Kolom ini WAJIB ada untuk spatial k-fold grouping (grup per "
            f"kawasan survei, bukan per baris) - lihat PRD.md Bagian 4. "
            f"Kolom yang tersedia: {df_label.columns.tolist()}. "
            f"Tambahkan kolom ini ke data survei sebelum training (tiap "
            f"baris perlu ditandai kawasan survei mana asalnya)."
        )

    n_kawasan = df_label[config.KOLOM_KAWASAN_SURVEI].nunique()
    if n_kawasan < config.MIN_KAWASAN_UNIK:
        raise InsufficientDataError(
            f"Cuma {n_kawasan} kawasan survei unik ditemukan, minimum "
            f"{config.MIN_KAWASAN_UNIK} diperlukan supaya spatial k-fold "
            f"punya cukup grup untuk dipisah train/test tanpa kebocoran "
            f"spasial (lihat PRD.md Bagian 4).\n"
            f"Kawasan yang ada saat ini: {df_label[config.KOLOM_KAWASAN_SURVEI].unique().tolist()}"
        )

    logger.info(f"Validasi kecukupan data LOLOS: {n_titik} titik, {n_kawasan} kawasan unik")


def _siapkan_fitur_dan_label(hex_features: gpd.GeoDataFrame, df_label: pd.DataFrame,
                               kolom_target: str) -> tuple:
    """Gabungkan hex_features (prediktor) dengan df_label (target),
    pisahkan jadi X (fitur numerik), y (target), groups (kawasan survei)."""
    merged = hex_features.merge(df_label[["hex_id", kolom_target, config.KOLOM_KAWASAN_SURVEI]],
                                  on="hex_id", how="inner")

    if len(merged) == 0:
        raise InsufficientDataError(
            f"Setelah join hex_features dengan data label berdasarkan 'hex_id', "
            f"hasilnya 0 baris. Ini berarti TIDAK ADA hex_id yang cocok antara "
            f"grid dan data survei - kemungkinan data survei belum di-spatial-join "
            f"ke hex_id yang benar, atau lokasi survei di luar bbox wilayah studi. "
            f"Cek koordinat data survei terhadap BBOX di config.py: {config.BBOX}"
        )

    kolom_fitur = [c for c in hex_features.columns if c not in ("hex_id", "geometry")]
    kolom_fitur_numerik = merged[kolom_fitur].select_dtypes(include=[np.number]).columns.tolist()

    if not kolom_fitur_numerik:
        raise RuntimeError(
            "Tidak ada kolom fitur numerik ditemukan di hex_features. "
            "Cek apakah feature_engineering.py berhasil menghasilkan kolom "
            "prediktor - kemungkinan semua kolom bertipe non-numerik (string/object)."
        )

    logger.info(f"Fitur yang dipakai training: {kolom_fitur_numerik}")

    X = merged[kolom_fitur_numerik]
    y = merged[kolom_target]
    groups = merged[config.KOLOM_KAWASAN_SURVEI]

    mask_valid = y.notna()
    n_dibuang = (~mask_valid).sum()
    if n_dibuang > 0:
        logger.warning(f"{n_dibuang} baris dibuang karena target '{kolom_target}' NaN")

    return X[mask_valid], y[mask_valid], groups[mask_valid]


def train_dengan_spatial_kfold(X: pd.DataFrame, y: pd.Series, groups: pd.Series,
                                  nama_model: str) -> tuple:
    """Latih model dengan GroupKFold (grup = kawasan survei). Mengembalikan
    (model_final_dilatih_semua_data, hasil_metrik_per_fold)."""
    n_splits = min(config.MIN_KAWASAN_UNIK, groups.nunique())
    gkf = GroupKFold(n_splits=n_splits)

    hasil_per_fold = []
    for fold_idx, (train_idx, test_idx) in enumerate(gkf.split(X, y, groups)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        X_train_filled = X_train.fillna(X_train.median())
        X_test_filled = X_test.fillna(X_train.median())  # pakai median TRAIN, bukan test

        model_fold = GradientBoostingRegressor(random_state=42)
        try:
            model_fold.fit(X_train_filled, y_train)
        except Exception as e:
            raise RuntimeError(
                f"Gagal training model '{nama_model}' pada fold {fold_idx}: {e}\n"
                f"Ukuran X_train: {X_train_filled.shape}, y_train: {y_train.shape}. "
                f"Cek apakah ada nilai infinite atau tipe data tidak sesuai."
            ) from e

        y_pred = model_fold.predict(X_test_filled)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        kawasan_test = groups.iloc[test_idx].unique().tolist()

        logger.info(f"[{nama_model}] Fold {fold_idx} (test kawasan={kawasan_test}): "
                    f"R2={r2:.3f}, MAE={mae:.3f}")
        hasil_per_fold.append({
            "fold": fold_idx,
            "kawasan_test": kawasan_test,
            "r2": r2,
            "mae": mae,
            "n_test": len(test_idx),
        })

    X_filled = X.fillna(X.median())
    model_final = GradientBoostingRegressor(random_state=42)
    model_final.fit(X_filled, y)

    r2_rata = float(np.mean([h["r2"] for h in hasil_per_fold]))
    mae_rata = float(np.mean([h["mae"] for h in hasil_per_fold]))
    logger.info(f"[{nama_model}] Rata-rata cross-validation: R2={r2_rata:.3f}, MAE={mae_rata:.3f}")

    if r2_rata < 0:
        logger.warning(
            f"[{nama_model}] R2 rata-rata NEGATIF ({r2_rata:.3f}) - model ini "
            f"lebih buruk daripada sekadar menebak rata-rata. JANGAN dipakai "
            f"untuk prediksi produksi meski file model tetap disimpan untuk "
            f"referensi/debugging."
        )

    return model_final, {"per_fold": hasil_per_fold, "r2_rata": r2_rata, "mae_rata": mae_rata}


def main():
    if config.USE_DUMMY_DATA:
        logger.warning("=" * 70)
        logger.warning("MODE DUMMY AKTIF - hasil training ini pakai data SINTETIS,")
        logger.warning("BUKAN data survei asli. TIDAK VALID untuk produksi/submission.")
        logger.warning(f"Output akan disimpan dengan akhiran '_DUMMY_TEST' untuk mencegah")
        logger.warning("tertukar dengan hasil asli.")
        logger.warning("=" * 70)

    logger.info("=== Mulai pipeline training ===")

    logger.info("Langkah 1/4: memuat data label survei...")
    df_label = data_loader.load_survey_labels()

    logger.info("Langkah 2/4: validasi kecukupan data...")
    _validasi_kecukupan_data(df_label)

    logger.info("Langkah 3/4: membangun hex_features...")
    hex_features = build_hex_features()

    logger.info("Langkah 4/4: training kedua model...")
    hasil_semua = {}
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for kolom_target, path_model, nama in [
        (config.TARGET_SKOR_RAMAI, config.MODEL_SKOR_RAMAI_PATH, "skor_ramai"),
        (config.TARGET_HARGA, config.MODEL_HARGA_PATH, "harga"),
    ]:
        if kolom_target not in df_label.columns:
            logger.error(
                f"Kolom target '{kolom_target}' tidak ada di data label survei. "
                f"Skip training model '{nama}'. Kolom yang tersedia: {df_label.columns.tolist()}"
            )
            continue

        X, y, groups = _siapkan_fitur_dan_label(hex_features, df_label, kolom_target)
        model, hasil = train_dengan_spatial_kfold(X, y, groups, nama)

        joblib.dump({"model": model, "features": list(X.columns)}, path_model)
        logger.info(f"Model '{nama}' + daftar fitur ({len(X.columns)} kolom) disimpan -> {path_model}")
        hasil_semua[nama] = hasil

    with open(config.HASIL_VALIDASI_PATH, "w", encoding="utf-8") as f:
        json.dump(hasil_semua, f, indent=2, ensure_ascii=False)
    logger.info(f"Hasil validasi disimpan -> {config.HASIL_VALIDASI_PATH}")

    logger.info("=== Training selesai ===")


if __name__ == "__main__":
    main()