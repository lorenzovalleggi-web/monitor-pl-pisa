import streamlit as st
import datetime
import pytz
import requests
from streamlit_autorefresh import st_autorefresh

# Configurazione della pagina
st.set_page_config(page_title="Monitor PL Pisa Live", page_icon="🚦", layout="centered")

# INTERFACCIA MINIMALISTA STILE TESLA / CARPLAY
st.markdown("""
    <style>
    /* Sfondo scuro opaco moderno */
    .stApp { background-color: #1A1C20; color: #E2E8F0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    
    /* Titoli minimali */
    h1 { color: #FFFFFF !important; font-size: 26px !important; text-align: center; font-weight: 700; margin-bottom: 2px; }
    p.subtitle { text-align: center; color: #94A3B8; font-size: 14px; margin-bottom: 20px; }
    
    /* Box info superiore */
    .stAlert { background-color: #262930 !important; border: none !important; border-radius: 12px !important; }
    
    /* Card passaggi a livello stile CarPlay */
    .pl-card {
        display: flex;
        align-items: center;
        background-color: #262930;
        padding: 16px 20px;
        border-radius: 14px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Icona di stato tonda */
    .status-dot {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        margin-right: 18px;
        flex-shrink: 0;
    }
    .dot-aperto { background-color: rgba(16, 185, 129, 0.15); border: 2px solid #10B981; }
    .dot-preallarme { background-color: rgba(245, 158, 11, 0.15); border: 2px solid #F59E0B; }
    .dot-chiuso { background-color: rgba(239, 68, 68, 0.15); border: 2px solid #EF4444; }
    
    /* Testi interni alle card */
    .pl-details { flex-grow: 1; }
    .pl-name { font-size: 16px; font-weight: 600; color: #FFFFFF; margin: 0; }
    .pl-info { font-size: 13px; color: #94A3B8; margin-top: 2px; }
    
    /* Timer sul lato destro */
    .pl-timer {
        font-size: 16px;
        font-weight: 700;
        text-align: right;
        white-space: nowrap;
    }
    .timer-chiuso { color: #EF4444; }
    .timer-preallarme { color: #F59E0B; }
    .timer-aperto { color: #10B981; }
    
    /* Separatore freccia */
    .road-arrow { text-align: center; color: #475569; font-size: 14px; margin: -4px 0 8px 0; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🚦 MONITOR TRAFFICO LIVE</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>San Giuliano Terme ↔ Pisa S. Rossore</p>", unsafe_allow_html=True)

# Aggiornamento automatico ogni 5 secondi per un countdown fluido
st_autorefresh(interval=5000, key="carplay_refresh")

fuso_italia = pytz.timezone('Europe/Rome')
ora_adesso = datetime.datetime.now(fuso_italia)

secondi_attuali_assoluti = (ora_adesso.hour * 3600) + (ora_adesso.minute * 60) + ora_adesso.second

ID_SAN_GIULIANO = "S06411"
ID_PISA_ROSSORE = "S06501"

@st.cache_data(ttl=8)
def recupera_treni_reali():
    treni_attivi = []
    # 1. Verso Pisa (Partenze da San Giuliano)
    try:
        url_sg = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/{ID_SAN_GIULIANO}/{ora_adesso.strftime('%Y-%m-%dT00:00:00')}"
        res = requests.get(url_sg, timeout=3).json()
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
                        "info": f"Treno {t.get('numeroTreno')} per {t.get('destinazione')}"
                    })
    except: pass

    # 2. Verso Lucca (Partenze da Pisa S. Rossore)
    try:
        url_pr = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/{ID_PISA_ROSSORE}/{ora_adesso.strftime('%Y-%m-%dT00:00:00')}"
        res = requests.get(url_pr, timeout=3).json()
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
                        "info": f"Treno {t.get('numeroTreno')} per {t.get('destinazione')}"
                    })
    except: pass
    return treni_attivi

lista_treni_fs = recupera_treni_reali()

# --- DETERMINA MESSAGGIO DI LINEA ---
prossimo_treno_testo = ""
treni_futuri = []
for t in lista_treni_fs:
    sec_reali_treno = (t["ora_p"] * 3600) + (t["min_p"] * 60) + (t["ritardo"] * 60)
    if sec_reali_treno > secondi_attuali_assoluti:
        treni_futuri.append((sec_reali_treno, t))

if treni_futuri:
    _, prox = min(treni_futuri, key=lambda x: x[0])
    min_totale = prox["ora_p"] * 60 + prox["min_p"] + prox["ritardo"]
    ora_effettiva = min_totale // 60
    min_effettiva = min_totale % 60
    nota_ritardo = f" (+{prox['ritardo']} min)" if prox['ritardo'] > 0 else ""
    prossimo_treno_testo = f"Prossimo arrivo: {prox['info']} alle **{ora_effettiva:02d}:{min_effettiva:02d}**{nota_ritardo}"
else:
    if ora_adesso.hour >= 22:
        prossimo_treno_testo = "Servizio concluso. Primi passaggi dalle ore 05:30."
    else:
        prossimo_treno_testo = "Linea regolare. Nessun treno imminente rilevato."

st.info(f"ℹ️ {prossimo_treno_testo}")
st.write("")

# ELENCO PASSAGGI A LIVELLO
pl_lista = [
    {"nome": "San Giuliano Terme", "ind_pisa": 0, "ind_lucca": 4},
    {"nome": "Via Ulisse Dini (Gello)", "ind_pisa": 2, "ind_lucca": 3},
    {"nome": "Via di Gagno (Pisa)", "ind_pisa": 5, "ind_lucca": 2},
    {"nome": "Via Ugo Rindi (Pisa)", "ind_pisa": 7, "ind_lucca": 0}
]

for idx, pl in enumerate(pl_lista):
    if idx > 0:
        st.markdown('<div class="road-arrow">│</div>', unsafe_allow_html=True)
        
    stato = "APERTO"
    info_segnaletica = "Strada libera"
    secondi_rimanenti = 0
    
    for treno in lista_treni_fs:
        sec_partenza_reale = (treno["ora_p"] * 3600) + (treno["min_p"] * 60) + (treno["ritardo"] * 60)
        durata_occupazione = 600 if (treno["ora_p"] == 21 and treno["min_p"] == 58) else 360
        
        if treno["direzione"] == "PISA":
            sec_inizio_chiusura = sec_partenza_reale - 360 + (pl["ind_pisa"] * 60)
            sec_fine_chiusura = sec_partenza_reale + durata_occupazione + 60
        else:
            sec_inizio_chiusura = sec_partenza_reale - 360 + (pl["ind_lucca"] * 60)
            sec_fine_chiusura = sec_partenza_reale + 300 + 120
            
        sec_preavviso = sec_inizio_chiusura - 120 # Preallarme giallo 2 minuti prima delle sbarre giù
        
        if sec_inizio_chiusura <= secondi_attuali_assoluti <= sec_fine_chiusura:
            stato = "CHIUSO"
            secondi_rimanenti = sec_fine_chiusura - secondi_attuali_assoluti
            info_segnaletica = treno["info"]
            break
        elif sec_preavviso <= secondi_attuali_assoluti < sec_inizio_chiusura:
            stato = "PRE-ALLARME"
            secondi_rimanenti = sec_inizio_chiusura - secondi_attuali_assoluti
            info_segnaletica = "Sbarre in discesa imminente"
            break

    # Rendering grafico CarPlay / Tesla Style
    if stato == "CHIUSO":
        m_timer = secondi_rimanenti // 60
        s_timer = secondi_rimanenti % 60
        st.markdown(f"""
            <div class="pl-card">
                <div class="status-dot dot-chiuso">🔴</div>
                <div class="pl-details">
                    <p class="pl-name">{pl['nome']}</p>
                    <p class="pl-info">{info_segnaletica}</p>
                </div>
                <div class="pl-timer timer-chiuso">🛑 {m_timer}:{s_timer:02d}</div>
            </div>
        """, unsafe_allow_html=True)
        
    elif stato == "PRE-ALLARME":
        m_timer = secondi_rimanenti // 60
        s_timer = secondi_rimanenti % 60
        st.markdown(f"""
            <div class="pl-card">
                <div class="status-dot dot-preallarme">🟠</div>
                <div class="pl-details">
                    <p class="pl-name">{pl['nome']}</p>
                    <p class="pl-info">{info_segnaletica}</p>
                </div>
                <div class="pl-timer timer-preallarme">⏳ {m_timer}:{s_timer:02d}</div>
            </div>
        """, unsafe_allow_html=True)
        
    else:
        st.markdown(f"""
            <div class="pl-card">
                <div class="status-dot dot-aperto">🟢</div>
                <div class="pl-details">
                    <p class="pl-name">{pl['nome']}</p>
                    <p class="pl-info">{info_segnaletica}</p>
                </div>
                <div class="pl-timer timer-aperto">OK</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #475569; font-size: 11px; margin-top: 30px;'>Aggiornato alle " + ora_adesso.strftime('%H:%M:%S') + " | Nav-System v4.0</p>", unsafe_allow_html=True)
