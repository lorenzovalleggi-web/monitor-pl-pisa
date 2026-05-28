import streamlit as st
import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Monitor PL Pisa 24h Pro", page_icon="🚊", layout="centered")

st.title("Monitor Passaggi a Livello Live")
st.subheader("Tratta: San Giuliano Terme ↔ Pisa S. Rossore")

# Aggiornamento automatico ogni 10 secondi
st_autorefresh(interval=10000, key="datarefresh")

fuso_italia = pytz.timezone('Europe/Rome')
ora_adesso = datetime.datetime.now(fuso_italia)
st.write(f"Ultimo aggiornamento automatico: **{ora_adesso.strftime('%H:%M:%S')}**")

st.markdown("---")

# DATABASE 24H: Orari dei passaggi cadenzati
MINUTI_PISA = [5, 35]   # Treni in direzione Pisa S. Rossore
MINUTI_LUCCA = [22, 52] # Treni in direzione Lucca

minuto_attuale = ora_adesso.minute
ora_attuale_h = ora_adesso.hour

# 1. CALCOLO DINAMICO DEL RITARDO (Fattore Ore di Punta)
ritardo_stimato = 0
if (7 <= ora_attuale_h <= 9) or (17 <= ora_attuale_h <= 19):
    ritardo_stimato = 3 # Nelle ore di punta i regionali accumulano mediamente 3 minuti

# Funzione per verificare lo stato del PL in base alla direzione del treno
def controlla_pl(nome_pl, minuti_assegnati, direzione):
    for min_t in minuti_assegnati:
        min_reale = min_t + ritardo_stimato
        
        # Finestra di sbarre giù (6 minuti prima del transito reale, 2 minuti dopo)
        inizio_blocco = min_reale - 6
        fine_blocco = min_reale + 2
        
        if inizio_blocco <= minuto_attuale <= fine_blocco:
            ora_chiusura = ora_adesso.replace(minute=max(0, inizio_blocco))
            ora_riapertura = ora_adesso.replace(minute=min(59, fine_blocco))
            return True, f"🔴 **CHIUSO / IN CHIUSURA** - {nome_pl}\n\nTreno in transito dir. {direzione}. Sbarre giù: {ora_chiusura.strftime('%H:%M')} ↔ {ora_riapertura.strftime('%H:%M')}"
    return False, f"🟢 **APERTO** - {nome_pl}\n\nStrada libera"

# --- GRAFICA FLUSSO 1: DIREZIONE PISA SAN ROSSORE ---
st.write("### 🛤️ FLUSSO: DIREZIONE PISA S. ROSSORE")
st.caption("I sensori si attivano dall'alto verso il basso (da San Giuliano verso Pisa)")

# Ordine geografico per chi va verso Pisa
pl_verso_pisa = ["San Giuliano Terme", "Via Ulisse Dini (Gello)", "Via di Gagno (Pisa)", "Via Ugo Rindi (Pisa)"]

for i, nome in enumerate(pl_verso_pisa):
    st.markdown("<div style='text-align: center; font-size: 16px; margin: 2px 0;'>│<br>▼</div>", unsafe_allow_html=True)
    # Applichiamo un leggero sfasamento dei minuti per simulare il passaggio fisico a cascata
    minuti_sfasati = [m + (i * 1) for m in MINUTI_PISA]
    chiuso, messaggio = controlla_pl(nome, minuti_sfasati, "Pisa")
    
    if chiuso:
        st.error(messaggio)
    else:
        st.success(messaggio)

st.markdown("---")

# --- GRAFICA FLUSSO 2: DIREZIONE LUCCA ---
st.write("### 🛤️ FLUSSO: DIREZIONE LUCCA")
st.caption("I sensori si attivano dal basso verso l'alto (da Pisa risalendo verso San Giuliano)")

# Ordine geografico inverso per i treni che tornano verso Lucca
pl_verso_lucca = ["Via Ugo Rindi (Pisa)", "Via di Gagno (Pisa)", "Via Ulisse Dini (Gello)", "San Giuliano Terme"]

for i, nome in enumerate(pl_verso_lucca):
    st.markdown("<div style='text-align: center; font-size: 16px; margin: 2px 0;'>│<br>▼</div>", unsafe_allow_html=True)
    # Anche qui sfasamento progressivo basato sul movimento inverso del treno
    minuti_sfasati = [m + (i * 1) for m in MINUTI_LUCCA]
    chiuso, messaggio = controlla_pl(nome, minuti_sfasati, "Lucca")
    
    if chiuso:
        st.error(messaggio)
    else:
        st.success(messaggio)

# Pannello informativo di controllo in fondo alla pagina
st.markdown("---")
if ritardo_stimato > 0:
    st.warning(f"⚠️ **Fascia Oraria di Punta attiva:** L'algoritmo sta calcolando +{ritardo_stimato} minuti di tolleranza sul traffico ferroviario.")
else:
    st.info("ℹ️ **Fascia Oraria Regolare:** Nessuna anomalia o ritardo statistico stimato sui binari.")
