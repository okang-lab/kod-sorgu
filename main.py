import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kaffesa B2 Depo Kontrol Sistemi", layout="wide")

# Google Sheets → CSV link
JSON_URL = "https://docs.google.com/spreadsheets/d/1S66WOnKDDMdsb-9j7GLczXI3tcnOftMA/gviz/tq?tqx=out:csv"

@st.cache_data
def load_data():
    df = pd.read_csv(JSON_URL)

    # Sütunları temizleyelim
    df.columns = df.columns.str.strip()

    # Arama için temp kolon
    if "Stok kodu" in df.columns:
        df["Kod_Temp"] = df["Stok kodu"].astype(str).str.strip().str.upper()
    else:
        st.error("'Stok kodu' sütunu bulunamadı!")

    return df

df = load_data()

st.write("**Mevcut Sütunlar:**", df.columns.tolist())

st.title("Kaffesa B2 Depo Kontrol Sistemi")

# Kod girişi
kod_girisi = st.text_input("Stok kodlarını girin (boşlukla ayırın):")

if kod_girisi:
    kodlar = [k.strip().upper() for k in kod_girisi.split()]

    filtre = df[df["Kod_Temp"].isin(kodlar)]

    if not filtre.empty:
        st.dataframe(
            filtre[[
                "Stok kodu",
                "Stok ismi",
                "KONUM",
                "Marka kodu",
                "ADET"
            ]]
        )
    else:
        st.warning("Parça bulunamadı.")
