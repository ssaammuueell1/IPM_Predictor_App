import streamlit as st
from tampilan import hero
from halaman.Prediksi_Data_Baru import tampilkan_prediksi_data_baru
from halaman.Prediksi_Data_Tersedia import tampilkan_prediksi_data_tersedia

hero("Prediksi IPM",
        "Prediksi Indeks Pembangunan dengan 2 Skenario.",
        label="Per daerah")

jenis = st.selectbox("Pilih jenis prediksi", ["Data tersedia", "Data baru"])
if jenis == "Data tersedia":
    tampilkan_prediksi_data_tersedia()
else:
    tampilkan_prediksi_data_baru()