import pandas as pd
import streamlit as st
from io import BytesIO
import datetime

# Google Sheets CSV linkin
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_O1wYfDZc1nlVcmfwY491muJSojVIP5tcW0ipegIzv_6JTHAINhO3gV_uiLrdvQ/pub?gid=1982264017&single=true&output=csv"

# Veri çekme
@st.cache_data
def load_data():
    return pd.read_csv(sheet_url)

df = load_data()

# Session state ile geçici veri kaydı
if "hareketler" not in st.session_state:
    st.session_state.hareketler = []

# Sekmeler
tab1, tab2, tab3 = st.tabs(["📦 Kod Sorgulama", "➕ Parça Hareketi Kaydı", "📋 Hareket Geçmişi"])

# ---------------- Tab 1: Kod Sorgulama ----------------
with tab1:
    st.header("Kod Sorgulama")
    user_input = st.text_input("Sorunuzu yazın:", "")

    def cevapla(soru):
        soru = soru.lower()
        kodlar = df.iloc[:, 0].astype(str).tolist()

        import re
        kod_arama = re.findall(r"\b\w+\b", soru)
        kod = next((k for k in kod_arama if k in kodlar), None)

        if not kod:
            return "Kod bulunamadı. Lütfen geçerli bir kod yazın."

        row = df[df.iloc[:, 0].astype(str) == kod]

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

    with st.form("hareket_form"):
        parca_kodu = st.text_input("Parça Kodu")
        islem_turu = st.selectbox("İşlem Türü", ["Alım", "İade"])
        miktar = st.number_input("Miktar", min_value=1, value=1)
        alan_kisi = st.text_input("Alan Kişi")
        notlar = st.text_area("Not (Opsiyonel)")
        submitted = st.form_submit_button("Kaydı Ekle")

        if submitted:
            if parca_kodu and alan_kisi:
                yeni_kayit = {
                    "Tarih": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Parça Kodu": parca_kodu,
                    "İşlem": islem_turu,
                    "Miktar": miktar,
                    "Alan Kişi": alan_kisi,
                    "Not": notlar
                }
                st.session_state.hareketler.append(yeni_kayit)
                st.success("✅ Kayıt başarıyla eklendi!")
            else:
                st.error("❌ Parça kodu ve alan kişi zorunludur.")


# ---------------- Tab 3: Hareket Geçmişi ----------------
with tab3:
    st.header("Hareket Geçmişi")

    if st.session_state.hareketler:
        df_hareket = pd.DataFrame(st.session_state.hareketler)
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
        
