import hashlib
import sqlite3
import streamlit as st
import pandas as pd
import os
from graphviz import Digraph

# ===================== KONFIGURASI STREAMLIT =====================
st.set_page_config(layout="wide")  # Pastikan paparan lebar penuh

# ===================== FUNGSI DATABASE =====================
def create_tables():
    conn = sqlite3.connect("family_tree.db")
    cursor = conn.cursor()

    # Buat jadual pengguna jika belum ada
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

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
    dot.attr(dpi="100", size="10,6", bgcolor="#ffffff")  # Saiz lebih besar untuk elak grafik terpotong

    # Pilih data yang perlu dipaparkan
    if selected_parent_id is None:
        selected_data = data
    else:
        selected_data = [row for row in data if row[3] and selected_parent_id in row[3].split(",")]

    # Tambah nod (ahli keluarga)
    for row in selected_data:
        id, name, spouse, parent_id, birth_date, phone, interest, owner_id = row

        # Pastikan nama tidak kosong
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

menu = st.radio("Pilih Menu:", ["Login", "Daftar Akaun"], key="menu_selector")

if menu == "Login":
    st.subheader("🔑 Login ke Aplikasi")
    username = st.text_input("Nama Pengguna")
    password = st.text_input("Kata Laluan", type="password")
    if st.button("Login"):
        st.success(f"✅ Selamat datang, {username}!")
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.rerun()

elif menu == "Daftar Akaun":
    st.subheader("📝 Daftar Akaun Baru")
    new_username = st.text_input("Nama Pengguna Baru")
    new_password = st.text_input("Kata Laluan Baru", type="password")
    if st.button("Daftar"):
        register_user(new_username, new_password)
        st.success("✅ Akaun berjaya didaftarkan! Sila login.")

if st.session_state.get("logged_in", False):
    st.subheader("🎉 Selamat Datang ke Aplikasi Keluarga!")

    st.header("📋 Senarai Ahli Keluarga")
    family_df = get_family_dataframe()
    st.dataframe(family_df)

    # Pilih ID Induk untuk paparan pohon
    st.header("🔍 Paparkan Pohon Berdasarkan Induk")
    parent_id_search = st.selectbox("Pilih ID Induk", family_df["ID"].astype(str))

    if st.button("Paparkan Pohon"):
        tree_path = draw_family_tree_graphviz(parent_id_search)
        st.image(tree_path, use_column_width=True)  # Pastikan grafik mengisi ruang sepenuhnya

    # ===================== TAMBAH & PADAM AHLI KELUARGA =====================
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
            user_id = st.session_state["user_id"]
            add_family_member(name, spouse, parent_id, birth_date, phone, interest, user_id)
            st.success(f"{name} berjaya ditambah!")
            st.rerun()

    st.header("🗑️ Padam Ahli Keluarga")
    delete_id = st.selectbox("Pilih ID untuk Padam", family_df["ID"].astype(str))
    if st.button("❌ Padam Ahli"):
        delete_family_member(delete_id)
        st.warning(f"Ahli dengan ID {delete_id} telah dipadam!")
        st.rerun()
