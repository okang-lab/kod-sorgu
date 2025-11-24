import streamlit as st
import pandas as pd
from io import BytesIO

# Sayfa ayarları
st.set_page_config(page_title="Kaffesa B2 Depo Kontrol", layout="wide", page_icon="☕")

# Başlık
st.markdown("<h1 style='text-align:center; color:#333;'>☕ Kaffesa B2 Depo Kontrol Sistemi</h1>", unsafe_allow_html=True)
st.markdown("---")

# Google Sheets CSV linki
SHEET_URL = "https://docs.google.com/spreadsheets/d/1S66WOnKDDMdsb-9j7GLczXI3tcnOftMA/export?format=csv&gid=1463822398"

# Dosyayı oku, 2. satır başlık
df = pd.read_csv(SHEET_URL, header=1)

# ADET sütununu integer yap
df['ADET'] = pd.to_numeric(df['ADET'], errors='coerce').fillna(0).astype(int)

# Mevcut sütunlar
st.markdown("### Mevcut Sütunlar")
st.write(df.columns.tolist())

# Kullanıcıdan stok kodlarını al
st.markdown("### Stok Kodlarını Girin")
kodlar_input = st.text_input("Boşlukla ayırarak girin (ör: RGH2025 1501552)")
kodlar = kodlar_input.split() if kodlar_input else []

if kodlar:
    if "Stok kodu" in df.columns:
        filtre = df[df["Stok kodu"].isin(kodlar)]

        # Renkli tablo: adet 0 kırmızı, 10'dan fazla yeşil, diğerleri gri
        def highlight_stock(row):
            if row['ADET'] <= 0:
                return ['background-color: #f8d7da']*len(row)  # kırmızı
            elif row['ADET'] > 10:
                return ['background-color: #d4edda']*len(row)  # yeşil
            else:
                return ['background-color: #f9f9f9']*len(row)  # gri

        st.markdown("### Filtrelenmiş Stoklar")
        st.dataframe(filtre.style.apply(highlight_stock, axis=1)
                     .set_properties(**{'color': '#333', 'border-color': '#ddd'}))

        # Excel oluşturma fonksiyonu
        def to_excel(df_filtered):
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_filtered.to_excel(writer, index=False, sheet_name='Filtrelenmis_Stoklar')
            buffer.seek(0)
            return buffer

        excel_buffer = to_excel(filtre)
        st.download_button(
            label="📥 Filtrelenmiş Stokları Excel olarak indir",
            data=excel_buffer,
            file_name="Filtrelenmis_Stoklar.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("❌ Stok kodu sütunu bulunamadı!")
