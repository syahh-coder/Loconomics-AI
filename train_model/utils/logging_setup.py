"""
logging_setup.py
===================
Logging terpusat dipakai semua modul pipeline. Import get_logger(nama)
di tiap modul, jangan pakai print() langsung supaya semua log konsisten
formatnya dan bisa diarahkan ke file kalau perlu.
"""

import logging
import sys


def get_logger(nama: str) -> logging.Logger:
    logger = logging.getLogger(nama)
    if logger.handlers:
        # Sudah pernah di-setup (mis. dipanggil ulang di sesi yang sama),
        # jangan tambah handler dobel - itu bikin tiap log tercetak berkali-kali
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
