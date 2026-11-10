import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils import muat_info, muat_model, muat_tabel, angka, LABEL_PREDIKTOR, WARNA_STATUS, kategori_ipm
from tampilan import (hero, kartu, badge_status, badge_kategori, kotak_kategori, grafik_selisih, tentukan_status,
                      penjelasan, arti_hasil)

def grafik_profil_indikator(nilai, rata_rata, kolom):
    nama_indikator = []
    perbedaan = []
    teks_batang = []
    detail = []

    for k in kolom:
        nilai_input = float(nilai[k])
        nilai_rata = float(rata_rata[k])
        if nilai_rata == 0:
            selisih_persen = None
            teks = "N/A"
            detail_persen = "Tidak dapat dihitung (rata-rata 0)"
        else:
            selisih_persen = ((nilai_input - nilai_rata) / nilai_rata) * 100
            teks = f"{selisih_persen:+.1f}%"
            detail_persen = f"{selisih_persen:+.2f}%"

        nama_indikator.append(LABEL_PREDIKTOR[k])
        perbedaan.append(selisih_persen)
        teks_batang.append(teks)
        detail.append([nilai_input, nilai_rata, detail_persen])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=perbedaan,
        y=nama_indikator,
        orientation="h",
        marker_color="#0F766E",
        text=teks_batang,
        textposition="outside",
        cliponaxis=False,
        customdata=detail,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Perbedaan relatif: %{customdata[2]}<br>"
            "Nilai input: %{customdata[0]:,.2f}<br>"
            "Rata-rata data latih: %{customdata[1]:,.2f}"
            "<extra></extra>"
        )
    ))
    fig.add_vline(x=0, line_dash="dash", line_color="#9CA3AF")

    fig.update_layout(
        height=350,
        title="Profil Indikator terhadap Rata-rata Data Latih",
        margin=dict(l=12, r=80, t=55, b=55),
        xaxis_title="Perbedaan terhadap rata-rata data latih (%)",
        yaxis_title="Indikator",
        showlegend=False,
        template="plotly_dark" if st.get_option("theme.base") == "dark" else "plotly_white",
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(automargin=True, zeroline=False)
    return fig


def tampilkan_prediksi_data_baru():
    info = muat_info()
    model = muat_model("tuning")
    tabel = muat_tabel()
    ambang = info["ambang_status"]
    rentang = info["rentang_prediktor"]
    kolom = info["kolom_prediktor"]
    INDIKATOR_PERSEN = ["PPM", "TPAK", "TPT"]
    KUNCI = {k: f"masukan_{k}" for k in kolom + ["IPM"]}


    # Isi awal kotak masukan (kosong)
    for kunci in KUNCI.values():
        st.session_state.setdefault(kunci, None)

    def isi_contoh():
        """Isi dengan median data penelitian tahun terakhir, supaya mudah dicoba."""
        terakhir = tabel[tabel["Tahun"] == tabel["Tahun"].max()]
        for k in kolom:
            st.session_state[KUNCI[k]] = round(float(terakhir[k].median()), 2)
        st.session_state[KUNCI["IPM"]] = round(float(terakhir["IPM"].median()), 2)

    def kosongkan():
        """mengosongkan data yang sudah di input user sebleimnya"""
        for kunci in KUNCI.values():
            st.session_state[kunci] = None
            
            

    # ---------- Form masukan ----------
    penjelasan(
        "1. Isi kelima indikator sebuah daerah, atau tekan **Isi contoh** untuk mencoba dengan nilai tengah data.\n"
        "2. Jika IPM aktual daerah tersebut diketahui, isi juga kotak **IPM aktual** supaya statusnya bisa dihitung.\n"
        "3. Tekan **Hitung IPM prediksi**.\n\n"
        "Arahkan kursor ke ikon (?) di setiap kotak untuk melihat rentang nilai yang ada di data penelitian.",
        judul="Cara memakai halaman ini",
    )
    tombol1, tombol2, _ = st.columns([1, 1, 4])
    tombol1.button("Isi contoh", icon=":material/auto_fix_high:", on_click=isi_contoh,
            help="Nilai tengah (median) data tahun terakhir.")
    tombol2.button("Kosongkan", icon=":material/restart_alt:", on_click=kosongkan,
            help="Hapus semua isian.")


    with st.form("form_data_baru", border=True):
        kiri, kanan = st.columns(2)
        nilai = {}
        for i, k in enumerate(kolom):
            tempat = kiri if i % 2 == 0 else kanan
            nilai[k] = tempat.number_input( 
                LABEL_PREDIKTOR[k],
                # min_value=0.0,
                # max_value=100.0 if k in INDIKATOR_PERSEN else None,
                value=None, step=0.01, format="%.2f", placeholder="Isi nilai", key=KUNCI[k],
                help=f"Rentang data: {angka(rentang[k]['min'])} - {angka(rentang[k]['max'])}",
            )
        ipm_aktual = kanan.number_input("IPM aktual (opsional)",
                                        value=None, step=0.01, format="%.2f", key=KUNCI["IPM"],
                                        placeholder="Kosongkan jika tidak ada",
                                        help="Isi untuk melihat selisih dan status.")
        kirim = st.form_submit_button("Hitung IPM prediksi", type="primary", icon=":material/calculate:")


    # ---------- Hasil ----------
    def tampilkan_hasil():
        if not kirim:
            return

        kosong = [LABEL_PREDIKTOR[k] for k in kolom if nilai[k] is None]
        if kosong:
            st.error("Isi semua indikator terlebih dahulu: " + ", ".join(kosong) + ".", icon=":material/error:")
            return
        tidak_mungkin = [LABEL_PREDIKTOR[k] for k in kolom
                        if nilai[k] < 0 or (k in INDIKATOR_PERSEN and nilai[k] > 100)]
        if tidak_mungkin:
            st.error("Nilai tidak mungkin (negatif, atau persentase di atas 100): "
                    + ", ".join(tidak_mungkin) + ".", icon=":material/error:")
            return
        if ipm_aktual is not None and (ipm_aktual < 0 or ipm_aktual > 100):
            st.error("IPM aktual harus antara 0 dan 100.", icon=":material/error:")
            return
        ipm_prediksi = float(model.predict(pd.DataFrame([nilai], columns=kolom))[0])

        st.subheader("Hasil")
        if ipm_aktual is None:
            kiri, _ = st.columns([1, 2])
            with kiri:
                kartu("IPM prediksi", angka(ipm_prediksi), "Isi IPM aktual untuk melihat statusnya.")
                badge_kategori(ipm_prediksi)
            st.markdown(
                f":material/summarize: **Artinya:** daerah dengan kondisi seperti yang dimasukkan diperkirakan memiliki "
                f"IPM sekitar **{angka(ipm_prediksi)}**, dengan kemungkinan meleset ±{angka(ambang)} poin "
                f"(antara {angka(ipm_prediksi - ambang)} dan {angka(ipm_prediksi + ambang)}). "
                f"Menurut kategori BPS, nilai ini termasuk **{kategori_ipm(ipm_prediksi)}**."
            )
            kotak_kategori(prediksi=ipm_prediksi)
        else:
            selisih = ipm_aktual - ipm_prediksi
            status = tentukan_status(selisih, ambang)
            k1, k2, k3 = st.columns(3)
            with k1:
                kartu("IPM aktual", angka(ipm_aktual), "Nilai yang dimasukkan")
                badge_kategori(ipm_aktual)
            with k2:
                kartu("IPM prediksi", angka(ipm_prediksi), "Perkiraan model")
                badge_kategori(ipm_prediksi)
            with k3:
                kartu("Selisih", ("+" if selisih > 0 else "") + angka(selisih), status, WARNA_STATUS[status])
            badge_status(status)
            st.markdown(":material/summarize: **Artinya:** " + arti_hasil(selisih, ambang, subjek="daerah tersebut"))
            st.plotly_chart(grafik_selisih(selisih, ambang), width="stretch", config={"displayModeBar": False})
            penjelasan(
                "- Kotak di atas adalah selisih (IPM aktual - IPM prediksi). Angka **0** di tengah berarti "
                "IPM aktual sama persis dengan prediksi.\n"
                f"- **Area biru di tengah** (-{angka(ambang)} sampai +{angka(ambang)}) = **sesuai prediksi**. "
                "Selisih sekecil ini masih wajar karena model rata-rata meleset sebesar itu.\n"
                "- **Area teal di kanan** = **di atas prediksi** (IPM aktual lebih tinggi dari perkiraan).\n"
                "- **Area merah di kiri** = **di bawah prediksi** (IPM aktual lebih rendah dari perkiraan).\n"
                "- **Tanda belah ketupat** menunjukkan posisi selisih daerah Anda. Makin jauh dari tengah, "
                "makin besar perbedaannya."
            )
            kotak_kategori(ipm_aktual, ipm_prediksi)

        rata_rata = info.get("rata_rata_prediktor")
        if not isinstance(rata_rata, dict) or any(k not in rata_rata for k in kolom):
            st.error(
                "Grafik profil indikator belum dapat ditampilkan karena metadata rata-rata data latih "
                "belum tersedia atau belum lengkap. Jalankan ulang bagian ekspor metadata pada notebook "
                "`aplikasi/notebook/Model+tuning+fold.ipynb`; proses tuning tidak perlu dijalankan ulang."
            )
        else:
            st.plotly_chart(
                grafik_profil_indikator(nilai, rata_rata, kolom),
                width="stretch",
                config={"displayModeBar": False},
            )
            penjelasan(
                "- Batang ke kanan menunjukkan nilai input di atas rata-rata data latih.\n"
                "- Batang ke kiri menunjukkan nilai input di bawah rata-rata data latih.\n"
                "- Persentase menunjukkan besarnya perbedaan relatif terhadap rata-rata.\n"
                "- Grafik hanya membandingkan karakteristik indikator, bukan menunjukkan hubungan sebab-akibat "
                "atau kontribusi indikator terhadap nilai prediksi IPM.",
                judul="Cara membaca profil indikator",
            )

        # Model tidak bisa memperkirakan di luar rentang data penelitian
        di_luar = [LABEL_PREDIKTOR[k] for k in kolom if not rentang[k]["min"] <= nilai[k] <= rentang[k]["max"]]
        if di_luar:
            st.warning("Di luar rentang data penelitian, jadi hasilnya kurang dapat diandalkan: "
                    + ", ".join(di_luar) + ".", icon=":material/warning:")


    tampilkan_hasil()
