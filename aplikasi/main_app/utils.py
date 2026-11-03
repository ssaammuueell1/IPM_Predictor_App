from pathlib import Path
import json

import pandas as pd
import streamlit as st
from xgboost import XGBRegressor

# Lokasi folder, dihitung dari letak file utils.py ini
FOLDER_APP = Path(__file__).parent
FOLDER_DATA = FOLDER_APP / "data"
FOLDER_MODEL = FOLDER_APP / "model"

# Nama status (harus sama persis dengan isi kolom Status di tabel_prediksi.csv)
STATUS_ATAS = "Di atas prediksi"
STATUS_SESUAI = "Sesuai prediksi"
STATUS_BAWAH = "Di bawah prediksi"
URUTAN_STATUS = [STATUS_ATAS, STATUS_SESUAI, STATUS_BAWAH]
WARNA_STATUS = {STATUS_ATAS: "#0F766E", STATUS_SESUAI: "#214A9E", STATUS_BAWAH: "#C0392B"}

@st.cache_data
def muat_tabel():
    """Tabel 920 baris: IPM aktual, jenis data (latih/uji), 5 prediktor, dan IPM prediksi/selisih/status.

    IPM prediksi, selisih, dan status HANYA untuk data uji (184 baris), yaitu tebakan model utama pada daerah
    yang tidak pernah dipakai untuk melatihnya. Data latih (736 baris) dipakai model untuk belajar, sehingga
    prediksinya dikosongkan dan hanya IPM aktualnya yang ditampilkan.
    """
    tabel = pd.read_csv(FOLDER_DATA / "tabel_prediksi.csv")
    latih = tabel["Jenis data"] == "Latih"
    tabel.loc[latih, ["IPM_prediksi", "Selisih"]] = float("nan")
    tabel["Status"] = tabel["Status"].where(~latih, None)
    return tabel


@st.cache_data
def muat_info():
    """Info model: jumlah data, parameter, metrik, ambang, rentang prediktor, kontribusi fitur."""
    with open(FOLDER_MODEL / "info_model.json", encoding="utf-8") as f:
        return json.load(f)


@st.cache_resource
def muat_model(nama="tuning"):
    """Model yang dilatih di data latih. nama = 'tuning' (dipakai aplikasi) atau 'awal' (pembanding)."""
    model = XGBRegressor()
    model.load_model(str(FOLDER_MODEL / f"model_{nama}.json"))
    return model
    # Alternatif format joblib (butuh joblib + scikit-learn di requirements.txt):
    # import joblib
    # return joblib.load(FOLDER_MODEL / f"model_{nama}.joblib")


def angka(x, desimal=2):
    """Format angka gaya Indonesia: 1234.5 -> '1.234,50'."""
    teks = f"{x:,.{desimal}f}"
    return teks.replace(",", "#").replace(".", ",").replace("#", ".")


# Nama lengkap dan satuan setiap prediktor (dipakai halaman Prediksi Data Tersedia dan Data Baru)
LABEL_PREDIKTOR = {
    "PPM": "Persentase penduduk miskin (%)",
    "TPAK": "Tingkat partisipasi angkatan kerja (%)",
    "TPT": "Tingkat pengangguran terbuka (%)",
    "PDRB": "PDRB per kapita ADHB (ribu Rp)",
    "KP": "Kepadatan penduduk (jiwa/km²)",
}