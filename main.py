import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import os


st.set_page_config(page_title="Kaffesa B2 Depo Kontrol Sistemi", layout="wide")

# Google Sheets CSV Linki
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_O1wYfDZc1nlVcmfwY491muJSojVIP5tcW0ipegIzv_6JTHAINhO3gV_uiLrdvQ/pub?gid=1982264017&single=true&output=csv"

# Hareket CSV dosyası
hareket_csv = "hareketler.csv"

# Hareket dosyası yoksa oluştur
if not os.path.exists(hareket_csv):
    with open(hareket_csv, "w") as f:
        f.write("Tarih,Kod,Islem,Miktar,Kullanici\n")

# Veri yükleme
@st.cache_data
def load_data():
    return pd.read_csv(sheet_url)

df = load_data()
df.iloc[:,0] = df.iloc[:,0].astype(str)  # Kod sütununu string yap

# Hareket geçmişi oku
def load_hareket():
    try:
        df_h = pd.read_csv(hareket_csv)
        # 1 ay öncesinden eski kayıtları sil
        cutoff = datetime.now() - timedelta(days=30)
        df_h["Tarih"] = pd.to_datetime(df_h["Tarih"])
        df_h = df_h[df_h["Tarih"] > cutoff]
        df_h.to_csv(hareket_csv, index=False)
        return df_h
    except:
        return pd.DataFrame(columns=["Tarih","Kod","Islem","Miktar","Kullanici"])

df_hareket = load_hareket()

st.title("📦 Kaffesa B2 Depo Kontrol Sistemi / Okan-Lab Camoon")
st.markdown("Depo kodlarını sorgulayabilir, alım/iade kaydı oluşturabilirsin.")

tab1, tab2, tab3 = st.tabs(["🔍 Parça Sorgu", "➕ Parça Hareketi", "📊 Hareket Geçmişi"])

# ---------------- Tab 1: Parça Sorgu ----------------
with tab1:
    st.subheader("Parça Sorgulama")
    user_input = st.text_input("Kod veya kodları boşluk ile ayırarak yazın:")

    if user_input:
        kodlar = user_input.upper().split()  # boşluk ile ayır
        sorgu_sonuc = df[df.iloc[:,0].isin(kodlar)]

        if sorgu_sonuc.empty:
            st.error("Hiçbir kod bulunamadı.")
        else:
            st.dataframe(sorgu_sonuc, use_container_width=True)

            # Hızlı adet ekleme
            st.subheader("Hızlı İşlem")
            for _, row in sorgu_sonuc.iterrows():
                kod = row.iloc[0]
                miktar = st.number_input(f"{kod} için adet gir:", min_value=0, step=1, key=f"miktar_{kod}")
                islem = st.selectbox(f"{kod} için işlem türü:", ["Yok", "Alım", "İade"], key=f"islem_{kod}")
                kullanici = st.text_input(f"{kod} için kullanıcı:", key=f"kullanici_{kod}")
                if st.button(f"{kod} Kaydet", key=f"buton_{kod}"):
                    if islem != "Yok" and miktar > 0 and kullanici:
                        with open(hareket_csv, "a") as f:
                            f.write(f"{datetime.now()},{kod},{islem},{miktar},{kullanici}\n")
                        st.success(f"{kod} için işlem kaydedildi!")

# ---------------- Tab 2: Parça Hareketi ----------------
with tab2:
    st.subheader("Parça Alım / İade Kaydı")

    kod = st.text_input("Parça Kodu:")
    miktar = st.number_input("Miktar:", min_value=1, step=1)
    islem = st.selectbox("İşlem Türü", ["Alım", "İade"])
    kullanici = st.text_input("Kullanıcı:")

    if st.button("Kaydı Ekle"):
        if kod.upper() not in df.iloc[:,0].values:
            st.error("❌ Kod listede yok, işlem yapılmadı.")
        elif not kullanici:
            st.error("❌ Kullanıcı girilmeli.")
        else:
            with open(hareket_csv, "a") as f:
                f.write(f"{datetime.now()},{kod.upper()},{islem},{miktar},{kullanici}\n")
            st.success("✅ İşlem kaydedildi!")

# ---------------- Tab 3: Hareket Geçmişi ----------------
with tab3:
    st.subheader("Son 1 Ay Hareketleri")
    if df_hareket.empty:
        st.info("Henüz hareket kaydı yok.")
    else:
        st.dataframe(df_hareket, use_container_width=True)

        # En çok hareket eden parçalar
        st.subheader("En Çok Hareket Eden Parçalar")
        hareket_sayim = df_hareket.groupby("Kod").size().reset_index(name="Hareket Sayısı")
        hareket_sayim = hareket_sayim.sort_values("Hareket Sayısı", ascending=False)
        st.dataframe(hareket_sayim, use_container_width=True)
