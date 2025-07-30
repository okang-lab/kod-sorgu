import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- AYARLAR ---
DATA_FILE = "envanter.csv"
HAREKET_FILE = "hareketler.csv"
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Parça Kodu","KONUM","Parça Adı","Marka","Stok"])
    df.to_csv(DATA_FILE, index=False)
    
st.set_page_config(
    page_title="Kaffesa B2 Depo Kontrol Sistemi",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- VERİLERİ YÜKLE ---
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def load_hareketler():
    if not os.path.exists(HAREKET_FILE):
        return pd.DataFrame(columns=["Tarih","Kod","Parça Adı","Hareket","Adet","Personel"])
    return pd.read_csv(HAREKET_FILE)

def save_hareketler(df):
    df.to_csv(HAREKET_FILE, index=False)

df = load_data()
hareketler = load_hareketler()

# --- SAYFA SEÇİMİ ---
menu = st.sidebar.radio("Menü", ["📦 Parça Sorgu ve Hareket", "📊 Hareket Geçmişi & İstatistik"])

# ============================================================
# 1️⃣ SAYFA: PARÇA SORGU ve HAREKET
# ============================================================
if menu == "📦 Parça Sorgu ve Hareket":
    st.title("📦 Parça Sorgu ve Hareket Ekleme")

    # --- Toplu Kod Girişi ---
    kod_giris = st.text_input("Parça Kod(lar)ını Girin (boşluk ile ayırın):")

    secilen_hareket = st.radio("Hareket Türü", ["Alım", "İade"], horizontal=True)
    personel = st.text_input("Personel Adı")

    if kod_giris:
        kodlar = kod_giris.split()
        bulunanlar = df[df['Parça Kodu'].isin(kodlar)]

        if not bulunanlar.empty:
            st.subheader("🔍 Bulunan Parçalar")
            # Yan yana butonlu tablo
            for i, row in bulunanlar.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns([2,2,2,1,1,1])
                with col1: st.markdown(f"**{row['Parça Kodu']}**")
                with col2: st.markdown(row['Parça Adı'])
                with col3: st.markdown(row['KONUM'])
                with col4: st.markdown(str(row['Stok']))
                with col5:
                    adet = st.number_input(f"Adet {row['Parça Kodu']}", min_value=0, step=1, key=f"adet_{row['Parça Kodu']}")
                with col6:
                    if st.button("✅ Kaydet", key=f"kaydet_{row['Parça Kodu']}"):
                        if adet > 0 and personel.strip() != "":
                            hareket = pd.DataFrame([{
                                "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "Kod": row['Parça Kodu'],
                                "Parça Adı": row['Parça Adı'],
                                "Hareket": secilen_hareket,
                                "Adet": adet,
                                "Personel": personel
                            }])
                            hareketler = pd.concat([hareketler, hareket], ignore_index=True)
                            save_hareketler(hareketler)

                            # Stok Güncelle
                            if secilen_hareket == "Alım":
                                df.loc[df['Parça Kodu']==row['Parça Kodu'], 'Stok'] -= adet
                            else:
                                df.loc[df['Parça Kodu']==row['Parça Kodu'], 'Stok'] += adet
                            save_data(df)
                            st.success(f"{row['Parça Kodu']} için {adet} adet {secilen_hareket} kaydedildi.")
                        else:
                            st.warning("Personel adı ve adet girilmeli.")
        else:
            st.error("❌ Hiçbir kod bulunamadı.")

# ============================================================
# 2️⃣ SAYFA: HAREKET GEÇMİŞİ ve İSTATİSTİK
# ============================================================
elif menu == "📊 Hareket Geçmişi & İstatistik":
    st.title("📊 Hareket Geçmişi ve İstatistik")

    if not hareketler.empty:
        # Personel filtresi
        personeller = ["Tümü"] + list(hareketler['Personel'].unique())
        secilen_personel = st.selectbox("Personel Filtrele", personeller)

        df_goster = hareketler.copy()
        if secilen_personel != "Tümü":
            df_goster = df_goster[df_goster['Personel'] == secilen_personel]

        st.dataframe(df_goster, use_container_width=True)

        # İstatistik
        st.subheader("📈 Kullanım Sıklığı")
        kullanilan = hareketler.groupby("Kod")['Adet'].sum().reset_index()
        kullanilan = kullanilan.sort_values("Adet", ascending=False)
        st.bar_chart(kullanilan.set_index("Kod"))
    else:
        st.info("Henüz hareket kaydı yok.")
