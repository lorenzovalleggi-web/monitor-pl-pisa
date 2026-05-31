import streamlit as st
import datetime, pytz, requests, os
from streamlit_autorefresh import st_autorefresh

# Configurazione Pagina
st.set_page_config(page_title="BinarioLibero Pisa", page_icon="🚦", layout="centered")

# --- CUSTOM CSS PER CAMBIARE SFONDO E STILE ---
st.markdown("""
    <style>
    /* Sfondo principale dell'app */
    .stApp {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #f8fafc;
    }
    
    /* Personalizzazione Titoli, Sottotitoli e Testi generici */
    h1, h2, h3, h4, p, span, div {
        color: #f8fafc !important;
    }
    
    /* Link ipertestuali tradizionali */
    a {
        color: #38bdf8 !important;
        text-decoration: underline;
    }
    
    /* Stile dei riquadri Info/Success/Error */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }

    /* Pulsante Aggiorna */
    .stButton>button {
        background-color: #334155 !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #475569 !important;
        width: 100%;
    }
    
    /* Box segnaposto per gli sponsor se manca l'immagine */
    .sponsor-box {
        background-color: #1e293b;
        border: 1px dashed #475569;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
        color: #94a3b8 !important;
        font-size: 14px;
    }
    
    /* Linea di separazione */
    hr {
        border-top: 1px solid #334155 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Autorefresh ogni 15 secondi
st_autorefresh(interval=15000, key="datarefresh")

st.title("⚡ BinarioLibero")
st.subheader("Meteo passaggi a livello: Pisa - San Giuliano")

if st.button("🔄 Aggiorna Stato In Tempo Reale"):
    st.rerun()

fuso = pytz.timezone('Europe/Rome')
ora_adesso = datetime.datetime.now(fuso)
st.write(f"Ultimo controllo: **{ora_adesso.strftime('%H:%M:%S')}**")
minuti_ora = ora_adesso.hour * 60 + ora_adesso.minute

ORARIO_TABELLA = [
    {"ora": 5, "min": 30, "dir": "LUCCA", "num": "18502"}, {"ora": 5, "min": 51, "dir": "PISA", "num": "18501"},
    {"ora": 6, "min": 23, "dir": "LUCCA", "num": "18504"}, {"ora": 6, "min": 35, "dir": "PISA", "num": "18503"},
    {"ora": 6, "min": 54, "dir": "LUCCA", "num": "18506"}, {"ora": 7, "min": 17, "dir": "PISA", "num": "6915"},
    {"ora": 7, "min": 30, "dir": "LUCCA", "num": "18508"}, {"ora": 7, "min": 47, "dir": "PISA", "num": "18505"},
    {"ora": 8, "min": 23, "dir": "LUCCA", "num": "18514"}, {"ora": 8, "min": 51, "dir": "PISA", "num": "18511"},
    {"ora": 9, "min": 23, "dir": "LUCCA", "num": "18516"}, {"ora": 9, "min": 51, "dir": "PISA", "num": "18515"},
    {"ora": 10, "min": 23, "dir": "LUCCA", "num": "18518"}, {"ora": 10, "min": 51, "dir": "PISA", "num": "18517"},
    {"ora": 11, "min": 23, "dir": "LUCCA", "num": "18520"}, {"ora": 11, "min": 51, "dir": "PISA", "num": "18519"},
    {"ora": 12, "min": 23, "dir": "LUCCA", "num": "18522"}, {"ora": 12, "min": 43, "dir": "PISA", "num": "18521"},
    {"ora": 13, "min": 13, "dir": "LUCCA", "num": "18524"}, {"ora": 13, "min": 36, "dir": "PISA", "num": "18523"},
    {"ora": 13, "min": 53, "dir": "LUCCA", "num": "18526"}, {"ora": 14, "min": 13, "dir": "PISA", "num": "18525"},
    {"ora": 14, "min": 35, "dir": "LUCCA", "num": "18528"}, {"ora": 14, "min": 43, "dir": "PISA", "num": "18527"},
    {"ora": 15, "min": 23, "dir": "LUCCA", "num": "18532"}, {"ora": 15, "min": 51, "dir": "PISA", "num": "18531"},
    {"ora": 16, "min": 23, "dir": "LUCCA", "num": "18534"}, {"ora": 16, "min": 51, "dir": "PISA", "num": "18533"},
    {"ora": 17, "min": 23, "dir": "LUCCA", "num": "18536"}, {"ora": 17, "min": 46, "dir": "PISA", "num": "18535"},
    {"ora": 18, "min": 23, "dir": "LUCCA", "num": "18540"}, {"ora": 18, "min": 51, "dir": "PISA", "num": "18537"},
    {"ora": 19, "min": 23, "dir": "LUCCA", "num": "18542"}, {"ora": 19, "min": 51, "dir": "PISA", "num": "18541"},
    {"ora": 20, "min": 23, "dir": "LUCCA", "num": "18544"}, {"ora": 20, "min": 46, "dir": "PISA", "num": "18543"},
    {"ora": 21, "min": 23, "dir": "LUCCA", "num": "18546"}, {"ora": 21, "min": 58, "dir": "PISA", "num": "18545"}
]

@st.cache_data(ttl=10)
def recupera_treni():
    treni = []
    dt_str = ora_adesso.strftime('%Y-%m-%dT00:00:00')
    for v_id, d_name, f_key in [("S06411", "PISA", "PISA"), ("S06501", "LUCCA", "LUCCA")]:
        try:
            res = requests.get(f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/{v_id}/{dt_str}", timeout=5).json()
            for t in res.get('tabellone', []):
                dest = t.get('destinazione', '').upper()
                if f_key in dest or ("LIVORNO" in dest and f_key == "PISA") or (("PISTOIA" in dest or "FIRENZE" in dest) and f_key == "LUCCA"):
                    h, m = map(int, t.get('orarioProgrammato', '').split(':'))
                    rit = t.get('ritardo', 0)
                    rit = 0 if rit in ["---", None] else int(rit)
                    treni.append({"ora_p": h, "min_p": m, "ritardo": rit, "direzione": d_name, "num": t.get('numeroTreno'), "fonte": "LIVE"})
        except: pass
    return treni

lista_treni = recupera_treni()
if not lista_treni:
    for tp in ORARIO_TABELLA:
        if (tp["ora"] * 60 + tp["min"]) > minuti_ora:
            lista_treni.append({"ora_p": tp["ora"], "min_p": tp["min"], "ritardo": 0, "direzione": tp["dir"], "num": tp["num"], "fonte": "TABELLA"})

ritardo_rilevato = any(t.get("fonte") == "LIVE" and t.get("ritardo", 0) >= 4 for t in lista_treni)
estensione = min(max(
