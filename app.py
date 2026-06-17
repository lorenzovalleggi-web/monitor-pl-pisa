import streamlit as st
import datetime
import pytz
import requests

st.set_page_config(
    page_title="BinarioLibero",
    layout="centered"
)

# CSS Personalizzato
st.markdown("""<style>
    .stApp { background-color: #0f172a !important; color: #ffffff !important; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp span, .stApp div, .stApp li { color: #ffffff !important; }
    .stAlert p { color: #ffffff !important; }
    .stButton>button, .stLinkButton>a { background-color: #1e293b !important; color: #ffffff !important; border: 1px solid #475569 !important; width: 100% !important; text-align: center !important; }
    .stSuccess, .stError { border-radius: 15px !important; }
</style>""", unsafe_allow_html=True)

# Auto-refresh 30s
st.components.v1.html("""
    <script>
        setTimeout(function(){ window.parent.location.reload(); }, 30000);
    </script>
""", height=0, width=0)

# 1. TABELLA ORARIA
ORARI_PISA = [
    (5,31), (7,10), (7,55),
    (8,55), (9,55), (5,25),
    (6,13), (7,4), (7,50),
    (8,50), (9,3), (9,22),
    (9,50), (10,20), (12,20),
    (12,50), (13,20), (13,43),
    (14,20), (14,50), (15,20),
    (15,50), (16,19), (16,50),
    (17,20), (17,50), (18,20),
    (18,50), (19,20), (19,50),
    (20,50), (21,20), (21,50)
]

ORARI_LUCCA = [
    (6,52), (7,8), (7,40),
    (7,53), (8,15), (9,10),
    (9,42), (10,12), (10,42),
    (12,42), (13,12)
]

st.title("⚡ BinarioLibero Pisa")

try:
    tz_it = pytz.timezone(
        'Europe/Rome'
    )
    ora_adesso = (
        datetime.datetime.now(
            tz_it
        )
    )
except:
    ora_adesso = (
        datetime.datetime.now()
    )

h_or = ora_adesso.hour
m_or = ora_adesso.minute
min_ora = h_or * 60 + m_or

txt_ora = (
    ora_adesso.strftime(
        '%H:%M:%S'
    )
)
st.write(
    f"⏱️ Ora attuale: {txt_ora}"
)

# 2. CHIAMATE API
treni = []
str_pisa = "PISA"
str_lucca = "LUCCA"
str_liv = "LIVORNO"
str_pist = "PISTOIA"
str_fir = "FIRENZE"

dt = (
    ora_adesso.strftime(
        '%Y-%m-%dT00:00:00'
    )
)

# Fetch Pisa
try:
    base_p = (
        "http://www.viaggiat"
        "reno.it/viaggiatren"
        "onew/api/esitoPart"
        "enze/S06411/"
    )
    url_p = base_p + dt
    res_p = (
        requests.get(
            url_p,
            timeout=3
        ).json().get(
            'tabellone',
            []
        )
    )
    for t in
