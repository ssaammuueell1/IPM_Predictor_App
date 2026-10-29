import plotly.express as px
import streamlit as st

from utils import muat_info, muat_tabel, angka, URUTAN_STATUS, WARNA_STATUS, STATUS_ATAS, STATUS_SESUAI, STATUS_BAWAH
from tampilan import hero, kartu, rapikan, penjelasan

info = muat_info()
tabel = muat_tabel()
jumlah = info["jumlah"]
ambang = angka(info["ambang_status"])

hero("Tentang aplikasi",
     "Cara kerja aplikasi, cara membaca hasil, dan batasannya.",
     label="Tentang")

# ---------- Apa yang dilakukan aplikasi ini ----------
st.subheader("Apa yang dilakukan aplikasi ini?")
st.markdown(
    "Model **XGBoost** memperkirakan IPM setiap kabupaten/kota dari lima indikator: persentase penduduk miskin, "
    "Tingkat Partisipasi Angkatan Kerja, Tingkat Pengangguran Terbuka, Produk Domestik Regional Bruto (PDRB) per kapita, dan kepadatan penduduk.\n\n"
    "Perkiraan ini disebut **IPM prediksi**. Dengan membandingkannya dengan IPM aktual, kita bisa melihat "
    "daerah mana yang capaiannya lebih tinggi atau lebih rendah daripada daerah lain dengan kondisi serupa."
)

# ---------- Tutorial ----------
st.subheader("Cara memakai aplikasi")
st.markdown("Ikuti langkah berikut jika baru pertama kali membuka aplikasi ini.")
LANGKAH = [
    ("halaman/Landing_Page.py", "Beranda", ":material/home:",
     "Lihat peta. Pilih **Selisih IPM** untuk melihat daerah yang IPM-nya di atas (teal) atau di bawah (merah) "
     "perkiraan. Arahkan kursor ke daerah untuk melihat angkanya."),
    ("halaman/Daftar_wilayah.py", "Daftar Wilayah", ":material/table_view:",
     "Cari daerah dengan mengetik namanya, atau saring berdasarkan provinsi, tahun, dan status. "
     "Tabelnya bisa diunduh."),
    ("halaman/Prediksi_Data_Tersedia.py", "Prediksi Data Tersedia", ":material/query_stats:",
     "Pilih satu daerah dan tahun. Aplikasi menampilkan IPM aktual, IPM prediksi, statusnya, "
     "dan perkembangannya dari tahun ke tahun."),
    ("halaman/Prediksi_Data_Baru.py", "Prediksi Data Baru", ":material/edit_note:",
     "Masukkan lima indikator sendiri (atau tekan **Isi contoh**), lalu tekan **Hitung IPM prediksi**."),
    ("halaman/Evaluasi_Model.py", "Evaluasi Model", ":material/analytics:",
     "Lihat seberapa akurat model. Buka kotak bertanda :material/lightbulb: untuk penjelasan sederhana."),
]
for nomor, (halaman, nama, ikon, teks) in enumerate(LANGKAH, 1):
    with st.container(border=True):
        teks_kolom, tombol_kolom = st.columns([5, 1], vertical_alignment="center")
        teks_kolom.markdown(f"**{nomor}. {nama}**  \n{teks}")
        tombol_kolom.page_link(halaman, label="Buka", icon=ikon)
st.caption("Di setiap halaman, kotak :material/lightbulb: **Cara membaca grafik ini** bisa dibuka untuk penjelasan grafik.")

# ---------- Istilah ----------
penjelasan(
    "| Istilah | Arti sederhana |\n"
    "|---|---|\n"
    "| **IPM** (Indeks Pembangunan Manusia) | Ukuran kualitas hidup dari BPS (0–100), dilihat dari kesehatan "
    "(umur harapan hidup), pendidikan (lama sekolah), dan pengeluaran. Makin tinggi makin baik. |\n"
    "| **IPM aktual** | IPM resmi yang dicatat BPS. |\n"
    "| **IPM prediksi** | IPM yang diperkirakan model dari lima indikator, yaitu IPM yang \"wajar\" untuk "
    "daerah dengan kondisi seperti itu. |\n"
    "| **Selisih** | IPM aktual dikurangi IPM prediksi. Positif = lebih tinggi dari perkiraan. |\n"
    "| **Status** | Kesimpulan dari selisih: di atas, sesuai, atau di bawah prediksi. |\n"
    "| **XGBoost** | Metode *machine learning* yang belajar pola dari data lama untuk membuat perkiraan. |\n"
    f"| **MAE** | Rata-rata kesalahan model, yaitu ±{ambang} poin IPM. Dipakai sebagai batas status. |\n"
    "| **R²** | Seberapa baik model menjelaskan perbedaan IPM antardaerah (0–1). Makin besar makin baik. |",
    judul="Istilah penting",
)

# ---------- Cakupan data ----------
st.subheader("Data yang dipakai")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Kabupaten/Kota", jumlah["daerah"], border=True, icon=":material/location_city:")
k2.metric("Provinsi", tabel["Provinsi"].nunique(), border=True, icon=":material/map:")
k3.metric("Periode", f"{jumlah['tahun_awal']}–{jumlah['tahun_akhir']}", border=True, icon=":material/calendar_month:")
k4.metric("Jumlah data", f"{angka(jumlah['baris'], 0)} baris", border=True, icon=":material/dataset:")
st.caption("Daerah dengan penduduk miskin di atas 15% selama 2018-2020 (kriteria wilayah kemiskinan tinggi Bappenas).")

# ---------- Cara membaca hasil ----------
st.subheader("Cara membaca hasil")
st.markdown(f"**Selisih = IPM aktual - IPM prediksi.** Batas ±{ambang} adalah rata-rata kesalahan model.")
arti = {
    STATUS_ATAS: f"Selisih lebih dari +{ambang}. IPM lebih tinggi dari daerah serupa.",
    STATUS_SESUAI: f"Selisih antara -{ambang} dan +{ambang}. Sesuai perkiraan.",
    STATUS_BAWAH: f"Selisih kurang dari -{ambang}. IPM lebih rendah dari daerah serupa.",
}
jumlah_status = tabel["Status"].value_counts()
for kolom, status in zip(st.columns(3), URUTAN_STATUS):
    with kolom:
        kartu(status, f"{angka(jumlah_status.get(status, 0), 0)} baris", arti[status], WARNA_STATUS[status])
    st.write("")
penjelasan(
    "Misalkan sebuah kabupaten punya **IPM aktual 66,00**, sedangkan model memperkirakan **IPM prediksi 62,00**.\n\n"
    "1. Selisih = 66,00 - 62,00 = **+4,00**.\n"
    f"2. +4,00 lebih besar dari +{ambang}, jadi statusnya **Di atas prediksi**.\n"
    "3. Artinya, kabupaten ini mencapai IPM lebih tinggi daripada daerah lain dengan kondisi kemiskinan, "
    "lapangan kerja, dan ekonomi yang mirip.\n\n"
    f"Jika IPM prediksinya 64,50, selisihnya hanya +1,50 (masih di dalam ±{ambang}), jadi statusnya "
    "**Sesuai prediksi**.",
    judul="Contoh perhitungan",
)

# # ---------- Komposisi status per tahun ----------
# st.subheader("Status per tahun")
# komposisi = tabel.groupby(["Tahun", "Status"]).size().reset_index(name="Jumlah daerah")
# fig = px.bar(komposisi, x="Tahun", y="Jumlah daerah", color="Status", color_discrete_map=WARNA_STATUS,
#              category_orders={"Status": URUTAN_STATUS}, text="Jumlah daerah")
# fig.update_traces(textposition="inside", textfont_color="white")
# fig.update_xaxes(dtick=1, title=None)
# st.plotly_chart(rapikan(fig, tinggi=340), width="stretch")
# penjelasan(
#     f"Setiap batang adalah satu tahun dan tingginya menunjukkan jumlah daerah ({jumlah['daerah']}). "
#     "Warna dalam batang menunjukkan berapa daerah yang berstatus di atas (teal), sesuai (abu-abu), "
#     "atau di bawah prediksi (merah) pada tahun itu. Bagian merah yang mengecil dari tahun ke tahun "
#     "berarti makin sedikit daerah yang tertinggal."
# )

# ---------- Batasan ----------
st.subheader("Batasan")
st.markdown(
    "- IPM prediksi **bukan ramalan** IPM tahun depan.\n"
    "- Hasilnya **bukan hubungan sebab-akibat**.\n"
    "- Model hanya andal untuk nilai indikator di dalam rentang data penelitian."
)
