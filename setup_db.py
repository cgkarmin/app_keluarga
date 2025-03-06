import sqlite3

# Buat database SQLite
conn = sqlite3.connect("family_tree.db")
cursor = conn.cursor()

# Hapuskan jadual lama jika ada dan buat yang baru
cursor.execute("DROP TABLE IF EXISTS family")

cursor.execute("""
CREATE TABLE family (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    spouse TEXT,
    parent_id TEXT,  -- Simpan ID ibu bapa dalam format "1,2"
    birth_date TEXT,
    phone TEXT,
    interest TEXT
)
""")

# Masukkan data keluarga
family_data = [
    ("Samijah", "Abbas", None, None, None, None),  # ID 1
    ("Abbas", "Samijah", None, None, None, None),  # ID 2
    ("Suwardi", "Zubaidah", "1,
