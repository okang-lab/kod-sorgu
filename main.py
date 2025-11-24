import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kaffesa B2 Depo Kontrol Sistemi", layout="wide")

# Google Sheets → JSON linki
# GID = hangi sayfa/sekme ise onu temsil ediyor
JSON_URL = "https://docs.google.com/spreadsheets/d/1S66WOnKDDMdsb-9j7GLczXI3tcnOftMA/gviz/tq?tqx=out:csv"

@st.cache_data
def load_data():
    df = pd.read_csv(JSON_URL)

    df.columns = df.columns.str.strip()

    if "Parça Kodu" in df.columns:
        df["Kod_Temp"] = df["Parça Kodu"].astype(str).str.strip().str.upper()
    else:
        st.error("'Parça Kodu' sütunu bulunamadı!")

    return df

df = load_data()

st.write("**Sheet Sütunları:**", df.columns.tolist())

st.title("Kaffesa B2 Depo Kontrol Sistemi")

kod_girisi = st.text_input("Parça kodlarını girin (boşlukla ayırın):")

if kod_girisi:
    kodlar = [k.strip().upper() for k in kod_girisi.split()]
    filtre = df[df["Kod_Temp"].isin(kodlar)]

    if not filtre.empty:
        st.dataframe(
            filtre[[
                "Parça Kodu",
                "Parça Adı",
                "KONUM",
                "Marka",
                "Stok"
            ]]
        )
    else:
        st.warning("Parça bulunamadı.")
