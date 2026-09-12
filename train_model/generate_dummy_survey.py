"""
generate_dummy_survey.py
===========================
Generate data survei SINTETIS untuk menguji pipeline training end-to-end
SEBELUM data survei lapangan asli tersedia. INI BUKAN DATA ASLI - jangan
pernah dikirim ke tim WebGIS atau dipakai sebagai dasar keputusan produk.

CARA PAKAI:
    python -m train_model.generate_dummy_survey

Output ditulis ke folder TERPISAH (data_raw/survei_dummy/), BUKAN ke
data_raw/survei/ tempat data asli seharusnya ada - supaya tidak mungkin
tertukar secara tidak sengaja.

PENDEKATAN: label sintetis dibuat sebagai FUNGSI dari fitur asli (populasi,
jarak ke simpul transit, dst) DITAMBAH noise acak - bukan angka random
murni. Tujuannya supaya kalau pipeline training dijalankan dengan data ini,
hasilnya menunjukkan R² yang masuk akal (bukan mendekati nol karena label
memang tidak berhubungan apa pun dengan fitur) - ini yang membuktikan KODE
pipeline bekerja benar, bukan cuma "tidak crash".

Kawasan survei sintetis dibuat dengan clustering (KMeans) pada centroid
heksagon asli - meniru struktur "12 kawasan" yang direncanakan tim,
supaya spatial k-fold di train_model.py punya grup yang realistis untuk
diuji, bukan grup yang asal random.
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from sklearn.cluster import KMeans

from train_model import config
from train_model.feature_engineering import build_hex_features
from train_model.utils.logging_setup import get_logger

logger = get_logger(__name__)

RANDOM_SEED = 42


def _cek_mode_dummy_aktif():
    """Generator ini SELALU boleh jalan generate filenya (menulis ke folder
    dummy terpisah tidak berbahaya), tapi kita ingatkan user kalau
    STATIONOMICS_USE_DUMMY belum di-set - berarti train_model.py belum
    akan otomatis PAKAI file yang baru dibuat ini."""
    if not config.USE_DUMMY_DATA:
        logger.warning(
            "Environment variable STATIONOMICS_USE_DUMMY belum di-set ke '1'. "
            "File dummy AKAN TETAP dibuat, tapi train_model.py TIDAK AKAN "
            "otomatis memakainya sampai kamu set:\n"
            "  Windows (cmd):  set STATIONOMICS_USE_DUMMY=1\n"
            "  Windows (powershell):  $env:STATIONOMICS_USE_DUMMY=\"1\"\n"
            "  lalu jalankan ulang python -m train_model.run_pipeline di terminal yang sama."
        )


def buatkan_kawasan_sintetis(hex_features: gpd.GeoDataFrame, n_kawasan: int) -> pd.Series:
    """Cluster heksagon jadi n_kawasan grup berdasarkan lokasi geografis -
    meniru pengelompokan kawasan survei asli, bukan random grouping yang
    tidak realistis secara spasial."""
    if "centroid_lat" not in hex_features.columns or "centroid_lon" not in hex_features.columns:
        raise RuntimeError(
            "Kolom 'centroid_lat'/'centroid_lon' tidak ada di hex_features - "
            "tidak bisa membuat kawasan sintetis berbasis lokasi. Cek "
            "generate_h3_grid.py apakah kolom ini masih dihasilkan."
        )

    koordinat = hex_features[["centroid_lat", "centroid_lon"]].values
    km = KMeans(n_clusters=n_kawasan, random_state=RANDOM_SEED, n_init=10)
    label_cluster = km.fit_predict(koordinat)
    nama_kawasan = pd.Series(
        [f"kawasan_dummy_{i:02d}" for i in label_cluster],
        index=hex_features.index,
    )
    logger.info(f"{n_kawasan} kawasan sintetis dibuat via KMeans pada centroid heksagon")
    return nama_kawasan


def buatkan_label_sintetis(hex_features: gpd.GeoDataFrame) -> pd.DataFrame:
    """Bangun skor_ramai_terkoreksi dan harga_median_porsi sintetis sebagai
    fungsi fitur asli + noise. Formulanya SEMBARANG (tidak berdasar riset),
    cuma dirancang supaya ada korelasi yang bisa dipelajari model - jangan
    dikira formula ini merepresentasikan hubungan ekonomi yang valid."""
    np.random.seed(RANDOM_SEED)
    n = len(hex_features)

    pop = hex_features.get("pop_100m", pd.Series(np.zeros(n))).fillna(0)
    jarak = hex_features.get("jarak_simpul_m", pd.Series(np.full(n, 1000.0))).fillna(1000.0)
    n_kompetitor = hex_features.get("n_kompetitor", pd.Series(np.zeros(n))).fillna(0)

    pop_norm = (pop - pop.min()) / (pop.max() - pop.min() + 1e-9)
    jarak_norm = 1 - (jarak - jarak.min()) / (jarak.max() - jarak.min() + 1e-9)  # dekat = tinggi

    skor_ramai = 1 + 2 * pop_norm + 1.5 * jarak_norm + np.random.normal(0, 0.3, n)
    skor_ramai = np.clip(skor_ramai, 1, 3)  # sesuai skala asli Sepi=1/Sedang=2/Ramai=3

    harga = 15000 + 20000 * pop_norm - 500 * n_kompetitor + np.random.normal(0, 3000, n)
    harga = np.clip(harga, 5000, 100000)

    return pd.DataFrame({
        "hex_id": hex_features["hex_id"].values,
        config.TARGET_SKOR_RAMAI: skor_ramai,
        config.TARGET_HARGA: harga,
    })


def main():
    _cek_mode_dummy_aktif()

    logger.info("Membangun hex_features (fitur asli) sebagai basis label sintetis...")
    hex_features = build_hex_features()

    logger.info(f"Membuat {config.N_KAWASAN_DUMMY} kawasan sintetis...")
    hex_features["kawasan_sintetis"] = buatkan_kawasan_sintetis(hex_features, config.N_KAWASAN_DUMMY)

    n_total = config.N_KAWASAN_DUMMY * config.TITIK_PER_KAWASAN_DUMMY
    if n_total > len(hex_features):
        logger.warning(
            f"Diminta {n_total} titik survei dummy, tapi cuma ada "
            f"{len(hex_features)} heksagon total. Ambil semua heksagon yang ada."
        )
        sampel = hex_features
    else:
        sampel = hex_features.groupby("kawasan_sintetis", group_keys=False).apply(
            lambda g: g.sample(min(len(g), config.TITIK_PER_KAWASAN_DUMMY), random_state=RANDOM_SEED)
        )

    logger.info(f"Sampel {len(sampel)} titik dipilih sebagai 'lokasi survei' sintetis")

    label_sintetis = buatkan_label_sintetis(sampel)
    label_sintetis[config.KOLOM_KAWASAN_SURVEI] = sampel["kawasan_sintetis"].values
    label_sintetis["is_dummy"] = True  # penanda eksplisit di dalam data, bukan cuma nama file

    config.SURVEI_DUMMY_DIR.mkdir(parents=True, exist_ok=True)

    # menu_go dummy - berisi skor_ramai_terkoreksi dan harga_median_porsi
    label_sintetis.to_csv(config.MENU_GO_FILE_DUMMY, index=False)
    logger.info(f"Data dummy Menu Go disimpan -> {config.MENU_GO_FILE_DUMMY} "
                f"({len(label_sintetis)} baris)")

    # struk_go dummy - kolom lebih sedikit, dibuat minimal supaya loader lain
    # yang mungkin butuh file ini tidak crash karena file tidak ada
    struk_dummy = label_sintetis[["hex_id", config.KOLOM_KAWASAN_SURVEI, "is_dummy"]].copy()
    struk_dummy.to_csv(config.STRUK_GO_FILE_DUMMY, index=False)
    logger.info(f"Data dummy Struk Go (minimal) disimpan -> {config.STRUK_GO_FILE_DUMMY}")

    # File peringatan yang taruh di folder yang sama, sulit diabaikan
    peringatan_path = config.SURVEI_DUMMY_DIR / "_PERINGATAN_INI_DATA_PALSU.txt"
    with open(peringatan_path, "w", encoding="utf-8") as f:
        f.write(
            "DATA DI FOLDER INI ADALAH DATA SINTETIS/DUMMY UNTUK PENGUJIAN PIPELINE.\n"
            "BUKAN HASIL SURVEI LAPANGAN ASLI.\n\n"
            "JANGAN dikirim ke tim WebGIS, JANGAN dipakai untuk keputusan produk,\n"
            "JANGAN dicampur dengan data survei asli tanpa memisahkan sumbernya.\n\n"
            f"Dibuat oleh generate_dummy_survey.py, seed={RANDOM_SEED}.\n"
            "Formula label: fungsi sederhana dari populasi + jarak simpul + noise,\n"
            "TIDAK merepresentasikan hubungan ekonomi nyata apa pun.\n"
        )

    logger.info(f"\n{'='*70}\n"
                f"SELESAI. Data dummy ada di: {config.SURVEI_DUMMY_DIR}\n"
                f"Untuk pipeline MEMAKAI data ini, set environment variable:\n"
                f"  Windows (cmd):        set STATIONOMICS_USE_DUMMY=1\n"
                f"  Windows (powershell): $env:STATIONOMICS_USE_DUMMY=\"1\"\n"
                f"lalu jalankan: python -m train_model.run_pipeline\n"
                f"(di terminal/session yang SAMA setelah set environment variable)\n"
                f"{'='*70}")


if __name__ == "__main__":
    main()
