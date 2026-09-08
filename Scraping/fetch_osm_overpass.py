"""
fetch_osm_overpass.py
======================
Ekstraksi data OSM via Overpass API untuk STATIONOMICS.

Menarik 3 kelompok tag sesuai Bagian 5.1 laporan pendataan:
  1. Usaha / kompetitor (shop=*, amenity=restaurant|cafe|..., dst)
  2. Simpul transportasi darat (railway=station, highway=bus_stop, dst)
  3. Generator keramaian (school, hospital, place_of_worship, dst)

Output: GeoJSON per kelompok, tersimpan di ./data_raw/osm/

CATATAN PENTING SEBELUM DIJALANKAN:
- Ganti BBOX kalau wilayah studi final BUKAN Jabodetabek penuh
  (lihat briefing: wilayah studi belum final, ini masih keputusan tim).
- Endpoint publik Overpass punya kuota ±10.000 query/hari dan bisa lambat
  kalau bbox besar. Kalau sering timeout, pakai alternatif bulk:
  Geofabrik PBF (download.geofabrik.de/asia/indonesia.html) lalu
  filter offline pakai osmium/pyrosm — lebih stabil untuk area seluas
  Jabodetabek.
- Lisensi ODbL 1.0: WAJIB atribusi "© OpenStreetMap contributors".
  Kalau digabung ke database lain dan dipublikasikan, kena share-alike.
  -> Simpan raw OSM ini di data_raw/ (tidak dipublikasikan), yang boleh
  dipublikasikan cuma hasil agregat per heksagon.
"""

import json
import time
import requests
from pathlib import Path

# ── Konfigurasi ──────────────────────────────────────────────────────
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
TIMEOUT_S = 300  # naikkan sampai 900 kalau bbox besar & sering timeout

# Bbox DKI Jakarta + Bekasi (kota & kabupaten) + sebagian Tangerang/Tangsel.
# Ini kotak persegi (rectangular bbox), BUKAN potongan batas administratif
# presisi -> di sudut-sudutnya bisa nyerempet dikit ke Depok/Bogor di selatan,
# atau kepotong dikit di ujung barat Kabupaten Tangerang (mis. Balaraja,
# Kronjo). Kalau butuh presisi per-kabupaten, perlu filter pakai polygon
# admin boundary OSM (relation), bukan bbox kotak seperti ini.
# Cek visual bbox: bboxfinder.com -> paste 4 angka di bawah.
BBOX = {
    "lon_min": 106.55, "lat_min": -6.45,
    "lon_max": 107.25, "lat_max": -5.95,
}
OVERPASS_BBOX = f'{BBOX["lat_min"]},{BBOX["lon_min"]},{BBOX["lat_max"]},{BBOX["lon_max"]}'

OUT_DIR = Path("data_raw/osm")
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Query per kelompok tag (persis dari Bagian 5.1 laporan) ─────────
QUERIES = {
    "kompetitor": f"""
        [out:json][timeout:{TIMEOUT_S}];
        (
          node["shop"]({OVERPASS_BBOX});
          way["shop"]({OVERPASS_BBOX});
          node["amenity"~"^(restaurant|cafe|fast_food|food_court|bar|bank|atm|pharmacy|marketplace|fuel)$"]({OVERPASS_BBOX});
          way["amenity"~"^(restaurant|cafe|fast_food|food_court|bar|bank|atm|pharmacy|marketplace|fuel)$"]({OVERPASS_BBOX});
          node["office"]({OVERPASS_BBOX});
          way["office"]({OVERPASS_BBOX});
          way["building"~"^(retail|commercial)$"]({OVERPASS_BBOX});
          way["landuse"~"^(retail|commercial)$"]({OVERPASS_BBOX});
        );
        out center tags;
    """,
    "simpul_transit": f"""
        [out:json][timeout:{TIMEOUT_S}];
        (
          node["railway"~"^(station|halt)$"]({OVERPASS_BBOX});
          node["public_transport"~"^(station|stop_position)$"]({OVERPASS_BBOX});
          node["amenity"="bus_station"]({OVERPASS_BBOX});
          node["highway"="bus_stop"]({OVERPASS_BBOX});
        );
        out center tags;
    """,
    "generator_keramaian": f"""
        [out:json][timeout:{TIMEOUT_S}];
        (
          node["amenity"~"^(school|university|hospital|place_of_worship|marketplace)$"]({OVERPASS_BBOX});
          way["amenity"~"^(school|university|hospital|place_of_worship|marketplace)$"]({OVERPASS_BBOX});
          node["leisure"~"^(park|sports_centre)$"]({OVERPASS_BBOX});
          way["leisure"~"^(park|sports_centre)$"]({OVERPASS_BBOX});
        );
        out center tags;
    """,
}


def overpass_to_geojson(osm_json: dict, kategori: str) -> dict:
    """Konversi hasil Overpass (node/way+center) jadi GeoJSON FeatureCollection.
    Kolom kategori_asli disimpan utuh sesuai aturan taksonomi (Bagian 4.1 laporan):
    jangan pernah dibuang, dipakai untuk audit dan penjelasan ke juri.
    """
    features = []
    for el in osm_json.get("elements", []):
        if el["type"] == "node":
            lon, lat = el["lon"], el["lat"]
        elif "center" in el:  # way dengan out center
            lon, lat = el["center"]["lon"], el["center"]["lat"]
        else:
            continue

        tags = el.get("tags", {})
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "osm_id": el["id"],
                "osm_type": el["type"],
                "kelompok": kategori,
                "kategori_asli": json.dumps(tags, ensure_ascii=False),
                "name": tags.get("name"),
                **{k: v for k, v in tags.items() if k in
                   ("shop", "amenity", "office", "building", "landuse",
                    "railway", "public_transport", "highway", "leisure")},
            },
        })

    return {"type": "FeatureCollection", "features": features}


# Mirror publik Overpass. overpass-api.de kadang 406 kalau header Accept/
# Content-Type di-override manual (konflik dengan proxy-nya) - solusinya
# biarkan requests library yang atur header default, jangan dipaksa.
# overpass.openstreetmap.fr dipilih sebagai mirror kedua (lebih stabil untuk
# query area Indonesia dibanding mirror .ru yang endpoint-nya sering berubah).
OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter",
]

HEADERS = {
    # Cukup User-Agent saja. JANGAN set Accept/Content-Type manual -
    # itu penyebab 406 di overpass-api.de karena bentrok dengan proxy-nya.
    "User-Agent": "STATIONOMICS-DataAcquisition/1.0 (kompetisi MAPID WebGIS 2026; kontak: ganti-email-tim@example.com)",
}


def fetch_group(nama: str, query: str, max_retry: int = 3) -> dict:
    print(f"[{nama}] mengirim query ke Overpass...")
    last_err = None
    for mirror in OVERPASS_MIRRORS:
        for attempt in range(1, max_retry + 1):
            try:
                resp = requests.post(
                    mirror,
                    data={"data": query},
                    headers=HEADERS,
                    timeout=TIMEOUT_S + 30,
                )
                if resp.status_code != 200:
                    # Cetak potongan body respons - Overpass biasanya kasih
                    # pesan error spesifik (mis. rate_limited, syntax error)
                    # di dalam body meski status code-nya generic.
                    snippet = resp.text[:300].replace("\n", " ")
                    print(f"[{nama}] {mirror} status {resp.status_code}: {snippet}")
                resp.raise_for_status()
                data = resp.json()
                n = len(data.get("elements", []))
                print(f"[{nama}] berhasil via {mirror}, {n} elemen diterima.")
                return data
            except requests.exceptions.RequestException as e:
                last_err = e
                print(f"[{nama}] {mirror} percobaan {attempt}/{max_retry} gagal: {e}")
                if attempt < max_retry:
                    time.sleep(10 * attempt)  # backoff
        print(f"[{nama}] pindah ke mirror berikutnya...")
    raise RuntimeError(
        f"[{nama}] gagal di semua mirror. Error terakhir: {last_err}. "
        f"Kalau semua mirror gagal terus, bbox kemungkinan masih kebesaran "
        f"untuk endpoint publik, atau jaringan lokal (proxy/firewall) "
        f"memblokir - pindah ke jalur bulk: download PBF dari Geofabrik "
        f"(download.geofabrik.de/asia/indonesia.html) lalu filter offline "
        f"pakai pyrosm/osmium. Saya bisa siapkan skrip itu kalau perlu."
    )


def main():
    for nama, query in QUERIES.items():
        raw = fetch_group(nama, query)
        geojson = overpass_to_geojson(raw, nama)
        out_path = OUT_DIR / f"{nama}.geojson"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(geojson, f, ensure_ascii=False, indent=2)
        print(f"[{nama}] disimpan -> {out_path} ({len(geojson['features'])} titik)\n")
        time.sleep(2)  # jeda sopan antar query ke server publik

    print("Selesai. Ingat: cantumkan atribusi '© OpenStreetMap contributors' "
          "di halaman Metodologi, dan jangan publikasikan file GeoJSON mentah ini "
          "kalau sudah digabung dengan sumber lain (ODbL share-alike).")


if __name__ == "__main__":
    main()