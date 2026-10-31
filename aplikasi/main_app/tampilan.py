"""Komponen tampilan yang dipakai bersama oleh semua halaman (kepala halaman, kartu, grafik selisih)."""
import plotly.graph_objects as go
import streamlit as st

from utils import angka, WARNA_STATUS, STATUS_ATAS, STATUS_SESUAI, STATUS_BAWAH

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
BADGE_STATUS = {STATUS_ATAS: "green", STATUS_SESUAI: "gray", STATUS_BAWAH: "red"}
IKON_STATUS = {STATUS_ATAS: ":material/trending_up:", STATUS_SESUAI: ":material/check_circle:",
               STATUS_BAWAH: ":material/trending_down:"}


def pasang_gaya():
    """Tampilan memakai gaya bawaan Streamlit, jadi tidak ada CSS tambahan."""
    pass


def hero(judul, deskripsi, label=None, gambar_nama=None, aksen="", chip=None, besar=False):
    """Kepala halaman sederhana: judul, satu kalimat penjelasan, dan keterangan singkat (jika ada)."""
    st.title(f"{judul} {aksen}".strip())
    st.write(deskripsi)
    if chip:
        st.caption(" · ".join(chip))
    st.divider()


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
        return (f"IPM aktual **{angka(selisih)} poin lebih tinggi** daripada perkiraan model. Artinya, capaian "
                f"pembangunan manusia {subjek} **lebih baik** daripada daerah lain yang kondisi sosial-ekonominya mirip.")
    if status == STATUS_BAWAH:
        return (f"IPM aktual **{angka(-selisih)} poin lebih rendah** daripada perkiraan model. Artinya, capaian "
                f"pembangunan manusia {subjek} **tertinggal** dari daerah lain yang kondisi sosial-ekonominya mirip, "
                f"sehingga perlu perhatian lebih.")
    return (f"IPM aktual dan IPM prediksi hanya berbeda **{angka(abs(selisih))} poin**, masih di dalam batas "
            f"±{angka(ambang)}. Artinya, capaian {subjek} **setara** dengan daerah lain yang kondisinya mirip.")


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
