import streamlit as st
import pandas as pd
import sqlite3
from graphviz import Digraph

# ===================== KONFIGURASI STREAMLIT =====================
st.set_page_config(layout="wide")  # Pastikan paparan penuh

# ===================== FUNGSI DATABASE =====================
def create_tables():
    conn = sqlite3.connect("family_tree.db")
    cursor = conn.cursor()

    # Buat jadual keluarga jika belum ada
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS family (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        spouse TEXT,
        parent_id TEXT,
        birth_date TEXT,
        phone TEXT,
        interest TEXT,
        owner_id INTEGER NOT NULL
    )
    """)

    conn.commit()
    conn.close()

# Fungsi untuk mendapatkan senarai keluarga dalam DataFrame
def get_family_dataframe():
    conn = sqlite3.connect("family_tree.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM family")
    data = cursor.fetchall()
    conn.close()
    
    df = pd.DataFrame(data, columns=["ID", "Nama", "Pasangan", "Induk (Parent ID)", "Tarikh Lahir", "Telefon", "Minat", "Owner ID"])
    return df

# ===================== POHON KELUARGA DENGAN GRAPHVIZ =====================
def draw_family_tree_graphviz(selected_parent_id=None):
    data = get_family_dataframe().values.tolist()
    
    dot = Digraph(format="png")
    dot.attr(dpi="100", size="10,6", bgcolor="#ffffff")  # Saiz besar untuk elak terpotong

    # Pilih data yang perlu dipaparkan
    if selected_parent_id is None:
        selected_data = data
    else:
        selected_data = [row for row in data if row[3] and selected_parent_id in row[3].split(",")]

    # Tambah nod (ahli keluarga)
    for row in selected_data:
        id, name, spouse, parent_id, birth_date, phone, interest, owner_id = row
        label = name if name else f"ID: {id}"
        dot.node(str(id),
