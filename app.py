import streamlit as st
import datetime, pytz, requests

st.set_page_config(page_title="BinarioLibero - Monitor PL", layout="centered")

# CSS Personalizzato: Design scuro, pulito e testi leggibili
st.markdown("""<style>
    .stApp { background-color: #0f172a !important; color: #ffffff !important; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp span, .stApp div, .stApp li { color: #ffffff !important; }
    .stAlert p { color: #ffffff !important; }
    .stButton>button, .stLinkButton>a { background-color: #1e293b !important; color: #ffffff !important; border: 1px solid #475569 !important; width: 100% !important; text-align: center !important; }
    .stSuccess, .stError { border-radius: 15px !important; }
</style>""", unsafe_allow_html=True)

# Auto-refresh ogni 30 secondi per un monitoraggio fluido
st.components.v1.html("""
    <script>
        setTimeout(function(){ window.parent.location.reload(); }, 30000);
    </script>
""", height=0, width=0)

# 1. TABELLA ORARIA AGGIORNATA (Cronologia Trenitalia verificata)
# Orari di PARTENZA da Pisa S. Rossore verso Lucca
ORARI_PISA = [
    (5,31), (7,10), (7,55), (8,55), (9,55),
    (5,25), (6,13), (7,4), (7,50), (8,50), (9,3), (9,22), (9,50), (10,20), 
    (12,20), (12,50), (13,20), (13,43), (14,20), (14,50), (15,20), (15,50), 
    (16,19), (16,50), (17,20), (17,50), (18,20), (18,50), (19,20), (19,50), 
    (20,50), (21,20), (21,50)
]

# Orari di PARTENZA da Lucca verso Pisa
ORARI_LUCCA = [
    (6,52), (7,8), (7,40), (7,53), (8,15), (9,10), (9,42), (10,12), (10,42), 
    (12,42), (13,12)
]

st.title("⚡ BinarioLibero Pisa")

# Gestione Orario Italiano
try:
    ora_adesso = datetime.datetime.now(pytz.timezone('Europe/Rome'))
except:
    ora_adesso = datetime.datetime.now()

min_ora = ora_adesso.hour * 60 + ora_adesso.minute
st.write(f"⏱️ Ora attuale: {ora_adesso.strftime('%H:%M:%S')} (Aggiornamento automatico 30s)")

# 2. MOTORE DI RECUPERO DATI LIVE
@st.cache_data(ttl=5)
def prendi_treni(min_attuale):
    treni = []
    try:
        dt = ora_adesso.strftime('%Y-%m-%dT00:00:00')
        # API ViaggiaTreno per Pisa (Partenze verso Lucca) e Lucca (Partenze verso Pisa)
        for v_id, d_name, f_key in [("S06411", "PISA", "PISA"), ("S06501", "LUCCA", "LUCCA")]:
            url = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/{v_id}/{dt}"
            res = requests.get(url, timeout=3).json().get('tabellone', [])
            for t in res:
                dest = t.get('destinazione', '').upper()
                if f_key in dest or "LIVORNO" in dest or "PISTOIA" in dest or "FIRENZE" in dest:
                    h, m = map(int, t.get('orarioProgrammato', '').split(':'))
                    rit = max(0, int(t.get('ritardo', 0) or 0))
                    treni.append({"ora_p": h, "min_p": m, "ritardo": rit, "direzione": d_name, "num": t.get('numeroTreno'), "live": True})
    except:
        pass
    
    # Fallback su orari programmati se il server Trenitalia è lento
    if not treni:
        for o, m in ORARI_PISA:
            if (o * 60 + m) > min_attuale:
                treni.append({"ora_p": o, "min_p": m, "ritardo": 0, "direzione": "LUCCA", "num": "PROG", "live": False})
        for o, m in ORARI_LUCCA:
            if (o * 60 + m) > min_attuale:
                treni.append({"ora_p": o, "min_p": m, "ritardo": 0, "direzione
