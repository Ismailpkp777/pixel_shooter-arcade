import os

SCORE_FILE = "scores.txt"

def save_score(score):
    """Simpan skor ke dalam file scores.txt"""
    with open(SCORE_FILE, "a") as file:
        file.write(f"{score}\n")

def get_high_scores(limit=5):
    """Ambil skor tertinggi dari file"""
    if not os.path.exists(SCORE_FILE):
        return []
    
    with open(SCORE_FILE, "r") as file:
        scores = [int(line.strip()) for line in file.readlines()]
    
    scores.sort(reverse=True)  # Urutkan dari terbesar ke terkecil
    return scores[:limit]
