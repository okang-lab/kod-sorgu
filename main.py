# index.py
import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Sayfa ayarları
st.set_page_config(page_title="Kaffesa B2 Depo Kontrol", layout="wide", page_icon="☕")

# Sayfa başlığı
st.markdown("<h1 style='text-align:center; color:#333;'>☕ Kaffesa B2 Depo Kontrol Sistemi</h1>", unsafe_allow_html=True)
st.markdown("---")

# Google Sheets CSV linki (2. satır başlık)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1S66WOnKDDMdsb-9j7GLczXI3tcnOftMA/export?format=csv&gid=1463822398"

# Dosyayı oku, 2. satırı başlık olarak al
df = pd.read_csv(SHEET_URL, header=1)

# Mevcut sütunları yan yana göster
st.markdown("### Mevcut Sütunlar")
st.write(df.columns.tolist())

# Kullanıcıdan stok kodlarını al
st.markdown("### Stok Kodlarını Girin")
kodlar_input = st.text_input("Boşlukla ayırarak girin (ör: RGH2025 1501552)")
kodlar = kodlar_input.split() if kodlar_input else []

# Filtreleme ve tablo gösterimi
if kodlar:
    if "Stok kodu" in df.columns:
        filtre = df[df["Stok kodu"].isin(kodlar)]
        st.markdown("### Filtrelenmiş Stoklar")
        st.dataframe(filtre.style.set_properties(**{'background-color': '#f9f9f9', 'color': '#333', 'border-color': '#ddd'}))
        
        # PDF oluşturma fonksiyonu
        def create_pdf(df_filtered):
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            y = height - 50

            for idx, row in df_filtered.iterrows():
                line = f"{row['Stok kodu']} | {row['KONUM']} | {row['Stok ismi']} | {row['Marka kodu']} | {row['ADET']} | {row['Eski Kod']}"
                c.drawString(50, y, line)
                y -= 20
                if y < 50:
                    c.showPage()
                    y = height - 50

            c.save()
            buffer.seek(0)
            return buffer

        # PDF indirme butonu
        st.markdown("### PDF Olarak İndir")
        if st.button("📄 PDF Oluştur ve İndir"):
            pdf_buffer = create_pdf(filtre)
            st.download_button(
                label="Filtrelenmiş Stokları PDF olarak indir",
                data=pdf_buffer,
                file_name="stoklar.pdf",
                mime="application/pdf"
            )
    else:
        st.error("❌ Stok kodu sütunu bulunamadı!")
