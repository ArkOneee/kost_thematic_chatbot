import json
import os
from chatbot.engine import ChatbotEngine

# Mengarahkan ke file tema yang sudah kita buat
THEME_FILE = os.path.join("themes", "kos.json")

def main():
    # 1. Membaca file JSON
    try:
        with open(THEME_FILE, "r", encoding="utf-8") as f:
            theme_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {THEME_FILE} tidak ditemukan!")
        return

    # 2. Menghidupkan mesin chatbot dengan data kos.json
    bot = ChatbotEngine(theme_data)
    
    print(f"=== UJI COBA TERMINAL: {theme_data.get('bot_name', 'Bot')} ===")
    print("Ketik 'keluar' untuk mengakhiri percakapan.\n")
    
    # 3. Looping percakapan di terminal
    while True:
        pesan = input("Anda: ")
        
        # Fitur untuk berhenti
        if pesan.lower() in ['keluar', 'exit', 'quit']:
            print("Berhenti.")
            break
            
        if not pesan.strip():
            continue
            
        # 4. Mesin memproses pesan dan mencari jawaban
        hasil = bot.reply(pesan)
        
        # 5. Menampilkan jawaban beserta data di balik layarnya (intent & skor)
        print(f"Bot : {hasil['reply']}")
        print(f"      [Intent yang ditebak: {hasil['intent']} | Skor: {hasil['score']}]\n")

if __name__ == "__main__":
    main()