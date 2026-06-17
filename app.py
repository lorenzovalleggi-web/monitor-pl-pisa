import streamlit as st
import datetime, pytz, requests

st.set_page_config(page_title="BinarioLibero - Monitor PL", layout="centered")

# CSS Personalizzato
st.markdown("""<style>
    .stApp { background-color: #0f172a !important; color: #ffffff !important; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp span, .stApp div, .stApp li { color: #ffffff !important; }
    .stAlert p { color: #ffffff !important; }
    .stButton>button, .stLinkButton>a { background-color: #1e293b !important; color: #ffffff !important; border: 1px solid #475569 !important; width: 100% !important; text-align: center !important; }
    .stSuccess, .stError { border-radius: 15px !important; }
</style>""", unsafe_allow_html=True)

# Auto-refresh a 30 secondi
st.components.v1.html("""
    <script>
        setTimeout(function(){ window.parent.location.reload(); }, 30000);
    </script>
""", height=0, width=0)

# 1. TABELLA ORARIA AGGIORNATA
ORARI_PISA = [
    (5,31), (7,10), (7,55), (8,55), (9,55),
    (5,25), (6,13), (7,4), (7,50), (8,50), (9,3), (9,22), (9,50), (10,20), 
    (12,20), (12,50), (13,20), (13,43), (14,20), (14,50), (15,20), (15,50), 
    (16,19), (16,50), (17,20), (17,50), (18,20), (18,50), (19,20), (19,50), 
    (20,50), (21,20), (21,50)
]

ORARI_LUCCA = [
    (6,52), (7,8), (7,40), (7,53), (8,15), (9,10), (9,42), (10,12), (10,42), 
    (12,42), (13,12)
]

st.title("⚡ BinarioLibero Pisa")

try:
    ora_adesso = datetime.datetime.now(pytz.timezone('Europe/Rome'))
except:
    ora_adesso = datetime.datetime.now()

min_ora = ora_adesso.hour * 60 + ora_adesso.minute
st.write(f"⏱️ Ora attuale: {ora_adesso.strftime('%H:%M:%S')} (Aggiornamento automatico 30s)")

# 2. MOTORE DI RECUPERO DATI LIVE (STRUTTURA LINEARE ANTI-TRONCAMENTO)
@st.cache_data(ttl=5)
def prendi_treni(min_attuale):
    treni = []
    str_pisa = "PISA"
    str_lucca = "LUCCA"
    str_liv = "LIVORNO"
    str_pist = "PISTOIA"
    str_fir = "FIRENZE"
    dt = ora_adesso.strftime('%Y-%m-%dT00:00:00')
    
    # Blocco Pisa dedicato
    try:
        url_p = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/S06411/{dt}"
        res_p = requests.get(url_p, timeout=3).json().get('tabellone', [])
        for t in res_p:
            dest = t.get('destinazione', '').upper()
            if str_pisa in dest or str_liv in dest or str_pist in dest or str_fir in dest:
                h, m = map(int, t.get('orarioProgrammato', '').split(':'))
                rit = max(0, int(t.get
