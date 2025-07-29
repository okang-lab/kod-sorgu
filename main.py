import pandas as pd
import streamlit as st
import datetime

# Google Sheets CSV linki
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_O1wYfDZc1nlVcmfwY491muJSojVIP5tcW0ipegIzv_6JTHAINhO3gV_uiLrdvQ/pub?gid=1982264017&single=true&output=csv"

# Hareketler CSV
hareket_csv = "hareketler.csv"

st.set_page_config(page_title="Kaffesa B2 Depo Kontrol Sistemi", layout="wide")
st.title("📦 Kaffesa B2 Depo Kontrol Sistemi")

# Veriyi yükle
@st.cache_data
def load_data():
    return pd.read_csv(sheet_url)

try:
    df = load_data()
except Exception:
    st.error("Google Sheets verisi çekilemedi. Linki kontrol edin.")
    st.stop()

# Kod sütununu string yap
df.iloc[:, 0] = df.iloc[:, 0].astype(str)

# Hareketler CSV yükle/oluştur
try:
    df_hareket = pd.read_csv(hareket_csv)
except:
    df_hareket = pd.DataFrame(columns=["Tarih", "Kod", "İşlem", "Miktar", "Kullanıcı"])

# Eski kayıtları temizle (30 gün)
bugun = datetime.datetime.now()
df_hareket["Tarih"] = pd.to_datetime(df_hareket["Tarih"], errors="coerce")
df_hareket = df_hareket[df_hareket["Tarih"] >= bugun - pd.Timedelta(days=30)]

# Sekmeler
sekme = st.tabs(["🔍 Kod Sorgu ve Hızlı İşlem", "📊 Hareket Analizi", "📜 Hareket Geçmişi"])

# --------------------- 1. Sekme: Kod Sorgu ---------------------
with sekme[0]:
    st.subheader("Kod Sorgulama ve Hızlı Hareket")
    kod_input = st.text_area("Kod(lar)ı girin (virgül ile ayırın):")
    user = st.text_input("Kullanıcı Adı (Hareket kaydı için):")

    if kod_input:
        kodlar = [k.strip() for k in kod_input.split(",") if k.strip()]
        sorgu_sonuc = df[df.iloc[:,0].isin(kodlar)]

        if sorgu_sonuc.empty:
            st.warning("Hiçbir kod bulunamadı.")
        else:
            st.dataframe(sorgu_sonuc)

            st.markdown("### Hızlı Hareket Girişi")
            for idx, row in sorgu_sonuc.iterrows():
                kod = row.iloc[0]
                miktar = st.number_input(f"{kod} için miktar:", min_value=0, step=1, key=f"miktar_{kod}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Alım Kaydet ({kod})", key=f"alım_{kod}") and miktar > 0:
                        yeni = pd.DataFrame([[bugun, kod, "Alım", miktar, user]], 
                                            columns=df_hareket.columns)
                        df_hareket = pd.concat([df_hareket, yeni], ignore_index=True)
                        df_hareket.to_csv(hareket_csv, index=False)
                        st.success(f"{kod} için {miktar} adet Alım kaydedildi.")
                with col2:
                    if st.button(f"İade Kaydet ({kod})", key=f"iade_{kod}") and miktar > 0:
                        yeni = pd.DataFrame([[bugun, kod, "İade", miktar, user]], 
                                            columns=df_hareket.columns)
                        df_hareket = pd.concat([df_hareket, yeni], ignore_index=True)
                        df_hareket.to_csv(hareket_csv, index=False)
                        st.success(f"{kod} için {miktar} adet İade kaydedildi.")

# --------------------- 2. Sekme: Hareket Analizi ---------------------
with sekme[1]:
    st.subheader("Hareket Analizi (Son 30 Gün)")
    hareket_sayim = df_hareket.groupby("Kod").size().reset_index(name="Hareket Sayısı")
    df_analiz = df.merge(hareket_sayim, left_on=df.columns[0], right_on="Kod", how="left").fillna(0)
    df_analiz["Hareket Sayısı"] = df_analiz["Hareket Sayısı"].astype(int)

    def sınıfla(x):
        if x >= 6: return "🔴 Yüksek"
        elif x >= 3: return "🟡 Orta"
        elif x >= 1: return "🟢 Düşük"
        else: return "⚪ Hareket Yok"

    df_analiz["Hareket Sıklığı"] = df_analiz["Hareket Sayısı"].apply(sınıfla)
    st.dataframe(df_analiz)

# --------------------- 3. Sekme: Hareket Geçmişi ---------------------
with sekme[2]:
    st.subheader("Hareket Geçmişi (Son 30 Gün)")
    st.dataframe(df_hareket.sort_values("Tarih", ascending=False))
