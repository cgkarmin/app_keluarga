import streamlit as st
import pandas as pd
import sqlite3

# ===================== KONFIGURASI STREAMLIT =====================
st.set_page_config(layout="wide")  # Pastikan paparan penuh & kemas

# ===================== FUNGSI DATABASE =====================
def create_tables():
    """Membuat jadual database jika belum wujud."""
    conn = sqlite3.connect("family_tree.db")
    cursor = conn.cursor()
    
    # Buat jadual pengguna untuk login
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    
    # Buat jadual keluarga
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

# Fungsi mendapatkan data keluarga dalam DataFrame
def get_family_dataframe():
    """Mendapatkan data keluarga dalam bentuk Pandas DataFrame."""
    conn = sqlite3.connect("family_tree.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM family")
    data = cursor.fetchall()
    conn.close()
    
    df = pd.DataFrame(data, columns=["ID", "Nama", "Pasangan", "Induk (Parent ID)", "Tarikh Lahir", "Telefon", "Minat", "Owner ID"])
    return df

# Fungsi untuk semak login pengguna
def authenticate(username, password):
    conn = sqlite3.connect("family_tree.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# ===================== PAPARAN STREAMLIT =====================
create_tables()  # Pastikan database tersedia sebelum aplikasi dimuatkan

st.title("🌳 Aplikasi Pokok Keluarga")

# ===================== LOGIN SISTEM =====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.subheader("🔐 Sila Log Masuk")
    username = st.text_input("Nama Pengguna", key="username")
    password = st.text_input("Kata Laluan", type="password", key="password")
    
    if st.button("Login"):
        user = authenticate(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.error("❌ Nama pengguna atau kata laluan salah!")

    st.stop()  # Hentikan aplikasi jika belum login

# ===================== MENU UTAMA =====================
st.success(f"✅ Selamat datang, **{st.session_state.username}**!")

st.subheader("📋 Senarai Ahli Keluarga & Tambah Ahli Baru")

family_df = get_family_dataframe()

# Paparkan Senarai Keluarga
if family_df.empty:
    st.warning("⚠ Tiada data ahli keluarga!")
else:
    st.dataframe(family_df, use_container_width=True)

# ===================== TAMBAH AHLI KELUARGA =====================
st.header("🆕 Tambah Ahli Keluarga")
with st.form("add_member"):
    name = st.text_input("Nama")
    spouse = st.text_input("Pasangan")
    parent_id = st.text_input("ID Induk (Boleh kosong jika tiada)")
    birth_date = st.text_input("Tarikh Lahir")
    phone = st.text_input("Telefon")
    interest = st.text_area("Minat")
    submitted = st.form_submit_button("✅ Tambah Ahli")

    if submitted:
        conn = sqlite3.connect("family_tree.db")
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO family (name, spouse, parent_id, birth_date, phone, interest, owner_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, spouse, parent_id, birth_date, phone, interest, 1))
        conn.commit()
        conn.close()
        st.success(f"🎉 {name} berjaya ditambah!")
        st.experimental_rerun()
