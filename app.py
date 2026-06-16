import streamlit as st
import datetime, pytz, requests, os
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="BinarioLibero", layout="centered")

try:
    st_autorefresh(interval=15000, key="datarefresh")
except:
    pass

st.markdown("""
    <style>
    .stApp { background: #0f172a; color: #f8fafc; }
    h1, h2, h3, h4, p, span, div { color: #f8fafc !important; }
    .stAlert { border-radius: 8px !important; }
    .sponsor-box { background: #1e293b; border: 1px dashed #475569; padding: 10px; text-align: center; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ BinarioLibero")
st.subheader("Pisa - San Giuliano")

if st.button("🔄 Aggiorna"):
    st.rerun()

try:
    fuso = pytz.timezone('Europe/Rome')
    ora_adesso = datetime.datetime.now(fuso)
except:
    ora_adesso = datetime.datetime.now()

st.write(f"Orario: {ora_adesso.strftime('%H:%M:%S')}")
minuti_ora = ora_adesso.hour * 60 + ora_adesso.minute

ORARIO_TABELLA = [
    {"ora": 5, "min": 30, "dir": "LUCCA", "num": "18502"},
    {"ora": 5, "min": 51, "dir": "PISA", "num": "18501"},
    {"ora": 6, "min": 23, "dir": "LUCCA", "num": "18504"},
    {"ora": 6, "min": 35, "dir": "PISA", "num": "18503"},
    {"ora": 6, "min": 54, "dir": "LUCCA", "num": "18506"},
    {"ora": 7, "min": 17, "dir": "PISA", "num": "6915"},
    {"ora": 7, "min": 30, "dir": "LUCCA", "num": "18508"},
    {"ora": 7, "min": 47, "dir": "PISA", "num": "18505"},
    {"ora": 8, "min": 23, "dir": "LUCCA", "num": "18514"},
    {"ora": 8, "min": 51, "dir": "PISA", "num": "18511"},
    {"ora": 9, "min": 23, "dir": "LUCCA", "num": "18516"},
    {"ora": 9, "min": 51, "dir": "PISA", "num": "18515"},
    {"ora": 10, "min": 23, "dir": "LUCCA", "num": "18518"},
    {"ora": 10, "min": 51, "dir": "PISA", "num": "18517"},
    {"ora": 11, "min": 23, "dir": "LUCCA", "num": "18520"},
    {"ora": 11, "min": 51, "dir": "PISA", "num": "18519"},
    {"ora": 12, "min": 23, "dir": "LUCCA", "num": "18522"},
    {"ora": 12, "min": 43, "dir": "PISA", "num": "18521"},
    {"ora": 13, "min": 13, "dir": "LUCCA", "num": "18524"},
    {"ora": 13, "min": 36, "dir": "PISA", "num": "18523"},
    {"ora": 13, "min": 53, "dir": "LUCCA", "num": "18526"},
    {"ora": 14, "min": 13, "dir": "PISA", "num": "18525"},
    {"ora": 14, "min": 35, "dir": "LUCCA", "num": "18528"},
    {"ora": 14, "min": 43, "dir": "PISA", "num": "18527"},
    {"ora": 15, "min": 23, "dir": "LUCCA", "num": "18532"},
    {"ora": 15, "min": 51, "dir": "PISA", "num": "18531"},
    {"ora": 16, "min": 23, "dir": "LUCCA", "num": "18534"},
    {"ora": 16, "min": 51, "dir": "PISA", "num": "18533"},
    {"ora": 17, "min": 23, "dir": "LUCCA", "num": "18536"},
    {"ora": 17, "min": 46, "dir": "PISA", "num": "18535"},
    {"ora": 18, "min": 23, "dir": "LUCCA", "num": "18540"},
    {"ora": 18, "min": 51, "dir": "PISA", "num": "18537"},
    {"ora": 19, "min": 23, "dir": "LUCCA", "num": "18542"},
    {"ora": 19, "min": 51, "dir": "PISA", "num": "18541"},
    {"ora": 20, "min": 23, "dir": "LUCCA", "num": "18544"},
    {"ora": 20, "min": 46, "dir": "PISA", "num": "18543"},
    {"ora": 21, "min": 23, "dir": "LUCCA", "num": "18546"},
    {"ora": 21, "min": 58, "dir": "PISA", "num": "18545"}
]

@st.cache_data(ttl=10)
def recupera_treni():
    treni = []
    try:
        dt = ora_adesso.strftime('%Y-%m-%dT00:00:00')
        stazioni = [("S06411", "PISA", "PISA"), ("S06501", "LUCCA", "LUCCA")]
        for v_id, d_name, f_key in stazioni:
            try:
                url = f
