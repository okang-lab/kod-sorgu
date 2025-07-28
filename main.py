import pandas as pd
import streamlit as st
import re

sheet_url = "https://docs.google.com/spreadsheets/d/1zD8TCZKWOFT-LjMaajYFfMWZKCdPn2KLNpDbS1_xJt4/export?format=csv"

@st.cache_data
def load_data():
    return pd.read_csv(sheet_url)

df = load_data()

st.title("📦 Kod Sorgulama Sistemi")
st.markdown("Google Sheets'teki kodları sorgulamak için aşağıya yazman yeterli.")

user_input = st.text_input("Sorunuzu yazın:")

def cevapla(soru):
    soru = soru.lower()
    kodlar = df.iloc[:,0].astype(str).tolist()
    kod_arama = re.findall(r"\b\w+\b", soru)
    kod = next((k for k in kod_arama if k in kodlar), None)

    if not kod:
        return "Kod bulunamadı. Lütfen geçerli bir kod yazın."

    row = df[df.iloc[:,0].astype(str) == kod]

    if "hangi dolap" in soru:
        return f"📦 Kod **{kod}**, dolap: **{row.iloc[0,1]}**"
    elif "stok" in soru:
        return f"📦 Kod **{kod}**, stok durumu: **{row.iloc[0,2]}**"
    elif "var mı" in soru:
        return f"✅ Kod **{kod}** listede var."
    else:
        return "🤔 Ne sorduğunu anlayamadım. Lütfen 'hangi dolapta', 'stok durumu', ya da 'var mı' gibi sorular sor."
if user_input:
    st.write(cevapla(user_input))
    
