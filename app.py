import streamlit as st
import pandas as pd
import sqlite3

# ===================== KONFIGURASI STREAMLIT =====================
st.set_page_config(layout="wide")

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
        owner_id INTEGER
    )
    """)

    conn.commit()
    conn.close()

def get_family_dataframe(user_id):
    """Dapatkan senarai keluarga berdasarkan pengguna."""
    conn = sqlite3.connect("family_tree.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM family WHERE owner_id=?", (user_id,))
    data = cursor.fetchall()
    conn.close()
    
    df = pd.DataFrame(data, columns=["ID", "Nama", "Pasangan", "Induk (Parent ID)", "Tarikh Lahir", "Telefon", "Minat", "Owner ID"])
    return df

def authenticate(username, password):
    conn = sqlite3.connect("family_tree.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

def register_user(username, password):
    """Daftar pengguna baru ke dalam database."""
    conn = sqlite3.connect("family_tree.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        st.success("🎉 Pendaftaran berjaya! Sila log masuk.")
    except sqlite3.IntegrityError:
        st.error("❌ Nama pengguna sudah wujud. Sila cuba yang lain.")
    finally:
        conn.close()

# ===================== PAPARAN STREAMLIT =====================
create_tables()  # Pastikan database tersedia sebelum aplikasi dimuatkan

st.title("🌳 Aplikasi Pokok Keluarga")

# ===================== SISTEM LOGIN =====================
if "user_id" not in st.session_state:
    st.session_state.user_id = None

tab_login, tab_register, tab_forgot = st.tabs(["🔐 Log Masuk", "🆕 Daftar Akaun", "🔑 Lupa Kata Laluan"])

# **TAB 1: LOGIN**
with tab_login:
    st.subheader("🔐 Log Masuk")
    username = st.text_input("Nama Pengguna", key="login_user")
    password = st.text_input("Kata Laluan", type="password", key="login_pass")
    
    if st.button("Login"):
        user_id = authenticate(username, password)
        if user_id:
            st.session_state.user_id = user_id
            st.session_state.username = username
            st.rerun()
        else:
            st.error("❌ Nama pengguna atau kata laluan salah!")

if st.session_state.user_id is None:
    st.stop()  # Hentikan aplikasi jika belum login

# **TAB 2: DAFTAR AKAUN**
with tab_register:
    st.subheader("🆕 Daftar Akaun Baru")
    
    new_username = st.text_input("Nama Pengguna", key="register_user")
    new_password = st.text_input("Kata Laluan", type="password", key="register_pass")
    confirm_password = st.text_input("Sahkan Kata Laluan", type="password", key="confirm_pass")

    if st.button("📝 Daftar"):
        if not new_username or not new_password or not confirm_password:
            st.error("❌ Semua ruangan mesti diisi!")
        elif new_password != confirm_password:
            st.error("❌ Kata laluan tidak sepadan!")
        else:
            register_user(new_username, new_password)
            st.success("✅ Akaun berjaya didaftarkan! Sila log masuk.")

# ===================== MENU UTAMA =====================
st.success(f"✅ Selamat datang, **{st.session_state.username}**!")

st.subheader("📋 Senarai Ahli Keluarga & Tambah Ahli Baru")

family_df = get_family_dataframe(st.session_state.user_id)

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
        """, (name, spouse, parent_id, birth_date, phone, interest, st.session_state.user_id))
        conn.commit()
        conn.close()
        st.success(f"🎉 {name} berjaya ditambah!")
        st.rerun()

# ===================== SEMAK DATABASE (UNTUK DEBUG) =====================
if st.button("🔍 Semak Database"):
    conn = sqlite3.connect("family_tree.db")
    cursor = conn.cursor()
    users = cursor.execute("SELECT * FROM users").fetchall()
    family = cursor.execute("SELECT * FROM family").fetchall()
    conn.close()
    
    st.subheader("👤 Senarai Pengguna")
    st.dataframe(pd.DataFrame(users, columns=["ID", "Nama Pengguna", "Kata Laluan"]) if users else "Tiada pengguna dalam database.")

    st.subheader("👨‍👩‍👧‍👦 Senarai Ahli Keluarga")
    st.dataframe(pd.DataFrame(family, columns=["ID", "Nama", "Pasangan", "Induk (Parent ID)", "Tarikh Lahir", "Telefon", "Minat", "Owner ID"]) if family else "Tiada ahli keluarga dalam database.")
