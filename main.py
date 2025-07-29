import pandas as pd
import streamlit as st
import os
from datetime import datetime, timedelta

# --------------------
# AYARLAR
# --------------------
STOCK_DEFAULT = 100  # Test aşamasında sabit stok
HAREKET_CSV = "hareketler.csv"
GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_O1wYfDZc1nlVcmfwY491muJSojVIP5tcW0ipegIzv_6JTHAINhO3gV_uiLrdvQ/pub?gid=1982264017&single=true&output=csv"

st.set_page_config(page_title="B2 Depo Kontrol Sistemi / Okan-Lab Camoon", layout="wide")
st.title("📦 Kaffesa B2 Depo Kontrol Sistemi")

# --------------------
# VERİLERİ YÜKLE
# --------------------
@st.cache_data
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_CSV)
    # Unnamed sütunları temizle
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = ["Kod", "Parça Adı", "Konum"]  # Başlıkları düzenle
    return df

df = load_data()

# Hareketler CSV yoksa oluştur
if not os.path.exists(HAREKET_CSV):
    pd.DataFrame(columns=["Tarih", "İşlem", "Kod", "Parça Adı", "Adet"]).to_csv(HAREKET_CSV, index=False)

# Hareketleri oku
df_hareket = pd.read_csv(HAREKET_CSV)

# 1 ay öncesinden eski kayıtları sil
now = datetime.now()
if not df_hareket.empty:
    df_hareket['Tarih'] = pd.to_datetime(df_hareket['Tarih'])
    df_hareket = df_hareket[df_hareket['Tarih'] > now - timedelta(days=30)]
    df_hareket.to_csv(HAREKET_CSV, index=False)

# --------------------
# ARAYÜZ
# --------------------
st.subheader("🔍 Parça Sorgulama ve Toplu İşlem")

# İşlem tipi seç
islem_tipi = st.radio("İşlem Seçin", ["Alım", "İade"])

# Kod girişi
kod_giris = st.text_input("Parça kodlarını boşlukla ayırarak yazın:")

if kod_giris:
    kodlar = kod_giris.strip().split()  # Boşlukla ayır
    sorgu_df = df[df["Kod"].astype(str).isin(kodlar)].copy()

    if sorgu_df.empty:
        st.warning("⚠️ Girdiğiniz kodların hiçbiri listede yok!")
    else:
        sorgu_df["Stok"] = STOCK_DEFAULT
        sorgu_df["Adet"] = 0  # Kullanıcının gireceği adet

        # Adet giriş kutuları
        for i in range(len(sorgu_df)):
            sorgu_df.at[i, "Adet"] = st.number_input(
                f"{sorgu_df.iloc[i]['Kod']} için adet:",
                min_value=0,
                step=1,
                key=f"adet_{i}"
            )

        st.dataframe(sorgu_df[["Kod", "Parça Adı", "Konum", "Stok", "Adet"]], use_container_width=True)

        if st.button("💾 İşlemi Kaydet"):
            hareket_kayit = []
            for _, row in sorgu_df.iterrows():
                if row["Adet"] > 0:  # Sıfır adetleri kaydetme
                    hareket_kayit.append([datetime.now(), islem_tipi, row["Kod"], row["Parça Adı"], row["Adet"]])

            if hareket_kayit:
                df_yeni = pd.DataFrame(hareket_kayit, columns=["Tarih", "İşlem", "Kod", "Parça Adı", "Adet"])
                df_hareket = pd.concat([df_hareket, df_yeni], ignore_index=True)
                df_hareket.to_csv(HAREKET_CSV, index=False)
                st.success("✅ İşlem kaydedildi!")
            else:
                st.info("ℹ️ Hiçbir adet girilmediği için kayıt yapılmadı.")

# --------------------
# HAREKET GEÇMİŞİ
# --------------------
st.subheader("📜 Son 30 Günlük Hareketler")
if df_hareket.empty:
    st.info("Henüz hareket kaydı yok.")
else:
    st.dataframe(df_hareket.sort_values(by="Tarih", ascending=False), use_container_width=True)
