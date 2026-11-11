import os
import json
import pytest
from chatbot.engine import ChatbotEngine

# 1. Menyiapkan Data Engine untuk Pengujian
@pytest.fixture
def engine():
    path = os.path.join("themes", "kos.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ChatbotEngine(data)

# 2. Kasus Uji 1: Praproses dan Normalisasi
def test_praproses_normalisasi(engine):
    # Menguji apakah 'gmn' diubah jadi 'bagaimana' dan 'sih' dihapus
    tokens = engine.preprocess("gmn sih cara bayar")
    assert "bagaimana" in tokens
    assert "sih" not in tokens

# 3. Kasus Uji 2: Klasifikasi Salam
def test_klasifikasi_salam(engine):
    tag, skor = engine.classify("halo selamat pagi")
    assert tag == "salam_identitas"
    assert skor >= 0.45

# 4. Kasus Uji 3: Klasifikasi Pembayaran
def test_klasifikasi_pembayaran(engine):
    tag, skor = engine.classify("bayar kos kemana ya")
    assert tag == "info_pembayaran"
    assert skor >= 0.45

# 5. Kasus Uji 4: Typo Tetap Dikenali
def test_salah_ketik_dikenali(engine):
    # Menguji fuzzy matching
    tag, skor = engine.classify("listrik mti")
    assert tag == "lapor_listrik_air"
    assert skor >= 0.45

# 6. Kasus Uji 5: Fallback
def test_pertanyaan_luar_tema_fallback(engine):
    # Harus ditolak (skor di bawah 0.45) karena tidak ada di JSON
    tag, skor = engine.classify("siapa presiden indonesia?")
    assert tag is None
    assert skor < 0.45

# 7. Kasus Uji 6: Lapor Kerusakan
def test_klasifikasi_kerusakan(engine):
    tag, skor = engine.classify("ac kamar saya bocor nih")
    assert tag == "lapor_kerusakan_kamar"
    assert skor >= 0.45

# 8. Kasus Uji 7: Struktur JSON Balasan Benar
def test_reply_berisi_data_lengkap(engine):
    hasil = engine.reply("aturan jam malam")
    assert "reply" in hasil
    assert hasil["intent"] == "aturan_jam_malam"
    assert hasil["score"] >= 0.45

# 9. Kasus Uji 8: Balasan Fallback Sesuai JSON
def test_reply_fallback_tepat(engine):
    hasil = engine.reply("resep nasi goreng")
    assert hasil["intent"] is None
    # Harus memuat penggalan kalimat fallback dari JSON
    assert "Maaf, saya hanya bisa menjawab pertanyaan seputar layanan kos" in hasil["reply"]