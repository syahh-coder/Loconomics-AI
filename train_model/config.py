"""
config.py
===========
Konfigurasi terpusat: semua path file dan konstanta dipakai bersama oleh
seluruh modul pipeline training. Jangan hardcode path di modul lain -
selalu import dari sini, supaya kalau struktur folder berubah cukup edit
satu tempat.
"""

import os
from pathlib import Path

# ── Root project ─────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRAPING_DIR = PROJECT_ROOT / "Scraping"
DATA_RAW = SCRAPING_DIR / "data_raw"
SCORING_DIR = PROJECT_ROOT / "scoring"

# ── File input (fitur prediktor - dari Scraping/data_raw) ────────────
GRID_BASE = DATA_RAW / "h3_grid_res9.geojson"
POP_FILE = DATA_RAW / "h3_grid_with_pop.geojson"
POP_AGE_FILE = DATA_RAW / "h3_grid_with_pop_age.geojson"
BUILDINGS_FILE = DATA_RAW / "open_buildings" / "h3_grid_with_buildings.geojson"
INARISK_FILE = DATA_RAW / "inarisk" / "h3_grid_with_risiko_banjir.geojson"
OSM_KOMPETITOR = DATA_RAW / "osm" / "kompetitor.geojson"
OSM_SIMPUL_TRANSIT = DATA_RAW / "osm" / "simpul_transit.geojson"
OSM_GENERATOR_KERAMAIAN = DATA_RAW / "osm" / "generator_keramaian.geojson"
POI_TERPADU = DATA_RAW / "poi_terpadu.geojson"
RDTR_FILE = DATA_RAW / "jakarta_satu" / "rdtr.geojson"

# ── File input (data survei ASLI - sample resmi, sebagian jatuh dalam bbox) ──
SURVEI_ASLI_SAMPLE_DIR = DATA_RAW / "survei_asli_sample"
MENU_GO_SAMPLE_ASLI = SURVEI_ASLI_SAMPLE_DIR / "menu_go_sample.csv"

# ── File output hasil pemrosesan data asli (process_real_survey.py) ──
SURVEI_DIR = DATA_RAW / "survei"
REAL_PROCESSED_FILE = SURVEI_DIR / "real_processed.csv"

# ── File output gabungan real + sintetis (merge_training_data.py) ────
TRAINING_DATA_GABUNGAN = SURVEI_DIR / "training_data_gabungan.csv"

# ── File dummy murni (infra-test only, TIDAK dipakai untuk training produksi) ──
SURVEI_DUMMY_DIR = DATA_RAW / "survei_dummy"
MENU_GO_FILE_DUMMY = SURVEI_DUMMY_DIR / "menu_go.csv"
STRUK_GO_FILE_DUMMY = SURVEI_DUMMY_DIR / "struk_go.csv"

# ── Mode training - menentukan file mana yang dibaca data_loader.py ──
# 'blended'    (DEFAULT): training_data_gabungan.csv - real + sintetis, INI YANG DIPAKAI PRODUKSI
# 'dummy_only': survei_dummy/menu_go.csv - murni sintetis, cuma untuk uji infra pipeline
# 'real_only' : real_processed.csv - murni 15 titik asli, kemungkinan gagal validasi
#               kecukupan data (di bawah MIN_TITIK_BERLABEL) - berguna sekali survei
#               lapangan 12 kawasan sudah selesai dan datanya cukup tanpa augmentasi
TRAINING_MODE = os.environ.get("STATIONOMICS_TRAINING_MODE", "blended")
if TRAINING_MODE not in ("blended", "dummy_only", "real_only"):
    raise ValueError(
        f"STATIONOMICS_TRAINING_MODE='{TRAINING_MODE}' tidak valid. "
        f"Harus salah satu dari: blended, dummy_only, real_only"
    )

MENU_GO_FILE = {
    "blended": TRAINING_DATA_GABUNGAN,
    "dummy_only": MENU_GO_FILE_DUMMY,
    "real_only": REAL_PROCESSED_FILE,
}[TRAINING_MODE]
STRUK_GO_FILE = STRUK_GO_FILE_DUMMY  # belum ada versi real/blended untuk Struk Go

# Dipakai logging_setup dan modul lain untuk validasi/warning kondisional
USE_DUMMY_DATA = (TRAINING_MODE == "dummy_only")

# ── File referensi tim scoring (opsional, dipakai cross-check) ──────
SCORING_METODOLOGI = SCORING_DIR / "metodologi.json"
SCORING_CAKUPAN = SCORING_DIR / "laporan_cakupan.csv"

# ── Output pipeline ───────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
HEX_FEATURES_PATH = DATA_RAW / "hex_features.geojson"

# Suffix output cuma untuk mode dummy_only (biar tidak ketuker file asli).
# Mode 'blended' dan 'real_only' pakai nama file NORMAL (tanpa suffix)
# karena keduanya boleh dianggap kandidat hasil produksi - bedanya sudah
# tercatat di kolom 'sumber_data' di dalam file itu sendiri, bukan di nama file.
_SUFFIX = "_DUMMY_TEST" if USE_DUMMY_DATA else ""
HEX_FEATURES_FINAL_PATH = DATA_RAW / f"hex_features_final{_SUFFIX}.geojson"
MODEL_SKOR_RAMAI_PATH = OUTPUT_DIR / f"model_skor_ramai{_SUFFIX}.joblib"
MODEL_HARGA_PATH = OUTPUT_DIR / f"model_harga{_SUFFIX}.joblib"
HASIL_VALIDASI_PATH = OUTPUT_DIR / f"hasil_validasi{_SUFFIX}.json"

# ── Konstanta wilayah studi (HARUS sinkron dengan Scraping/*.py) ────
BBOX = {"lon_min": 106.55, "lat_min": -6.45, "lon_max": 107.25, "lat_max": -5.95}
CRS_METRIK = "EPSG:32748"  # UTM 48S, dipakai untuk hitung jarak dalam meter

# ── Ambang tingkat keyakinan (sesuai laporan Bagian 7.1 Langkah 4) ──
AMBANG_KEYAKINAN_TINGGI = 30
AMBANG_KEYAKINAN_SEDANG = 10

# ── Kriteria minimum data untuk training (lihat PRD.md Bagian 6) ────
MIN_TITIK_BERLABEL = 30
MIN_KAWASAN_UNIK = 3

# ── Jumlah kawasan dummy yang digenerate (meniru rencana 12 kawasan asli) ──
N_KAWASAN_DUMMY = 12
TITIK_PER_KAWASAN_DUMMY = 40  # total ~480, sesuai rencana 360-600 titik di laporan

# ── Kolom target ──────────────────────────────────────────────────────
TARGET_SKOR_RAMAI = "skor_ramai_terkoreksi"  # D10
TARGET_HARGA = "harga_median_porsi"          # B07
KOLOM_KAWASAN_SURVEI = "kawasan_survei"      # dipakai untuk spatial k-fold grouping