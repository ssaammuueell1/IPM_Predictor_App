import streamlit as st

from utils import muat_info, muat_tabel, angka, LABEL_PREDIKTOR
from tampilan import hero, penjelasan

info = muat_info()
tabel = muat_tabel()
jumlah = info["jumlah"]
ambang = angka(info["ambang_status"])

hero("Prediksi IPM di Wilayah dengan Kemiskinan Tinggi di Indonesia",
     "Membandingkan IPM aktual tiap kabupaten/kota dengan IPM yang diperkirakan model XGBoost Regression "
     "dari kondisi sosial-ekonominya.")

# ---------- Fitur aplikasi ----------
st.subheader("Fitur Aplikasi")
FITUR = [
    ("halaman/Landing_Page.py", "Beranda", ":material/home:",
     "Informasi dasar aplikasi, cakupan wilayah, dan panduan penggunaan."),
    ("halaman/Prediksi_IPM.py", "Prediksi IPM", ":material/insights:",
     "Lihat IPM prediksi dari data tersedia atau masukkan data baru."),
    ("halaman/Evaluasi_Model.py", "Evaluasi Model", ":material/analytics:",
     "Kinerja model pada data uji dan tiap fold beserta metrik evaluasi (MAE, RMSE, R²)."),
    ("halaman/Daftar_wilayah.py", "Daftar Wilayah", ":material/table_view:",
     "Seluruh daerah dalam cakupan beserta IPM prediksi, selisih, dan jenis data (latih/uji)."),
]
for i, (kolom, (halaman, nama, ikon, teks)) in enumerate(zip(st.columns(4), FITUR)):
    with kolom.container(border=True, height="stretch", key=f"kartu_fitur{i}"):
        st.markdown(f"#### :primary[{ikon}] {nama}")
        st.write(teks)
        st.page_link(halaman, label="Buka", icon=ikon)

# ---------- Cakupan dan periode ----------
kiri, kanan = st.columns(2)
with kiri.container(border=True, height="stretch"):
    st.markdown("#### :primary[:material/location_on:] Cakupan Wilayah")
    st.write("Kabupaten/kota dengan persentase penduduk miskin di atas 15% selama tiga tahun berturut-turut "
             "(2018–2020), mengacu pada kriteria wilayah kemiskinan tinggi Bappenas.")
    st.markdown(f"**Jumlah: {jumlah['daerah']} kabupaten/kota di {tabel['Provinsi'].nunique()} provinsi.**")
with kanan.container(border=True, height="stretch"):
    st.markdown("#### :primary[:material/calendar_month:] Periode & Variabel")
    st.write(f"Data {jumlah['tahun_awal']}–{jumlah['tahun_akhir']} ({angka(jumlah['baris'], 0)} baris). "
             "Target: Indeks Pembangunan Manusia (IPM).")
    st.markdown("**Prediktor:** " + ", ".join(LABEL_PREDIKTOR.values()) + ".")
    st.caption(f"Data dibagi per kabupaten/kota: {jumlah['daerah_latih']} daerah data latih dan "
               f"{jumlah['daerah_uji']} daerah data uji. Sumber: Badan Pusat Statistik (BPS).")

# ---------- Cara menggunakan ----------
st.subheader("Cara Menggunakan")
LANGKAH = [
    "Buka **Prediksi IPM**. Pilih kabupaten/kota dan tahun (**Data tersedia**), atau masukkan nilai kelima "
    "indikator sendiri (**Data baru**).",
    "Lihat **IPM prediksi**, **selisih** (IPM aktual − IPM prediksi), dan **statusnya**.",
    "Periksa ketepatan model di halaman **Evaluasi Model**.",
]
for kolom, (nomor, teks) in zip(st.columns(3), enumerate(LANGKAH, 1)):
    with kolom.container(border=True, height="stretch", key=f"kartu_langkah{nomor}"):
        st.markdown(f"#### :primary[Langkah {nomor}]")
        st.markdown(teks)

# ---------- Cara membaca hasil ----------
st.subheader("Cara Membaca Hasil")
st.markdown(f"**Selisih = IPM aktual − IPM prediksi.** Batas ±{ambang} adalah rata-rata kesalahan model (MAE) "
            "pada data uji.")
s1, s2, s3 = st.columns(3)
s1.success(f"**Di atas prediksi**: selisih lebih dari +{ambang}. IPM lebih tinggi dari daerah lain dengan kondisi serupa.")
s2.info(f"**Sesuai prediksi**: selisih antara −{ambang} dan +{ambang}. Masih dalam batas kesalahan model.")
s3.error(f"**Di bawah prediksi**: selisih kurang dari −{ambang}. IPM lebih rendah dari daerah serupa, perlu perhatian lebih.")
penjelasan(
    "| Istilah | Arti sederhana |\n"
    "|---|---|\n"
    "| **IPM** | Ukuran kualitas hidup dari BPS (0–100): kesehatan, pendidikan, dan pengeluaran. |\n"
    "| **IPM aktual** | IPM resmi yang dicatat BPS. |\n"
    "| **IPM prediksi** | IPM yang diperkirakan model dari lima indikator. |\n"
    "| **Data latih** | Daerah yang dipakai model untuk belajar. IPM prediksinya berasal dari validasi silang "
    "(k-fold), yaitu ditebak oleh model yang tidak melihat daerah itu. |\n"
    "| **Data uji** | Daerah yang disisihkan sejak awal dan tidak dipakai untuk belajar. |\n"
    "| **MAE** | Rata-rata kesalahan model dalam poin IPM. |\n"
    "| **R²** | Seberapa baik model menjelaskan perbedaan IPM antardaerah (0–1). |",
    judul="Istilah penting",
)

# ---------- Batasan ----------
st.subheader("Batasan Aplikasi")
st.warning(
    "- Hasil **bukan peramalan** IPM tahun berikutnya.\n"
    "- Hasil **bukan hubungan sebab-akibat** antara prediktor dan IPM.\n"
    "- Model hanya andal untuk nilai indikator di dalam rentang data latih.\n"
    "- Nilai yang dimasukkan sebaiknya berupa data resmi BPS.",
    icon=":material/warning:",
)

# ---------- Perancang ----------
st.subheader("Perancang")
with st.container(border=True):
    kiri, kanan = st.columns(2)
    kiri.markdown(
        "**Dirancang oleh**  \n"
        "Samuel Gregorio Criswell Kastono  \n"
        "NIM 535230077  \n"
        "Program Studi Teknik Informatika"
    )
    kanan.markdown(
        "**Dosen pembimbing**  \n"
        "1. Desi Arisandi, S.Kom., M.T.I.  \n"
        "2. Yemima Monica Geasela, S.Kom., M.Kom."
    )
st.caption("Aplikasi ini dibuat sebagai bagian dari skripsi: Prediksi IPM di Wilayah dengan Kemiskinan Tinggi "
           "di Indonesia Menggunakan XGBoost Regression.")
