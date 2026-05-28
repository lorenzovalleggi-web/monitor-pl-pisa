import streamlit as st
import datetime
import pytz
import requests
from streamlit_autorefresh import st_autorefresh

# Configurazione della pagina minimale
st.set_page_config(page_title="Pisa ⇄ Lucca Live", page_icon="🚦", layout="centered")

# Aggiornamento automatico ogni 15 secondi
st_autorefresh(interval=15000, key="datarefresh")

fuso_italia = pytz.timezone('Europe/Rome')
ora_adesso = datetime.datetime.now(fuso_italia)

# --- HEADER MODERNO ED ELEGANTE ---
col_titolo, col_sync = st.columns([3, 1])
with col_titolo:
    st.markdown("<h2 style='margin:0; font-weight:800; letter-spacing:-1px;'>PISA ⇄ LUCCA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='margin:0; color:#888888; font-size:14px; font-weight:500;'>Rilevamento Barriere Ferrovia</p>", unsafe_allow_html=True)

with col_sync:
    st.markdown(f"<p style='text-align:right; margin:0; color:#888888; font-size:12px;'>Sync Live<br><b style='font-size:14px; color:#ffffff;'>{ora_adesso.strftime('%H:%M:%S')}</b></p>", unsafe_allow_html=True)
    if st.button("🔄 Ricarica", use_container_width=True):
        st.rerun()

st.markdown("---")

minuti_assoluti_ora = ora_adesso.hour * 60 + ora_adesso.minute

# ID Stazioni ufficiali ViaggiaTreno
ID_SAN_GIULIANO = "S06411"
ID_PISA_ROSSORE = "S06501"

@st.cache_data(ttl=10)
def recupera_treni_reali():
    treni_attivi = []
    # 1. Controlla partenze da San Giuliano (Verso Pisa)
    try:
        url_sg = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/{ID_SAN_GIULIANO}/{ora_adesso.strftime('%Y-%m-%dT00:00:00')}"
        res = requests.get(url_sg, timeout=5).json()
        for t in res.get('tabellone', []):
            dest = t.get('destinazione', '').upper()
            if "PISA" in dest or "LIVORNO" in dest:
                orario_prog = t.get('orarioProgrammato', '')
                if orario_prog:
                    h, m = map(int, orario_prog.split(':'))
                    ritardo = t.get('ritardo', 0)
                    if ritardo == "---" or ritardo is None: ritardo = 0
                    treni_attivi.append({
                        "ora_p": h, "min_p": m, "ritardo": int(ritardo), "direzione": "PISA",
                        "info": f"➔ **REG {t.get('numeroTreno')}** per {t.get('destinazione')}"
                    })
    except: pass

    # 2. Controlla partenze da Pisa S. Rossore (Verso Lucca)
    try:
        url_pr = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/{ID_PISA_ROSSORE}/{ora_adesso.strftime('%Y-%m-%dT00:00:00')}"
        res = requests.get(url_pr, timeout=5).json()
        for t in res.get('tabellone', []):
            dest = t.get('destinazione', '').upper()
            if "LUCCA" in dest or "PISTOIA" in dest or "FIRENZE" in dest:
                orario_prog = t.get('orarioProgrammato', '')
                if orario_prog:
                    h, m = map(int, orario_prog.split(':'))
                    ritardo = t.get('ritardo', 0)
                    if ritardo == "---" or ritardo is None: ritardo = 0
                    treni_attivi.append({
                        "ora_p": h, "min_p": m, "ritardo": int(ritardo), "direzione": "LUCCA",
                        "info": f"🡨 **REG {t.get('numeroTreno')}** per {t.get('destinazione')}"
                    })
    except: pass
    return treni_attivi

lista_treni_fs = recupera_treni_reali()

# --- DETECTOR ANOMALIE LINEA ---
ritardo_rilevato_linea = False
minuti_estensione_blocco = 0
if lista_treni_fs:
    for t in lista_treni_fs:
        if t["ritardo"] >= 4:
            ritardo_rilevato_linea = True
            minuti_estensione_blocco = min(t["ritardo"], 12)

# --- TROVA PROSSIMO TRENO ---
prossimo_treno_testo = ""
treni_futuri = []
if lista_treni_fs:
    for t in lista_treni_fs:
        min_ass_treno = t["ora_p"] * 60 + t["min_p"] + t["ritardo"]
        if min_ass_treno > minuti_assoluti_ora:
            treni_futuri.append((min_ass_treno, t))

if treni_futuri:
    _, prox = min(treni_futuri, key=lambda x: x[0])
    min_totale = prox["ora_p"] * 60 + prox["min_p"] + prox["ritardo"]
    ora_effettiva = min_totale // 60
    min_effettiva = min_totale % 60
    stringa_ora = f"{ora_effettiva:02d}:{min_effettiva:02d}"
    nota_ritardo = f" (+{prox['ritardo']} min ritardo)" if prox['ritardo'] > 0 else " (In orario)"
    prossimo_treno_testo = f"Prossimo transito reale: {prox['info']} alle **{stringa_ora}**{nota_ritardo}"
else:
    if ora_adesso.hour >= 22 or ora_adesso.hour < 5:
        prossimo_treno_testo = "Servizio giornaliero terminato. 🌅 Primo del mattino: REG delle 05:30 per Lucca / 05:51 per Pisa."
    else:
        prossimo_treno_testo = "Nessun transito imminente rilevato dai sistemi di stazione."

st.info(f"📋 **STATO LINEA:** {prossimo_treno_testo}")
st.caption("ℹ️ **Nota traffico merci:** Servizio passeggeri monitorato in tempo reale. I treni merci non sono programmati e possono causare chiusure estemporanee fuori tabellone.")

if ritardo_rilevato_linea:
    st.warning("⚠️ **RALLENTAMENTO DINAMICO RILEVATO:** Tratta congestionata. Le barriere potrebbero rimanere abbassate più a lungo del previsto.")

st.write("### 🚊 STATO DEI PASSAGGI A LIVELLO")

pl_lista = [
    {"nome": "San Giuliano Terme", "ind_pisa": 0, "ind_lucca": 4},
    {"nome": "Via Ulisse Dini (Gello)", "ind_pisa": 2, "ind_lucca": 3},
    {"nome": "Via di Gagno (Pisa)", "ind_pisa": 5, "ind_lucca": 2},
    {"nome": "Via Ugo Rindi (Pisa)", "ind_pisa": 7, "ind_lucca": 0}
]

# --- RENDERING DELLA DASHBOARD A CONTAINER ---
for i, pl in enumerate(pl_lista):
    if i > 0:
        st.markdown("<div style='text-align: center; color: #555555; margin: -5px 0 5px 0; font-size: 14px;'>⋮</div>", unsafe_allow_html=True)
    
    stato_chiuso = False
    info_segnaletica = "Strada libera da treni passeggeri"
    
    if lista_treni_fs:
        for treno in lista_treni_fs:
            min_partenza_reale = treno["ora_p"] * 60 + treno["min_p"] + treno["ritardo"]
            durata_viaggio = 10 if (treno["ora_p"] == 21 and treno["min_p"] == 58) else 6
            
            if treno["direzione"] == "PISA":
                inizio_chiusura = min_partenza_reale - 6 + pl
