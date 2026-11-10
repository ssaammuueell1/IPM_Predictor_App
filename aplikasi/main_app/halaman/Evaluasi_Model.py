import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import muat_info, muat_tabel, angka, LABEL_PREDIKTOR
from tampilan import hero, rapikan, penjelasan, WARNA_UTAMA, WARNA_SEKUNDER

info = muat_info()
tabel = muat_tabel()
uji = info["metrik_uji"]
jumlah = info["jumlah"]
uji_tuning = uji["Dengan tuning"]
fold = pd.DataFrame(info["tabel_fold"]["tuning"])

hero("Evaluasi Model",
     "Seberapa akurat model memperkirakan IPM?",
     label="Kinerja model")

# ---------- Angka utama: data uji ----------
k1, k2, k3, k4 = st.columns(4)
k1.metric("R² data uji", angka(uji_tuning["R2"], 2), border=True,
          help=f"Diukur pada {jumlah['daerah_uji']} kabupaten/kota yang tidak dipakai saat melatih model.")
k2.metric("MAE data uji", f"±{angka(uji_tuning['MAE'], 2)}", border=True,
          help="Rata-rata kesalahan dalam poin IPM. Dipakai sebagai batas status di seluruh aplikasi.")
k3.metric("RMSE data uji", angka(uji_tuning["RMSE"], 2), border=True,
          help="Seperti MAE, tetapi kesalahan besar dihukum lebih berat.")
k4.metric("MAE rata-rata k-fold", f"±{angka(fold['MAE'].mean(), 2)}", border=True,
          help="Rata-rata MAE 5 fold validasi silang pada data latih.")
st.caption(f"Data uji: {jumlah['daerah_uji']} kabupaten/kota ({jumlah['baris_uji']} baris) yang disisihkan sejak awal. "
           f"Data latih: {jumlah['daerah_latih']} kabupaten/kota ({jumlah['baris_latih']} baris).")
penjelasan(
    f"**R² data uji = {angka(uji_tuning['R2'], 2)}**: pada daerah yang tidak dipakai saat melatih, model dapat "
    f"menjelaskan sekitar **{angka(uji_tuning['R2'] * 100, 0)}%** perbedaan IPM antardaerah hanya dari lima indikator. "
    "Nilai 1 berarti sempurna, nilai 0 berarti tidak lebih baik dari menebak rata-rata.\n\n"
    f"**MAE data uji = {angka(uji_tuning['MAE'], 2)}**: rata-rata tebakan model meleset sekitar "
    f"{angka(uji_tuning['MAE'], 2)} poin IPM. Angka ini dipakai sebagai batas status (di atas / sesuai / di bawah prediksi)."
)

# ---------- Tabel per fold ----------
st.subheader("Hasil validasi silang (5-Fold GroupKFold) pada data latih")
tampil_fold = pd.DataFrame({
    "Fold": [str(f) for f in fold["Fold"]] + ["Rata-rata", "Standar deviasi"],
    "Daerah validasi": [str(int(v)) for v in fold["Daerah validasi"]] + ["", ""],
    "Baris": [str(int(v)) for v in fold["Baris"]] + ["", ""],
    "MAE": [angka(v, 3) for v in fold["MAE"]] + [angka(fold["MAE"].mean(), 3), angka(fold["MAE"].std(), 3)],
    "RMSE": [angka(v, 3) for v in fold["RMSE"]] + [angka(fold["RMSE"].mean(), 3), angka(fold["RMSE"].std(), 3)],
    "R²": [angka(v, 3) for v in fold["R2"]] + [angka(fold["R2"].mean(), 3), angka(fold["R2"].std(), 3)],
})
st.dataframe(tampil_fold, hide_index=True, width="stretch")
penjelasan(
    f"- Data latih ({jumlah['daerah_latih']} daerah) dibagi menjadi 5 kelompok per kabupaten/kota. Lima kali, empat "
    "kelompok dipakai untuk belajar dan satu kelompok ditebak.\n"
    "- **Standar deviasi kecil** berarti hasil model stabil, tidak bergantung pada daerah mana yang ditebak.\n"
    "- R² per fold bisa lebih kecil dari R² data uji karena dihitung hanya dari sebaran IPM daerah di fold itu. "
    "Untuk membandingkan fold, gunakan MAE.",
    judul="Cara membaca tabel ini",
)

# ---------- Rata-rata IPM aktual vs prediksi per tahun (data uji) ----------
st.subheader("Rata-rata IPM aktual dan IPM prediksi per tahun (data uji)")
data_uji = tabel[tabel["Jenis data"] == "Uji"]
per_tahun = data_uji.groupby("Tahun").agg(aktual=("IPM", "mean"), prediksi=("IPM_prediksi", "mean")).reset_index()
per_tahun["selisih"] = per_tahun["aktual"] - per_tahun["prediksi"]
teks_selisih = [("+" if v > 0 else "") + angka(v) for v in per_tahun["selisih"]]

fig_tahun = go.Figure()
fig_tahun.add_trace(go.Scatter(x=per_tahun["Tahun"], y=per_tahun["prediksi"], mode="lines+markers",
                               name="Rata-rata IPM prediksi", line=dict(color=WARNA_SEKUNDER, dash="dash", width=2),
                               marker=dict(size=8), hovertemplate="Prediksi %{y:.2f}<extra></extra>"))
fig_tahun.add_trace(go.Scatter(x=per_tahun["Tahun"], y=per_tahun["aktual"], mode="lines+markers",
                               name="Rata-rata IPM aktual", line=dict(color=WARNA_UTAMA, width=3),
                               marker=dict(size=9, line=dict(color="white", width=2)), customdata=teks_selisih,
                               hovertemplate="Aktual %{y:.2f} · selisih %{customdata}<extra></extra>"))
fig_tahun.update_layout(hovermode="x unified", yaxis_title="Rata-rata IPM", legend_traceorder="reversed")
fig_tahun.update_xaxes(dtick=1)
st.plotly_chart(rapikan(fig_tahun, tinggi=360), width="stretch")

awal, akhir = per_tahun.iloc[0], per_tahun.iloc[-1]
naik_aktual, naik_prediksi = akhir["aktual"] - awal["aktual"], akhir["prediksi"] - awal["prediksi"]
tahun_positif = per_tahun.loc[per_tahun["selisih"] > 0, "Tahun"].tolist()
penjelasan(
    f"- Setiap titik adalah **rata-rata {jumlah['daerah_uji']} kabupaten/kota data uji** pada satu tahun.\n"
    "- **Garis teal** = rata-rata IPM aktual (BPS), **garis abu-abu putus-putus** = rata-rata IPM prediksi model "
    "untuk daerah dan tahun yang sama.\n"
    "- Jika kedua garis berdekatan, secara rata-rata model mengikuti IPM sebenarnya. Jarak antargaris = rata-rata selisih "
    "(arahkan kursor ke titik untuk melihat angkanya).\n"
    f"- Dari {int(awal['Tahun'])} ke {int(akhir['Tahun'])}, rata-rata IPM aktual naik **{angka(naik_aktual)}** poin, "
    f"sedangkan rata-rata IPM prediksi naik **{angka(naik_prediksi)}** poin.\n"
    + (f"- Garis aktual berada di atas garis prediksi pada tahun {', '.join(str(t) for t in tahun_positif)}: "
       "pada tahun-tahun itu IPM aktual cenderung lebih tinggi daripada perkiraan model.\n" if tahun_positif else "")
    + "- Model hanya memakai lima indikator pada tahun yang sama, tanpa informasi tahun. Kenaikan IPM yang tidak "
    "tercermin pada kelima indikator tersebut tidak ikut tertangkap oleh model."
)

# ---------- Aktual vs prediksi | Kontribusi indikator ----------
kiri, kanan = st.columns([3, 2], gap="large")
with kiri:
    st.subheader("IPM aktual dan IPM prediksi (data uji)")
    data_uji = tabel[tabel["Jenis data"] == "Uji"]
    fig = px.scatter(data_uji, x="IPM", y="IPM_prediksi", color_discrete_sequence=[WARNA_UTAMA],
                     hover_data=["Kabupaten/Kota", "Provinsi", "Tahun"], opacity=0.8,
                     labels={"IPM": "IPM aktual", "IPM_prediksi": "IPM prediksi"})
    garis = [data_uji[["IPM", "IPM_prediksi"]].min().min(), data_uji[["IPM", "IPM_prediksi"]].max().max()]
    fig.add_trace(go.Scatter(x=garis, y=garis, mode="lines", name="Prediksi tepat",
                             line=dict(color="gray", dash="dash")))
    st.plotly_chart(rapikan(fig, tinggi=440), width="stretch")
    penjelasan(
        f"- Setiap **titik** adalah satu kabupaten/kota data uji pada satu tahun ({len(data_uji)} titik).\n"
        "- **Sumbu horizontal** = IPM aktual (BPS), **sumbu vertikal** = IPM prediksi.\n"
        "- Semua titik ditebak oleh model utama pada daerah yang tidak pernah dipakai untuk melatihnya.\n"
        "- Titik **tepat di garis putus-putus** berarti tebakan sama persis dengan kenyataan. Makin rapat titik "
        "mengikuti garis, makin akurat model."
    )

with kanan:
    st.subheader("Indikator paling berpengaruh")
    kontribusi = pd.Series(info["kontribusi_fitur"]).rename(index=LABEL_PREDIKTOR).sort_values()
    fig2 = px.bar(x=kontribusi.values, y=kontribusi.index, orientation="h", text_auto=".0f",
                  labels={"x": "Kontribusi (%)", "y": ""}, color_discrete_sequence=[WARNA_UTAMA])
    st.plotly_chart(rapikan(fig2, tinggi=440, legenda=False), width="stretch")
    teratas = kontribusi.index[-1]
    penjelasan(
        "- Seberapa besar model bergantung pada tiap indikator (total gain). Total semua batang = 100%.\n"
        f"- Batang terpanjang, **{teratas}** ({angka(kontribusi.iloc[-1], 0)}%), paling banyak dipakai model.\n"
        "- Grafik ini **tidak** menunjukkan arah pengaruh dan **bukan** bukti sebab-akibat."
    )
