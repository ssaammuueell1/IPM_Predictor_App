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
     label="Kinerja model")

# ---------- Angka utama ----------
uji_tuning = uji["Dengan tuning"]
k1, k2, k3, k4 = st.columns(4)
k1.metric("R² data uji", angka(uji_tuning["R2"], 2), border=True,
          help="Diukur pada 20% kabupaten/kota yang tidak dipakai saat melatih model.")
k2.metric("MAE data uji", f"±{angka(uji_tuning['MAE'], 2)} poin", border=True)
k3.metric("R² validasi silang", angka(r2, 2), border=True,
          help=f"Seluruh {jumlah_daerah} daerah diuji bergiliran dengan model yang tidak pernah melihatnya (5 fold).")
k4.metric("MAE validasi silang", f"±{mae} poin", border=True,
          help="Dipakai sebagai batas status di seluruh aplikasi.")
st.caption(f"Data uji: 23 kabupaten/kota yang disisihkan sejak awal. Validasi silang: pengujian yang lebih ketat "
           f"pada seluruh {jumlah_daerah} daerah.")

penjelasan(
    f"**R² data uji = {angka(uji_tuning['R2'], 2)}**: pada daerah yang tidak dipakai saat melatih, model dapat "
    f"menjelaskan sekitar **{angka(uji_tuning['R2'] * 100, 0)}%** perbedaan IPM antardaerah hanya dari lima indikator. "
    f"Pada validasi silang yang menguji seluruh {jumlah_daerah} daerah, angkanya {angka(r2, 2)}, karena daerah yang "
    f"sulit ditebak (misalnya di Papua) ikut diuji. Nilai 1 berarti sempurna, nilai 0 berarti tidak lebih baik "
    f"dari menebak rata-rata.\n\n"
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
        "- **Nomor/Sumbu Horizontal** = IPM aktual (data BPS), **Nomor/Sumbu Vertikal** = IPM prediksi model.\n"
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
    f"- **Mengapa R² validasi silang ({angka(r2)}) lebih kecil?** Tabel ini hanya memakai 23 daerah uji. "
    f"Validasi silang menguji seluruh {jumlah_daerah} daerah, termasuk yang paling sulit ditebak, jadi lebih ketat. "
    f"Batas status ±{mae} diambil dari validasi silang supaya status setiap daerah tidak terlalu longgar.",
    judul="Cara membaca tabel ini",
)
