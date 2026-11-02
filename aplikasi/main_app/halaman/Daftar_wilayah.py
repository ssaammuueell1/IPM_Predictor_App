import streamlit as st

from utils import muat_tabel, muat_info, angka
from tampilan import hero

tabel = muat_tabel()
info = muat_info()
JENIS = ["Latih", "Uji"]

hero("Daftar Wilayah",
     "Cari dan saring IPM aktual dan IPM prediksi setiap kabupaten/kota.",
     label="Data")

# ---------- Filter ----------
with st.container(border=True):
    f1, f2, f3 = st.columns([2, 2, 1])
    cari = f1.text_input("Cari kabupaten/kota", placeholder="Contoh: Aceh Barat", icon=":material/search:")
    pilih_provinsi = f2.multiselect("Provinsi", sorted(tabel["Provinsi"].unique()), placeholder="Semua provinsi")
    pilih_tahun = f3.selectbox("Tahun", ["Semua tahun"] + sorted(tabel["Tahun"].unique(), reverse=True))
    pilih_jenis = st.pills("Jenis data", JENIS, selection_mode="multi")

hasil = tabel
if cari:
    hasil = hasil[hasil["Kabupaten/Kota"].str.contains(cari, case=False, regex=False)]
if pilih_provinsi:
    hasil = hasil[hasil["Provinsi"].isin(pilih_provinsi)]
if pilih_tahun != "Semua tahun":
    hasil = hasil[hasil["Tahun"] == pilih_tahun]
if pilih_jenis:
    hasil = hasil[hasil["Jenis data"].isin(pilih_jenis)]

# ---------- Ringkasan jumlah per jenis data ----------
k1, k2, k3 = st.columns(3)
k1.metric("Jumlah baris", angka(len(hasil), 0), border=True)
for kolom, jenis in zip([k2, k3], JENIS):
    bagian = hasil[hasil["Jenis data"] == jenis]
    kolom.metric(f"Data {jenis.lower()}", f"{angka(len(bagian), 0)} baris", border=True)
    kolom.caption(f"{bagian['Kabupaten/Kota'].nunique()} kabupaten/kota")
st.caption(f"{angka(len(hasil), 0)} dari {angka(len(tabel), 0)} baris · klik judul kolom untuk mengurutkan")

# ---------- Tabel ----------
if hasil.empty:
    st.warning("Tidak ada data yang cocok dengan filter.", icon=":material/search_off:")
else:
    tampil = (hasil[["Kabupaten/Kota", "Provinsi", "Tahun", "Jenis data", "IPM", "IPM_prediksi", "Selisih"]]
              .rename(columns={"IPM": "IPM aktual", "IPM_prediksi": "IPM prediksi"})
              .sort_values(["Tahun", "Kabupaten/Kota"], ascending=[False, True]))
    gaya = tampil.style.format({"IPM aktual": "{:.2f}", "IPM prediksi": "{:.2f}", "Selisih": "{:+.2f}"}, decimal=",")
    st.dataframe(gaya, hide_index=True, width="stretch", height=520,
                 column_config={"Tahun": st.column_config.NumberColumn(format="%d")})
    st.caption("Data latih: IPM prediksi dari validasi silang (k-fold) pada data latih. "
               "Data uji: IPM prediksi dari model hasil tuning, daerah ini tidak dipakai untuk melatih model.")

    st.download_button(
        "Unduh tabel (CSV)", tampil.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
        file_name="daftar_wilayah_ipm.csv", mime="text/csv", icon=":material/download:",
    )
