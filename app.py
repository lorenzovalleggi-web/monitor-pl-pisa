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

# 1. TABELLA ORARIA COMPLETA
ORARI_PISA = [
    (5,31), (7,10), (7,55), (8,55), (9,55), (5,25),
    (6,13), (7,4), (7,50), (8,50), (9,3), (9,22),
    (9,50), (10,20), (12,20), (12,50), (13,20), (13,43),
    (14,20), (14,50), (15,20), (15,50), (16,19), (16,50),
    (17,20), (17,50), (18,20), (18,50), (19,20), (19,50),
    (20,50), (21,20), (21,50)
]

ORARI_LUCCA = [
    (6,52), (7,8), (7,40), (7,53), (8,15), (9,10),
    (9,42), (10,12), (10,42), (12,42), (13,12)
]

st.title("⚡ BinarioLibero Pisa")

try:
    tz_it = pytz.timezone('Europe/Rome')
    ora_adesso = datetime.datetime.now(tz_it)
except:
    ora_adesso = datetime.datetime.now()

h_or = ora_adesso.hour
m_or = ora_adesso.minute
min_ora = h_or * 60 + m_or

txt_ora = ora_adesso.strftime('%H:%M:%S')
st.write(f"⏱️ Ora attuale: {txt_ora} (Aggiornamento auto 30s)")

treni = []
str_pisa = "PISA"
str_lucca = "LUCCA"

# Prova a prendere i dati live
try:
    dt = ora_adesso.strftime('%Y-%m-%dT00:00:00')
    url_p = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/S06411/{dt}"
    res_p = requests.get(url_p, timeout=2).json().get('tabellone', [])
    for t in res_p:
        prog = t.get('orarioProgrammato', '')
        if prog and ':' in prog:
            h_p, m_p = map(int, prog.split(':'))
            r_p = t.get('ritardo', 0)
            rit = max(0, int(r_p if r_p else 0))
            treni.append({
                "ora_p": h_p, "min_p": m_p, "ritardo": rit,
                "direzione": str_pisa, "num": t.get('numeroTreno', 'REG'), "live": True
            })
except:
    pass

try:
    url_l = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/S06501/{dt}"
    res_l = requests.get(url_l, timeout=2).json().get('tabellone', [])
    for t in res_l:
        prog = t.get('orarioProgrammato', '')
        if prog and ':' in prog:
            h_p, m_p = map(int, prog.split(':'))
            r_p = t.get('ritardo', 0)
            rit = max(0, int(r_p if r_p else 0))
            treni.append({
                "ora_p": h_p, "min_p": m_p, "ritardo": rit,
                "direzione": str_lucca, "num": t.get('numeroTreno', 'REG'), "live": True
            })
except:
    pass

# SE I DATI LIVE MANCANO, CARICA GLI ORARI PROGRAMMATI (CORRETTO INDENTAZIONE)
if not treni:
    for o, m in ORARI_PISA:
        if (o * 60 + m) > min_ora:
            treni.append({
                "ora_p": o, "min_p": m, "ritardo": 0,
                "direzione": str_lucca, "num": "PROG", "live": False
            })
    for o, m in ORARI_LUCCA:
        if (o * 60 + m) > min_ora:
            treni.append({
                "ora_p": o, "min_p": m, "ritardo": 0,
                "direzione": str_pisa, "num": "PROG", "live": False
            })

# Calcolo del ritardo massimo per l'estensione
est = 0
r_lista = [t["ritardo"] for t in treni if t["live"]]
if r_lista and max(r_lista) >= 4:
    est = min(max(r_lista), 12)

# Filtro dei treni attivi nei prossimi 25 minuti
treni_futuri = []
for t in treni:
    m_tr = (t["ora_p"] * 60) + t["min_p"] + t["ritardo"]
    if (m_tr + 25) > min_ora:
        treni_futuri.append((m_tr, t))

# Box informativo del prossimo treno
if treni_futuri:
    p_el = min(treni_futuri, key=lambda x: x[0])
    prox = p_el[1]
    m_
