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
        owner_id INTEGER NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()

# Fungsi mendapatkan data keluarga dalam DataFrame berdasarkan pengguna
def get_family_dataframe(user_id):
    """Dapatkan senarai keluarga berdasarkan pengguna."""
    conn = sqlite3.connect("family_tree.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM family WHERE owner_id=?", (user_id,))
    data = cursor.fetchall()
    conn.close()
    
    df = pd.DataFrame(data, columns=["ID", "Nama", "Pasangan", "Induk (Parent ID)", "Tarikh Lahir", "Telefon", "Minat", "Owner ID"])
    return df

# Fungsi untuk semak login pengguna
def authenticate(username, password):
    conn = sqlite3.connect("family_tree.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

# Fungsi untuk daftar pengguna baru
def register_user(username, password):
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

# Fungsi untuk reset kata laluan
def reset_password(username, new_password):
    conn = sqlite3.connect("family_tree.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
    conn.commit()
    conn.close()

# ===================== PAPARAN STREAMLIT =====================
create_tables()  # Pastikan database tersedia sebelum aplikasi dimuatkan

st.title("🌳 Aplikasi Pokok Keluarga")

# ===================== SISTEM LOGIN, PENDAFTARAN & RESET PASSWORD =====================
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
            st.experimental_rerun()
        else:
            st.error("❌ Nama pengguna atau kata laluan salah!")

# **TAB 2: PENDAFTARAN**
with tab_register:
    st.subheader("🆕 Daftar Akaun Baru")
    new_username = st.text_input("Nama Pengguna Baru", key="register_user")
    new_password = st.text_input("Kata Laluan", type="password", key="register_pass")
    
    if st.button("Daftar"):
        if new_username and new_password:
            register_user(new_username, new_password)
        else:
            st.error("⚠ Nama pengguna dan kata laluan tidak boleh kosong!")

# **TAB 3: LUPA KATA LALUAN**
with tab_forgot:
    st.subheader("🔑 Reset Kata Laluan")
    forgot_username = st.text_input("Nama Pengguna", key="forgot_user")
    new_password = st.text_input("Kata Laluan Baru", type="password", key="forgot_pass1")
    confirm_password = st.text_input("Sahkan Kata Laluan Baru", type="password", key="forgot_pass2")
    
    if st.button("Reset Kata Laluan"):
        if forgot_username and new_password and confirm_password:
            if new_password == confirm_password:
                conn = sqlite3.connect("family_tree.db")
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE username=?", (forgot_username,))
                user = cursor.fetchone()
                conn.close()
                
                if user:
                    reset_password(forgot_username, new_password)
                    st.success("✅ Kata laluan berjaya ditukar! Sila log masuk dengan kata laluan baru.")
                else:
                    st.error("❌ Nama pengguna tidak wujud!")
            else:
                st.error("⚠ Kata laluan baru tidak sepadan!")
        else:
            st.error("⚠ Semua medan mesti diisi!")

if st.session_state.user_id is None:
    st.stop()  # Hentikan aplikasi jika belum login

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
        st.experimental_rerun()

# ===================== BUTANG LOGOUT =====================
if st.button("🚪 Log Keluar"):
    st.session_state.user_id = None
    st.session_state.username = ""
    st.experimental_rerun()
