"""
summarize_mapid_data.py

Baca semua file .csv di satu direktori (data misi MAPID: Menu Go, Struk Go,
Properti Go, Activity/Community Maps) dan cetak ringkasan tiap dataset:
- jumlah baris & kolom
- nama kolom asli + tipe data pandas + jumlah non-null
- 3 baris contoh
- untuk kolom yang kelihatan kategorikal (dropdown): daftar nilai unik
- untuk kolom yang kelihatan lat/lon: cek tipe data & rentang nilai
  (flag kalau ternyata Text, bukan Angka -- sesuai catatan "HATI-HATI" di
  laporan Struk Go)
- untuk kolom yang kelihatan tanggal/waktu: tampilkan beberapa format unik
  yang muncul (biar ketahuan seberapa berantakan formatnya)

Hasil ringkasan dicetak ke terminal DAN disimpan sebagai
`ringkasan_data_mapid.md` di direktori yang sama, supaya bisa dibaca ulang
atau dilampirkan ke proposal/dibagikan ke tim tanpa perlu jalanin skrip lagi.

Cara pakai:
    python summarize_mapid_data.py /path/ke/folder/csv
    # atau, kalau CSV-nya ada di direktori yang sama dengan skrip ini:
    python summarize_mapid_data.py
"""

import sys
from pathlib import Path
from typing import Optional, List

import pandas as pd

# ----------------------------------------------------------------------
# Konfigurasi kecil -- silakan sesuaikan kalau nama kolommu beda
# ----------------------------------------------------------------------

# Ambang jumlah nilai unik supaya kolom dianggap "kategorikal" (dropdown)
MAX_UNIQUE_FOR_CATEGORICAL = 20

# Kata kunci untuk menebak kolom lat/lon secara otomatis
LAT_KEYWORDS = ["lat", "latitude", "lintang"]
LON_KEYWORDS = ["lon", "long", "longitude", "bujur"]

# Kata kunci untuk menebak kolom tanggal/waktu
DATE_KEYWORDS = ["tanggal", "date", "tgl"]
TIME_KEYWORDS = ["waktu", "time", "jam"]


def guess_column_role(col_name: str) -> Optional[str]:
    """Tebak peran kolom dari namanya (lat/lon/tanggal/waktu), case-insensitive."""
    name = col_name.lower()
    if any(k in name for k in LAT_KEYWORDS):
        return "lat"
    if any(k in name for k in LON_KEYWORDS):
        return "lon"
    if any(k in name for k in DATE_KEYWORDS):
        return "date"
    if any(k in name for k in TIME_KEYWORDS):
        return "time"
    return None


def check_lat_lon_column(series: pd.Series, role: str) -> List[str]:
    """Cek kesehatan kolom lat/lon: tipe data & rentang nilai."""
    notes = []
    is_numeric_dtype = pd.api.types.is_numeric_dtype(series)
    notes.append(f"  tipe pandas saat ini: {series.dtype} "
                 f"({'NUMERIK' if is_numeric_dtype else 'BUKAN NUMERIK -- perlu di-cast!'})")

    if not is_numeric_dtype:
        # Coba lihat pola: pakai koma atau titik sebagai desimal?
        sample_vals = series.dropna().astype(str).head(5).tolist()
        notes.append(f"  contoh nilai mentah: {sample_vals}")
        has_comma = series.dropna().astype(str).str.contains(",").any()
        if has_comma:
            notes.append("  -> terdeteksi ada koma di dalam nilainya, "
                          "kemungkinan dipakai sebagai pemisah desimal "
                          "(perlu .replace(',', '.') sebelum di-cast float)")

    # Kalau bisa dipaksa jadi numerik, cek rentangnya terhadap bbox Jabodetabek
    numeric_series = pd.to_numeric(
        series.astype(str).str.strip().str.replace(",", ".", regex=False),
        errors="coerce",
    )
    valid = numeric_series.dropna()
    if len(valid) > 0:
        notes.append(f"  rentang nilai (setelah dipaksa numerik): "
                      f"{valid.min():.5f} s/d {valid.max():.5f}")
        if role == "lat":
            out_of_bbox = ((valid < -6.95) | (valid > -5.95)).sum()
        else:  # lon
            out_of_bbox = ((valid < 106.30) | (valid > 107.10)).sum()
        if out_of_bbox > 0:
            notes.append(f"  PERINGATAN: {out_of_bbox} baris di luar bounding box "
                          f"Jabodetabek -- cek kemungkinan lat/lon tertukar atau salah ketik")
    n_failed = numeric_series.isna().sum() - series.isna().sum()
    if n_failed > 0:
        notes.append(f"  PERINGATAN: {n_failed} nilai gagal dikonversi ke angka sama sekali")

    return notes


def summarize_csv(path: Path) -> str:
    """Bangun ringkasan satu file CSV, dikembalikan sebagai string markdown."""
    lines = []
    lines.append(f"\n## {path.name}\n")

    try:
        df = pd.read_csv(path, dtype=str)  # baca semua sebagai string dulu,
                                            # biar kita yang kontrol deteksi tipe
    except Exception as e:
        lines.append(f"**GAGAL DIBACA:** `{e}`\n")
        return "\n".join(lines)

    lines.append(f"- Jumlah baris: **{len(df)}**")
    lines.append(f"- Jumlah kolom: **{len(df.columns)}**\n")

    lines.append("### Daftar kolom\n")
    lines.append("| # | Nama kolom (asli) | Non-null | % terisi | Contoh nilai |")
    lines.append("|---|---|---|---|---|")
    for i, col in enumerate(df.columns, start=1):
        non_null = df[col].notna().sum()
        pct = 100 * non_null / len(df) if len(df) else 0
        sample = df[col].dropna().iloc[0] if non_null > 0 else ""
        sample = str(sample)[:40].replace("|", "\\|")
        lines.append(f"| {i} | `{col}` | {non_null}/{len(df)} | {pct:.0f}% | {sample} |")

    lines.append("\n### 3 baris contoh\n")
    lines.append("```")
    lines.append(df.head(3).to_string())
    lines.append("```")

    # --- kolom kategorikal (dropdown) ---
    # Catatan: pada sample kecil (mis. 15 baris), kolom numerik (harga, lat/lon)
    # bisa ikut ketangkap ambang unik <= 20. Untuk itu kolom yang sebagian besar
    # nilainya bisa di-parse jadi angka, atau yang sudah kedeteksi role
    # lat/lon/date/time, tidak dimasukkan ke daftar kategorikal.
    lines.append("\n### Kolom yang kelihatan kategorikal / dropdown (nilai unik sedikit)\n")
    found_categorical = False
    for col in df.columns:
        if guess_column_role(col) is not None:
            continue  # sudah ditangani di bagian lat/lon/tanggal/waktu

        n_unique = df[col].nunique(dropna=True)
        if not (0 < n_unique <= MAX_UNIQUE_FOR_CATEGORICAL):
            continue

        non_null = df[col].dropna()
        numeric_parseable = pd.to_numeric(
            non_null.astype(str).str.strip().str.replace(",", ".", regex=False),
            errors="coerce",
        ).notna()
        frac_numeric = numeric_parseable.mean() if len(non_null) else 0
        if frac_numeric >= 0.8:
            continue  # mayoritas bisa jadi angka -> bukan dropdown, skip

        found_categorical = True
        values = sorted(df[col].dropna().unique().tolist())
        lines.append(f"- `{col}` ({n_unique} nilai unik): {values}")
    if not found_categorical:
        lines.append("(tidak ada kolom yang cocok kriteria kategorikal)")

    # --- kolom lat/lon/tanggal/waktu ---
    lines.append("\n### Pengecekan kolom lokasi & waktu\n")
    found_special = False
    for col in df.columns:
        role = guess_column_role(col)
        if role in ("lat", "lon"):
            found_special = True
            lines.append(f"\n**`{col}`** (terdeteksi sebagai kolom {role.upper()})")
            for note in check_lat_lon_column(df[col], role):
                lines.append(note)
        elif role in ("date", "time"):
            found_special = True
            unique_formats = df[col].dropna().astype(str).unique()[:8]
            lines.append(f"\n**`{col}`** (terdeteksi sebagai kolom {role.upper()})")
            lines.append(f"  contoh nilai unik (maks 8 ditampilkan): {list(unique_formats)}")
    if not found_special:
        lines.append("(tidak ada kolom yang cocok pola nama lat/lon/tanggal/waktu -- "
                      "cek manual kalau nama kolomnya tidak baku)")

    return "\n".join(lines)


def main():
    target_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    csv_files = sorted(target_dir.glob("*.csv"))

    if not csv_files:
        print(f"Tidak ada file .csv ditemukan di: {target_dir.resolve()}")
        sys.exit(1)

    print(f"Ditemukan {len(csv_files)} file CSV di {target_dir.resolve()}:")
    for f in csv_files:
        print(f"  - {f.name}")

    report_parts = [f"# Ringkasan Data Misi MAPID\n\nDitemukan {len(csv_files)} file CSV.\n"]
    for f in csv_files:
        summary = summarize_csv(f)
        print(summary)  # tampil juga di terminal biar bisa langsung dibaca
        report_parts.append(summary)

    out_path = target_dir / "ringkasan_data_mapid.md"
    out_path.write_text("\n".join(report_parts), encoding="utf-8")
    print(f"\n\nRingkasan lengkap disimpan ke: {out_path.resolve()}")


if __name__ == "__main__":
    main()