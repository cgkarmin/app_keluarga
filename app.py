import hashlib
import sqlite3
import streamlit as st
import pandas as pd
import os

# ===================== SEMAK GRAPHVIZ =====================
try:
    # Semak jika Graphviz tersedia dalam sistem
    if not os.path.exists("/usr/bin/dot") and not os.path.exists("/usr/local/bin/dot"):
        st.error("❌ Graphviz tidak tersedia dalam sistem Streamlit Cloud. Sila semak `packages.txt`.")
        st.stop()

    import graphviz
    from graphviz import Digraph
except ImportError:
    st.error("❌ Modul Python `graphviz` tidak tersedia! Pastikan `requirements.txt` mengandungi 'python-graphviz'.")
    st.stop()

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
        dot.node(str(id), label, shape="box", style="filled", fillcolor="#87CEEB", fontcolor="black")

        # Hubungkan dengan induk (parent)
        if parent_id:
            parent_ids = str(parent_id).split(",")
            for pid in parent_ids:
                pid = pid.strip()
                if pid.isdigit():
                    dot.edge(pid, str(id))  # Hubungkan induk ke anak

    # Simpan fail gambar sementara
    output_path = "family_tree"
    dot.render(output_path, format="png", cleanup=True)
    
    return output_path + ".png"

# ===================== PAPARAN STREAMLIT =====================
create_tables()

st.title("🌳 Aplikasi Pokok Keluarga")

menu = st.radio("Pilih Menu:", ["Papar Pokok Keluarga", "Tambah Ahli Keluarga", "Padam Ahli Keluarga"])

if menu == "Papar Pokok Keluarga":
    st.subheader("🔍 Paparkan Pohon Berdasarkan Induk")
    family_df = get_family_dataframe()
    if family_df.empty:
        st.warning("Tiada data ahli keluarga!")
    else:
        parent_id_search = st.selectbox("Pilih ID Induk", family_df["ID"].astype(str))
        if st.button("Paparkan Pohon"):
            tree_path = draw_family_tree_graphviz(parent_id_search)
            st.image(tree_path, use_column_width=True)

elif menu == "Tambah Ahli Keluarga":
    st.header("🆕 Tambah Ahli Keluarga")
    with st.form("add_member"):
        name = st.text_input("Nama")
        spouse = st.text_input("Pasangan")
        parent_id = st.text_input("ID Induk")
        birth_date = st.text_input("Tarikh Lahir")
        phone = st.text_input("Telefon")
        interest = st.text_area("Minat")
        submitted = st.form_submit_button("Tambah Ahli")
        if submitted:
            conn = sqlite3.connect("family_tree.db")
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO family (name, spouse, parent_id, birth_date, phone, interest, owner_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, spouse, parent_id, birth_date, phone, interest, 1))
            conn.commit()
            conn.close()
            st.success(f"{name} berjaya ditambah!")
            st.rerun()

elif menu == "Padam Ahli Keluarga":
    st.header("🗑️ Padam Ahli Keluarga")
    family_df = get_family_dataframe()
    if family_df.empty:
        st.warning("Tiada ahli keluarga untuk dipadam.")
    else:
        delete_id = st.selectbox("Pilih ID untuk Padam", family_df["ID"].astype(str))
        if st.button("❌ Padam Ahli"):
            conn = sqlite3.connect("family_tree.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM family WHERE id=?", (delete_id,))
            conn.commit()
            conn.close()
            st.warning(f"Ahli dengan ID {delete_id} telah dipadam!")
            st.rerun()
