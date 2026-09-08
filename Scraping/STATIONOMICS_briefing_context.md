# Briefing Konteks — STATIONOMICS (MAPID WebGIS Competition 2026)

Dokumen ini adalah ringkasan status proyek untuk melanjutkan diskusi di percakapan baru.
Baca ini dulu sebelum menjawab apa pun, karena beberapa kesimpulan di sini mengoreksi
asumsi awal di laporan tim.

## 1. Ringkasan proyek

**STATIONOMICS** — platform WebGIS Decision Support System berbasis AI untuk membantu
pemilihan lokasi UMKM/ritel di sekitar kawasan transportasi massal darat, untuk **MAPID
WebGIS Competition 2026 (Maps That Think! — Mass Transportation Edition)**.

Tesis inti: mencari lokasi "hidden gem" — skor peluang ekonomi tinggi tapi prestise visual
kasat mata rendah (NJOP rendah, bukan jalan protokol, dsb) — karena lokasi seperti ini
diabaikan pasar padahal datanya menunjukkan potensi nyata.

**Peran saya (user) di tim:** AI engineer. Tugas utama: mengakuisisi data dari MAPID lebih
dulu, lalu melatih model ML untuk memprediksi/skor variabel yang cuma tersedia sebagian
di data misi MAPID (skor keramaian, intensitas transaksi, harga menu, nominal struk, harga
sewa, indeks churn), menggunakan fitur yang tersedia di mana-mana (OSM, WorldPop,
Buildings, NJOP, data transit) sebagai prediktor.

Tim sudah punya 2 laporan internal (dibuat sebelum ketentuan resmi dikonfirmasi):
- **Laporan Pendataan Data STATIONOMICS** — bedah 30+ kolom data misi MAPID, katalog
  sumber eksternal Tier-1/Tier-2, kamus 41 variabel analisis (D01-D12, B01-B09, C01-C08,
  P01-P06, L01-L03, M01-M03), rumus skor komposit (IPT, IAE, IKP, IBR → Skor Peluang →
  Hidden Gem Score).
- **Laporan Konsep AI dan Automation** — 14 fitur AI yang direncanakan (A1-A6 pipeline,
  B1-B5 produk, C1-C3 operasional tim), urutan prioritas kalau waktu terbatas.

**PENTING:** kedua laporan itu ditulis berdasarkan asumsi/interpretasi tim sendiri, BUKAN
salinan langsung ketentuan resmi panitia. Beberapa asumsinya sudah terkoreksi (lihat
Bagian 3).

## 2. Ketentuan resmi panitia (sudah dikonfirmasi dari dokumen resmi)

- Data yang boleh dipakai: **Data Community Maps** (activity), **Data Mission** (Properti
  Go, Struk Go, Menu Go), dan **Data Pendukung/Sekunder**. Minimal wajib pakai salah satu
  dari Community Maps atau Data Mission.
- **Wilayah studi TIDAK ditentukan panitia.** Data mission diambil "di berbagai kota di
  Indonesia" — sample yang ada bisa dari kota mana saja. Pemilihan wilayah (misal
  Jabodetabek) adalah keputusan tim, bukan syarat lomba.
- Data pendukung/sekunder harus **resmi, terbuka, relevan, dan sumbernya dicantumkan**
  — bisa dicari lewat menu **Import Data** di mode Editor GEO MAPID (MAPID Data
  Catalogue, mapid.co.id/data-catalog), atau sumber terbuka lain yang eksplisit disebut
  panitia: **InaRISK, BIG, KLHK**.
- "Open-source" di aturan lomba merujuk ke **tools analisis spasial** (disarankan pakai
  QGIS/GEE), BUKAN syarat lisensi data.
- Basemap **wajib MAPID MAPS**.
- AI **wajib** hadir sebagai interaksi langsung di interface WebGIS (bukan proses internal
  doang), dan disarankan menghasilkan output yang bisa dipetakan/dikaitkan ke lokasi.
- Setelah lolos **50 tim terkurasi**: wajib pakai data dasar panitia + ikut survey activities
  via MAPID APPS, dan dapat akses **API resmi (dengan dokumentasi dari tim MAPID)** untuk
  data yang lebih lengkap dari 15 titik sample. Sebelum lolos kurasi, yang tersedia baru
  4 sample CSV (15 titik/dataset, 50 untuk Activity).
- Dilarang: menyebarluaskan data mentah MAPID/partner ke pihak luar, memakai data
  Community Maps di luar kompetisi tanpa izin, mengambil data pribadi sensitif.

## 3. Temuan teknis dari profiling data sample (sudah dijalankan & dikonfirmasi)

Sudah download 4 sample CSV resmi dan diprofilekan pakai skrip Python (kolom, tipe data,
nilai unik, rentang lat/lon). Temuan:

- **Lokasi sample data tersebar**, bukan di satu wilayah: Menu Go → sekitar Depok; Struk
  Go, Properti Go, Activity Maps → Bandung. Ini **sesuai ketentuan resmi** (data nasional,
  bukan pelanggaran), tapi berarti sample 15 titik ini TIDAK representatif untuk wilayah
  studi manapun yang mau dipilih tim — jangan dipakai sebagai ground truth wilayah,
  cukup sebagai referensi format/struktur kolom.
- **Nama kolom di CSV asli beda dari dokumen ketentuan**, termasuk beberapa yang
  terpotong (Properti Go: "Kategori Properti" → `Kategori P`, "Foto Tampak Depan" →
  `Foto Tampa`, dst; ada juga kolom `Tanggal` dengan leading space). Wajib verifikasi
  manual per kolom sebelum nulis skrip, jangan asumsi nama kolom dari dokumen PDF.
- Struk Go py 12 kolom ekstra `(Lama)`/legacy kosong semua (aman diabaikan), plus 2 kolom
  berguna yang tidak disebut dokumen: `Kontributor` (nama surveyor — untuk normalisasi
  upaya survei) dan `ID data`.
- Activity Maps py 8 kolom (bukan 7): ada tambahan `medias_all`.
- Lat/lon di semua dataset **numerik lurus pakai titik desimal** (bukan pakai koma seperti
  yang awalnya dikhawatirkan untuk Struk Go).
- Dropdown Menu Go isinya deskripsi panjang + ada leading space, perlu dibersihkan
  sebelum dipetakan ke skor numerik (mis. "Sepi"/"Sedang"/"Ramai" → 1/2/3).

## 4. Aset yang sudah dimiliki tim

- 4 CSV sample resmi (sudah didownload & diprofilekan).
- Skrip Python `summarize_mapid_data.py` — profiling otomatis CSV MAPID (kolom, tipe,
  kategori, deteksi lat/lon bermasalah, format tanggal).
- **API key MAPID (Map Service API)** — HANYA untuk autentikasi basemap MAPID MAPS di
  frontend WebGIS (wajib dipakai per B.2), BUKAN untuk narik data POI/demografi.
- **Lisensi Personal SINI AI + SINI DATA** (aktif ±5 minggu dari sekarang) — kemungkinan
  besar UI klik-per-titik (belum terkonfirmasi ada API/export bulk atau tidak), berisi data
  demografi, kategori bisnis/POI, guna lahan, indikasi nilai lahan per titik. Sisi
  "Form (6)" di dokumentasi MAPID belum dicek — berpotensi jadi jalur API buat data
  mission dalam jumlah lebih besar dari sample, perlu dicek isinya.

## 5. Keputusan yang masih menggantung

- **Wilayah studi final**: tetap Jabodetabek (sesuai draft laporan awal tim) atau
  disesuaikan? Karena panitia tidak mensyaratkan wilayah tertentu, ini murni keputusan
  tim — pertimbangkan ketersediaan data eksternal (NJOP/RDTR Jakarta Satu itu khusus DKI)
  vs cakupan tema transportasi massal yang lebih kaya di Jabodetabek dibanding kota lain.
- Apakah section **"Form"** di dokumentasi API MAPID (`mapid.co.id/docs`) punya endpoint
  untuk narik Data Mission secara terprogram — belum dicek isinya.
- Apakah lisensi SINI AI/DATA Personal ada jalur export/API atau cuma UI manual.

## 6. Lampiran yang sebaiknya di-attach di percakapan lanjutan

1. `Laporan Pendataan Data STATIONOMICS` (PDF asli tim)
2. `Laporan Konsep AI dan Automation` (PDF asli tim)
3. `Ketentuan_Data___WebGIS__-_MAPID_WebGIS_Competition_2026.pdf` (dokumen resmi panitia
   — **rujukan tertinggi**, dokumen ini yang menang kalau ada konflik dengan laporan
   internal tim)
4. File `ringkasan_data_mapid.md` hasil profiling 4 CSV sample (kalau masih ada)
5. Dokumen briefing ini sendiri
