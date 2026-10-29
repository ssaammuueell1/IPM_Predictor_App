import streamlit as st

from utils import muat_tabel, muat_info, angka, URUTAN_STATUS, WARNA_STATUS, STATUS_ATAS, STATUS_BAWAH
from tampilan import hero, kartu_status, LATAR_STATUS

tabel = muat_tabel()
info = muat_info()

hero("Daftar Wilayah",
     "Cari dan saring IPM aktual dan IPM prediksi setiap kabupaten/kota.",
     label="Data")

# ---------- Filter ----------
with st.container(border=True):
    f1, f2, f3 = st.columns([2, 2, 1])
    cari = f1.text_input("Cari kabupaten/kota", placeholder="Contoh: Aceh Barat", icon=":material/search:")
    pilih_provinsi = f2.multiselect("Provinsi", sorted(tabel["Provinsi"].unique()), placeholder="Semua provinsi")
    pilih_tahun = f3.selectbox("Tahun", ["Semua tahun"] + sorted(tabel["Tahun"].unique(), reverse=True))
    pilih_status = st.pills("Status", URUTAN_STATUS, selection_mode="multi")

hasil = tabel
if cari:
    hasil = hasil[hasil["Kabupaten/Kota"].str.contains(cari, case=False, regex=False)]
if pilih_provinsi:
    hasil = hasil[hasil["Provinsi"].isin(pilih_provinsi)]
if pilih_tahun != "Semua tahun":
    hasil = hasil[hasil["Tahun"] == pilih_tahun]
if pilih_status:
    hasil = hasil[hasil["Status"].isin(pilih_status)]

# ---------- Ringkasan jumlah per status ----------
jumlah_status = hasil["Status"].value_counts()
for kolom, status in zip(st.columns(3), URUTAN_STATUS):
    with kolom:
        kartu_status(status, int(jumlah_status.get(status, 0)), len(hasil))
st.caption(f"{angka(len(hasil), 0)} dari {angka(len(tabel), 0)} baris · klik judul kolom untuk mengurutkan")

# ---------- Tabel ----------
if hasil.empty:
    st.warning("Tidak ada data yang cocok dengan filter.", icon=":material/search_off:")
else:
    tampil = (hasil[["Kabupaten/Kota", "Provinsi", "Tahun", "IPM", "IPM_prediksi", "Selisih", "Status"]]
              .rename(columns={"IPM": "IPM aktual", "IPM_prediksi": "IPM prediksi"})
              .sort_values(["Tahun", "Kabupaten/Kota"], ascending=[False, True]))

    def warna_status(nilai):
        return (f"color: {WARNA_STATUS.get(nilai, 'inherit')}; background-color: {LATAR_STATUS.get(nilai, 'transparent')}; "
                f"font-weight: 600")

    def warna_selisih(nilai):
        if nilai > info["ambang_status"]:
            return f"color: {WARNA_STATUS[STATUS_ATAS]}; font-weight: 600"
        if nilai < -info["ambang_status"]:
            return f"color: {WARNA_STATUS[STATUS_BAWAH]}; font-weight: 600"
        return ""

    gaya = (tampil.style
            .format({"IPM aktual": "{:.2f}", "IPM prediksi": "{:.2f}", "Selisih": "{:+.2f}"}, decimal=",")
            .map(warna_status, subset=["Status"])
            .map(warna_selisih, subset=["Selisih"]))

    st.dataframe(gaya, hide_index=True, width="stretch", height=520,
                 column_config={"Tahun": st.column_config.NumberColumn(format="%d")})

    st.download_button(
        "Unduh tabel (CSV)", tampil.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
        file_name="daftar_wilayah_ipm.csv", mime="text/csv", icon=":material/download:",
    )
