import io

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils import (muat_info, muat_model, muat_tabel, angka, LABEL_PREDIKTOR, WARNA_STATUS, kategori_ipm,
                   URUTAN_KATEGORI, STATUS_ATAS, STATUS_SESUAI, STATUS_BAWAH, jarak_kategori)
from tampilan import (hero, kartu, badge_status, badge_kategori, kotak_kategori, grafik_selisih, tentukan_status,
                      penjelasan, arti_hasil, rapikan, LATAR_KATEGORI, WARNA_TEKS_KATEGORI, WARNA_KATEGORI_DASAR,
                      transparan)

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


INDIKATOR_PERSEN = ["PPM", "TPAK", "TPT"]
BATAS_BARIS = 5000


def tampilkan_prediksi_data_baru():
    info = muat_info()
    model = muat_model("tuning")
    tabel = muat_tabel()

    cara = st.segmented_control("Cara memasukkan data", ["Satu daerah", "Banyak data (unggah file)"],
                                default="Satu daerah", key="cara_data_baru")
    st.caption("Isi kelima indikator dari **tahun yang sama** dengan IPM yang ingin diperkirakan "
               "(contoh: IPM 2027 membutuhkan indikator tahun 2027).")
    if cara == "Banyak data (unggah file)":
        tampilkan_unggah_file(model, info, tabel)
    else:
        tampilkan_satu_daerah(model, info, tabel)


def tampilkan_satu_daerah(model, info, tabel):
    ambang = info["ambang_status"]
    rentang = info["rentang_prediktor"]
    kolom = info["kolom_prediktor"]
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


# =====================================================================
# Banyak data: unggah file dengan format sama seperti Dataset_Final
# =====================================================================
KOLOM_TEMPLATE = ["Kabupaten/Kota", "Provinsi", "Tahun", "PPM", "TPAK", "TPT", "PDRB", "KP", "IPM"]
NAMA_KOLOM_LAIN = {
    "Kabupaten/Kota": ["kabupaten/kota", "kabupaten", "kota", "kab/kota", "daerah", "wilayah"],
    "Provinsi": ["provinsi", "prov"],
    "Tahun": ["tahun", "year"],
    "IPM": ["ipm", "ipm aktual", "ipm_aktual"],
}


def ke_excel(lembar):
    """{nama sheet: DataFrame} -> isi file .xlsx (bytes)."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as penulis:
        for nama, df in lembar.items():
            df.to_excel(penulis, sheet_name=nama, index=False)
    return buffer.getvalue()


def buat_template(tabel, info):
    """Template mengikuti kolom Dataset_Final. Dua baris contoh dari data asli tahun terakhir:
    satu dengan IPM (untuk melihat status), satu tanpa IPM (hanya prediksi)."""
    terakhir = tabel[(tabel["Tahun"] == tabel["Tahun"].max()) & (tabel["Jenis data"] == "Uji")]
    contoh = terakhir.head(2)[KOLOM_TEMPLATE].reset_index(drop=True)
    contoh.loc[1, "IPM"] = None
    rentang = info["rentang_prediktor"]
    petunjuk = pd.DataFrame({
        "Kolom": KOLOM_TEMPLATE,
        "Wajib?": ["Tidak", "Tidak", "Tidak", "Ya", "Ya", "Ya", "Ya", "Ya", "Tidak"],
        "Isi": [
            "Nama kabupaten/kota (untuk identitas baris)",
            "Nama provinsi (untuk identitas baris)",
            "Tahun data. Kelima indikator dan IPM harus dari tahun yang sama",
        ] + [f"{LABEL_PREDIKTOR[k]}. Rentang data latih {angka(rentang[k]['min'])} - {angka(rentang[k]['max'])}"
             for k in info["kolom_prediktor"]]
        + ["IPM aktual (BPS). Isi jika ingin melihat selisih dan status; kosongkan jika hanya ingin prediksi"],
    })
    return contoh, petunjuk


def baca_file(berkas):
    """Baca .xlsx (sheet pertama) atau .csv (pemisah koma/titik koma dideteksi otomatis)."""
    if berkas.name.lower().endswith(".xlsx"):
        return pd.read_excel(berkas, dtype=object)
    teks = berkas.getvalue().decode("utf-8-sig", errors="replace")
    return pd.read_csv(io.StringIO(teks), sep=None, engine="python", dtype=str)


def seragamkan_kolom(df, kolom):
    """Cocokkan nama kolom file dengan nama baku (tidak peka huruf besar/kecil; boleh nama lengkap indikator)."""
    peta = {}
    for c in df.columns:
        kunci = str(c).strip().lower()
        for k in kolom:
            if kunci in (k.lower(), LABEL_PREDIKTOR[k].lower()):
                peta[c] = k
        for baku, lain in NAMA_KOLOM_LAIN.items():
            if kunci in lain:
                peta[c] = baku
    return df.rename(columns=peta)


def ke_angka(seri):
    """Teks -> angka (koma desimal boleh). Hasil: (angka, kosong, bukan_angka)."""
    teks = seri.astype(str).str.strip().str.replace(" ", "", regex=False)
    kosong = seri.isna() | teks.isin(["", "nan", "None", "NaN", "-", "–"])
    nilai = pd.to_numeric(teks.str.replace(",", ".", regex=False).where(~kosong), errors="coerce")
    return nilai, kosong, ~kosong & nilai.isna()


def proses_banyak_data(df, model, info, tabel):
    """Validasi tiap baris, prediksi baris yang valid sekaligus, lalu hitung kategori, selisih, dan status."""
    kolom, rentang, ambang = info["kolom_prediktor"], info["rentang_prediktor"], info["ambang_status"]
    ada_ipm = "IPM" in df.columns
    hasil = df.copy()
    catatan = [[] for _ in range(len(df))]       # alasan baris tidak diprediksi
    peringatan = [[] for _ in range(len(df))]    # indikator di luar rentang data latih

    for k in kolom:
        nilai, kosong, bukan = ke_angka(df[k])
        hasil[k] = nilai
        for i in range(len(df)):
            if kosong.iloc[i]:
                catatan[i].append(f"{k} kosong")
            elif bukan.iloc[i]:
                catatan[i].append(f"{k} bukan angka")
            elif nilai.iloc[i] < 0 or (k in INDIKATOR_PERSEN and nilai.iloc[i] > 100):
                catatan[i].append(f"{k} tidak mungkin")
            elif not rentang[k]["min"] <= nilai.iloc[i] <= rentang[k]["max"]:
                peringatan[i].append(k)

    if ada_ipm:
        ipm, kosong, bukan = ke_angka(df["IPM"])
        for i in range(len(df)):
            if bukan.iloc[i] or (not kosong.iloc[i] and not 0 <= ipm.iloc[i] <= 100):
                catatan[i].append("IPM harus angka 0-100 atau dikosongkan")
        hasil["IPM"] = ipm.where((ipm >= 0) & (ipm <= 100))

    # Baris daerah data latih pada tahun penelitian tidak diprediksi (model sudah melihatnya),
    # sama seperti aturan di halaman Data tersedia
    latih = set(tabel.loc[tabel["Jenis data"] == "Latih", "Kabupaten/Kota"].str.strip().str.lower())
    tahun_data = set(tabel["Tahun"])
    if "Kabupaten/Kota" in df.columns and "Tahun" in df.columns:
        tahun_file, _, _ = ke_angka(df["Tahun"])
        for i in range(len(df)):
            nama = str(df["Kabupaten/Kota"].iloc[i]).strip().lower()
            if nama in latih and tahun_file.iloc[i] in tahun_data:
                catatan[i].append("daerah dan tahun ini termasuk data latih model (lihat halaman Data tersedia)")

    # Baris ganda: kabupaten/kota dan tahun yang sama muncul lebih dari sekali (tetap diprediksi, diberi tanda)
    ganda = pd.Series(False, index=df.index)
    if "Kabupaten/Kota" in df.columns and "Tahun" in df.columns:
        kunci = df["Kabupaten/Kota"].astype(str).str.strip().str.lower() + "|" + df["Tahun"].astype(str).str.strip()
        isi = df["Kabupaten/Kota"].notna() & df["Tahun"].notna()
        ganda = kunci.duplicated(keep=False) & isi
        for i in range(len(df)):
            if ganda.iloc[i]:
                lain = [str(j + 2) for j in range(len(df)) if j != i and ganda.iloc[j] and kunci.iloc[j] == kunci.iloc[i]]
                peringatan[i].append(f"baris ganda (sama dengan baris {', '.join(lain)} di file)")

    valid = pd.Series([not c for c in catatan], index=df.index)
    hasil["IPM prediksi"] = float("nan")
    if valid.any():
        hasil.loc[valid, "IPM prediksi"] = model.predict(hasil.loc[valid, kolom].astype(float))
    hasil["Kategori prediksi"] = hasil["IPM prediksi"].map(kategori_ipm)
    if ada_ipm:
        hasil["Kategori aktual"] = hasil["IPM"].map(kategori_ipm)
        hasil["Selisih"] = hasil["IPM"] - hasil["IPM prediksi"]
        hasil["Status"] = hasil["Selisih"].map(lambda v: None if pd.isna(v) else tentukan_status(v, ambang))

    # Jarak ke kategori BPS berikutnya: dari IPM aktual jika diisi, jika tidak dari IPM prediksi
    def teks_jarak(aktual, prediksi):
        dasar, sumber = (aktual, "aktual") if pd.notna(aktual) else (prediksi, "prediksi")
        j = jarak_kategori(dasar)
        if pd.isna(dasar):
            return None
        return "Sudah tertinggi" if j is None else f"+{angka(j[0])} ke {j[1]} ({sumber})"
    aktual = hasil["IPM"] if ada_ipm else pd.Series(float("nan"), index=hasil.index)
    hasil["Ke kategori berikutnya"] = [teks_jarak(a, p) if ok else None
                                       for a, p, ok in zip(aktual, hasil["IPM prediksi"], valid)]

    def teks_keterangan(c, p):
        if c:
            return "Tidak diprediksi: " + "; ".join(c)
        luar = [x for x in p if not x.startswith("baris ganda")]
        lain = [x for x in p if x.startswith("baris ganda")]
        bagian = (["Di luar rentang data latih: " + ", ".join(luar)] if luar else []) + lain
        return "; ".join(bagian) if bagian else "OK"
    hasil["Keterangan"] = [teks_keterangan(c, p) for c, p in zip(catatan, peringatan)]
    hasil = hasil.rename(columns={"IPM": "IPM aktual"})
    urutan = ([c for c in ["Kabupaten/Kota", "Provinsi", "Tahun"] if c in hasil.columns] + kolom
              + (["IPM aktual", "Kategori aktual"] if ada_ipm else []) + ["IPM prediksi", "Kategori prediksi"]
              + (["Selisih", "Status"] if ada_ipm else []) + ["Ke kategori berikutnya", "Keterangan"])
    di_luar = pd.Series([any(not x.startswith("baris ganda") for x in p) and not c
                         for c, p in zip(catatan, peringatan)], index=df.index)
    return hasil[urutan], valid, di_luar, ganda


def tampilkan_unggah_file(model, info, tabel):
    kolom = info["kolom_prediktor"]
    penjelasan(
        "1. Unduh **template Excel**. Kolomnya sama dengan dataset penelitian: Kabupaten/Kota, Provinsi, Tahun, "
        "PPM, TPAK, TPT, PDRB, KP, IPM. Sheet **Petunjuk** berisi arti dan satuan setiap kolom.\n"
        f"2. Isi satu baris untuk setiap daerah per tahun. Kolom wajib: **{', '.join(kolom)}**. "
        "Kolom **IPM** boleh dikosongkan; jika diisi, selisih dan status ikut dihitung.\n"
        "3. Angka desimal boleh memakai koma atau titik, tanpa pemisah ribuan (contoh PDRB: 32150).\n"
        f"4. Unggah file (.xlsx atau .csv, maksimal {angka(BATAS_BARIS, 0)} baris), lalu unduh hasilnya.\n\n"
        "Data yang diunggah **hanya diprediksi**: tidak disimpan dan tidak dipakai untuk melatih ulang model. "
        "Baris daerah **data latih** pada tahun 2017–2024 tidak diprediksi, karena model sudah melihat data tersebut.",
        judul="Cara memakai fitur unggah file", buka=True,
    )
    contoh, petunjuk = buat_template(tabel, info)
    st.download_button("Unduh template Excel", ke_excel({"Data": contoh, "Petunjuk": petunjuk}),
                       file_name="template_prediksi_ipm.xlsx", icon=":material/download:",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    berkas = st.file_uploader("Unggah file data (.xlsx atau .csv)", type=["xlsx", "csv"])
    if berkas is None:
        return
    try:
        df = seragamkan_kolom(baca_file(berkas), kolom)
    except Exception as galat:
        st.error(f"File tidak dapat dibaca: {galat}", icon=":material/error:")
        return
    df = df.dropna(how="all").reset_index(drop=True)
    hilang = [k for k in kolom if k not in df.columns]
    if hilang:
        st.error("Kolom wajib tidak ditemukan: " + ", ".join(hilang) + ". Gunakan template yang disediakan.",
                 icon=":material/error:")
        return
    if df.empty:
        st.error("File tidak berisi data.", icon=":material/error:")
        return
    if len(df) > BATAS_BARIS:
        st.error(f"Jumlah baris {angka(len(df), 0)} melebihi batas {angka(BATAS_BARIS, 0)}.", icon=":material/error:")
        return

    hasil, valid, di_luar, ganda = proses_banyak_data(df, model, info, tabel)

    # ---------- Ringkasan ----------
    st.subheader("Hasil")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Jumlah baris", angka(len(hasil), 0), border=True)
    m2.metric("Berhasil diprediksi", angka(int(valid.sum()), 0), border=True)
    m3.metric("Tidak diprediksi", angka(int((~valid).sum()), 0), border=True)
    m4.metric("Di luar rentang", angka(int(di_luar.sum()), 0), border=True)
    if (~valid).any():
        st.warning("Sebagian baris tidak diprediksi. Alasannya ada di kolom **Keterangan**.", icon=":material/info:")
    if di_luar.any():
        st.warning("Sebagian baris berada di luar rentang data latih, jadi hasilnya kurang dapat diandalkan.",
                   icon=":material/warning:")
    if ganda.any():
        st.warning(f"Ada {angka(int(ganda.sum()), 0)} baris ganda (kabupaten/kota dan tahun yang sama muncul lebih "
                   "dari sekali). Baris tetap diprediksi; periksa kolom **Keterangan**.", icon=":material/content_copy:")

    # ---------- Grafik ringkasan ----------
    ada_status = "Status" in hasil.columns and hasil["Status"].notna().any()
    g1, g2 = st.columns(2, gap="large")
    with g1:
        st.markdown("**Sebaran kategori BPS (IPM prediksi)**")
        kat = hasil["Kategori prediksi"].value_counts().reindex(URUTAN_KATEGORI, fill_value=0)
        warna_kat = [transparan(WARNA_KATEGORI_DASAR, a) for a in (0.35, 0.55, 0.75, 1.0)]
        fig = go.Figure(go.Bar(x=kat.index, y=kat.values, marker_color=warna_kat, text=kat.values,
                               textposition="outside", cliponaxis=False,
                               hovertemplate="%{x}: %{y} baris<extra></extra>"))
        fig.update_yaxes(title="Jumlah baris", rangemode="tozero", dtick=1 if kat.max() <= 10 else None)
        st.plotly_chart(rapikan(fig, tinggi=260, legenda=False), width="stretch", config={"displayModeBar": False})
    with g2:
        st.markdown("**Sebaran status (baris yang IPM-nya diisi)**")
        if ada_status:
            urut_status = [STATUS_ATAS, STATUS_SESUAI, STATUS_BAWAH]
            sts = hasil["Status"].value_counts().reindex(urut_status, fill_value=0)
            fig = go.Figure(go.Bar(x=sts.index, y=sts.values, marker_color=[WARNA_STATUS[s] for s in urut_status],
                                   text=sts.values, textposition="outside", cliponaxis=False,
                                   hovertemplate="%{x}: %{y} baris<extra></extra>"))
            fig.update_yaxes(title="Jumlah baris", rangemode="tozero", dtick=1 if sts.max() <= 10 else None)
            st.plotly_chart(rapikan(fig, tinggi=260, legenda=False), width="stretch", config={"displayModeBar": False})
        else:
            st.info("Isi kolom **IPM** di file untuk melihat selisih dan status.", icon=":material/info:")

    # ---------- Selisih terbesar ----------
    if ada_status:
        st.markdown("##### Selisih terbesar")
        kolom_top = [c for c in ["Kabupaten/Kota", "Tahun", "IPM aktual", "IPM prediksi", "Selisih"] if c in hasil.columns]
        def tabel_top(data):
            t = data[kolom_top].copy()
            for c in ["IPM aktual", "IPM prediksi"]:
                t[c] = t[c].map(angka)
            t["Selisih"] = t["Selisih"].map(lambda v: ("+" if v > 0 else "") + angka(v))
            if "Tahun" in t.columns:
                t["Tahun"] = t["Tahun"].map(lambda v: str(v).split(".")[0])
            return t.astype(str)
        dinilai = hasil[hasil["Selisih"].notna()]
        s1, s2 = st.columns(2, gap="large")
        with s1:
            st.markdown(f":green[**5 teratas di atas prediksi**] (selisih > +{angka(info['ambang_status'])})")
            atas = dinilai[dinilai["Status"] == STATUS_ATAS].nlargest(5, "Selisih")
            if atas.empty:
                st.caption("Tidak ada baris di atas prediksi.")
            else:
                st.dataframe(tabel_top(atas), hide_index=True, width="stretch")
        with s2:
            st.markdown(f":red[**5 teratas di bawah prediksi**] (selisih < −{angka(info['ambang_status'])})")
            bawah = dinilai[dinilai["Status"] == STATUS_BAWAH].nsmallest(5, "Selisih")
            if bawah.empty:
                st.caption("Tidak ada baris di bawah prediksi.")
            else:
                st.dataframe(tabel_top(bawah), hide_index=True, width="stretch")
        st.caption("Daerah dengan selisih besar adalah daerah yang IPM-nya paling berbeda dari daerah lain dengan "
                   "kondisi sosial-ekonomi mirip, sehingga layak dikaji lebih lanjut. Ini bukan penjelasan sebab-akibat.")

    st.markdown("##### Tabel lengkap")

    # ---------- Tabel hasil (angka gaya Indonesia, kosong ditulis "-") ----------
    tampil = hasil.copy()
    for c in kolom + ["IPM aktual", "IPM prediksi", "Selisih"]:
        if c in tampil.columns:
            tanda = c == "Selisih"
            tampil[c] = tampil[c].map(lambda v, t=tanda, d=(0 if c == "PDRB" else 2): "-" if pd.isna(v)
                                      else ("+" if t and v > 0 else "") + angka(float(v), d))
    if "Tahun" in tampil.columns:
        tampil["Tahun"] = tampil["Tahun"].map(lambda v: "-" if pd.isna(v) else str(v).split(".")[0])
    tampil = tampil.astype(object).where(tampil.notna(), "-").astype(str)
    st.dataframe(tampil, hide_index=True, width="stretch", height=420)
    st.caption(f"Status: selisih (IPM aktual − IPM prediksi) di luar ±{angka(info['ambang_status'])} berarti di atas/di "
               "bawah prediksi. Kategori mengikuti BPS: Rendah (< 60), Sedang (60 - < 70), Tinggi (70 - < 80), "
               "Sangat tinggi (≥ 80). **Ke kategori berikutnya** = tambahan poin IPM yang dibutuhkan untuk naik "
               "kategori, dihitung dari IPM aktual (jika diisi) atau IPM prediksi.")

    st.download_button("Unduh hasil (Excel)", ke_excel({"Hasil prediksi": hasil.round({"IPM prediksi": 2, "Selisih": 2})}),
                       file_name="hasil_prediksi_ipm.xlsx", icon=":material/download:", type="primary",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
