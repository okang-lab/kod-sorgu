import pandas as pd
import streamlit as st
import datetime
import os
import re

# Google Sheets CSV linki
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_O1wYfDZc1nlVcmfwY491muJSojVIP5tcW0ipegIzv_6JTHAINhO3gV_uiLrdvQ/pub?gid=1982264017&single=true&output=csv"

# Hareketler CSV dosyası
hareket_csv = "hareketler.csv"

# Veri çekme
@st.cache_data
def load_data():
    return pd.read_csv(sheet_url)

df = load_data()

# Hareketler CSV'yi yükle (yoksa oluştur)
if not os.path.exists(hareket_csv):
    pd.DataFrame(columns=["Tarih","Parça Kodu","İşlem","Miktar","Alan Kişi","Not"]).to_csv(hareket_csv, index=False)

# Mevcut hareketleri oku
df_hareket = pd.read_csv(hareket_csv)

# Tarihi datetime'e çevir
if not df_hareket.empty:
    df_hareket["Tarih"] = pd.to_datetime(df_hareket["Tarih"], errors="coerce")
    # 1 aydan eski kayıtları sil
    cutoff = datetime.datetime.now() - datetime.timedelta(days=30)
    df_hareket = df_hareket[df_hareket["Tarih"] >= cutoff]
    df_hareket.to_csv(hareket_csv, index=False)

# Sekmeler
tab1, tab2, tab3 = st.tabs(["📦 Kod Sorgulama", "➕ Parça Hareketi Kaydı", "📋 Hareket Geçmişi"])

# ---------------- Tab 1: Kod Sorgulama ----------------
with tab1:
    st.header("Kod Sorgulama")
    user_input = st.text_input("Sorunuzu yazın:", "")

    def cevapla(soru):
        soru = soru.lower()
        kodlar = df.iloc[:, 0].astype(str).tolist()

        # Sorudaki kelimeleri sırayla kontrol et (alfanumerik dahil)
        kod_arama = re.findall(r"[A-Za-z0-9\-]+", soru)
        kod = next((k for k in kod_arama if k.upper() in [x.upper() for x in kodlar]), None)

        if not kod:
            return "Kod bulunamadı. Lütfen geçerli bir kod yazın."

        row = df[df.iloc[:, 0].astype(str).str.upper() == kod.upper()]

        if "hangi dolap" in soru:
            return f"📦 Kod **{kod}**, dolap: **{row.iloc[0,1]}**"

        elif "stok" in soru:
            return f"📦 Kod **{kod}**, stok durumu: **{row.iloc[0,2]}**"

        elif "var mı" in soru:
            return f"✅ Kod **{kod}** listede var." if not row.empty else f"❌ Kod **{kod}** listede yok."

        else:
            return "🤔 Ne sorduğunu anlayamadım. Lütfen 'hangi dolapta', 'stok durumu', ya da 'var mı' şeklinde sor."

    if user_input:
        cevap = cevapla(user_input)
        st.write(cevap)


# ---------------- Tab 2: Parça Hareketi Kaydı ----------------
with tab2:
    st.header("Parça Alım / İade Kaydı")

    # Tüm kodları büyük harfe çevirerek listede tut
    mevcut_kodlar = df.iloc[:, 0].astype(str).str.upper().tolist()

    with st.form("hareket_form"):
        parca_kodu = st.text_input("Parça Kodu").upper()
        islem_turu = st.selectbox("İşlem Türü", ["Alım", "İade"])
        miktar = st.number_input("Miktar", min_value=1, value=1)
        alan_kisi = st.text_input("Alan Kişi")
        notlar = st.text_area("Not (Opsiyonel)")
        submitted = st.form_submit_button("Kaydı Ekle")

        if submitted:
            if not parca_kodu or not alan_kisi:
                st.error("❌ Parça kodu ve alan kişi zorunludur.")
            elif parca_kodu not in mevcut_kodlar:
                st.error(f"❌ Bu parça kodu **{parca_kodu}** listede yok! Lütfen doğru kodu girin.")
            else:
                yeni_kayit = {
                    "Tarih": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Parça Kodu": parca_kodu,
                    "İşlem": islem_turu,
                    "Miktar": miktar,
                    "Alan Kişi": alan_kisi,
                    "Not": notlar
                }
                df_hareket = pd.concat([df_hareket, pd.DataFrame([yeni_kayit])], ignore_index=True)
                df_hareket.to_csv(hareket_csv, index=False)
                st.success("✅ Kayıt başarıyla eklendi!")


# ---------------- Tab 3: Hareket Geçmişi ----------------
with tab3:
    st.header("Hareket Geçmişi (Son 30 Gün)")

    if not df_hareket.empty:
        st.dataframe(df_hareket)

        # CSV indirme butonu
        csv = df_hareket.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ CSV Olarak İndir",
            data=csv,
            file_name="hareket_gecmisi.csv",
            mime="text/csv",
        )
    else:
        st.info("Henüz kayıt yok.")
