import pandas as pd
import streamlit as st
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Kaffesa B2 Depo Kontrol Sistemi", layout="wide")

# ------------------- AYARLAR -------------------
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_O1wYfDZc1nlVcmfwY491muJSojVIP5tcW0ipegIzv_6JTHAINhO3gV_uiLrdvQ/pub?gid=1982264017&single=true&output=csv"
hareket_csv = "hareketler.csv"
kayit_suresi = 30  # gün

# ------------------- VERİLERİ YÜKLE -------------------
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(sheet_url)
    df.columns = [c.strip() for c in df.columns]
    return df

df = load_data()

if not os.path.exists(hareket_csv):
    pd.DataFrame(columns=["Tarih","Kod","Islem","Miktar","Kullanici"]).to_csv(hareket_csv, index=False)

df_hareket = pd.read_csv(hareket_csv)
df_hareket = df_hareket.dropna(how="all")

# Eski kayıtları temizle
if not df_hareket.empty:
    df_hareket["Tarih"] = pd.to_datetime(df_hareket["Tarih"])
    df_hareket = df_hareket[df_hareket["Tarih"] >= datetime.now() - timedelta(days=kayit_suresi)]
    df_hareket.to_csv(hareket_csv, index=False)

st.title("📦 Kaffesa B2 Depo Kontrol Sistemi")

menu = st.sidebar.radio("Menü", ["Tekli Kod Sorgu","Toplu Kod Sorgu","Parça Hareketleri","Hareket Geçmişi"])

# ------------------- TEKLİ SORGU -------------------
if menu == "Tekli Kod Sorgu":
    kod = st.text_input("Kod girin:")
    if kod:
        row = df[df.iloc[:,0].astype(str).str.lower() == kod.lower()]
        if not row.empty:
            st.dataframe(row)
        else:
            st.error("❌ Kod bulunamadı.")

# ------------------- TOPLU SORGU -------------------
elif menu == "Toplu Kod Sorgu":
    kodlar = st.text_area("Kodları aralarında boşluk olacak şekilde yazın (örn: TL2526 H1001 70235):")
    if kodlar:
        sorgu_list = [k.strip() for k in kodlar.split() if k.strip()]
        sonuc_df = df[df.iloc[:,0].astype(str).str.lower().isin([k.lower() for k in sorgu_list])]
        if not sonuc_df.empty:
            st.dataframe(sonuc_df)

            st.subheader("⬇️ Hızlı Hareket Ekle")
            kullanici = st.text_input("Kullanıcı adı:")
            for i, row in sonuc_df.iterrows():
                miktar = st.number_input(f"{row.iloc[0]} için miktar:", min_value=0, step=1, key=f"miktar_{i}")
                islem = st.selectbox(f"{row.iloc[0]} için işlem:", ["Alım","İade"], key=f"islem_{i}")
                if st.button(f"Ekle ({row.iloc[0]})", key=f"ekle_{i}") and miktar > 0:
                    yeni_kayit = pd.DataFrame([[datetime.now(), row.iloc[0], islem, miktar, kullanici]],
                                              columns=["Tarih","Kod","Islem","Miktar","Kullanici"])
                    yeni_kayit.to_csv(hareket_csv, mode='a', header=not os.path.exists(hareket_csv), index=False)
                    st.success(f"{row.iloc[0]} için {islem} kaydedildi.")
        else:
            st.error("❌ Hiçbir kod bulunamadı.")

# ------------------- PARÇA HAREKETLERİ -------------------
elif menu == "Parça Hareketleri":
    st.subheader("Yeni Hareket Ekle")
    kod = st.text_input("Parça Kodu:")
    miktar = st.number_input("Miktar:", min_value=0, step=1)
    islem = st.selectbox("İşlem:", ["Alım","İade"])
    kullanici = st.text_input("Kullanıcı adı:")

    if st.button("Kaydet"):
        # Kod kontrolü
        if df.iloc[:,0].astype(str).str.lower().eq(kod.lower()).any():
            if miktar > 0:
                yeni_kayit = pd.DataFrame([[datetime.now(), kod, islem, miktar, kullanici]],
                                          columns=["Tarih","Kod","Islem","Miktar","Kullanici"])
                yeni_kayit.to_csv(hareket_csv, mode='a', header=not os.path.exists(hareket_csv), index=False)
                st.success("✅ Kayıt eklendi.")
            else:
                st.warning("Miktar sıfır olamaz.")
        else:
            st.error("❌ Kod listede yok, işlem reddedildi.")

# ------------------- HAREKET GEÇMİŞİ -------------------
elif menu == "Hareket Geçmişi":
    st.subheader("Son 30 Günlük Hareketler")
    if not df_hareket.empty:
        st.dataframe(df_hareket.sort_values("Tarih", ascending=False))
        hareket_sayim = df_hareket.groupby("Kod").size().reset_index(name="Hareket Sayısı")
        hareket_sayim = hareket_sayim.sort_values("Hareket Sayısı", ascending=False)
        st.subheader("En Çok Hareket Eden Parçalar")
        st.dataframe(hareket_sayim)
    else:
        st.info("Son 30 günde hareket yok.")
