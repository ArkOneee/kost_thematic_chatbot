import re
import random
from difflib import SequenceMatcher
from datetime import datetime

# Kamus untuk memperbaiki salah ketik atau kata gaul (Normalisasi)
NORMALISASI = {
    "gmn": "bagaimana",
    "bgmn": "bagaimana",
    "brp": "berapa",
    "byr": "bayar",
    "bocorrr": "bocor",
    "lemot": "lambat",
    "nginep": "menginap",
    "gak": "tidak",
    "ga": "tidak",
    "aja": "saja",
    "kalo": "kalau"
}

# Kata-kata umum yang dibiarkan 
STOPWORDS = {"yang", "di", "ke", "dari", "ini", "itu", "untuk", "ya", "sih", "dong", "kak", "min", "saya", "nya", "nih", "aku"}

class ChatbotEngine:
    def __init__(self, theme_data):
        self.theme = theme_data
        self.intents = theme_data.get("intents", [])
        self.threshold = 0.45 # Ambang batas skor kemiripan

    def preprocess(self, teks):
        """Langkah 1 & 2: Huruf kecil dan buang tanda baca"""
        teks = re.sub(r"[^a-z0-9\s]", "", teks.lower())
        tokens = []
        
        """Langkah 3 & 4: Tokenizing, normalisasi, dan buang stopword"""
        for kata in teks.split():
            norm_word = NORMALISASI.get(kata, kata)
            for k in norm_word.split():
                if k and k not in STOPWORDS:
                    tokens.append(k)
        return tokens

    def similarity(self, tokens_pesan, tokens_pola):
        """Menghitung skor kemiripan gabungan"""
        if not tokens_pesan or not tokens_pola:
            return 0.0

        set_pesan = set(tokens_pesan)
        set_pola = set(tokens_pola)

        # 1. Jaccard Similarity (Bobot 40%)
        irisan = len(set_pesan & set_pola)
        gabungan = len(set_pesan | set_pola)
        jaccard = irisan / gabungan if gabungan > 0 else 0

        # 2. Fuzzy / Kemiripan Huruf (Bobot 30%)
        str_pesan = " ".join(tokens_pesan)
        str_pola = " ".join(tokens_pola)
        fuzzy = SequenceMatcher(None, str_pesan, str_pola).ratio()

        # 3. Cakupan (Bobot 30%)
        cakupan = irisan / len(set_pola) if len(set_pola) > 0 else 0

        # Hitung skor total
        skor = (0.4 * jaccard) + (0.3 * fuzzy) + (0.3 * cakupan)
        return skor

    def classify(self, pesan):
        """Mencari pola dengan skor tertinggi"""
        tokens_pesan = self.preprocess(pesan)
        kandidat = []

        for intent in self.intents:
            for pola in intent.get("patterns", []):
                tokens_pola = self.preprocess(pola)
                skor = self.similarity(tokens_pesan, tokens_pola)
                kandidat.append({"tag": intent["tag"], "skor": skor, "pola": pola})

        if not kandidat:
            return None, 0.0

        # Urutkan dari skor tertinggi ke terendah
        kandidat.sort(key=lambda x: x["skor"], reverse=True)
        terbaik = kandidat[0]

        # Cek apakah skor mencapai ambang batas (threshold 0.45)
        if terbaik["skor"] >= self.threshold:
            return terbaik["tag"], terbaik["skor"]
        else:
            return None, terbaik["skor"]

    def reply(self, pesan):
        """Memberikan jawaban (NLG) berdasarkan intent yang terpilih"""
        tag, skor = self.classify(pesan)
        
        if tag is None:
            # Jika skor di bawah threshold, ambil dari array fallback
            teks = random.choice(self.theme.get("fallback", ["Maaf, saya tidak mengerti."]))
        else:
            # Jika lolos threshold, ambil respons acak dari intent yang cocok
            for intent in self.intents:
                if intent["tag"] == tag:
                    teks = random.choice(intent.get("responses", ["..."]))
                    break
        
        # Mengganti placeholder  
        waktu_sekarang = datetime.now().strftime("%H:%M")
        teks = teks.replace("{waktu}", waktu_sekarang).replace("{nama_bot}", self.theme.get("bot_name", "Bot"))

        return {
            "reply": teks,
            "intent": tag,
            "score": round(skor, 2)
        }