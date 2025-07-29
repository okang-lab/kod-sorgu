import pandas as pd
import streamlit as st
import os
from datetime import datetime, timedelta

# --- AYARLAR ---
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_O1wYfDZc1nlVcmfwY491muJSojVIP5tcW0ipegIzv_6JTHAINhO3gV_uiLrdvQ/pub?gid=1982264017&single=true&output=csv"
hareket_csv = "hareketler.csv"
kayit_suresi = 30  # gün

# --- HAREKETLER CSV'Yİ OLUŞTUR ---
if not os.path.exists(hareket_csv):
    pd.DataFrame(columns=["Tarih", "Kod", "İşlem", "Miktar", "Kullanıcı"]).to_csv(hareket_csv, index=False)

# --- VERİLERİ YÜKLE ---
@st.cache_data
def load_data():
    return pd.read_csv(sheet_url)

df = load_data()
df_hareket = pd.read_csv(hareket_csv)

# Tarih filtresi (1 ay)
if not df_hareket.empty:
    df_hareket["Tarih"] = pd.to_datetime(df_hareket["Tarih"])
    son_tarih = datetime.now() - timedelta(days=kayit_suresi)
    df_hareket = df_hareket[df_hareket["Tarih"] >= son_tarih]

st.title("Kaffesa B2 Depo Kontrol Sistemi")
st.markdown("Kod sorgula, stok durumuna bak, alım/iade hareketlerini kaydet. ✅")

# --- SEKME MENÜ ---
secim = st.sidebar.radio("İşlem Seçin:", ["Kod Sorgu", "Toplu Kod Sorgu", "Parça Hareket Girişi", "Hareket Geçmişi", "En Çok Hareket Edenler"])

# ---------------------------------------------------
# 1️⃣ KOD SORGU
# ---------------------------------------------------
if secim == "Kod Sorgu":
    kod = st.text_input("Kod girin:")
    if kod:
        kod = kod.strip()
        row = df[df.iloc[:,0].astype(str).str.lower() == kod.lower()]
        if not row.empty:
            st.success(f"**Kod:** {kod}")
            st.write(f"**Dolap:** {row.iloc[0,1]}")
            st.write(f"**Stok:** {row.iloc[0,2]}")
        else:
            st.error("Kod bulunamadı ❌")

# ---------------------------------------------------
# 2️⃣ TOPLU KOD SORGU
# ---------------------------------------------------
elif secim == "Toplu Kod Sorgu":
    kodlar = st.text_area("Kodları alt alta yazın:")
    if kodlar:
        sorgu_list = [k.strip() for k in kodlar.splitlines() if k.strip()]
        sonuc_df = df[df.iloc[:,0].astype(str).str.lower().isin([k.lower() for k in sorgu_list])]
        if not sonuc_df.empty:
            st.dataframe(sonuc_df)
        else:
            st.error("Hiçbir kod bulunamadı ❌")

# ---------------------------------------------------
# 3️⃣ PARÇA HAREKET GİRİŞİ
# ---------------------------------------------------
elif secim == "Parça Hareket Girişi":
    st.write("Alınan veya iade edilen parçaları buradan kaydedin.")
    kod = st.text_input("Parça Kodu:")
    miktar = st.number_input("Miktar:", min_value=1, step=1)
    islem = st.selectbox("İşlem Tipi", ["Alım", "İade"])
    kullanici = st.text_input("Kullanıcı Adı:")

    if st.button("Kaydı Ekle"):
        # Kodun listede olup olmadığını kontrol et
        if df.iloc[:,0].astype(str).str.lower().eq(kod.lower()).any():
            yeni_kayit = pd.DataFrame([[datetime.now(), kod, islem, miktar, kullanici]],
                                      columns=["Tarih", "Kod", "İşlem", "Miktar", "Kullanıcı"])
            df_hareket = pd.concat([df_hareket, yeni_kayit], ignore_index=True)
            df_hareket.to_csv(hareket_csv, index=False)
            st.success("Hareket kaydedildi ✅")
        else:
            st.error("Kod listede yok, kayıt alınmadı ❌")

# ---------------------------------------------------
# 4️⃣ HAREKET GEÇMİŞİ
# ---------------------------------------------------
elif secim == "Hareket Geçmişi":
    if not df_hareket.empty:
        st.dataframe(df_hareket.sort_values(by="Tarih", ascending=False))
    else:
        st.info("Son 30 gün içinde hareket bulunamadı.")

# ---------------------------------------------------
# 5️⃣ EN ÇOK HAREKET EDENLER
# ---------------------------------------------------
elif secim == "En Çok Hareket Edenler":
    if not df_hareket.empty:
        hareket_sayim = df_hareket.groupby("Kod").size().reset_index(name="Hareket Sayısı")
        hareket_sayim = hareket_sayim.sort_values(by="Hareket Sayısı", ascending=False)
        st.dataframe(hareket_sayim)
    else:
        st.info("Henüz hiç hareket kaydı yok.")
