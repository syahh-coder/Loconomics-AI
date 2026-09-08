# Ringkasan Data Misi MAPID

Ditemukan 4 file CSV.


## Sample_Activity_WebGIS2026.csv

- Jumlah baris: **50**
- Jumlah kolom: **8**

### Daftar kolom

| # | Nama kolom (asli) | Non-null | % terisi | Contoh nilai |
|---|---|---|---|---|
| 1 | `title` | 50/50 | 100% | Macet cicukang |
| 2 | `description` | 50/50 | 100% | Telat dikit gpp y |
| 3 | `latitude` | 50/50 | 100% | -6.9679774088170126 |
| 4 | `longitude` | 50/50 | 100% | 107.5594142463214 |
| 5 | `medias_all` | 25/50 | 50% | https://mapid-app-chat.cdn.mapid.io/692d |
| 6 | `images` | 25/50 | 50% | https://mapid-app-chat.cdn.mapid.io/692d |
| 7 | `videos` | 7/50 | 14% | https://mapid-app-chat.cdn.mapid.io/692d |
| 8 | `medias` | 25/50 | 50% | https://mapid-app-chat.cdn.mapid.io/692d |

### 3 baris contoh

```
                     title                                                                                                                                   description             latitude           longitude                                                                                                                                                                                                                                                                                                                                                                                                                                                                    medias_all                                                                                                                                                                                                                                                                                                                                                                                                                                                                        images                                                                                                               videos medias
0           Macet cicukang                                                                                                                             Telat dikit gpp y  -6.9679774088170126   107.5594142463214                                                                                                                                                                                                                                                                                                                                                           https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/5c7e0e80-7375-4f2b-80de-d4bf33ef89a4_1780968994582.jpg                                                                                                                                                                                                                                                                                                                                                           https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/5c7e0e80-7375-4f2b-80de-d4bf33ef89a4_1780968994582.jpg                                                                                                                  NaN    NaN
1        Sawah Menghijau 🌾               Setiap weekend saya sepedahan lewat sini untuk melepas lelah otak dalam berfikir dan mencari inspirasi dari dunia nyata #alam 🌾   -6.994012311120087  107.50824556369318                                                                                                                      https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/2b1cc5dc-23fd-4246-8cca-ce779b40b29a_JU7A62qmWX.png,https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/e7637b66-5a20-4730-96ba-f2160b0972bc_1780798855593.jpg,https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/012a43b0-db92-4319-b14b-b6aab557f81b_1780798778125.mp4                                                                                                                                                                                                                                          https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/2b1cc5dc-23fd-4246-8cca-ce779b40b29a_JU7A62qmWX.png,https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/e7637b66-5a20-4730-96ba-f2160b0972bc_1780798855593.jpg  https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/012a43b0-db92-4319-b14b-b6aab557f81b_1780798778125.mp4    NaN
2  Inflasi Harga Sayur 📈🌶️  Pagi ini saya ke pasar dan mendapati Bawang putih terpantau naik dari 38rb jadi 44rb, lainnya akan saya update segera di pin ini #hargasayur   -6.963147686002662  107.56258134575548  https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/ed63d264-0757-4307-9d83-d6b8939333c4_x5QXdB6HaZ.png,https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/26915071-f819-4c13-a405-15221d227def_1780792116364.jpg,https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/6d6ff9e9-0323-4c9b-8800-406d9369c869_1780792116400.jpg,https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/38a73b06-5d2f-4a26-a3de-c0df0d687c28_1780792116424.jpg  https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/ed63d264-0757-4307-9d83-d6b8939333c4_x5QXdB6HaZ.png,https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/26915071-f819-4c13-a405-15221d227def_1780792116364.jpg,https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/6d6ff9e9-0323-4c9b-8800-406d9369c869_1780792116400.jpg,https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/38a73b06-5d2f-4a26-a3de-c0df0d687c28_1780792116424.jpg                                                                                                                  NaN    NaN
```

### Kolom yang kelihatan kategorikal / dropdown (nilai unik sedikit)

- `videos` (7 nilai unik): ['https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/012a43b0-db92-4319-b14b-b6aab557f81b_1780798778125.mp4', 'https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/08ce156f-310b-49cf-b03d-919498915fde_1780019256374.mp4,https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/22ff7419-c8d6-45b3-94bf-694a72f6da43_1780019281953.mp4', 'https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/3598ad31-8383-4e77-bfb9-12ac10691d9f_000AF887-4D0C-4467-A649-563179C09A84_L0_001_1777509039.239466_IMG_0757.MOV,https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/4c99b15d-43e4-4bb5-bbaf-4a868979d902_CD9F4525-57A9-4856-8E7E-0FF519EEC48A_L0_001_1777509063.514805_IMG_0758.MOV', 'https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/38adbe37-9bfc-44e0-b91e-47677dcaf817_20260529Outdoor_walk_20260529081029.mp4', 'https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/5024f19b-766a-4560-8d24-31bd5218b378_1778311412339.mp4', 'https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/6d75cb96-9472-4744-8e5c-57123590cb56_20260527_080233.mp4,https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/9faff357-6f69-49cb-ae8b-92f3975a52ba_20260527_080256.mp4', 'https://mapid-app-chat.cdn.mapid.io/692d03413a0cf54ea6633e89/8236ca0f-b563-4842-8316-74400f394a54_1780143302906.mp4']

### Pengecekan kolom lokasi & waktu


**`latitude`** (terdeteksi sebagai kolom LAT)
  tipe pandas saat ini: str (BUKAN NUMERIK -- perlu di-cast!)
  contoh nilai mentah: ['-6.9679774088170126', '-6.994012311120087', '-6.963147686002662', '-6.97119279892982', '-6.885265356956939']
  rentang nilai (setelah dipaksa numerik): -7.01903 s/d -6.81939
  PERINGATAN: 24 baris di luar bounding box Jabodetabek -- cek kemungkinan lat/lon tertukar atau salah ketik

**`longitude`** (terdeteksi sebagai kolom LON)
  tipe pandas saat ini: str (BUKAN NUMERIK -- perlu di-cast!)
  contoh nilai mentah: ['107.5594142463214', '107.50824556369318', '107.56258134575548', '107.54570672987012', '107.5192663356965']
  rentang nilai (setelah dipaksa numerik): 107.42799 s/d 107.61635
  PERINGATAN: 50 baris di luar bounding box Jabodetabek -- cek kemungkinan lat/lon tertukar atau salah ketik

## Sample_MenuGo_WebGIS2026.csv

- Jumlah baris: **15**
- Jumlah kolom: **14**

### Daftar kolom

| # | Nama kolom (asli) | Non-null | % terisi | Contoh nilai |
|---|---|---|---|---|
| 1 | `Nama Tempat Makan` | 15/15 | 100% | DOPAMINE |
| 2 | `Jenis Tempat Makan` | 15/15 | 100% | Kafe |
| 3 | `Tanggal` | 15/15 | 100% | 2026/06/10 |
| 4 | `Waktu` | 15/15 | 100% | 09:19:00 |
| 5 | `Foto Tempat` | 15/15 | 100% | https://mapidstorage.s3.ap-southeast-1.a |
| 6 | `Foto Menu 1 (Foto Menu Utama)` | 15/15 | 100% | https://mapidstorage.s3.ap-southeast-1.a |
| 7 | `Foto Menu 2 (Foto Menu Lainnya)` | 15/15 | 100% | https://mapidstorage.s3.ap-southeast-1.a |
| 8 | `Menu Dalam Bentuk Link Digital` | 0/15 | 0% |  |
| 9 | `Apa Menu Utama/Andalan Yang Dijual?` | 15/15 | 100% | kopi dan makan berat |
| 10 | `Berapa Harga Rata-rata Menu Tersebut (Per porsi)?` | 15/15 | 100% | 35000 |
| 11 | `Bagaimana Kondisi Pembeli Saat Kunjungan Dilakukan?` | 15/15 | 100% | Ramai (Terdapat antrean lebih dari 3 ora |
| 12 | `Apakah Berjualan Dengan Berkeliling (Mobilitas)?` | 15/15 | 100% |  Tidak (Menetap/Mangkal di satu titik) |
| 13 | `Latitude` | 15/15 | 100% | -6.40223649998775 |
| 14 | `Longitude` | 15/15 | 100% | 106.821909400001 |

### 3 baris contoh

```
  Nama Tempat Makan Jenis Tempat Makan     Tanggal     Waktu                                                                                                           Foto Tempat                                                                                         Foto Menu 1 (Foto Menu Utama)                                                                                       Foto Menu 2 (Foto Menu Lainnya) Menu Dalam Bentuk Link Digital Apa Menu Utama/Andalan Yang Dijual? Berapa Harga Rata-rata Menu Tersebut (Per porsi)?                                   Bagaimana Kondisi Pembeli Saat Kunjungan Dilakukan? Apakah Berjualan Dengan Berkeliling (Mobilitas)?           Latitude         Longitude
0          DOPAMINE               Kafe  2026/06/10  09:19:00  https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1781057981037_stamped_1781057962886.jpg      https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1781058000673_scaled_1000546928.jpg      https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1781058010244_scaled_1000546929.jpg                            NaN                kopi dan makan berat                                             35000  Ramai (Terdapat antrean lebih dari 3 orang / kursi atau meja mayoritas penuh terisi)            Tidak (Menetap/Mangkal di satu titik)  -6.40223649998775  106.821909400001
1           D'BESTO          Fast Food  2026/06/03  11:34:00      https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780534010331_scaled_1000544815.jpg      https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780534021485_scaled_1000544817.jpg      https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780534033038_scaled_1000544818.jpg                            NaN              AYAM GORENG DAN BURGER                                             12000                        Sepi (Hanya ada penjual / tidak ada antrean atau pembeli lain)            Tidak (Menetap/Mangkal di satu titik)  -6.39662329996681  106.836347899985
2       POINT COFFE               Kafe  2026/06/09  09:56:00  https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780973805942_stamped_1780973797944.jpg  https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780973833180_stamped_1780973826265.jpg  https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780973849592_stamped_1780973839560.jpg                            NaN                                kopi                                             25000                                   Sedang (Ada 1-3 pembeli yang sedang menunggu/makan)            Tidak (Menetap/Mangkal di satu titik)  -6.40329440002159  106.837846700016
```

### Kolom yang kelihatan kategorikal / dropdown (nilai unik sedikit)

- `Nama Tempat Makan` (15 nilai unik): ['BUBUR AYAM CIANJUR', 'CALF ', 'CHATIME', "D'BESTO", 'DOPAMINE', 'JANJI JIWA', 'JUSANTARA', 'KEDAI KIMUNG', 'KOAT COFFE', 'MIE UENA', 'POINT COFFE', 'SUSU MBOK DARMI', 'TAHU SUSU CIHUNI', 'UBI CILEMBU', 'mie ayam alim']
- `Jenis Tempat Makan` (4 nilai unik): ['Fast Food', 'Kafe', 'Kaki Lima/Gerobak', 'Restoran']
- `Foto Tempat` (15 nilai unik): ['https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780533472409_stamped_1780533461230.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780533755589_scaled_1000544814.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780534010331_scaled_1000544815.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780569284193_scaled_1000545043.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780570049932_stamped_1780570036844.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780619844289_stamped_1780619835356.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780620071719_stamped_1780620062533.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780620582045_stamped_1780620571846.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780630076142_stamped_1780630063000.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780630210275_stamped_1780630198435.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780630570893_stamped_1780630557249.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780973805942_stamped_1780973797944.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780997930790_stamped_1780997921286.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1781057981037_stamped_1781057962886.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1781058192598_stamped_1781058186632.jpg']
- `Foto Menu 1 (Foto Menu Utama)` (15 nilai unik): ['https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780533401092_scaled_1000544813.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780533774057_scaled_1000544129.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780534021485_scaled_1000544817.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780569294171_scaled_1000545034.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780570074909_stamped_1780570067736.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780619854976_scaled_1000545190.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780620087633_scaled_1000545195.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780620597411_scaled_1000545199.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780630099905_scaled_1000545266.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780630309618_stamped_1780630228912.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780630589689_stamped_1780630579357.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780973833180_stamped_1780973826265.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780997820132_stamped_1780997815529.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1781058000673_scaled_1000546928.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1781058203988_scaled_1000546932.jpg']
- `Foto Menu 2 (Foto Menu Lainnya)` (15 nilai unik): ['https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780533410975_scaled_1000544812.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780533789549_scaled_1000544129.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780534033038_scaled_1000544818.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780569301695_scaled_1000545035.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780570167404_scaled_1000545048.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780619861587_scaled_1000545191.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780620099934_scaled_1000545194.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780620606221_scaled_1000545198.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780630121256_scaled_1000545265.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780630443868_stamped_1780630428621.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780630600946_scaled_1000545271.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780973849592_stamped_1780973839560.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1780997838615_stamped_1780997832903.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1781058010244_scaled_1000546929.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1781058212358_scaled_1000546933.jpg']
- `Apa Menu Utama/Andalan Yang Dijual?` (14 nilai unik): ['AYAM GORENG DAN BURGER', 'BUBUR AYAM,SATE JEROAN', 'JUS BUAH DAN ROTI/SNACK MANIS', 'MIE CHILI OIL MIE AYAM', 'SUSU PLAIN', 'TAHU, SUSU KEDELAI', 'UBI BAKAR', 'kopi', 'kopi dan makan berat', 'kopi dan roti', 'kopi dan roti bakar', 'kopi dan snack', 'mie yamin', 'minuman boba dan snack asin']
- `Bagaimana Kondisi Pembeli Saat Kunjungan Dilakukan?` (3 nilai unik): ['Ramai (Terdapat antrean lebih dari 3 orang / kursi atau meja mayoritas penuh terisi)', 'Sedang (Ada 1-3 pembeli yang sedang menunggu/makan)', 'Sepi (Hanya ada penjual / tidak ada antrean atau pembeli lain)']
- `Apakah Berjualan Dengan Berkeliling (Mobilitas)?` (2 nilai unik): [' Tidak (Menetap/Mangkal di satu titik)', 'Ya (Berkeliling)']

### Pengecekan kolom lokasi & waktu


**`Tanggal`** (terdeteksi sebagai kolom DATE)
  contoh nilai unik (maks 8 ditampilkan): ['2026/06/10', '2026/06/03', '2026/06/09', '2026/06/04', '2026/06/05']

**`Waktu`** (terdeteksi sebagai kolom TIME)
  contoh nilai unik (maks 8 ditampilkan): ['09:19:00', '11:34:00', '09:56:00', '07:36:00', '10:29:00', '10:34:00', '10:27:00', '09:22:00']

**`Latitude`** (terdeteksi sebagai kolom LAT)
  tipe pandas saat ini: str (BUKAN NUMERIK -- perlu di-cast!)
  contoh nilai mentah: ['-6.40223649998775', '-6.39662329996681', '-6.40329440002159', '-6.40392009996759', '-6.39619340000111']
  rentang nilai (setelah dipaksa numerik): -6.42161 s/d -6.39553

**`Longitude`** (terdeteksi sebagai kolom LON)
  tipe pandas saat ini: str (BUKAN NUMERIK -- perlu di-cast!)
  contoh nilai mentah: ['106.821909400001', '106.836347899985', '106.837846700016', '106.837989100006', '106.836588900019']
  rentang nilai (setelah dipaksa numerik): 106.82191 s/d 106.85103

## Sample_PropertiGo_WebGIS2026.csv

- Jumlah baris: **15**
- Jumlah kolom: **8**

### Daftar kolom

| # | Nama kolom (asli) | Non-null | % terisi | Contoh nilai |
|---|---|---|---|---|
| 1 | `Kategori P` | 15/15 | 100% | Coworking Space |
| 2 | `Jenis Prop` | 15/15 | 100% | Disewa |
| 3 | ` Tanggal` | 15/15 | 100% | 2026/02/22 |
| 4 | `Alamat` | 15/15 | 100% | Jalan PH. H. Mustofa No 65 (Suci), Sukap |
| 5 | `Foto Tampa` | 15/15 | 100% | https://mapidstorage.s3.ap-southeast-1.a |
| 6 | `Foto Spand` | 15/15 | 100% | https://mapidstorage.s3.ap-southeast-1.a |
| 7 | `Latitude` | 15/15 | 100% | -6.900054000189712 |
| 8 | `Longitude` | 15/15 | 100% | 107.644248577245946 |

### 3 baris contoh

```
        Kategori P Jenis Prop     Tanggal                                                                                                      Alamat                                                                                                             Foto Tampa                                                                                                             Foto Spand            Latitude            Longitude
0  Coworking Space     Disewa  2026/02/22                      Jalan PH. H. Mustofa No 65 (Suci), Sukapada, Cibeunying Kidul, Kota Bandung, Indonesia   https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/mamang_devops/1771719271177_scaled_1000157219.jpg  https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/mamang_devops/1771719275600_scaled_1000157224.webp  -6.900054000189712  107.644248577245946
1           Gudang     Dijual  2026/02/28                             Jalan Sumber Endah I, Babakan Ciparay, Babakan Ciparay, Kota Bandung, Indonesia  https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/egipratama/1772252915380_stamped_1772252913623.jpg  https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/egipratama/1772252942578_stamped_1772252940466.jpg  -6.937680655906008  107.576561952734721
2           Gudang     Disewa  2026/03/02  Jalan Sederhana 8-10, Pasteur Sukajadi Kota Bandung Jawa Barat, Pasteur, Sukasari, Kota Bandung, Indonesia     https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/bagusid/1772417185278_stamped_1772417182445.jpg     https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/bagusid/1772417198337_stamped_1772417196239.jpg  -6.894745860457250  107.598206257953279
```

### Kolom yang kelihatan kategorikal / dropdown (nilai unik sedikit)

- `Kategori P` (10 nilai unik): ['Coworking Space', 'Gudang', 'Kantor', 'Kos', 'Restoran', 'Retail (toko baju, peralatan olahraga, toko elektronik, dll)', 'Retail FnB', 'Ruko', 'Rumah', 'Tanah']
- `Jenis Prop` (2 nilai unik): ['Dijual', 'Disewa']
- `Alamat` (15 nilai unik): ['Gang sereh 83/9b, Bandung Jawa Barat, Cibadak, Astanaanyar, Kota Bandung, Indonesia', 'Jalan Abdul Haris Nasution 21, Kel. Pakemitan, Pakemitan, Cinambo, Kota Bandung, Indonesia', 'Jalan Ikhlas VI, Panyileukan Regency, Cipadung Kidul, Panyileukan, Kota Bandung, Indonesia', 'Jalan Ir. H. Djuanda 216b, Cisitu Lama, Dago, Coblong, Kota Bandung, Indonesia', 'Jalan Merdeka 28, Babakan Ciamis Sumur Bandung Kota Bandung Jawa Barat, Babakan Ciamis, Sumur Bandung, Kota Bandung, Indonesia', 'Jalan Naripan 79, Sumur Bandung Kota Bandung Jawa Barat, Kebon Pisang, Sumur Bandung, Kota Bandung, Indonesia', 'Jalan Otto Iskandardinata 81, Bandung Jawa Barat, Braga, Sumur Bandung, Kota Bandung, Indonesia', 'Jalan PH. H. Mustofa 23, Kel. Padasuka, Padasuka, Cibeunying Kidul, Kota Bandung, Indonesia', 'Jalan PH. H. Mustofa No 65 (Suci), Sukapada, Cibeunying Kidul, Kota Bandung, Indonesia', 'Jalan Pak Gatot I No.16, Gegerkalong Sukasari Bandung City West Java, Gegerkalong, Sukajadi, Kota Bandung, Indonesia', 'Jalan Sederhana 8-10, Pasteur Sukajadi Kota Bandung Jawa Barat, Pasteur, Sukasari, Kota Bandung, Indonesia', 'Jalan Sumber Endah I, Babakan Ciparay, Babakan Ciparay, Kota Bandung, Indonesia', 'Jalan Surapati 61, Cihapit Bandung Wetan Bandung Jawa Barat, Cihaurgeulis, Coblong, Kota Bandung, Indonesia', 'Jalan Tamblong 48-50, Kebon Pisang Bandung Jawa Barat, Kebon Pisang, Sumur Bandung, Kota Bandung, Indonesia', 'Jalan Walagri Mulya, Pasanggrahan Indah Blok 27, Pasanggrahan, Ujungberung, Kota Bandung, Indonesia']
- `Foto Tampa` (15 nilai unik): ['https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/bagusid/1772417185278_stamped_1772417182445.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/bagusid/1776389749257_stamped_1776389746855.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/bagusid/1776569103952_stamped_1776569102089.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/bagusid/1776571908098_stamped_1776571898475.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/dwidwi/1771115315267_scaled_1000092951.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/egipratama/1772252915380_stamped_1772252913623.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/mamang_devops/1771666366638_scaled_1000156774.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/mamang_devops/1771718682467_scaled_1000157207.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/mamang_devops/1771719271177_scaled_1000157219.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/mapid.database/1776652249490_img_%25rumah2_%25f2fe261e-704f-42c8-b3b7-f1e118fff11f.png', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1778119931442_stamped_1778119926113.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1778637322706_stamped_1778637311624.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1778904026344_stamped_1778904021815.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1779186104400_stamped_1779186094249.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1779188753926_stamped_1779188748243.jpg']
- `Foto Spand` (15 nilai unik): ['https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/bagusid/1772417198337_stamped_1772417196239.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/bagusid/1776389479765_stamped_1776389476848.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/bagusid/1776389756737_stamped_1776389754937.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/bagusid/1776569111269_stamped_1776569109590.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/bagusid/1776571923643_stamped_1776571911828.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/dwidwi/1771115320310_scaled_1000092952.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/egipratama/1772252942578_stamped_1772252940466.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/mamang_devops/1771666365393_scaled_1000156775.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/mamang_devops/1771718687373_scaled_1000157208.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/mamang_devops/1771719275600_scaled_1000157224.webp', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1778119961816_stamped_1778119942046.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1778637339808_stamped_1778637329891.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1778904041172_stamped_1778904034712.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1779186125451_stamped_1779186120743.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/undefined/1779188773330_stamped_1779188768567.jpg']

### Pengecekan kolom lokasi & waktu


**` Tanggal`** (terdeteksi sebagai kolom DATE)
  contoh nilai unik (maks 8 ditampilkan): ['2026/02/22', '2026/02/28', '2026/03/02', '2026/04/17', '2026/04/19', '2026/02/15', '2026/02/21', '2026/05/16']

**`Latitude`** (terdeteksi sebagai kolom LAT)
  tipe pandas saat ini: str (BUKAN NUMERIK -- perlu di-cast!)
  contoh nilai mentah: ['-6.900054000189712', '-6.937680655906008', '-6.894745860457250', '-6.920343190093632', '-6.912045328366646']
  rentang nilai (setelah dipaksa numerik): -6.94483 s/d -6.86841

**`Longitude`** (terdeteksi sebagai kolom LON)
  tipe pandas saat ini: str (BUKAN NUMERIK -- perlu di-cast!)
  contoh nilai mentah: ['107.644248577245946', '107.576561952734721', '107.598206257953279', '107.612323931312631', '107.610581518494996']
  rentang nilai (setelah dipaksa numerik): 107.57656 s/d 107.72158
  PERINGATAN: 15 baris di luar bounding box Jabodetabek -- cek kemungkinan lat/lon tertukar atau salah ketik

## Sample_StrukGo_WebGIS2026.csv

- Jumlah baris: **15**
- Jumlah kolom: **20**

### Daftar kolom

| # | Nama kolom (asli) | Non-null | % terisi | Contoh nilai |
|---|---|---|---|---|
| 1 | `Nama Tempat/Merchant` | 15/15 | 100% | Balista Sushi and Tea |
| 2 | `Kategori Tempat` | 15/15 | 100% | E-commerce |
| 3 | `Tanggal Transaksi` | 15/15 | 100% | 2026/06/09 |
| 4 | `Waktu Transaksi` | 15/15 | 100% | 12:58:00 |
| 5 | `Metode Pembayaran` | 15/15 | 100% | QRIS |
| 6 | `Foto Struk/Bukti bayar` | 15/15 | 100% | https://mapidstorage.s3.ap-southeast-1.a |
| 7 | `Kontributor` | 15/15 | 100% | Candra Dewi |
| 8 | `Pengecekan` | 0/15 | 0% |  |
| 9 | `Latitude` | 15/15 | 100% | -6.97395966656616 |
| 10 | `Longitude` | 15/15 | 100% | 107.554199841529 |
| 11 | `ID data` | 15/15 | 100% | 6a27abd6f2c8ca5ff95f2605 |
| 12 | `Total Pengeluran per Orang (Lama)` | 15/15 | 100% | 0 |
| 13 | `Catatan Kesalahan` | 0/15 | 0% |  |
| 14 | `Jenis Kategori (Lama)` | 0/15 | 0% |  |
| 15 | `Alamat (Lama)` | 0/15 | 0% |  |
| 16 | `Tujuan makan (Lama)` | 0/15 | 0% |  |
| 17 | `Foto menu (Lama)` | 0/15 | 0% |  |
| 18 | `Rating kepuasan tempat (Lama)` | 0/15 | 0% |  |
| 19 | `Jumlah orang yang makan (Lama)` | 0/15 | 0% |  |
| 20 | `Total Pengeluaran (Tanpa PPN) (Lama)` | 0/15 | 0% |  |

### 3 baris contoh

```
    Nama Tempat/Merchant Kategori Tempat Tanggal Transaksi Waktu Transaksi Metode Pembayaran                                                                                                          Foto Struk/Bukti bayar           Kontributor Pengecekan           Latitude         Longitude                   ID data Total Pengeluran per Orang (Lama) Catatan Kesalahan Jenis Kategori (Lama) Alamat (Lama) Tujuan makan (Lama) Foto menu (Lama) Rating kepuasan tempat (Lama) Jumlah orang yang makan (Lama) Total Pengeluaran (Tanpa PPN) (Lama)
0  Balista Sushi and Tea      E-commerce        2026/06/09        12:58:00              QRIS  https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/candradewipramesthi/1780984788698_stamped_1780984783152.jpg           Candra Dewi        NaN  -6.97395966656616  107.554199841529  6a27abd6f2c8ca5ff95f2605                                 0               NaN                   NaN           NaN                 NaN              NaN                           NaN                            NaN                                  NaN
1          Sate Cantilan   Restoran/kafe        2026/06/08        19:03:00              QRIS              https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/bagusid/1780920258917_stamped_1780920256442.jpg  Bagus Imam Darmawan         NaN  -6.97036701362961   107.52714171526  6a26afc4cbafcbc7eac07841                                 0               NaN                   NaN           NaN                 NaN              NaN                           NaN                            NaN                                  NaN
2                    K24          Apotek        2026/06/08        19:52:00              QRIS              https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/bagusid/1780923157963_stamped_1780923155600.jpg  Bagus Imam Darmawan         NaN  -6.96153467565862  107.558743698203  6a26bb17cbafcbc7eac0788e                                 0               NaN                   NaN           NaN                 NaN              NaN                           NaN                            NaN                                  NaN
```

### Kolom yang kelihatan kategorikal / dropdown (nilai unik sedikit)

- `Nama Tempat/Merchant` (14 nilai unik): ['Balista Sushi and Tea', 'Blond the Bakery', 'Busa Coin Laundry', 'GiggleBox FCL', 'Indomaret TKI 3', 'Indomaret jalan tengah', 'Itsjours', 'K24', 'Kopi aren', 'Premiere Beaute Official Store', 'Sate Cantilan', 'Sop Burtok', 'Toko Kopi Pasar Cihapit', 'ztarize']
- `Kategori Tempat` (5 nilai unik): ['Apotek', 'E-commerce', 'Minimarket/supermarket', 'Restoran/kafe', 'Warung/kaki lima']
- `Metode Pembayaran` (3 nilai unik): ['E-wallet', 'QRIS', 'Tunai']
- `Foto Struk/Bukti bayar` (15 nilai unik): ['https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/abilakrisnaw/1780718294352_image_picker_8C6EC0A7-389E-475F-BBFC-9B91A18B014C-22670-000006710EEFB62C.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/abilakrisnaw/1780840278198_stamped_1780840272814.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/bagusid/1780830329621_stamped_1780830327129.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/bagusid/1780920258917_stamped_1780920256442.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/bagusid/1780923157963_stamped_1780923155600.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/candradewipramesthi/1780721669641_stamped_1780721663275.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/candradewipramesthi/1780727352952_image_picker_427938CA-FC4D-4406-8170-BB190C93F8BE-50108-000013A06695FF65.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/candradewipramesthi/1780815471846_image_picker_70162E5D-5979-491C-AECE-DFFE9DB02CC4-57581-0000148F7CFD86A3.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/candradewipramesthi/1780816583614_stamped_1780816580205.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/candradewipramesthi/1780882831314_image_picker_BCA9E5ED-648B-474D-B0FA-BF23B09EF5E0-60505-000014F90346D04E.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/candradewipramesthi/1780984788698_stamped_1780984783152.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/egipratama/1780821112077_stamped_1780821109952.jpg', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/wina/1780910604772_image_picker_9D1BECF7-0DEB-4C89-ABFA-63E2B1E0FF41-20216-0000022D6EED7C76.png', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/wina/1780910675660_image_picker_04D8A5D2-D4B0-4F78-A19B-200CF3B8B8E2-20216-0000022DD43C733E.png', 'https://mapidstorage.s3.ap-southeast-1.amazonaws.com/general_image/wina/1780929404840_stamped_1780929402669.jpg']
- `Kontributor` (5 nilai unik): ['Abila MAPID TEAM', 'Bagus Imam Darmawan ', 'Candra Dewi', 'Egi Pratama', 'Wina Ayu']
- `ID data` (15 nilai unik): ['6a239ae5cbafcbc7eac07410', '6a23a807f2c8ca5ff95e979a', '6a23be3d72a02d4f67effc15', '6a251672bddac90624660531', '6a251af6bddac906246605dc', '6a252c7a72a02d4f67f02cbd', '6a25507ccbafcbc7eac07556', '6a257758cbafcbc7eac07597', '6a261d94f2c8ca5ff95eeb53', '6a268a0ef2c8ca5ff95f0887', '6a268a5634c8bf00ff4fa275', '6a26afc4cbafcbc7eac07841', '6a26bb17cbafcbc7eac0788e', '6a26d37ea5240cf29f5beb4e', '6a27abd6f2c8ca5ff95f2605']

### Pengecekan kolom lokasi & waktu


**`Tanggal Transaksi`** (terdeteksi sebagai kolom DATE)
  contoh nilai unik (maks 8 ditampilkan): ['2026/06/09', '2026/06/08', '2026/06/07', '2026/06/06', '2026/06/05', '2026/06/04']

**`Waktu Transaksi`** (terdeteksi sebagai kolom TIME)
  contoh nilai unik (maks 8 ditampilkan): ['12:58:00', '19:03:00', '19:52:00', '13:57:00', '14:16:00', '15:31:00', '18:04:00', '20:50:00']

**`Latitude`** (terdeteksi sebagai kolom LAT)
  tipe pandas saat ini: str (BUKAN NUMERIK -- perlu di-cast!)
  contoh nilai mentah: ['-6.97395966656616', '-6.97036701362961', '-6.96153467565862', '-6.97282493555248', '-6.97280941002072']
  rentang nilai (setelah dipaksa numerik): -6.97396 s/d -6.88266
  PERINGATAN: 10 baris di luar bounding box Jabodetabek -- cek kemungkinan lat/lon tertukar atau salah ketik

**`Longitude`** (terdeteksi sebagai kolom LON)
  tipe pandas saat ini: str (BUKAN NUMERIK -- perlu di-cast!)
  contoh nilai mentah: ['107.554199841529', '107.52714171526', '107.558743698203', '107.547925833318', '107.547930524431']
  rentang nilai (setelah dipaksa numerik): 107.52712 s/d 107.62055
  PERINGATAN: 15 baris di luar bounding box Jabodetabek -- cek kemungkinan lat/lon tertukar atau salah ketik