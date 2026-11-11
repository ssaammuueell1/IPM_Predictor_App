import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import muat_tabel, muat_info, angka, WARNA_STATUS, LABEL_PREDIKTOR, BATAS_KATEGORI, kategori_ipm
from tampilan import (hero, badge_status, badge_kategori, kotak_kategori, rapikan, penjelasan, arti_hasil,
                      WARNA_UTAMA, WARNA_SEKUNDER)

def tampilkan_prediksi_data_tersedia():
    

    tabel = muat_tabel()
    info = muat_info()
    ambang = info["ambang_status"]
    jumlah_daerah = info["jumlah"]["daerah"]



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
    uji = baris["Jenis data"] == "Uji"
    judul, status_kolom = st.columns([3, 1], vertical_alignment="center")
    judul.subheader(f"{daerah}, {provinsi} · {tahun}")
    with status_kolom:
        if uji:
            badge_status(baris["Status"])
        badge_kategori(baris["IPM"])
        st.badge(f"Data {baris['Jenis data'].lower()}", icon=":material/dataset:", color="blue")
    if uji:
        st.caption("Daerah ini termasuk **data uji**: tidak dipakai untuk melatih model. "
                   "IPM prediksi berasal dari model utama (hasil tuning).")
        k1, k2, k3 = st.columns(3)
        k1.metric("IPM aktual", angka(baris["IPM"]), border=True)
        k2.metric("IPM prediksi", angka(baris["IPM_prediksi"]), border=True)
        k3.metric("Selisih", ("+" if baris["Selisih"] > 0 else "") + angka(baris["Selisih"]), border=True,
                help=f"IPM aktual - IPM prediksi. Di luar ±{angka(ambang)} (MAE data uji) berarti di atas/di bawah prediksi.")
        with st.container(border=True):
            st.markdown(":material/summarize: **Artinya:** " + arti_hasil(baris["Selisih"], ambang, subjek=daerah))
        kotak_kategori(baris["IPM"], baris["IPM_prediksi"])
    else:
        st.caption("Daerah ini termasuk **data latih**: dipakai model untuk belajar, sehingga IPM prediksinya "
                   "tidak ditampilkan (model sudah melihat daerah ini, jadi perbandingannya tidak adil). "
                   "Perbandingan IPM aktual dan prediksi hanya untuk daerah data uji.")
        k1, _ = st.columns([1, 2])
        k1.metric("IPM aktual", angka(baris["IPM"]), border=True)
        kotak_kategori(baris["IPM"])

    kiri, kanan = st.columns([3, 2], gap="large")

    # ---------- Grafik tren: IPM aktual vs IPM prediksi per tahun ----------
    with kiri:
        st.subheader("IPM aktual vs IPM prediksi per tahun" if uji else "Tren IPM aktual per tahun")
        tahun_x = data_daerah["Tahun"]
        prediksi = data_daerah["IPM_prediksi"]
        kategori_aktual = data_daerah["IPM"].map(kategori_ipm)

        fig = go.Figure()
        if uji:
            fig.add_trace(go.Scatter(x=tahun_x, y=prediksi + ambang, mode="lines", line=dict(width=0),
                                    showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=tahun_x, y=prediksi - ambang, mode="lines", line=dict(width=0), fill="tonexty",
                                    fillcolor="rgba(156,163,175,0.2)", name=f"Batas ±{angka(ambang)}", hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=tahun_x, y=prediksi, mode="lines+markers", name="IPM prediksi",
                                    line=dict(color=WARNA_SEKUNDER, dash="dash"),
                                    hovertemplate="IPM prediksi %{y:.2f}<extra></extra>"))
            info_hover = [f"{s} · selisih {'+' if d > 0 else ''}{angka(d)} · kategori {k}"
                          for s, d, k in zip(data_daerah["Status"], data_daerah["Selisih"], kategori_aktual)]
        else:
            info_hover = [f"kategori {k} · data latih" for k in kategori_aktual]
        warna_titik = [WARNA_STATUS[s] for s in data_daerah["Status"]] if uji else WARNA_UTAMA
        # Entri legenda terpisah supaya warnanya tetap teal (titik aslinya diwarnai sesuai status)
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines+markers", name="IPM aktual",
                                line=dict(color=WARNA_UTAMA, width=3), marker=dict(size=9, color=WARNA_UTAMA)))
        fig.add_trace(go.Scatter(x=tahun_x, y=data_daerah["IPM"], mode="lines+markers", name="IPM aktual",
                                showlegend=False, line=dict(color=WARNA_UTAMA, width=3),
                                marker=dict(size=11, color=warna_titik,
                                            line=dict(color="white", width=2)),
                                customdata=info_hover,
                                hovertemplate="IPM aktual %{y:.2f} · %{customdata}<extra></extra>"))
        fig.add_vline(x=tahun, line_dash="dot", line_color="gray")

        # Garis batas kategori IPM BPS (60, 70, 80) yang masuk ke rentang grafik
        nilai_y = pd.concat([data_daerah["IPM"], prediksi - ambang, prediksi + ambang]).dropna()
        bawah, atas = nilai_y.min() - 1.5, nilai_y.max() + 1.5
        for batas, nama in BATAS_KATEGORI.items():
            if bawah < batas < atas:
                fig.add_hline(y=batas, line=dict(color="#5B8F8A", width=1, dash="dot"),
                              annotation_text=f"{batas} · mulai {nama}", annotation_position="top left",
                              annotation_font=dict(size=11, color="#5B8F8A"))
        fig.update_layout(hovermode="x unified", yaxis_title="IPM")
        fig.update_xaxes(dtick=1)
        fig.update_yaxes(range=[bawah, atas])
        st.plotly_chart(rapikan(fig, tinggi=380), width="stretch")
        if not uji:
            st.caption("Hanya IPM aktual yang ditampilkan karena daerah ini data latih.")
        penjelasan(
            "- **Garis teal tebal** = IPM aktual (data BPS) dari tahun ke tahun.\n"
            "- **Garis abu-abu putus-putus** = IPM yang diperkirakan model pada tahun yang sama "
            "(hanya untuk daerah data uji).\n"
            f"- **Area abu-abu** = batas toleransi ±{angka(ambang)} poin di sekitar prediksi. Selama titik IPM aktual "
            "berada di dalam area ini, daerah dianggap **sesuai prediksi**.\n"
            "- **Warna titik** (khusus data uji) menunjukkan status tiap tahun: teal = di atas prediksi, biru = sesuai, "
            "merah = di bawah prediksi.\n"
            "- **Garis hijau keabuan titik-titik mendatar** = batas kategori IPM BPS: di bawah 60 Rendah, 60 sampai di bawah 70 "
            "Sedang, 70 sampai di bawah 80 Tinggi, 80 ke atas Sangat tinggi. Hanya batas yang masuk ke rentang grafik "
            "yang digambar.\n"
            "- **Garis titik-titik tegak** menandai tahun yang sedang dipilih.\n"
            "- Jika garis teal terus berada di atas area abu-abu, daerah ini konsisten naik (lebih baik) "
            "dari perkiraan; jika terus di bawah, daerah ini konsisten tertinggal."
        )

    # ---------- Posisi indikator ----------
    with kanan:
        st.subheader(f"Indikator {daerah} dibandingkan rata-rata ({tahun})")
        st.caption(f"Pembanding: rata-rata {jumlah_daerah} kabupaten/kota kemiskinan tinggi pada tahun {tahun}.")
        kolom = list(LABEL_PREDIKTOR)
        rata_tahun = [data_tahun[k].mean() for k in kolom]
        beda = pd.Series([(baris[k] / r - 1) * 100 for k, r in zip(kolom, rata_tahun)], index=LABEL_PREDIKTOR.values())
        fig2 = go.Figure(go.Bar(
            x=beda.values, y=beda.index, orientation="h",
            marker_color=[WARNA_UTAMA if v >= 0 else WARNA_SEKUNDER for v in beda.values],
            text=[("+" if v > 0 else "") + angka(v, 0) + "%" for v in beda.values],
            textposition="outside", cliponaxis=False,
            customdata=[[angka(baris[k]), angka(r)] for k, r in zip(kolom, rata_tahun)],
            hovertemplate=(f"<b>%{{y}}</b><br>{daerah}: %{{customdata[0]}}<br>"
                           f"Rata-rata {jumlah_daerah} kab/kota: %{{customdata[1]}}<br>Beda: %{{x:.1f}}%<extra></extra>"),
        ))
        fig2.add_vline(x=0, line_color="#9CA3AF")
        # Ruang tambahan di kiri-kanan supaya label angka di ujung batang tidak terpotong
        ruang = max(abs(beda.min()), abs(beda.max()), 10) * 0.45
        fig2.update_xaxes(title=f"Beda dari rata-rata {jumlah_daerah} kab/kota tahun {tahun} (%)", ticksuffix="%",
                        range=[min(beda.min(), 0) - ruang, max(beda.max(), 0) + ruang])
        fig2.update_yaxes(autorange="reversed", title=None)
        st.plotly_chart(rapikan(fig2, tinggi=380, legenda=False), width="stretch")
        tertinggi, terendah = beda.idxmax(), beda.idxmin()
        penjelasan(
            f"- Setiap batang membandingkan nilai indikator {daerah} dengan **rata-rata indikator yang sama dari "
            f"{jumlah_daerah} kabupaten/kota kemiskinan tinggi** pada tahun {tahun}.\n"
            "- Arahkan kursor ke batang untuk melihat nilai daerah ini dan nilai rata-ratanya.\n"
            "- **0%** = sama dengan rata-rata. **+20%** = 20% lebih tinggi dari rata-rata, **-20%** = 20% lebih rendah.\n"
            "- Teal = di atas rata-rata, abu-abu = di bawah rata-rata.\n"
            "- Hati-hati: **lebih tinggi tidak selalu lebih baik**. Untuk penduduk miskin dan pengangguran, "
            "nilai di atas rata-rata justru kurang baik.\n"
            f"- Pada {tahun}, indikator yang paling jauh di atas rata-rata adalah **{tertinggi}**, dan yang paling "
            f"jauh di bawah rata-rata adalah **{terendah}**.\n"
            "- Grafik ini hanya menggambarkan **posisi** daerah, bukan penyebab selisih IPM."
        )
