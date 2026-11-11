"""Komponen tampilan yang dipakai bersama oleh semua halaman (kepala halaman, kartu, grafik selisih)."""
import plotly.graph_objects as go
import streamlit as st

from utils import (angka, WARNA_STATUS, STATUS_ATAS, STATUS_SESUAI, STATUS_BAWAH, URUTAN_KATEGORI,
                   TEKS_BATAS_KATEGORI, kategori_ipm)

# Warna grafik dipilih supaya tetap terbaca di mode terang maupun gelap
WARNA_UTAMA = "#0F766E"      # satu-satunya warna aksen
WARNA_SEKUNDER = "#9CA3AF"   # abu-abu untuk pembanding
WARNA_REDUP = "#D1D5DB"      # abu-abu muda untuk latar/baseline
WARNA_GARIS = "#9CA3AF"


def transparan(warna_hex, alpha):
    """'#RRGGBB' -> 'rgba(r,g,b,alpha)'. Warna transparan menyatu dengan latar terang maupun gelap."""
    r, g, b = (int(warna_hex[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r},{g},{b},{alpha})"


# Warna latar lembut untuk setiap status (dipakai di tabel dan pita grafik)
LATAR_STATUS = {s: transparan(w, 0.16) for s, w in WARNA_STATUS.items()}
# Kategori IPM BPS: warna tema (teal) yang makin pekat dari Rendah ke Sangat tinggi
WARNA_KATEGORI_DASAR = "#0F766E"
WARNA_TEKS_KATEGORI = "#134E4A"
LATAR_KATEGORI = {k: transparan(WARNA_KATEGORI_DASAR, a)
                  for k, a in zip(URUTAN_KATEGORI, [0.05, 0.12, 0.21, 0.32])}
BADGE_STATUS = {STATUS_ATAS: "green", STATUS_SESUAI: "gray", STATUS_BAWAH: "red"}
IKON_STATUS = {STATUS_ATAS: ":material/trending_up:", STATUS_SESUAI: ":material/check_circle:",
               STATUS_BAWAH: ":material/trending_down:"}


GAYA = """
<style>
/* Kepala halaman: pita teal lembut */
.st-key-kepala {background: linear-gradient(120deg, rgba(15,118,110,.14), rgba(15,118,110,.03));
  border-left: 6px solid #0F766E; border-radius: 12px; padding: 1.1rem 1.4rem 1.2rem; margin-bottom: .8rem;}
/* Judul bagian: garis aksen di kiri */
[data-testid="stHeading"] h3 {border-left: 4px solid #0F766E; padding-left: .6rem;}
/* Kartu angka: latar teal tipis */
[data-testid="stMetric"] {background: rgba(15,118,110,.06);}
/* Kartu fitur & langkah di Beranda: garis teal di atas */
[class*="st-key-kartu"] {border-top: 4px solid #0F766E !important;}
/* Kotak kategori IPM BPS: garis teal di kiri dan latar teal tipis */
.st-key-kotak_kategori {border-left: 6px solid #0F766E !important; background: rgba(15,118,110,.04);}
</style>
"""


def pasang_gaya():
    """Sedikit warna aksen teal (kepala halaman, judul bagian, kartu). Transparan agar cocok di mode terang/gelap."""
    st.html(GAYA)


def hero(judul, deskripsi, label=None, gambar_nama=None, aksen="", chip=None, besar=False):
    """Kepala halaman sederhana: judul, satu kalimat penjelasan, dan keterangan singkat (jika ada)."""
    with st.container(key="kepala"):
        st.title(f"{judul} {aksen}".strip())
        st.write(deskripsi)
        if chip:
            st.caption(" · ".join(chip))


def kartu(label, angka_utama, keterangan, warna=None):
    """Angka ringkas memakai komponen metric bawaan Streamlit."""
    st.metric(label, angka_utama, border=True)
    st.caption(keterangan)


def penjelasan(isi, judul="Cara membaca grafik ini", buka=False):
    """Kotak penjelasan yang bisa dibuka-tutup, untuk pembaca yang belum terbiasa dengan istilah statistik."""
    with st.expander(judul, icon=":material/lightbulb:", expanded=buka):
        st.markdown(isi)


def arti_hasil(selisih, ambang, subjek="daerah ini"):
    """Kalimat sederhana yang menjelaskan arti selisih dan status untuk pembaca awam."""
    status = tentukan_status(selisih, ambang)
    if status == STATUS_ATAS:
        return (f"IPM aktual {subjek} **{angka(selisih)} poin lebih tinggi** daripada IPM prediksi dari kelima "
                f"indikatornya. Capaian IPM-nya **melampaui** perkiraan model.")
    if status == STATUS_BAWAH:
        return (f"IPM aktual {subjek} **{angka(-selisih)} poin lebih rendah** daripada IPM prediksi dari kelima "
                f"indikatornya. Capaian IPM-nya **belum mencapai** perkiraan model, sehingga perlu ditelusuri "
                f"faktor lain di luar kelima indikator.")
    return (f"IPM aktual {subjek} dan IPM prediksi dari kelima indikatornya hanya berbeda "
            f"**{angka(abs(selisih))} poin**, masih di dalam batas ±{angka(ambang)}. Capaian IPM-nya **sejalan** "
            f"dengan perkiraan model.")


def kartu_status(status, jumlah, total):
    persen = jumlah / total * 100 if total else 0
    kartu(status, angka(jumlah, 0), f"{angka(persen, 1)}% dari {angka(total, 0)} baris", WARNA_STATUS[status])


def badge_status(status):
    st.badge(status, icon=IKON_STATUS[status], color=BADGE_STATUS[status])


def tentukan_status(selisih, ambang):
    if selisih > ambang:
        return STATUS_ATAS
    if selisih < -ambang:
        return STATUS_BAWAH
    return STATUS_SESUAI


def rapikan(fig, tinggi=380, legenda=True):
    """Gaya grafik Plotly yang seragam di semua halaman."""
    fig.update_layout(
        height=tinggi, margin=dict(l=10, r=10, t=30 if legenda else 10, b=10), separators=",.",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
        hoverlabel=dict(font_size=13), showlegend=legenda,
        uniformtext=dict(minsize=10, mode="hide"),     # sembunyikan label yang tidak muat di batang kecil
    )
    fig.update_traces(textangle=0, selector=dict(type="bar"))
    return fig


def grafik_selisih(selisih, ambang):
    """Pita horizontal: terakota (di bawah), abu hangat (sesuai), teal (di atas), dengan penanda posisi selisih."""
    batas = max(abs(selisih) + 1.5, ambang * 2.2)
    status = tentukan_status(selisih, ambang)
    fig = go.Figure()
    for x0, x1, s in [(-batas, -ambang, STATUS_BAWAH), (-ambang, ambang, STATUS_SESUAI), (ambang, batas, STATUS_ATAS)]:
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=0, y1=1, fillcolor=LATAR_STATUS[s], line_width=0, layer="below")
        fig.add_annotation(x=(x0 + x1) / 2, y=0.18, text=s, showarrow=False,
                           font=dict(size=11, color=WARNA_STATUS[s]))
    for x in (-ambang, ambang):
        fig.add_vline(x=x, line=dict(color=WARNA_GARIS, width=1, dash="dot"))
    fig.add_vline(x=0, line=dict(color=WARNA_GARIS, width=1))
    fig.add_trace(go.Scatter(
        x=[selisih], y=[0.6], mode="markers+text", text=[("+" if selisih > 0 else "") + angka(selisih)],
        textposition="top center", textfont=dict(size=14, color=WARNA_STATUS[status]),
        marker=dict(symbol="diamond", size=20, color=WARNA_STATUS[status], line=dict(color="white", width=2)),
        hovertemplate="Selisih %{x:.2f}<extra></extra>",
    ))
    fig.update_xaxes(range=[-batas, batas], zeroline=False, showgrid=False,
                     tickvals=[-ambang, 0, ambang], ticktext=[f"−{angka(ambang)}", "0", f"+{angka(ambang)}"])
    fig.update_yaxes(range=[0, 1.15], visible=False)
    return rapikan(fig, tinggi=150, legenda=False)


def badge_kategori(nilai, awalan="Kategori BPS"):
    """Badge oranye berisi kategori IPM BPS dari sebuah nilai IPM."""
    st.badge(f"{awalan}: {kategori_ipm(nilai)}", icon=":material/military_tech:", color="primary")


def grafik_kategori(aktual=None, prediksi=None):
    """Pita empat kategori IPM BPS dengan penanda posisi IPM aktual dan/atau IPM prediksi."""
    nilai = [v for v in (aktual, prediksi) if v is not None]
    kiri = min(45.0, min(nilai) - 3)
    kanan = max(90.0, max(nilai) + 3)
    batas = [kiri, 60, 70, 80, kanan]
    fig = go.Figure()
    for i, k in enumerate(URUTAN_KATEGORI):
        fig.add_shape(type="rect", x0=batas[i], x1=batas[i + 1], y0=0, y1=1, line_width=0,
                      fillcolor=LATAR_KATEGORI[k], layer="below")
        fig.add_annotation(x=(batas[i] + batas[i + 1]) / 2, y=0.13, showarrow=False,
                           text=f"<b>{k}</b><br>{TEKS_BATAS_KATEGORI[k]}",
                           font=dict(size=11, color=WARNA_TEKS_KATEGORI))
    for x in (60, 70, 80):
        fig.add_vline(x=x, line=dict(color=WARNA_KATEGORI_DASAR, width=1, dash="dot"))
    penanda = []
    if aktual is not None:
        penanda.append(("IPM aktual", aktual, WARNA_TEKS_KATEGORI, "diamond", 0.66))
    if prediksi is not None:
        penanda.append(("IPM prediksi", prediksi, "#6B7280", "circle", 0.66 if aktual is None else 0.44))
    for nama, v, warna, simbol, y in penanda:
        fig.add_trace(go.Scatter(
            x=[v], y=[y], mode="markers+text", name=nama, text=[f"{nama} {angka(v)}"],
            textposition="middle right", textfont=dict(size=12, color=warna),
            marker=dict(symbol=simbol, size=16, color=warna, line=dict(color="white", width=2)),
            hovertemplate=f"{nama} %{{x:.2f}} · {kategori_ipm(v)}<extra></extra>"))
    fig.update_xaxes(range=[kiri, kanan], showgrid=False, zeroline=False, tickvals=[60, 70, 80])
    fig.update_yaxes(range=[0, 1], visible=False)
    return rapikan(fig, tinggi=170, legenda=False)


def kotak_kategori(aktual=None, prediksi=None):
    """Kotak menonjol: kategori IPM BPS untuk IPM aktual dan/atau IPM prediksi, beserta pitanya."""
    with st.container(border=True, key="kotak_kategori"):
        st.markdown("##### :material/military_tech: Kategori IPM menurut BPS")
        bagian = []
        if aktual is not None:
            bagian.append(f"IPM aktual **{angka(aktual)}** → **:primary[{kategori_ipm(aktual)}]**")
        if prediksi is not None:
            bagian.append(f"IPM prediksi **{angka(prediksi)}** → **:primary[{kategori_ipm(prediksi)}]**")
        st.markdown(" &nbsp;·&nbsp; ".join(bagian))
        st.plotly_chart(grafik_kategori(aktual, prediksi), width="stretch", config={"displayModeBar": False})
        if aktual is not None and prediksi is not None and kategori_ipm(aktual) != kategori_ipm(prediksi):
            st.caption("Kategori IPM aktual dan IPM prediksi berbeda: selisihnya melewati salah satu batas 60/70/80.")
        st.caption("Kategori melihat **besarnya** IPM menurut pengelompokan BPS. Berbeda dengan **status**, "
                   "yang membandingkan IPM aktual dengan IPM prediksi.")
