import sqlite3
from datetime import datetime

class ChatHistory:
    def __init__(self, db_path="chat_history.db"):
        self.db_path = db_path
        self.create_table()

    def _get_connection(self):
        """Membuat koneksi ke database SQLite"""
        conn = sqlite3.connect(self.db_path)
        # Mengatur agar hasil query bisa diakses seperti dictionary
        conn.row_factory = sqlite3.Row 
        return conn

    def create_table(self):
        """Membuat tabel messages sesuai struktur di materi praktikum"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    theme TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    text TEXT NOT NULL,
                    intent TEXT,
                    score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def save_message(self, session_id, theme, sender, text, intent=None, score=None):
        """Menyimpan satu baris pesan (dari user atau bot) ke database"""
        with self._get_connection() as conn:
            # Menggunakan parameter '?' untuk mencegah celah keamanan SQL Injection
            conn.execute("""
                INSERT INTO messages (session_id, theme, sender, text, intent, score) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, theme, sender, text, intent, score))

    def get_history(self, session_id, theme):
        """Mengambil riwayat percakapan untuk ditampilkan di layar chat web"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT sender, text FROM messages
                WHERE session_id = ? AND theme = ?
                ORDER BY id ASC
            """, (session_id, theme)).fetchall()
            return [{"sender": row["sender"], "text": row["text"]} for row in rows]

    def get_stats(self, theme):
        """Menghitung jumlah pertanyaan per intent untuk halaman Admin"""
        with self._get_connection() as conn:
            # COALESCE digunakan untuk mengubah nilai kosong menjadi teks '(tidak dikenali)'
            rows = conn.execute("""
                SELECT COALESCE(intent, '(tidak dikenali)') as intent_name, COUNT(*) as count 
                FROM messages 
                WHERE theme = ? AND sender = 'user' 
                GROUP BY intent 
                ORDER BY count DESC
            """, (theme,)).fetchall()
            return [{"intent": row["intent_name"], "jumlah": row["count"]} for row in rows]

    def get_unrecognized(self, theme, limit=5):
        """Mengambil daftar pertanyaan user yang gagal dikenali (untuk evaluasi)"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT text, score, created_at 
                FROM messages 
                WHERE theme = ? AND sender = 'user' AND (intent IS NULL OR intent = '') 
                ORDER BY id DESC LIMIT ?
            """, (theme, limit)).fetchall()
            return [{"pertanyaan": row["text"], "skor": row["score"], "waktu": row["created_at"]} for row in rows]

    def clear_session(self, session_id, theme):
        """Menghapus riwayat chat untuk sesi tertentu"""
        with self._get_connection() as conn:
            conn.execute("""
                DELETE FROM messages 
                WHERE session_id = ? AND theme = ?
            """, (session_id, theme))