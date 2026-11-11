import streamlit as st
from pathlib import Path

from utils import muat_info, muat_tabel, angka, URUTAN_KATEGORI, TEKS_BATAS_KATEGORI
from tampilan import LATAR_KATEGORI, WARNA_KATEGORI_DASAR, WARNA_TEKS_KATEGORI

info = muat_info()
tabel = muat_tabel()
jumlah = info["jumlah"]
ambang = angka(info["ambang_status"])
uji = info["metrik_uji"]["Dengan tuning"]

st.html("""<style>
/* Kepala Beranda: judul, tujuan, tombol utama */
.st-key-kepala_beranda {background: linear-gradient(120deg, rgba(15,118,110,.16), rgba(15,118,110,.03));
  border-left: 6px solid #0F766E; border-radius: 14px; padding: 1.6rem 1.8rem 1.3rem;}
.st-key-kepala_beranda h1 {font-size: 2.6rem;}
.st-key-kepala_beranda [data-testid="stMarkdownContainer"] p {font-size: 1.15rem; color:#374151;}
.st-key-kepala_beranda [data-testid="stPageLink"] a {background:#0F766E; border-radius:10px; padding:.6rem 1.6rem; width:auto;}
.st-key-kepala_beranda [data-testid="stPageLink"] a * {color:#fff !important; font-weight:700; font-size:1.05rem;}
/* Langkah prediksi */
.langkah4 {display:grid; grid-template-columns:repeat(4, 1fr); gap:.8rem;}
@media (max-width: 1000px) {.langkah4 {grid-template-columns:repeat(2, 1fr);}}
@media (max-width: 560px) {.langkah4 {grid-template-columns:1fr;}}
.langkah4 .lk {display:flex; gap:.85rem; align-items:center; border:1px solid rgba(15,118,110,.25);
  border-radius:12px; padding:1rem; background:rgba(15,118,110,.03);}
.langkah4 .ikon {font-family:"Material Symbols Rounded"; font-size:1.7rem; line-height:1; color:#0F766E;
  background:rgba(15,118,110,.12); border-radius:12px; width:3rem; height:3rem; flex:none;
  display:flex; align-items:center; justify-content:center; -webkit-font-smoothing:antialiased;}
.no {font-size:.72rem; font-weight:700; color:#0F766E; text-transform:uppercase; letter-spacing:.05em;}
.jd {font-weight:700; font-size:1.05rem; color:#1F2937; line-height:1.3;}
.sb {font-size:.88rem; color:#6B7280; line-height:1.4;}
/* Kartu mode prediksi */
[class*="st-key-mode"] {border-top: 4px solid #0F766E !important;}
[class*="st-key-mode"] [data-testid="stPageLink"] a {width:auto;}
</style>""")

# ---------- Kepala: tujuan aplikasi dan tombol utama ----------
with st.container(key="kepala_beranda"):
    st.title("Prediksi IPM Wilayah Kemiskinan Tinggi")
    st.markdown("Masukkan lima indikator sosial-ekonomi sebuah kabupaten/kota, model XGBoost menghitung "
                "**IPM prediksi**-nya, lalu bandingkan dengan **IPM aktual** BPS pada tahun yang sama.")
    st.page_link("halaman/Prediksi_IPM.py", label="Mulai Prediksi IPM", icon=":material/rocket_launch:")
    st.caption(f"{jumlah['daerah']} kabupaten/kota kemiskinan tinggi, periode {jumlah['tahun_awal']}–{jumlah['tahun_akhir']}, "
               f"sumber data BPS")

# ---------- Cara prediksi dihasilkan ----------
st.subheader("Bagaimana prediksi dihasilkan?")
LANGKAH = [
    ("edit_note", "Data masukan", "5 indikator dari BPS"),
    ("model_training", "Hitung IPM prediksi", "Model XGBoost Regression"),
    ("compare_arrows", "Bandingkan", "dengan IPM aktual BPS"),
    ("military_tech", "Baca hasil", "Selisih, status, dan kategori"),
]
st.html("<div class='langkah4'>" + "".join(
    f"<div class='lk'><div class='ikon'>{ik}</div>"
    f"<div><div class='no'>Langkah {i}</div><div class='jd'>{jd}</div><div class='sb'>{sb}</div></div></div>"
    for i, (ik, jd, sb) in enumerate(LANGKAH, 1)) + "</div>")

# ---------- Tiga cara memakai fitur prediksi ----------
st.subheader("Tiga cara memakai Prediksi IPM")
m1, m2, m3 = st.columns(3)
with m1.container(border=True, height="stretch", key="mode_a"):
    st.markdown("#### :primary[:material/database:] Data tersedia")
    st.caption("Pilih kabupaten/kota dan tahun dari data BPS 2017–2024.")
    st.page_link("halaman/Prediksi_IPM.py", label="Pilih daerah", icon=":material/arrow_forward:")
with m2.container(border=True, height="stretch", key="mode_b"):
    st.markdown("#### :primary[:material/edit_note:] Data baru")
    st.caption("Isi sendiri kelima indikator satu daerah, dengan atau tanpa IPM aktual.")
    st.page_link("halaman/Prediksi_IPM.py", label="Isi indikator", icon=":material/arrow_forward:")
with m3.container(border=True, height="stretch", key="mode_c"):
    st.markdown("#### :primary[:material/upload_file:] Unggah banyak data")
    st.caption("Unggah file berisi banyak daerah sekaligus, hasilnya bisa diunduh kembali.")
    st.page_link("halaman/Prediksi_IPM.py", label="Unggah file", icon=":material/arrow_forward:")

# ---------- Kunci membaca ----------
st.subheader("Membaca hasil")
s1, s2, s3 = st.columns(3)
s1.success(f"**Di atas prediksi**: selisih > +{ambang}", icon=":material/trending_up:")
s2.info(f"**Sesuai prediksi**: selisih −{ambang} s.d. +{ambang}", icon=":material/check_circle:")
s3.error(f"**Di bawah prediksi**: selisih < −{ambang}", icon=":material/trending_down:")
for kolom, k in zip(st.columns(4), URUTAN_KATEGORI):
    kolom.html(f"<div style='background:{LATAR_KATEGORI[k]};border-radius:8px;padding:8px 12px;"
               f"border-left:4px solid {WARNA_KATEGORI_DASAR};color:{WARNA_TEKS_KATEGORI}'>"
               f"<b>{k}</b>: {TEKS_BATAS_KATEGORI[k]}</div>")
st.caption(f"Selisih = IPM aktual − IPM prediksi. Batas ±{ambang} adalah rata-rata kesalahan model (MAE) pada "
           "data uji. Kategori IPM menurut BPS.")

# ---------- Sekilas fitur lain ----------
f1, f2, f3 = st.columns(3, vertical_alignment="center")
f1.page_link("halaman/Evaluasi_Model.py", label=f"Evaluasi Model (R² {angka(uji['R2'], 3)}, MAE {angka(uji['MAE'])})",
             icon=":material/analytics:")
f2.page_link("halaman/Daftar_wilayah.py", label=f"Daftar Wilayah ({jumlah['daerah']} kab/kota)",
             icon=":material/table_view:")
with f3.expander("Cakupan dan batasan", icon=":material/info:"):
    st.markdown("- Kab/kota dengan penduduk miskin > 15% selama 2018–2020 (Bappenas).\n"
                "- Bukan peramalan dan bukan sebab-akibat.\n- Andal di dalam rentang data latih.")

with st.container(border=True):
    kiri, kanan = st.columns(2)
    kiri.markdown("**Dirancang oleh**  \nSamuel Gregorio Criswell Kastono  \nNIM 535230077  \n"
                  "Program Studi Teknik Informatika")
    kanan.markdown("**Dosen pembimbing**  \n1. Desi Arisandi, S.Kom., M.T.I.  \n"
                   "2. Yemima Monica Geasela, S.Kom., M.Kom.")

# Buku panduan disimpan di folder main_app (ikut ter-deploy); tombol hanya muncul jika file ada
pdf_path = Path(__file__).resolve().parents[1] / "Manual_Book.pdf"
if pdf_path.exists():
    st.download_button("Download Buku Panduan Aplikasi (PDF)", data=pdf_path.read_bytes(),
                       file_name="Manual_Book.pdf", mime="application/pdf", type="primary")
