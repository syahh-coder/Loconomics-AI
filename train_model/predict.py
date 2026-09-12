"""
predict.py
============
Terapkan model terlatih (dari train_model.py) ke SEMUA heksagon yang
tidak punya data observasi asli. Heksagon dengan data survei asli TETAP
pakai nilai aslinya - model TIDAK PERNAH menimpa observasi asli dengan
prediksi (lihat PRD.md Bagian 6, kriteria penerimaan terakhir).

Output akhir: hex_features_final.geojson - file yang dikirim ke tim WebGIS
(lihat PRD.md Bagian 7).
"""

import geopandas as gpd
import joblib
import numpy as np
import pandas as pd

from train_model import config, data_loader
from train_model.feature_engineering import build_hex_features
from train_model.utils.logging_setup import get_logger

logger = get_logger(__name__)


def _tentukan_badge_keyakinan(n_titik_misi: int) -> str:
    if n_titik_misi >= config.AMBANG_KEYAKINAN_TINGGI:
        return "TINGGI"
    elif n_titik_misi >= config.AMBANG_KEYAKINAN_SEDANG:
        return "SEDANG"
    return "RENDAH"


def _load_model_bundle(path) -> dict:
    """Model disimpan bareng daftar fitur persis yang dipakai saat training
    (lihat train_model.py) - supaya prediksi TIDAK PERNAH salah pilih kolom
    fitur, walau hex_features sudah tercampur kolom hasil prediksi model lain."""
    if not path.exists():
        raise FileNotFoundError(
            f"Model tidak ditemukan di '{path}'. Jalankan train_model.py "
            f"dulu sebelum predict.py - lihat PRD.md untuk urutan pipeline."
        )
    try:
        bundle = joblib.load(path)
    except Exception as e:
        raise RuntimeError(
            f"Gagal load model dari '{path}': {e}\n"
            f"File mungkin korup atau dibuat dengan versi scikit-learn/joblib "
            f"yang tidak kompatibel dengan environment saat ini."
        ) from e

    if not isinstance(bundle, dict) or "model" not in bundle or "features" not in bundle:
        raise RuntimeError(
            f"'{path}' formatnya tidak sesuai yang diharapkan (dict dengan key "
            f"'model' dan 'features'). Kemungkinan file ini dibuat oleh versi "
            f"train_model.py yang lama sebelum bugfix - jalankan ulang training."
        )
    return bundle


def predict_dan_gabung(hex_features: gpd.GeoDataFrame, df_label: pd.DataFrame,
                         model_bundle: dict, kolom_target: str) -> pd.Series:
    """Prediksi HANYA untuk heksagon tanpa observasi asli. Heksagon dengan
    observasi asli mempertahankan nilai aslinya persis, tidak disentuh model.

    Kolom fitur yang dipakai adalah PERSIS yang tersimpan di model_bundle
    (hasil training) - BUKAN dihitung ulang dari hex_features saat ini,
    supaya tidak salah pilih kolom kalau hex_features sudah tercampur
    kolom hasil prediksi model lain (lihat main() - dua model dipanggil
    berurutan dan hex_features di-update di antaranya)."""
    model = model_bundle["model"]
    kolom_fitur_numerik = model_bundle["features"]

    kolom_hilang = [c for c in kolom_fitur_numerik if c not in hex_features.columns]
    if kolom_hilang:
        raise RuntimeError(
            f"Kolom fitur yang dipakai saat training tidak ditemukan di "
            f"hex_features saat prediksi untuk '{kolom_target}': {kolom_hilang}\n"
            f"Kemungkinan feature_engineering.py berubah setelah model ini "
            f"dilatih - training ulang diperlukan."
        )

    X_semua = hex_features[kolom_fitur_numerik].fillna(hex_features[kolom_fitur_numerik].median())

    try:
        prediksi_semua = model.predict(X_semua)
    except Exception as e:
        raise RuntimeError(
            f"Gagal prediksi untuk '{kolom_target}': {e}\n"
            f"Kolom fitur yang dipakai: {kolom_fitur_numerik}"
        ) from e

    hasil = pd.Series(prediksi_semua, index=hex_features["hex_id"], name=kolom_target)

    # Pengaman: kalau df_label ternyata masih ada hex_id duplikat (dari sumber
    # manapun), .update() di bawah akan crash dengan pesan pandas yang
    # membingungkan. Deteksi dan tangani eksplisit di sini dulu.
    dup_mask = df_label["hex_id"].duplicated(keep=False)
    if dup_mask.any():
        n_dup_hex = df_label.loc[dup_mask, "hex_id"].nunique()
        logger.warning(
            f"DITEMUKAN {dup_mask.sum()} baris dengan hex_id duplikat "
            f"({n_dup_hex} hex_id unik terpengaruh) di data label untuk "
            f"'{kolom_target}'. Ini seharusnya sudah diagregasi di langkah "
            f"sebelumnya (process_real_survey.py) - kalau masih muncul, ada "
            f"sumber data lain yang belum diagregasi dengan benar. "
            f"Diambil MEDIAN per hex_id sebagai pengaman sementara, TAPI "
            f"investigasi sumber duplikatnya - jangan andalkan pengaman ini terus-menerus."
        )
        observasi_asli = df_label.groupby("hex_id")[kolom_target].median()
    else:
        observasi_asli = df_label.set_index("hex_id")[kolom_target]

    n_ditimpa = observasi_asli.index.isin(hasil.index).sum()
    hasil.update(observasi_asli)
    logger.info(f"'{kolom_target}': {n_ditimpa} heksagon pakai nilai observasi asli, "
                f"{len(hasil) - n_ditimpa} heksagon pakai hasil prediksi model")

    return hasil


def main():
    if config.USE_DUMMY_DATA:
        logger.warning("=" * 70)
        logger.warning("MODE DUMMY AKTIF - prediksi ini pakai model yang dilatih dari data")
        logger.warning("SINTETIS. File output akan diberi akhiran '_DUMMY_TEST'.")
        logger.warning("JANGAN kirim file ini ke tim WebGIS sebagai hasil asli.")
        logger.warning("=" * 70)

    logger.info("=== Mulai prediksi ke seluruh heksagon ===")

    hex_features = build_hex_features()
    df_label = data_loader.load_survey_labels()

    hex_features["n_titik_misi"] = hex_features["hex_id"].map(
        df_label.groupby("hex_id").size()
    ).fillna(0).astype(int)
    hex_features["tingkat_keyakinan"] = hex_features["n_titik_misi"].apply(_tentukan_badge_keyakinan)
    hex_features["data_source"] = np.where(hex_features["n_titik_misi"] > 0, "observed", "predicted")

    for kolom_target, path_model in [
        (config.TARGET_SKOR_RAMAI, config.MODEL_SKOR_RAMAI_PATH),
        (config.TARGET_HARGA, config.MODEL_HARGA_PATH),
    ]:
        if kolom_target not in df_label.columns:
            logger.error(f"Kolom target '{kolom_target}' tidak ada di data label - skip prediksi ini.")
            continue

        model_bundle = _load_model_bundle(path_model)
        hasil_prediksi = predict_dan_gabung(hex_features, df_label, model_bundle, kolom_target)
        hex_features = hex_features.merge(
            hasil_prediksi.rename(kolom_target), on="hex_id", how="left"
        )

    hex_features.to_file(config.HEX_FEATURES_FINAL_PATH, driver="GeoJSON")
    logger.info(f"=== Selesai. File final untuk tim WebGIS -> {config.HEX_FEATURES_FINAL_PATH} ===")
    logger.info(
        "INGAT: sertakan hasil_validasi.json (R2/MAE) di pesan serah terima "
        "ke tim WebGIS - lihat PRD.md Bagian 7 soal apa yang wajib disebutkan."
    )


if __name__ == "__main__":
    main()