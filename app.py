import streamlit as st
import datetime
import pytz
import requests

st.set_page_config(page_title="BinarioLibero", layout="centered")

# CSS in una riga singola per evitare tagli
st.markdown("<style>.stApp { background-color: #0f172a !important; color: #ffffff !important; } * { color: #ffffff !important; }</style>", unsafe_allow_html=True)

# Auto-refresh 30s
st.components.v1.html("<script>setTimeout(function(){ window.parent.location.reload(); }, 30000);</script>", height=0, width=0)

# Tabelle Orarie flat
P_H = [5, 7, 7, 8, 9, 5, 6, 7, 7, 8, 9, 9, 9, 10, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18, 19, 19, 20, 21, 21]
P_M = [31, 10, 55, 55, 55, 25, 13, 4, 50, 50, 3, 22, 50, 20, 20, 50, 20, 43, 20, 50, 20, 50, 19, 50, 20, 50, 20, 50, 20, 50, 50, 20, 50]
L_H = [6, 7, 7, 7, 8, 9, 9, 10, 10, 12, 13]
L_M = [52, 8, 40, 53, 15, 10, 42, 12, 42, 42, 12]

st.title("⚡ BinarioLibero Pisa")

try:
    tz = pytz.timezone('Europe/Rome')
    ora = datetime.datetime.now(tz)
except:
    ora = datetime.datetime.now()

min_ora = ora.hour * 60 + ora.minute
st.write(f"⏱️ Ora attuale: {ora.strftime('%H:%M:%S')}")

# Liste piatte parallele (Niente dizionari!)
tr_min = []
tr_dir = []
tr_num = []

# Live Pisa
try:
    dt = ora.strftime('%Y-%m-%dT00:00:00')
    url_p = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/S06411/{dt}"
    res_p = requests.get(url_p, timeout=2).json().get('tabellone', [])
    for t in res_p:
        prog = t.get('orarioProgrammato', '')
        if prog and ':' in prog:
            sp = prog.split(':')
            m_calc = int(sp[0]) * 60 + int(sp[1]) + max(0, int(t.get('ritardo', 0) or 0))
            tr_min.append(m_calc)
            tr_dir.append("PISA")
            tr_num.append(str(t.get('numeroTreno', 'REG')))
except:
    pass

# Live Lucca
try:
    url_l = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/S06501/{dt}"
    res_l = requests.get(url_l, timeout=2).json().get('tab
