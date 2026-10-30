import pandas as pd
import streamlit as st

from utils import muat_info, muat_model, muat_tabel, angka, LABEL_PREDIKTOR, WARNA_STATUS
from tampilan import hero, kartu, badge_status, grafik_selisih, tentukan_status, penjelasan, arti_hasil
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
                step=0.01, format="%.2f", placeholder="Isi nilai", key=KUNCI[k],
                help=f"Rentang data: {angka(rentang[k]['min'])} - {angka(rentang[k]['max'])}",
            )
        ipm_aktual = kanan.number_input("IPM aktual (opsional)",
                                        step=0.01, format="%.2f", key=KUNCI["IPM"],
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
            st.markdown(
                f":material/summarize: **Artinya:** daerah dengan kondisi seperti yang dimasukkan diperkirakan memiliki "
                f"IPM sekitar **{angka(ipm_prediksi)}**, dengan kemungkinan meleset ±{angka(ambang)} poin "
                f"(antara {angka(ipm_prediksi - ambang)} dan {angka(ipm_prediksi + ambang)})."
            )
        else:
            selisih = ipm_aktual - ipm_prediksi
            status = tentukan_status(selisih, ambang)
            k1, k2, k3 = st.columns(3)
            with k1:
                kartu("IPM aktual", angka(ipm_aktual), "Nilai yang dimasukkan")
            with k2:
                kartu("IPM prediksi", angka(ipm_prediksi), "Perkiraan model")
            with k3:
                kartu("Selisih", ("+" if selisih > 0 else "") + angka(selisih), status, WARNA_STATUS[status])
            badge_status(status)
            st.markdown(":material/summarize: **Artinya:** " + arti_hasil(selisih, ambang, subjek="daerah tersebut"))
            st.plotly_chart(grafik_selisih(selisih, ambang), width="stretch", config={"displayModeBar": False})
            penjelasan(
                "- Pita ini adalah penggaris selisih (IPM aktual - IPM prediksi). Angka **0** di tengah berarti "
                "IPM aktual sama persis dengan prediksi.\n"
                f"- **Area abu-abu di tengah** (-{angka(ambang)} sampai +{angka(ambang)}) = **sesuai prediksi**. "
                "Selisih sekecil ini masih wajar karena model rata-rata meleset sebesar itu.\n"
                "- **Area teal di kanan** = **di atas prediksi** (IPM aktual lebih tinggi dari perkiraan).\n"
                "- **Area merah di kiri** = **di bawah prediksi** (IPM aktual lebih rendah dari perkiraan).\n"
                "- **Tanda belah ketupat** menunjukkan posisi selisih daerah Anda. Makin jauh dari tengah, "
                "makin besar perbedaannya."
            )

        # Model tidak bisa memperkirakan di luar rentang data penelitian
        di_luar = [LABEL_PREDIKTOR[k] for k in kolom if not rentang[k]["min"] <= nilai[k] <= rentang[k]["max"]]
        if di_luar:
            st.warning("Di luar rentang data penelitian, jadi hasilnya kurang dapat diandalkan: "
                    + ", ".join(di_luar) + ".", icon=":material/warning:")


    tampilkan_hasil()
