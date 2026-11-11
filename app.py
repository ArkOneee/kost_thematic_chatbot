import os
import json
import uuid
from flask import Flask, render_template, request, jsonify, session
from chatbot.engine import ChatbotEngine
from chatbot.database import ChatHistory

app = Flask(__name__)
# SECRET_KEY wajib ada untuk mengamankan cookie pengguna
app.secret_key = "kunci-rahasia-kosbot-sangat-aman"

# 1. Inisialisasi Database
history = ChatHistory("chat_history.db")

# 2. Fungsi Memuat Tema (Membaca file JSON)
def load_themes():
    themes = {}
    engines = {}
    # Membaca otomatis semua file .json di dalam folder themes/
    for filename in os.listdir("themes"):
        if filename.endswith(".json"):
            path = os.path.join("themes", filename)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                tid = data["id"]
                themes[tid] = data
                engines[tid] = ChatbotEngine(data)
    return themes, engines

THEMES, ENGINES = load_themes()

# 3. Manajemen Sesi Pengguna (Cookie)
def get_session_id():
    """Membuat ID unik untuk setiap pengunjung agar riwayat chat tidak tertukar"""
    if "sid" not in session:
        session["sid"] = uuid.uuid4().hex
    return session["sid"]

# 4. Route Halaman Utama
@app.route("/")
def index():
    return render_template("index.html", themes=THEMES.values())

# 5. Route Halaman Chat
@app.route("/chat/<theme_id>")
def chat_page(theme_id):
    if theme_id not in THEMES:
        return "Tema tidak ditemukan", 404
    return render_template("chat.html", theme=THEMES[theme_id])

# 6. REST API Endpoint: Menerima Pesan dari Frontend
@app.post("/api/chat")
def api_chat():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Body harus berformat JSON"}), 400
    
    message = str(data.get("message", "")).strip()
    theme_id = str(data.get("theme", "")).strip()

    # Validasi Input Dasar
    if not message:
        return jsonify({"error": "Pesan tidak boleh kosong"}), 400
    if len(message) > 500:
        return jsonify({"error": "Pesan maksimal 500 karakter"}), 400
    if theme_id not in ENGINES:
        return jsonify({"error": "Tema tidak valid"}), 400

    # Serahkan pesan ke mesin chatbot (engine.py)
    engine = ENGINES[theme_id]
    hasil = engine.reply(message)

    # Simpan riwayat chat ke SQLite (database.py)
    sid = get_session_id()
    history.save_message(sid, theme_id, "user", message)
    history.save_message(sid, theme_id, "bot", hasil["reply"], hasil["intent"], hasil["score"])

    # Kembalikan jawaban ke browser
    return jsonify(hasil)

# 7. REST API Endpoint: Mengambil Riwayat Sesi
@app.get("/api/history/<theme_id>")
def api_history(theme_id):
    sid = get_session_id()
    percakapan = history.get_history(sid, theme_id)
    return jsonify(percakapan)

if __name__ == "__main__":
    # Jalankan server dalam mode debug untuk tahap pengembangan
    app.run(debug=True)