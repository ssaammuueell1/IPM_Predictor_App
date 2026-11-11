import streamlit as st

from utils import muat_info
from tampilan import pasang_gaya

st.set_page_config(page_title="Prediksi IPM Wilayah Kemiskinan Tinggi", page_icon="", layout="wide")
pasang_gaya()

# ---------- Navigasi antarhalaman (menu di bagian atas) ----------
navigasi = st.navigation([
    st.Page("halaman/Landing_Page.py", title="Beranda", icon=":material/home:", default=True),
    st.Page("halaman/Prediksi_IPM.py", title="Prediksi IPM", icon=":material/insights:"),
    st.Page("halaman/Evaluasi_Model.py", title="Evaluasi Model", icon=":material/analytics:"),
    st.Page("halaman/Daftar_wilayah.py", title="Daftar Wilayah", icon=":material/table_view:"),
], position="top")

navigasi.run()

#  Keterangan di bagian bawah setiap halaman 
_info = muat_info()
st.divider()
st.caption(
    f"Model: XGBoost Regression dengan tuning. "
    f"Data: {_info['jumlah']['daerah']} kab/kota, {_info['jumlah']['tahun_awal']}–{_info['jumlah']['tahun_akhir']}"
)
