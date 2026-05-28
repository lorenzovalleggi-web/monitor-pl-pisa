import streamlit as st
import datetime
import pytz
import requests
from streamlit_autorefresh import st_autorefresh

# Configurazione della pagina
st.set_page_config(page_title="HUD Monitor PL Pisa", page_icon="🚦", layout="centered")

# STYLING HUD (Heads-Up Display) STILE NAVIGATORE AUTOMOBILISTICO
st.markdown("""
    <style>
    /* Sfondo nero assoluto per evitare riflessi di notte */
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Titoli in font elettronico */
    h1, h3 { 
        color: #00FFCC !important; 
        font-family: 'Courier New', Courier, monospace; 
        text-align: center;
        font-weight: bold;
    }
    
    /* Box informazioni di linea */
    .stAlert { 
        background-color: #111111 !important; 
        border: 1px solid #333333 !important;
    }
    
    /* Stili personalizzati per i grandi cartelli di stato */
    .status-card {
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 10px;
        text-align: center;
        font-family: 'Arial Black', Gadget, sans-serif;
    }
    .chiuso { background-color: #330000; border: 2px solid #FF0033; color: #FF3366; }
    .preallarme { background-color: #332200; border: 2px solid #FF9900; color: #FFCC00; }
    .aperto { background-color: #002200; border: 2px solid #00CC33; color: #33FF66; }
    
    .timer-text { font-size: 28px; font-weight: bold; display: block; margin: 5px 0; }
    .info-text { font-size: 14px; opacity: 0.8; }
    </style>
""", unsafe_allow_html=True)

st.title("📟 HUD MONITOR PL LIVE")
st.markdown("<p style='text-align: center; color: #888;'>Sincronizzato con Server Satellitari FS</p>", unsafe_allow_html=True)

# Aggiornamento super rapido ogni 5 secondi per far scendere il timer in modo fluido
st_autorefresh(interval=5000, key="hud_refresh")

if st.button("🔄 FORZA SINCRONIZZAZIONE SERVER"):
    st.rerun()

fuso_italia = pytz.timezone('Europe/Rome')
ora_adesso = datetime.datetime.now(fuso_italia)
st.markdown(f"<p style='text-align: center; font-size: 16px;'>Ora GPS: <b>{ora_adesso.strftime('%H:%M:%S')}</b></p>", unsafe_allow_html=True)

secondi_attuali_assoluti = (ora_adesso.hour * 3600) + (ora_adesso.minute * 60) + ora_adesso.second

ID_SAN_GIULIANO = "S06411"
ID_PISA_ROSSORE = "S06501"

@st.cache_data(ttl=8)
def recupera_treni_reali():
    treni_attivi = []
    # 1. Tratta da Lucca verso Pisa (Partenze da San Giuliano)
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
                        "info": f"➔ REG {t.get('numeroTreno')} per {t.get('destinazione')}"
                    })
    except: pass

    # 2. Tratta da Pisa verso Lucca (Partenze da Pisa S. Rossore)
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
                        "info": f"🡨 REG {t.get('numeroTreno')} per {t.get('destinazione')}"
                    })
    except: pass
    return treni_attivi

lista_treni_fs = recupera_treni_reali()

# --- BLOCCO PROSSIMO TRENO ---
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
    nota_ritardo = f" (+{prox['ritardo']} min ritardo)" if prox['ritardo'] > 0 else " (In orario)"
    prossimo_treno_testo = f"Prossimo transito reale: {prox['info']} stimato alle **{ora_effettiva:02d}:{min_effettiva:02d}**{nota_ritardo}"
else:
    if ora_adesso.hour >= 22:
        prossimo_treno_testo = "Servizio ferroviario concluso. 🌅 Primi treni: 05:30 (Lucca) / 05:51 (Pisa)."
    else:
        prossimo_treno_testo = "Nessun convoglio imminente rilevato sui monitor di stazione."

st.info(f"📋 **STATO DELLA LINEA:** {prossimo_treno_testo}")
st.markdown("---")

# CONFIGURAZIONE DISTANZE REALI PASSAGGI A LIVELLO
pl_lista = [
    {"nome": "San Giuliano Terme", "ind_pisa": 0, "ind_lucca": 4},
    {"nome": "Via Ulisse Dini (Gello)", "ind_pisa": 2, "ind_lucca": 3},
    {"nome": "Via di Gagno (Pisa)", "ind_pisa": 5, "ind_lucca": 2},
    {"nome": "Via Ugo Rindi (Pisa)", "ind_pisa": 7, "ind_lucca": 0}
]

st.write("### 🚊 PROSPEZIONE SBARRE AL VOLANTE")

for pl in pl_lista:
    st.markdown("<div style='text-align: center; color: #444; margin: 0;'>│</div>", unsafe_allow_html=True)
    
    stato = "APERTO"
    info_segnaletica = "STRADA LIBERA"
    secondi_rimanenti = 0
    
    for treno in lista_treni_fs:
        # Calcolo Orario Reale al secondo (Programmato + Ritardo)
        sec_partenza_reale = (treno["ora_p"] * 3600) + (treno["min_p"] * 60) + (treno["ritardo"] * 60)
        durata_occupazione = 600 if (treno["ora_p"] == 21 and treno["min_p"] == 58) else 360
        
        if treno["direzione"] == "PISA":
            sec_inizio_chiusura = sec_partenza_reale - 360 + (pl["ind_pisa"] * 60)
            sec_fine_chiusura = sec_partenza_reale + durata_occupazione + 60
        else: # LUCCA
            sec_inizio_chiusura = sec_partenza_reale - 360 + (pl["ind_lucca"] * 60)
            sec_fine_chiusura = sec_partenza_reale + 300 + 120
            
        sec_preavviso = sec_inizio_chiusura - 120 # Il Pre-allarme giallo si attiva 2 minuti prima della chiusura fissa
        
        if sec_inizio_chiusura <= secondi_attuali_assoluti <= sec_fine_chiusura:
            stato = "CHIUSO"
            secondi_rimanenti = sec_fine_chiusura - secondi_attuali_assoluti
            info_segnaletica = treno["info"].upper()
            break
        elif sec_preavviso <= secondi_attuali_assoluti < sec_inizio_chiusura:
            stato = "PRE-ALLARME"
            secondi_rimanenti = sec_inizio_chiusura - secondi_attuali_assoluti
            info_segnaletica = "SBARRE IN DISCESA ⚠️ CONVOGLIO IN ARRIVO"
            break

    # Stampa dei grandi cartelli HUD ad alto contrasto
    if stato == "CHIUSO":
        m_timer = secondi_rimanenti // 60
        s_timer = secondi_rimanenti % 60
        st.markdown(f"""
            <div class="status-card chiuso">
                <span style="font-size: 14px; letter-spacing: 2px;">BARRIERA CHIUSA</span>
                <span class="timer-text">🛑 RIAPERTURA: {m_timer}m {s_timer:02d}s</span>
                <span class="info-text">{info_segnaletica}</span>
            </div>
        """, unsafe_allow_html=True)
        
    elif stato == "PRE-ALLARME":
        m_timer = secondi_rimanenti // 60
        s_timer = secondi_rimanenti % 60
        st.markdown(f"""
            <div class="status-card preallarme">
                <span style="font-size: 14px; letter-spacing: 2px;">⚠️ ATTENZIONE</span>
                <span class="timer-text">🟠 CHIUSURA TRA: {m_timer}m {s_timer:02d}s</span>
                <span class="info-text">{info_segnaletica}</span>
            </div>
        """, unsafe_allow_html=True)
        
    else:
        st.markdown(f"""
            <div class="status-card aperto">
                <span style="font-size: 13px; letter-spacing: 2px;">VIA LIBERA</span>
                <span style="font-size: 20px; display: block; margin: 4px 0; font-weight: bold;">🟢 APERTO - {pl['nome']}</span>
                <span class="info-text">{info_segnaletica}</span>
            </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption("⚙️ HUD Automotive v3.0 | Modalità Notturna Permanente Attiva")
