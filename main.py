import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Kaffesa B2 Depo Kontrol Sistemi", layout="wide")

# Google Sheets CSV linki
DATA_FILE = "https://drive.google.com/file/d/1F2YiVArQCUXh34yyJNTKGMOwJ_d0QWiM/view?usp=share_link"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    # Sütun isimlerini temizle
    df.columns = df.columns.str.strip()
    # Parça kodunu string yap ve boşlukları temizle
    df["Kod_Temp"] = df["Parça Kodu"].astype(str).str.strip().str.upper()
    return df

df = load_data()

# --- Sütun isimlerini ekrana yaz (debug için) ---
st.write("**CSV Sütunları:**", df.columns.tolist())

st.title("Kaffesa B2 Depo Kontrol Sistemi")

# --- Parça kodu girişi ---
kod_girisi = st.text_input("Parça kodlarını girin (boşlukla ayırın):")

if kod_girisi:
    kodlar = [k.strip().upper() for k in kod_girisi.split()]
    filtre = df[df["Kod_Temp"].isin(kodlar)]

    if not filtre.empty:
        st.dataframe(filtre[["Parça Kodu", "Parça Adı", "KONUM", "Marka", "Stok"]])
    else:
        st.warning("Parça bulunamadı. Kodları ve CSV sütunlarını kontrol edin!")
