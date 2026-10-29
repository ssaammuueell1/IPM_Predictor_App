import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import muat_tabel, muat_info, angka, WARNA_STATUS, LABEL_PREDIKTOR
from tampilan import hero, badge_status, rapikan, penjelasan, arti_hasil, WARNA_UTAMA, WARNA_SEKUNDER

tabel = muat_tabel()
info = muat_info()
ambang = info["ambang_status"]
jumlah_daerah = info["jumlah"]["daerah"]

hero("Prediksi Data Tersedia",
     "Lihat IPM satu daerah: aktual, prediksi, dan selisihnya dari tahun ke tahun.",
     label="Per daerah")

# ---------- Pilihan daerah dan tahun ----------
with st.container(border=True):
    p1, p2 = st.columns(2)
    provinsi = p1.selectbox("Provinsi", sorted(tabel["Provinsi"].unique()))
    daftar_daerah = sorted(tabel.loc[tabel["Provinsi"] == provinsi, "Kabupaten/Kota"].unique())
    daerah = p2.selectbox("Kabupaten/Kota", daftar_daerah)

    data_daerah = tabel[(tabel["Provinsi"] == provinsi) & (tabel["Kabupaten/Kota"] == daerah)].sort_values("Tahun")
    daftar_tahun = data_daerah["Tahun"].tolist()
    tahun = st.segmented_control("Tahun", daftar_tahun, default=daftar_tahun[-1])
    if tahun is None:                      # tombol tahun yang aktif diklik lagi -> kembali ke tahun terakhir
        tahun = daftar_tahun[-1]

baris = data_daerah[data_daerah["Tahun"] == tahun].iloc[0]
data_tahun = tabel[tabel["Tahun"] == tahun]

# ---------- Hasil ----------
judul, status_kolom = st.columns([3, 1], vertical_alignment="center")
judul.subheader(f"{daerah}, {provinsi} · {tahun}")
with status_kolom:
    badge_status(baris["Status"])

k1, k2, k3 = st.columns(3)
k1.metric("IPM aktual", angka(baris["IPM"]), border=True)
k2.metric("IPM prediksi", angka(baris["IPM_prediksi"]), border=True)
k3.metric("Selisih", ("+" if baris["Selisih"] > 0 else "") + angka(baris["Selisih"]), border=True,
          help=f"IPM aktual − IPM prediksi. Di luar ±{angka(ambang)} berarti di atas/di bawah prediksi.")
with st.container(border=True):
    st.markdown(":material/summarize: **Artinya:** " + arti_hasil(baris["Selisih"], ambang))

kiri, kanan = st.columns([3, 2], gap="large")

# ---------- Grafik tren ----------
with kiri:
    st.subheader("Tren IPM")
    tahun_x = data_daerah["Tahun"]
    prediksi = data_daerah["IPM_prediksi"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tahun_x, y=prediksi + ambang, mode="lines", line=dict(width=0),
                             showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=tahun_x, y=prediksi - ambang, mode="lines", line=dict(width=0), fill="tonexty",
                             fillcolor="rgba(156,163,175,0.2)", name=f"Batas ±{angka(ambang)}", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=tahun_x, y=prediksi, mode="lines+markers", name="IPM prediksi",
                             line=dict(color=WARNA_SEKUNDER, dash="dash"),
                             hovertemplate="IPM prediksi %{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=tahun_x, y=data_daerah["IPM"], mode="lines+markers", name="IPM aktual",
                             line=dict(color=WARNA_UTAMA, width=3),
                             marker=dict(size=11, color=[WARNA_STATUS[s] for s in data_daerah["Status"]],
                                         line=dict(color="white", width=2)),
                             customdata=data_daerah["Status"],
                             hovertemplate="IPM aktual %{y:.2f} · %{customdata}<extra></extra>"))
    fig.add_vline(x=tahun, line_dash="dot", line_color="gray")
    fig.update_layout(hovermode="x unified", yaxis_title="IPM")
    fig.update_xaxes(dtick=1)
    st.plotly_chart(rapikan(fig, tinggi=380), width="stretch")
    penjelasan(
        "- **Garis teal tebal** = IPM aktual (data BPS) dari tahun ke tahun.\n"
        "- **Garis abu-abu putus-putus** = IPM yang diperkirakan model.\n"
        f"- **Area abu-abu** = batas toleransi ±{angka(ambang)} poin di sekitar prediksi. Selama titik IPM aktual "
        "berada di dalam area ini, daerah dianggap **sesuai prediksi**.\n"
        "- **Warna titik** menunjukkan status tiap tahun: teal = di atas prediksi, abu-abu = sesuai, "
        "merah = di bawah prediksi.\n"
        "- **Garis titik-titik tegak** menandai tahun yang sedang dipilih.\n"
        "- Jika garis teal terus berada di atas area abu-abu, daerah ini konsisten naik (lebih baik) "
        "dari perkiraan; jika terus di bawah, daerah ini konsisten tertinggal."
    )

# ---------- Posisi indikator ----------
with kanan:
    st.subheader(f"Indikator vs rata-rata ({tahun})")
    kolom = list(LABEL_PREDIKTOR)
    beda = pd.Series([(baris[k] / data_tahun[k].mean() - 1) * 100 for k in kolom], index=LABEL_PREDIKTOR.values())
    fig2 = go.Figure(go.Bar(
        x=beda.values, y=beda.index, orientation="h",
        marker_color=[WARNA_UTAMA if v >= 0 else WARNA_SEKUNDER for v in beda.values],
        text=[("+" if v > 0 else "") + angka(v, 0) + "%" for v in beda.values],
        textposition="outside", cliponaxis=False, hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))
    fig2.add_vline(x=0, line_color="#9CA3AF")
    # Ruang tambahan di kiri-kanan supaya label angka di ujung batang tidak terpotong
    ruang = max(abs(beda.min()), abs(beda.max()), 10) * 0.45
    fig2.update_xaxes(title=f"Beda dari rata-rata {jumlah_daerah} daerah (%)", ticksuffix="%",
                      range=[min(beda.min(), 0) - ruang, max(beda.max(), 0) + ruang])
    fig2.update_yaxes(autorange="reversed", title=None)
    st.plotly_chart(rapikan(fig2, tinggi=380, legenda=False), width="stretch")
    tertinggi, terendah = beda.idxmax(), beda.idxmin()
    penjelasan(
        f"- Setiap batang membandingkan indikator {daerah} dengan **rata-rata {jumlah_daerah} daerah** "
        f"pada tahun {tahun}.\n"
        "- **0%** = sama dengan rata-rata. **+20%** = 20% lebih tinggi dari rata-rata, **−20%** = 20% lebih rendah.\n"
        "- Teal = di atas rata-rata, abu-abu = di bawah rata-rata.\n"
        "- Hati-hati: **lebih tinggi tidak selalu lebih baik**. Untuk penduduk miskin dan pengangguran, "
        "nilai di atas rata-rata justru kurang baik.\n"
        f"- Pada {tahun}, indikator yang paling jauh di atas rata-rata adalah **{tertinggi}**, dan yang paling "
        f"jauh di bawah rata-rata adalah **{terendah}**.\n"
        "- Grafik ini hanya menggambarkan **posisi** daerah, bukan penyebab selisih IPM."
    )
