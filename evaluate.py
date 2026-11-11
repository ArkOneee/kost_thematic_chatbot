import os
import csv
import json
from chatbot.engine import ChatbotEngine

def run_evaluation(theme_id="kos"):
    # 1. Memuat data pola dari file JSON
    theme_path = os.path.join("themes", f"{theme_id}.json")
    try:
        with open(theme_path, "r", encoding="utf-8") as f:
            theme_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File tema {theme_path} tidak ditemukan.")
        return

    # Menghidupkan mesin chatbot
    engine = ChatbotEngine(theme_data)

    # 2. Membaca data uji dari file CSV
    csv_path = os.path.join("evaluasi", f"{theme_id}.csv")
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            # skipinitialspace berguna agar spasi setelah koma (misal: "kalimat, intent") diabaikan
            reader = csv.DictReader(f, skipinitialspace=True) 
            
            total_kalimat = 0
            benar = 0
            salah_list = []

            print(f"=== HASIL EVALUASI TEMA: {theme_data.get('bot_name', 'Bot')} ===")
            print(f"Ambang batas (Threshold): {engine.threshold}\n")

            for row in reader:
                kalimat = row.get("kalimat", "").strip()
                intent_harapan = row.get("intent", "").strip()

                if not kalimat:
                    continue
                
                total_kalimat += 1
                
                # Mesin mencoba menebak kalimat dari CSV
                intent_tebakan, skor = engine.classify(kalimat)

                # Jika skor di bawah threshold (fallback), intent_tebakan bernilai None
                # Kita ubah menjadi string "fallback" agar bisa dicocokkan dengan isi CSV
                intent_tebakan_str = intent_tebakan if intent_tebakan else "fallback"

                # 3. Mencocokkan tebakan mesin dengan harapan di CSV
                if intent_tebakan_str == intent_harapan:
                    benar += 1
                else:
                    salah_list.append({
                        "kalimat": kalimat,
                        "harapan": intent_harapan,
                        "tebakan": intent_tebakan_str,
                        "skor": skor
                    })

    except FileNotFoundError:
        print(f"Error: File evaluasi {csv_path} tidak ditemukan.")
        return

    # 4. Menghitung dan Menampilkan Akurasi Akhir
    if total_kalimat == 0:
        print("Tidak ada data kalimat di dalam file CSV.")
        return

    # Rumus Akurasi = (Tebakan Benar / Total Kalimat) * 100
    akurasi = (benar / total_kalimat) * 100
    
    print(f"Total Kalimat Uji : {total_kalimat}")
    print(f"Ditebak Benar     : {benar}")
    print(f"Ditebak Salah     : {len(salah_list)}")
    print(f"Akurasi Akhir     : {akurasi:.2f}%\n")

    # Menampilkan rincian kalimat yang gagal ditebak agar bisa diperbaiki
    if salah_list:
        print("--- DAFTAR KALIMAT YANG SALAH DITEBAK ---")
        for item in salah_list:
            print(f"Kalimat : \"{item['kalimat']}\"")
            print(f"Harapan : {item['harapan']} | Tebakan Mesin: {item['tebakan']} (Skor: {item['skor']:.2f})\n")

if __name__ == "__main__":
    run_evaluation("kos")