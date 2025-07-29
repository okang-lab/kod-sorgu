import pandas as pd
import streamlit as st
import os
from datetime import datetime, timedelta

# ==========================
# AYARLAR
# ==========================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_O1wYfDZc1nlVcmfwY491muJSojVIP5tcW0ipegIzv_6JTHAINhO3gV_uiLrdvQ/pub?gid=1982264017&single=true&output=csv"
HAREKET_CSV = "hareketler.csv"

# ==========================
# CSV HAZIRLIĞI
# ==========================
if not os.path.exists(HAREKET_CSV) or os.stat(HAREKET_CSV).st_size == 0:
    pd.DataFrame(columns=["Tarih","Parça Kodu","İşlem","Miktar","Alan Kişi","Not"]).to_csv(HAREKET_CSV, index=False)

# ==========================
# VERİLERİ YÜKLE
# ==========================
@st.cache_data
def load_data():
    return pd.read_csv(SHEET_URL)

df = load_data()
df_hareket = pd.read_csv(HAREKET_CSV)

# ==========================
# ARAYÜZ BAŞLIĞI
# ==========================
st.set_page_config(page_title="Kaffesa B2 Depo Kontrol Sistemi", layout="wide")
st.title("Kaffesa B2 Depo Kontrol Sistemi")

# Sekmeler
tab1, tab2, tab3 = st.tabs(["🔍 Kod Sorgulama", "➕ Parça Hareketi", "📜 Hareket Geçmişi"])

# ==========================
# 1️⃣ KOD SORGULAMA SEKMESİ
# ==========================
with tab1:
    st.subheader("Kod Sorgulama (Tekli veya Toplu)")

    kod_girdi = st.text_area(
        "Parça Kodunu Giriniz (virgül, boşluk veya alt alta yazabilirsiniz):",
        placeholder="Örn:\n12345\nH1001\nTL2526"
    )

    if st.button("Sorgula"):
        if kod_girdi.strip():
            # Kodları ayır
            kodlar = [k.strip() for k in kod_girdi.replace(",", "\n").split("\n") if k.strip()]
            results = []

            for kod in kodlar:
                row = df[df.iloc[:,0].astype(str) == kod]
                if not row.empty:
                    dolap = row.iloc[0,1]
                    stok = row.iloc[0,2]
                    results.append([kod, dolap, stok, "✅ Var"])
                else:
                    results.append([kod, "-", "-", "❌ Yok"])

            df_sonuc = pd.DataFrame(results, columns=["Kod", "Dolap", "Stok", "Listede Var mı"])
            st.dataframe(df_sonuc, use_container_width=True)
        else:
            st.warning("Lütfen en az bir parça kodu girin.")

# ==========================
# 2️⃣ PARÇA HAREKET SEKMESİ
# ==========================
with tab2:
    st.subheader("Parça Alım / İade Kaydı")

    col1, col2, col3 = st.columns(3)
    with col1:
        kod_input = st.text_input("Parça Kodu:")
    with col2:
        islem_tipi = st.selectbox("İşlem", ["Alım", "İade"])
    with col3:
        miktar = st.number_input("Miktar", min_value=1, value=1)

    col4, col5 = st.columns(2)
    with col4:
        alan_kisi = st.text_input("Alan Kişi:")
    with col5:
        not_input = st.text_input("Not (opsiyonel):")

    if st.button("Kaydı Ekle"):
        if not kod_input.strip() or not alan_kisi.strip():
            st.error("⚠️ Parça kodu ve alan kişi boş bırakılamaz.")
        else:
            # Kod listede mi?
            row = df[df.iloc[:,0].astype(str) == kod_input.strip()]
            if row.empty:
                st.error("❌ Bu parça kodu listede yok, işlem kaydedilmedi!")
            else:
                yeni_kayit = pd.DataFrame([[
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    kod_input.strip(),
                    islem_tipi,
                    miktar,
                    alan_kisi.strip(),
                    not_input.strip()
                ]], columns=["Tarih","Parça Kodu","İşlem","Miktar","Alan Kişi","Not"])

                df_hareket = pd.concat([df_hareket, yeni_kayit], ignore_index=True)
                df_hareket.to_csv(HAREKET_CSV, index=False)
                st.success("✅ İşlem başarıyla kaydedildi!")

# ==========================
# 3️⃣ HAREKET GEÇMİŞİ
# ==========================
with tab3:
    st.subheader("Son 30 Günlük Hareketler")

    if not df_hareket.empty:
        # Tarihi DateTime yap ve son 30 günü filtrele
        df_hareket["Tarih"] = pd.to_datetime(df_hareket["Tarih"])
        son_30gun = datetime.now() - timedelta(days=30)
        df_recent = df_hareket[df_hareket["Tarih"] >= son_30gun]

        if not df_recent.empty:
            st.dataframe(df_recent.sort_values("Tarih", ascending=False), use_container_width=True)
        else:
            st.info("📭 Son 30 günde hareket yok.")
    else:
        st.info("📭 Henüz hiç hareket kaydı yok.")
