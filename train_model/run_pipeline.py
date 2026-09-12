"""
run_pipeline.py
==================
Entrypoint tunggal untuk TAHAP TRAINING+PREDIKSI SAJA. Jalankan skrip
prasyarat berikut secara manual dulu (urutan penting):

    1. python -m train_model.process_real_survey     # proses 15 titik Menu Go real
    2. python -m train_model.merge_training_data      # gabung real + augmentasi sintetis
    3. python -m train_model.run_pipeline             # baru training + prediksi (skrip ini)

(Atau kalau mode training bukan 'blended', lihat config.py TRAINING_MODE
dan PRD.md Bagian 4a untuk alur yang sesuai - mis. 'dummy_only' cuma butuh
generate_dummy_survey.py, 'real_only' cuma butuh process_real_survey.py)

Skrip ini sendiri menjalankan:
  1. feature_engineering.build_hex_features() + simpan
  2. train_model.main() - termasuk validasi kecukupan data di dalamnya
  3. predict.main() - cuma jalan kalau training sukses

Kalau training gagal karena data belum cukup (InsufficientDataError),
skrip berhenti DI SINI dengan pesan jelas - TIDAK lanjut ke predict.py
dengan model yang tidak ada/tidak valid.
"""

import sys

from train_model import feature_engineering, config
from train_model.train_model import InsufficientDataError
from train_model.data_loader import DataLoadError
from train_model.utils.logging_setup import get_logger

logger = get_logger(__name__)


def main():
    if config.TRAINING_MODE == "dummy_only":
        logger.warning("#" * 70)
        logger.warning("# MODE 'dummy_only' AKTIF")
        logger.warning("# Seluruh pipeline ini jalan dengan DATA SINTETIS MURNI.")
        logger.warning("#" * 70)
    elif config.TRAINING_MODE == "blended":
        logger.info("Mode training: 'blended' (default) - data real Menu Go "
                     "digabung dengan augmentasi sintetis. Pastikan sudah "
                     "jalankan process_real_survey.py + merge_training_data.py.")
    elif config.TRAINING_MODE == "real_only":
        logger.info("Mode training: 'real_only' - HANYA 15 titik Menu Go real, "
                     "TANPA augmentasi. Kemungkinan besar gagal validasi kecukupan "
                     "data (lihat PRD.md Bagian 6) kecuali survei 12 kawasan sudah selesai.")

    try:
        logger.info(">>> TAHAP 1: Feature Engineering")
        features = feature_engineering.build_hex_features()
        feature_engineering.save_hex_features(features)
    except DataLoadError as e:
        logger.error(f"Feature engineering GAGAL - data prasyarat belum lengkap:\n{e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Feature engineering GAGAL karena error tak terduga: {e}")
        raise

    try:
        logger.info(">>> TAHAP 2: Training Model")
        from train_model import train_model
        train_model.main()
    except InsufficientDataError as e:
        logger.error(
            f"Training DIBATALKAN - data label belum cukup:\n{e}\n"
            f"Pipeline berhenti di sini. predict.py TIDAK dijalankan karena "
            f"belum ada model yang valid untuk dipakai."
        )
        sys.exit(1)
    except DataLoadError as e:
        logger.error(f"Training GAGAL - data prasyarat belum lengkap:\n{e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Training GAGAL karena error tak terduga: {e}")
        raise

    try:
        logger.info(">>> TAHAP 3: Prediksi ke Seluruh Heksagon")
        from train_model import predict
        predict.main()
    except Exception as e:
        logger.error(f"Prediksi GAGAL karena error tak terduga: {e}")
        raise

    logger.info(">>> PIPELINE SELESAI - lihat PRD.md Bagian 7 untuk langkah serah terima ke tim WebGIS")


if __name__ == "__main__":
    main()
