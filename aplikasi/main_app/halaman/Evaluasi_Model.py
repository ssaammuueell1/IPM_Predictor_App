import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import muat_info, muat_tabel, angka, LABEL_PREDIKTOR, WARNA_STATUS, URUTAN_STATUS
from tampilan import hero, rapikan, penjelasan, WARNA_UTAMA

info = muat_info()
tabel = muat_tabel()
silang = info["metrik_prediksi_silang"]["tuning"]
uji = info["metrik_uji"]
jumlah_daerah = info["jumlah"]["daerah"]
r2 = silang["R2"]
mae = angka(silang["MAE"], 2)

hero("Evaluasi Model",
     "Seberapa akurat model memperkirakan IPM?",
     label="Kinerja model", gambar_nama="header_evaluasi")

# ---------- Angka utama ----------
k1, k2 = st.columns(2)
k1.metric("R²", angka(r2, 2), border=True,
          help="Seberapa banyak variasi IPM yang dijelaskan model (0–1). Makin besar makin baik.")
k2.metric("Rata-rata kesalahan (MAE)", f"±{mae} poin IPM", border=True,
          help="Dipakai sebagai batas status di seluruh aplikasi.")
st.caption(f"Diukur pada {jumlah_daerah} daerah, masing-masing diprediksi oleh model yang tidak pernah "
           f"melihat daerah tersebut (validasi silang 5 fold).")

penjelasan(
    f"**R² = {angka(r2, 2)}**: IPM tiap daerah berbeda-beda. Model dapat menjelaskan sekitar "
    f"**{angka(r2 * 100, 0)}%** dari perbedaan itu hanya dari lima indikator. Sisanya, sekitar "
    f"{angka((1 - r2) * 100, 0)}%, dipengaruhi hal lain yang tidak ada di data, misalnya fasilitas sekolah "
    f"dan kesehatan. Nilai 1 berarti sempurna, nilai 0 berarti tidak lebih baik dari menebak rata-rata.\n\n"
    f"**MAE = ±{mae}**: rata-rata, perkiraan model meleset sekitar {mae} poin. Contohnya, jika IPM aktual "
    f"sebuah daerah 65, perkiraan model biasanya berada di antara {angka(65 - silang['MAE'])} dan "
    f"{angka(65 + silang['MAE'])}. Karena itu, selisih yang masih di dalam ±{mae} dianggap **sesuai prediksi**.\n\n"
    f"**Validasi silang 5 fold**: mirip ujian dengan soal yang belum pernah dilihat. Daerah dibagi menjadi "
    f"5 kelompok. Model belajar dari 4 kelompok, lalu menebak IPM kelompok ke-5. Ini diulang 5 kali, "
    f"sehingga setiap daerah pernah ditebak oleh model yang belum pernah melihatnya.",
    judul="Apa arti angka-angka ini?",
)

# ---------- Aktual vs prediksi | Kontribusi indikator ----------
kiri, kanan = st.columns([3, 2], gap="large")
with kiri:
    st.subheader("IPM aktual dan IPM prediksi")
    fig = px.scatter(tabel, x="IPM", y="IPM_prediksi", color="Status", color_discrete_map=WARNA_STATUS,
                     category_orders={"Status": URUTAN_STATUS},
                     hover_data=["Kabupaten/Kota", "Provinsi", "Tahun"], opacity=0.7,
                     labels={"IPM": "IPM aktual", "IPM_prediksi": "IPM prediksi"})
    garis = [tabel[["IPM", "IPM_prediksi"]].min().min(), tabel[["IPM", "IPM_prediksi"]].max().max()]
    fig.add_trace(go.Scatter(x=garis, y=garis, mode="lines", name="Prediksi tepat",
                             line=dict(color="gray", dash="dash")))
    st.plotly_chart(rapikan(fig, tinggi=440), width="stretch")
    penjelasan(
        "- Setiap **titik** adalah satu kabupaten/kota pada satu tahun.\n"
        "- **Sumbu mendatar** = IPM aktual (data BPS), **sumbu tegak** = IPM prediksi model.\n"
        "- Titik **tepat di garis putus-putus** berarti tebakan model sama persis dengan kenyataan.\n"
        "- Titik **di bawah garis** (hijau-teal): IPM aktual lebih tinggi dari tebakan model, "
        "jadi daerah itu **di atas prediksi**.\n"
        "- Titik **di atas garis** (merah): IPM aktual lebih rendah dari tebakan model, "
        "jadi daerah itu **di bawah prediksi**.\n"
        "- Makin rapat titik-titik mengikuti garis, makin akurat model. Arahkan kursor ke titik untuk melihat "
        "nama daerahnya."
    )

with kanan:
    st.subheader("Indikator paling berpengaruh")
    kontribusi = pd.Series(info["kontribusi_fitur"]).rename(index=LABEL_PREDIKTOR).sort_values()
    fig2 = px.bar(x=kontribusi.values, y=kontribusi.index, orientation="h", text_auto=".0f",
                  labels={"x": "Kontribusi (%)", "y": ""}, color_discrete_sequence=[WARNA_UTAMA])
    st.plotly_chart(rapikan(fig2, tinggi=440, legenda=False), width="stretch")
    teratas = kontribusi.index[-1]
    penjelasan(
        f"- Grafik ini menunjukkan **seberapa besar model bergantung** pada tiap indikator saat menebak IPM. "
        f"Total semua batang = 100%.\n"
        f"- Batang terpanjang, **{teratas}** ({angka(kontribusi.iloc[-1], 0)}%), paling banyak dipakai model.\n"
        f"- Grafik ini **tidak** menunjukkan arah (apakah indikator menaikkan atau menurunkan IPM) dan "
        f"**bukan** bukti sebab-akibat. Artinya hanya: tanpa indikator ini, tebakan model akan paling terganggu."
    )

# ---------- Perbandingan model ----------
st.subheader("Perbandingan model")
tabel_uji = (pd.DataFrame(uji).T[["MAE", "R2"]]
             .rename(columns={"MAE": "Rata-rata kesalahan (MAE)", "R2": "R²"},
                     index={"Baseline": "Tebak rata-rata (baseline)"}))
tabel_uji.index.name = "Model"
st.dataframe(tabel_uji.reset_index().style.format(precision=2, decimal=","), hide_index=True, width="stretch")
st.caption("Diukur pada data uji, yaitu 20% kabupaten/kota yang tidak dipakai saat melatih model.")
penjelasan(
    f"- **Tebak rata-rata (baseline)**: cara paling sederhana, yaitu menebak semua daerah dengan IPM rata-rata. "
    f"Kesalahannya sekitar ±{angka(uji['Baseline']['MAE'])} poin. Model baru berguna jika jauh lebih baik dari ini.\n"
    f"- **Tanpa tuning**: XGBoost dengan pengaturan bawaan.\n"
    f"- **Dengan tuning**: XGBoost yang pengaturannya dipilih dengan mencoba banyak kombinasi. Model inilah "
    f"yang dipakai di aplikasi.\n"
    f"- Cara membandingkan: **MAE makin kecil makin baik**, **R² makin besar makin baik**. "
    f"Kesalahan model dengan tuning (±{angka(uji['Dengan tuning']['MAE'])}) kira-kira "
    f"{angka(uji['Baseline']['MAE'] / uji['Dengan tuning']['MAE'], 1)} kali lebih kecil daripada baseline.\n"
    f"- **Mengapa R² di sini ({angka(uji['Dengan tuning']['R2'])}) berbeda dengan angka di atas "
    f"({angka(r2)})?** Tabel ini hanya memakai satu kelompok data uji. Angka di atas menguji seluruh "
    f"{jumlah_daerah} daerah lewat validasi silang, jadi lebih ketat dan lebih jujur. Aplikasi memakai angka "
    f"di atas.",
    judul="Cara membaca tabel ini",
)
