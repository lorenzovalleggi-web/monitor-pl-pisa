import streamlit as st
import datetime
import pytz
import requests
from streamlit_autorefresh import st_autorefresh

# Configurazione della pagina
st.set_page_config(page_title="Monitor PL Pisa Live", page_icon="🚦", layout="centered")

# INTERFACCIA MINIMALE AD ALTO CONTRASTO (PULITA)
st.markdown("""
    <style>
    /* Sfondo nero assoluto e testo bianco e nitido */
    .stApp { background-color: #000000; color: #FFFFFF; font-family: -apple-system, sans-serif; }
    
    /* Titolo centrale pulito */
    h1 { color: #FFFFFF !important; font-size: 24px !important; text-align: center; font-weight: bold; margin-bottom: 25px; }
    
    /* Riga separatrice invisibile o sottile */
    hr { border-top: 1px solid #222222 !important; }
    
    /* Layout riga passaggio a livello */
    .pl-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 5px;
        border-bottom: 1px solid #111111;
    }
    
    .pl-text-section { display: flex; flex-direction: column; }
    .pl-main-title { font-size: 18px; font-weight: bold; color: #FFFFFF; margin: 0; }
    .pl-sub-info { font-size: 13px; color: #888888; margin-top: 3px; }
    
    /* Stati colorati netti */
    .status-badge { font-size: 16px; font-weight: bold; padding: 4px 10px; border-radius: 6px; }
    .badge-aperto { color: #00FF66; }
    .badge-preallarme { color: #FF9900; }
    .badge-chiuso { color: #FF3333; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🚦 MONITOR PASSAGGI A LIVELLO</h1>", unsafe_allow_html=True)

# Aggiornamento automatico ogni 5 secondi
st_autorefresh(interval=5000, key="minimal_refresh")

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
                        "numero": t.get('numeroTreno')
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
                        "numero": t.get('numeroTreno')
                    })
    except: pass
    return treni_attivi

lista_treni_fs = recupera_treni_reali()

pl_lista = [
    {"nome": "San Giuliano Terme", "ind_pisa": 0, "ind_lucca": 4},
    {"nome": "Via Ulisse Dini (Gello)", "ind_pisa": 2, "ind_lucca": 3},
    {"nome": "Via di Gagno (Pisa)", "ind_pisa": 5, "ind_lucca": 2},
    {"nome": "Via Ugo Rindi (Pisa)", "ind_pisa": 7, "ind_lucca": 0}
]

# CREAZIONE DELLA LISTA MINIMALE PL
for pl in pl_lista:
    stato = "APERTO"
    secondi_rimanenti = 0
    prossimo_treno_orario = ""
    info_treno_corrente = ""
    
    # Lista dei transiti futuri specifici per questo Passaggio a Livello
    transiti_futuri_pl = []
    
    for treno in lista_treni_fs:
        sec_partenza_reale = (treno["ora_p"] * 3600) + (treno["min_p"] * 60) + (treno["ritardo"] * 60)
        durata_occupazione = 600 if (treno["ora_p"] == 21 and treno["min_p"] == 58) else 360
        
        if treno["direzione"] == "PISA":
            sec_inizio_chiusura = sec_partenza_reale - 360 + (pl["ind_pisa"] * 60)
            sec_fine_chiusura = sec_partenza_reale + durata_occupazione + 60
            dir_freccia = "➔ PISA"
        else:
            sec_inizio_chiusura = sec_partenza_reale - 360 + (pl["ind_lucca"] * 60)
            sec_fine_chiusura = sec_partenza_reale + 300 + 120
            dir_freccia = "🡨 LUCCA"
            
        sec_preavviso = sec_inizio_chiusura - 120
        
        # Memorizziamo tutti i transiti futuri per calcolare l'orario del prossimo treno
        if sec_inizio_chiusura > secondi_attuali_assoluti:
            transiti_futuri_pl.append((sec_inizio_chiusura, dir_freccia))
            
        # Controlliamo lo stato attuale del PL
        if sec_inizio_chiusura <= secondi_attuali_assoluti <= sec_fine_chiusura:
            stato = "CHIUSO"
            secondi_rimanenti = sec_fine_chiusura - secondi_attuali_assoluti
            info_treno_corrente = f"Treno {treno['numero']} ({dir_freccia})"
        elif sec_preavviso <= secondi_attuali_assoluti < sec_inizio_chiusura and stato != "CHIUSO":
            stato = "PRE-ALLARME"
            secondi_rimanenti = sec_inizio_chiusura - secondi_attuali_assoluti
            info_treno_corrente = f"Treno {treno['numero']} in arrivo"

    # Calcolo testo del prossimo treno se il PL è libero
    if transiti_futuri_pl:
        prossimo_sec, direzione_treno = min(transiti_futuri_pl, key=lambda x: x[0])
        ora_p = prossimo_sec // 3600
        min_p = (prossimo_sec % 3600) // 60
        prossimo_treno_orario = f"Prossimo transito: ore {ora_p:02d}:{min_p:02d} ({direzione_treno})"
    else:
        if ora_adesso.hour >= 22:
            prossimo_treno_orario = "Servizio terminato. Riprende domattina."
        else:
            prossimo_treno_orario = "Nessun treno rilevato nelle prossime ore"

    # Rendering grafico pulito a righe
    if stato == "CHIUSO":
        m = secondi_rimanenti // 60
        s = secondi_rimanenti % 60
        st.markdown(f"""
            <div class="pl-row">
                <div class="pl-text-section">
                    <span class="pl-main-title">{pl['nome']}</span>
                    <span class="pl-sub-info">{info_treno_corrente}</span>
                </div>
                <div class="status-badge badge-chiuso">🛑 CHIUSO ({m}:{s:02d})</div>
            </div>
        """, unsafe_allow_html=True)
    elif stato == "PRE-ALLARME":
        m = secondi_rimanenti // 60
        s = secondi_rimanenti % 60
        st.markdown(f"""
            <div class="pl-row">
                <div class="pl-text-section">
                    <span class="pl-main-title">{pl['nome']}</span>
                    <span class="pl-sub-info">{info_treno_corrente}</span>
                </div>
                <div class="status-badge badge-preallarme">⏳ IN CHIUSURA ({m}:{s:02d})</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="pl-row">
                <div class="pl-text-section">
                    <span class="pl-main-title">{pl['nome']}</span>
                    <span class="pl-sub-info">{prossimo_treno_orario}</span>
                </div>
                <div class="status-badge badge-aperto">🟢 APERTO</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #444444; font-size: 11px; margin-top: 40px;'>Aggiornato: " + ora_adesso.strftime('%H:%M:%S') + " | PureMinimal v5.0</p>", unsafe_allow_html=True)
