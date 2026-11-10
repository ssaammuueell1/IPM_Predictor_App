import pandas as pd
import streamlit as st

from utils import muat_tabel, muat_info, angka, kategori_ipm
from tampilan import hero, LATAR_KATEGORI, WARNA_TEKS_KATEGORI

tabel = muat_tabel()
info = muat_info()
JENIS = ["Latih", "Uji"]
KATEGORI = ["Rendah", "Sedang", "Tinggi", "Sangat tinggi"]

hero("Daftar Wilayah",
     "Cari dan saring IPM aktual dan IPM prediksi setiap kabupaten/kota.",
     label="Data")

# ---------- Filter ----------
with st.container(border=True):
    f1, f2, f3 = st.columns([2, 2, 1])
    cari = f1.text_input("Cari kabupaten/kota", placeholder="Contoh: Aceh Barat", icon=":material/search:")
    pilih_provinsi = f2.multiselect("Provinsi", sorted(tabel["Provinsi"].unique()), placeholder="Semua provinsi")
    pilih_tahun = f3.selectbox("Tahun", ["Semua tahun"] + sorted(tabel["Tahun"].unique(), reverse=True))
    j1, j2 = st.columns(2)
    pilih_jenis = j1.pills("Jenis data", JENIS, selection_mode="multi")
    pilih_kategori = j2.pills("Kategori IPM aktual (BPS)", KATEGORI, selection_mode="multi")

hasil = tabel.assign(**{"Kategori aktual": tabel["IPM"].map(kategori_ipm),
                        "Kategori prediksi": tabel["IPM_prediksi"].map(kategori_ipm)})
if cari:
    hasil = hasil[hasil["Kabupaten/Kota"].str.contains(cari, case=False, regex=False)]
if pilih_provinsi:
    hasil = hasil[hasil["Provinsi"].isin(pilih_provinsi)]
if pilih_tahun != "Semua tahun":
    hasil = hasil[hasil["Tahun"] == pilih_tahun]
if pilih_jenis:
    hasil = hasil[hasil["Jenis data"].isin(pilih_jenis)]
if pilih_kategori:
    hasil = hasil[hasil["Kategori aktual"].isin(pilih_kategori)]

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
    tampil = (hasil[["Kabupaten/Kota", "Provinsi", "Tahun", "Jenis data", "IPM", "Kategori aktual",
                     "IPM_prediksi", "Kategori prediksi", "Selisih"]]
              .rename(columns={"IPM": "IPM aktual", "IPM_prediksi": "IPM prediksi"})
              .sort_values(["Tahun", "Kabupaten/Kota"], ascending=[False, True]))
    # Data latih tidak punya IPM prediksi: ditulis "–" (Streamlit menampilkan sel kosong sebagai "None")
    tampil["IPM prediksi"] = tampil["IPM prediksi"].map(lambda v: "-" if pd.isna(v) else angka(v))
    tampil["Kategori prediksi"] = tampil["Kategori prediksi"].fillna("-")
    tampil["Selisih"] = tampil["Selisih"].map(lambda v: "-" if pd.isna(v) else ("+" if v > 0 else "") + angka(v))
    warnai = lambda k: (f"background-color: {LATAR_KATEGORI[k]}; color: {WARNA_TEKS_KATEGORI}; font-weight: 600"
                        if k in LATAR_KATEGORI else "")
    gaya = (tampil.style.format({"IPM aktual": "{:.2f}"}, decimal=",")
            .map(warnai, subset=["Kategori aktual", "Kategori prediksi"]))
    st.dataframe(gaya, hide_index=True, width="stretch", height=520,
                 column_config={"Tahun": st.column_config.NumberColumn(format="%d")})
    st.caption("Kategori mengikuti BPS: Rendah (< 60), Sedang (60 - < 70), Tinggi (70 - < 80), Sangat tinggi (≥ 80).")
    st.caption("IPM prediksi dan selisih hanya untuk **data uji** (daerah yang tidak dipakai melatih model). "
               "Data latih dipakai model untuk belajar, sehingga hanya IPM aktualnya yang ditampilkan (-).")

    st.download_button(
        "Unduh tabel (CSV)", tampil.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
        file_name="daftar_wilayah_ipm.csv", mime="text/csv", icon=":material/download:",
    )
