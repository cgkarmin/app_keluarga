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

# ===================== PAPARAN STREAMLIT =====================
create_tables()  # Pastikan database tersedia sebelum aplikasi dimuatkan

st.title("🌳 Aplikasi Pokok Keluarga")

menu = st.radio("📌 Pilih Menu:", ["Papar Senarai Keluarga", "Tambah Ahli Keluarga", "Padam Ahli Keluarga"])

# ========== 1️⃣ PAPAR SENARAI KELUARGA ==========
if menu == "Papar Senarai Keluarga":
    st.subheader("📋 Senarai Ahli Keluarga")
    family_df = get_family_dataframe()
    
    if family_df.empty:
        st.warning("⚠ Tiada data ahli keluarga!")
    else:
        st.dataframe(family_df, use_container_width=True)

# ========== 2️⃣ TAMBAH AHLI KELUARGA ==========
elif menu == "Tambah Ahli Keluarga":
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
            st.rerun()

# ========== 3️⃣ PADAM AHLI KELUARGA ==========
elif menu == "Padam Ahli Keluarga":
    st.header("🗑️ Padam Ahli Keluarga")
    family_df = get_family_dataframe()
    
    if family_df.empty:
        st.warning("⚠ Tiada ahli keluarga untuk dipadam.")
    else:
        delete_id = st.selectbox("🔽 Pilih ID untuk dipadam", family_df["ID"].astype(str))
        if st.button("❌ Padam Ahli"):
            conn = sqlite3.connect("family_tree.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM family WHERE id=?", (delete_id,))
            conn.commit()
            conn.close()
            st.warning(f"❌ Ahli dengan ID {delete_id} telah dipadam!")
            st.rerun()
