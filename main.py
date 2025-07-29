import pandas as pd
import streamlit as st
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Kaffesa B2 Depo Kontrol Sistemi", layout="wide")

DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_O1wYfDZc1nlVcmfwY491muJSojVIP5tcW0ipegIzv_6JTHAINhO3gV_uiLrdvQ/pub?gid=1982264017&single=true&output=csv"
HAREKET_CSV = "hareketler.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df = df.dropna(subset=["Parça Kodu"])  # Boş satırları at
    return df

df = load_data()

# Hareket dosyası yoksa oluştur
if not os.path.exists(HAREKET_CSV):
    pd.DataFrame(columns=["Tarih", "İşlem", "Kod", "Adet", "Kullanıcı"]).to_csv(HAREKET_CSV, index=False)

st.title("📦 Kaffesa B2 Depo Kontrol Sistemi")

# Menü
secim = st.sidebar.radio("Menü", ["Parça Sorgu", "Hareket Girişi", "Hareket Geçmişi"])

# ------------------------- PARÇA SORGU -------------------------
if secim == "Parça Sorgu":
    st.subheader("Parça Sorgu (Boşluk ile birden fazla kod yazabilirsiniz)")
    input_kod = st.text_input("Parça Kodlarını Girin (Boşluk ile ayrılacak)").strip().upper()

    if input_kod:
        kod_listesi = input_kod.split()
        sonuc = df[df["Parça Kodu"].isin(kod_listesi)]

        if not sonuc.empty:
            st.dataframe(sonuc[["Parça Kodu", "Parça Adı", "KONUM", "Marka", "Stok"]])
        else:
            st.warning("Hiçbir parça bulunamadı.")

# ------------------------- HAREKET GİRİŞİ -------------------------
elif secim == "Hareket Girişi":
    st.subheader("Parça Hareket Girişi")

    hareket_tip = st.radio("İşlem Tipi", ["Alım", "İade"])
    kullanici = st.text_input("Kullanıcı İsmi")

    input_kod = st.text_input("Parça Kodlarını Girin (Boşluk ile ayrılacak)").strip().upper()
    adet = st.number_input("Adet", min_value=1, value=1)

    if st.button("Kaydet"):
        if input_kod and kullanici:
            kod_listesi = input_kod.split()
            mevcut_kodlar = df["Parça Kodu"].tolist()
            gecersiz_kodlar = [k for k in kod_listesi if k not in mevcut_kodlar]

            if gecersiz_kodlar:
                st.error(f"Geçersiz kodlar bulundu: {', '.join(gecersiz_kodlar)}")
            else:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df_hareket = pd.read_csv(HAREKET_CSV)
                for kod in kod_listesi:
                    yeni_kayit = pd.DataFrame([[now, hareket_tip, kod, adet, kullanici]],
                                              columns=["Tarih", "İşlem", "Kod", "Adet", "Kullanıcı"])
                    df_hareket = pd.concat([df_hareket, yeni_kayit], ignore_index=True)
                df_hareket.to_csv(HAREKET_CSV, index=False)
                st.success("Hareket başarıyla kaydedildi!")
        else:
            st.warning("Kod ve kullanıcı alanı boş olamaz!")

# ------------------------- HAREKET GEÇMİŞİ -------------------------
elif secim == "Hareket Geçmişi":
    st.subheader("Son 30 Günlük Hareketler")
    df_hareket = pd.read_csv(HAREKET_CSV)

    # Sadece son 30 gün
    df_hareket["Tarih"] = pd.to_datetime(df_hareket["Tarih"])
    tarih_filtre = datetime.now() - timedelta(days=30)
    df_hareket = df_hareket[df_hareket["Tarih"] >= tarih_filtre]

    st.dataframe(df_hareket.sort_values("Tarih", ascending=False))
