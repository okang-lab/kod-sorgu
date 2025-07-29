import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Kaffesa B2 Depo Kontrol Sistemi", layout="wide")

GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_O1wYfDZc1nlVcmfwY491muJSojVIP5tcW0ipegIzv_6JTHAINhO3gV_uiLrdvQ/pub?gid=1982264017&single=true&output=csv"
HAREKET_CSV = "hareketler.csv"

# -------------------
# CSV YÜKLEME FONKSİYONU
# -------------------
@st.cache_data
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_CSV, sep=None, engine='python')  # otomatik ayırıcı algılar
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Sütun sayısına göre başlık ekle
    if df.shape[1] >= 3:
        df = df.iloc[:, :3]
        df.columns = ["Kod", "Parça Adı", "Konum"]
    else:
        st.error(f"Beklenen 3 sütun ama {df.shape[1]} sütun bulundu. CSV'yi kontrol et!")
    
    return df
    

df = load_data()

# Hareket CSV kontrolü
if not os.path.exists(HAREKET_CSV):
    pd.DataFrame(columns=["Tarih", "İşlem", "Kod", "Adet", "Kullanıcı"]).to_csv(HAREKET_CSV, index=False)

df_hareket = pd.read_csv(HAREKET_CSV)

# -------------------
# ANA SEKMELER
# -------------------
secenek = st.sidebar.radio("Menü", ["Parça Sorgu / Alım-İade", "Hareket Geçmişi", "En Çok Hareket Edenler"])

# -------------------
# PARÇA SORGU
# -------------------
if secenek == "Parça Sorgu / Alım-İade":
    st.subheader("Parça Sorgulama ve Hareket Girişi")

    # Kullanıcıdan işlem türünü önce seçelim
    islem = st.radio("İşlem Türü Seçin:", ["Alım", "İade"])
    kullanici = st.text_input("İşlemi yapan kişi")

    kodlar_input = st.text_area("Parça Kodlarını Girin (boşlukla ayırın)", height=100)
    
    if kodlar_input.strip():
        kodlar_list = kodlar_input.upper().split()

        # Eşleşen parçaları getir
        sonuc = df[df["Kod"].isin(kodlar_list)]
        
        if sonuc.empty:
            st.warning("Girilen kodlardan hiçbiri bulunamadı!")
        else:
            st.write("**Bulunan Parçalar:**")
            adetler = {}
            for idx, row in sonuc.iterrows():
                adetler[row["Kod"]] = st.number_input(
                    f"{row['Kod']} - {row['Parça Adı']} (Konum: {row['Konum']})",
                    min_value=1, value=1, step=1
                )
            
            if st.button("İşlemi Kaydet"):
                for kod, adet in adetler.items():
                    yeni_kayit = pd.DataFrame([{
                        "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "İşlem": islem,
                        "Kod": kod,
                        "Adet": adet,
                        "Kullanıcı": kullanici
                    }])
                    yeni_kayit.to_csv(HAREKET_CSV, mode='a', header=False, index=False)
                st.success("İşlemler başarıyla kaydedildi!")

# -------------------
# HAREKET GEÇMİŞİ
# -------------------
elif secenek == "Hareket Geçmişi":
    st.subheader("Hareket Geçmişi (Son 30 Gün)")
    df_hareket = pd.read_csv(HAREKET_CSV)

    if not df_hareket.empty:
        df_hareket["Tarih"] = pd.to_datetime(df_hareket["Tarih"])
        filtre_tarih = datetime.now() - timedelta(days=30)
        son_hareket = df_hareket[df_hareket["Tarih"] >= filtre_tarih]
        st.dataframe(son_hareket)
    else:
        st.info("Henüz kayıt bulunmuyor.")

# -------------------
# EN ÇOK HAREKET EDENLER
# -------------------
elif secenek == "En Çok Hareket Edenler":
    st.subheader("En Çok Hareket Eden Parçalar")
    df_hareket = pd.read_csv(HAREKET_CSV)
    if not df_hareket.empty:
        hareket_sayim = df_hareket.groupby("Kod").size().reset_index(name="Hareket Sayısı")
        hareket_sayim = hareket_sayim.sort_values("Hareket Sayısı", ascending=False)
        st.dataframe(hareket_sayim)
    else:
        st.info("Henüz hareket kaydı yok.")
