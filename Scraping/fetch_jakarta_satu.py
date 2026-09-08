"""
fetch_jakarta_satu.py
========================
Ekstraksi NJOP dan RDTR/Zonasi dari portal ArcGIS Jakarta Satu.

BEDA DENGAN SKRIP SEBELUMNYA: ini bukan file untuk didownload sekali
(kayak PBF/WorldPop), tapi API ArcGIS REST yang perlu 2 tahap:

  TAHAP 1 - CARI LAYER (search)
    Portal punya banyak layer/service dengan nama macam-macam. Perlu cari
    dulu URL service yang PERSIS, karena nama "NJOP" bisa muncul di
    beberapa produk (Web Map, Dashboard, FeatureServer, dst) dan cuma
    FeatureServer/MapServer yang bisa di-query datanya secara terprogram.

  TAHAP 2 - TARIK DATA (fetch)
    Setelah tahu URL layer yang benar, baru query datanya sebagai GeoJSON,
    dengan paginasi karena ArcGIS REST biasanya membatasi jumlah record
    per request (maxRecordCount, umumnya 1000-2000).

CAKUPAN: NJOP dan RDTR dari Jakarta Satu HANYA mencakup DKI Jakarta.
Untuk heksagon di Bekasi dan Tangerang, kedua variabel ini akan kosong
kecuali dicari penggantinya (ZNT Bhumi ATR/BPN untuk NJOP, GISTARU untuk
RDTR - keduanya viewer manual, belum ada API/bulk download yang
terverifikasi). Ini bukan bug, tapi keterbatasan cakupan sumber data
yang sudah dicatat di briefing dan perlu dinyatakan terbuka di proposal.

CARA PAKAI:
  1. python fetch_jakarta_satu.py search njop
     -> lihat daftar hasil, cari yang type-nya "Feature Service" atau
        "Map Service" (BUKAN "Web Map" atau "Dashboard" - itu cuma
        tampilan, bukan data mentahnya)
  2. Salin url yang muncul, tempel ke LAYER_URLS di bawah
  3. python fetch_jakarta_satu.py fetch njop
     -> data ditarik dan disimpan ke data_raw/jakarta_satu/
"""

import json
import sys
import time
from pathlib import Path

import requests

PORTAL_SEARCH = "https://jakartasatu.jakarta.go.id/portal/sharing/rest/search"
OUT_DIR = Path("data_raw/jakarta_satu")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Bbox query - sama dengan wilayah studi keseluruhan. Layer NJOP/RDTR cuma
# akan mengembalikan yang memang ada datanya (otomatis kepotong ke DKI),
# jadi tidak perlu bbox terpisah khusus DKI.
BBOX = {"lon_min": 106.55, "lat_min": -6.45, "lon_max": 107.25, "lat_max": -5.95}

# ── ISI SETELAH TAHAP SEARCH ─────────────────────────────────────────
# Ganti None dengan URL FeatureServer/MapServer layer yang benar, hasil
# dari "python fetch_jakarta_satu.py search njop" (atau "rdtr").
# Contoh format URL yang benar: ".../FeatureServer/0" atau ".../MapServer/2"
LAYER_URLS = {
    "njop": None,
    "rdtr": "https://jakartasatu.jakarta.go.id/server/rest/services/Rencana_Pola_Ruang_RDTR_2022/FeatureServer/0",
}


def search_portal(query: str):
    print(f"Mencari '{query}' di portal Jakarta Satu...\n")
    params = {"q": query, "f": "json", "num": 20}
    resp = requests.get(PORTAL_SEARCH, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    if not results:
        print("Tidak ada hasil. Coba kata kunci lain, atau cek manual lewat "
              "browser di jakartasatu.jakarta.go.id/portal")
        return

    for item in results:
        title = item.get("title")
        item_type = item.get("type")
        url = item.get("url", "(tidak ada url langsung - buka item ini di portal untuk detail)")
        item_id = item.get("id")
        print(f"- {title}")
        print(f"  type : {item_type}")
        print(f"  url  : {url}")
        print(f"  id   : {item_id}  (buka https://jakartasatu.jakarta.go.id/portal/home/item.html?id={item_id} untuk detail)")
        print()

    print("Cari yang type-nya 'Feature Service' atau 'Map Service'. "
          "Salin url-nya (tambahkan /0 atau nomor layer di ujungnya kalau "
          "belum ada) ke LAYER_URLS di dalam skrip ini, lalu jalankan "
          "'python fetch_jakarta_satu.py fetch <nama>'.")


def query_layer_paginated(layer_url: str, bbox: dict, page_size: int = 1000,
                           max_retry: int = 3, resume_offset: int = 0,
                           resume_features: list = None,
                           checkpoint_path: Path = None) -> dict:
    """Query ArcGIS REST FeatureServer/MapServer layer sebagai GeoJSON,
    dengan paginasi resultOffset karena server biasanya batasi jumlah
    record per request. Tiap halaman punya retry sendiri, dan progress
    disimpan ke checkpoint_path tiap halaman - kalau koneksi putus di
    tengah, jalankan ulang perintah yang sama untuk lanjut dari titik
    terakhir, bukan dari awal."""
    query_url = layer_url.rstrip("/") + "/query"
    geometry = {
        "xmin": bbox["lon_min"], "ymin": bbox["lat_min"],
        "xmax": bbox["lon_max"], "ymax": bbox["lat_max"],
        "spatialReference": {"wkid": 4326},
    }

    all_features = list(resume_features) if resume_features else []
    offset = resume_offset
    while True:
        params = {
            "where": "1=1",
            "geometry": json.dumps(geometry),
            "geometryType": "esriGeometryEnvelope",
            "spatialRel": "esriSpatialRelIntersects",
            "inSR": 4326,
            "outSR": 4326,
            "outFields": "*",
            "returnGeometry": "true",
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": page_size,
        }

        data = None
        for attempt in range(1, max_retry + 1):
            try:
                resp = requests.get(query_url, params=params, timeout=120)
                resp.raise_for_status()
                data = resp.json()
                break
            except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                print(f"  halaman offset={offset} percobaan {attempt}/{max_retry} gagal: {e}")
                if attempt < max_retry:
                    time.sleep(5 * attempt)
        if data is None:
            if checkpoint_path:
                with open(checkpoint_path, "w", encoding="utf-8") as f:
                    json.dump({"features": all_features, "next_offset": offset}, f)
                print(f"  checkpoint disimpan -> {checkpoint_path} "
                      f"({len(all_features)} fitur, next_offset={offset}). "
                      f"Jalankan ulang command yang sama untuk lanjut.")
            raise RuntimeError(
                f"Gagal ambil halaman offset={offset} setelah {max_retry} percobaan."
            )

        if "error" in data:
            raise RuntimeError(f"ArcGIS mengembalikan error: {data['error']}")

        features = data.get("features", [])
        all_features.extend(features)
        print(f"  ... {len(all_features)} fitur terkumpul")

        # checkpoint tiap halaman sukses, bukan cuma pas gagal - jaga-jaga
        # kalau proses ke-interrupt (Ctrl+C, laptop mati, dll) bukan cuma timeout
        if checkpoint_path:
            with open(checkpoint_path, "w", encoding="utf-8") as f:
                json.dump({"features": all_features, "next_offset": offset + page_size}, f)

        if len(features) < page_size:
            break  # halaman terakhir
        offset += page_size
        time.sleep(1)  # jeda sopan

    return {"type": "FeatureCollection", "features": all_features}


def fetch_layer(nama: str):
    url = LAYER_URLS.get(nama)
    if not url:
        print(f"LAYER_URLS['{nama}'] masih None. Jalankan dulu "
              f"'python fetch_jakarta_satu.py search {nama}', cari url layer "
              f"yang benar, lalu isi manual di dalam skrip ini sebelum fetch.")
        sys.exit(1)

    out_path = OUT_DIR / f"{nama}.geojson"
    checkpoint_path = OUT_DIR / f"{nama}_partial.json"

    resume_offset = 0
    resume_features = []
    if checkpoint_path.exists():
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            checkpoint = json.load(f)
        resume_features = checkpoint["features"]
        resume_offset = checkpoint["next_offset"]
        print(f"Ditemukan checkpoint: {len(resume_features)} fitur sudah "
              f"terkumpul sebelumnya, lanjut dari offset={resume_offset}.")

    print(f"Menarik data '{nama}' dari {url} ...")
    geojson = query_layer_paginated(
        url, BBOX,
        resume_offset=resume_offset,
        resume_features=resume_features,
        checkpoint_path=checkpoint_path,
    )

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)
    if checkpoint_path.exists():
        checkpoint_path.unlink()  # bersihkan checkpoint setelah sukses penuh

    print(f"Disimpan -> {out_path} ({len(geojson['features'])} fitur)")
    print("Ingat: ini data resmi Pemprov DKI - cantumkan atribusi sumber "
          "di halaman Metodologi. Cakupan cuma DKI, heksagon di Bekasi/"
          "Tangerang tidak akan ter-cover oleh data ini.")


def inspect_webmap(item_id: str):
    """Web Map di portal ArcGIS itu bukan layer langsung - dia JSON berisi
    daftar operationalLayers yang masing-masing punya url FeatureServer/
    MapServer asli. Fungsi ini buka JSON itu dan cetak url-url di dalamnya."""
    url = f"https://jakartasatu.jakarta.go.id/portal/sharing/rest/content/items/{item_id}/data"
    resp = requests.get(url, params={"f": "json"}, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    layers = data.get("operationalLayers", [])
    if not layers:
        print("Tidak ada operationalLayers ditemukan. Kemungkinan item ini "
              "bertipe beda dari yang diduga, atau strukturnya nested "
              "(group layer). Cek manual: buka url di atas langsung di browser.")
        print(f"URL mentah: {url}?f=json")
        return

    print(f"Ditemukan {len(layers)} layer di dalam web map ini:\n")
    for lyr in layers:
        title = lyr.get("title")
        lyr_url = lyr.get("url")
        print(f"- {title}")
        print(f"  url: {lyr_url}\n")
    print("Salin url yang paling relevan ke LAYER_URLS, lalu jalankan mode 'fetch'.")


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("search", "fetch", "inspect"):
        print(__doc__)
        print("\nMode tambahan: 'inspect <item_id>' - untuk item bertipe Web "
              "Map yang tidak punya url langsung (lihat hasil search).")
        sys.exit(1)

    mode, nama = sys.argv[1], sys.argv[2]
    if mode == "search":
        search_portal(nama)
    elif mode == "fetch":
        fetch_layer(nama)
    elif mode == "inspect":
        inspect_webmap(nama)


if __name__ == "__main__":
    main()