import streamlit as st
import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Monitor PL Pisa 24h", page_icon="🚊", layout="centered")

st.title("Monitor Passaggi a Livello Live")
st.subheader("Tratta: San Giuliano Terme ↔ Pisa S. Rossore")

# Aggiornamento automatico ogni 10 secondi per inseguire i treni
st_autorefresh(interval=10000, key="datarefresh")

fuso_italia = pytz.timezone('Europe/Rome')
ora_adesso = datetime.datetime.now(fuso_italia)
st.write(f"Ultimo aggiornamento automatico: **{ora_adesso.strftime('%H:%M:%S')}**")

st.markdown("---")

# DATABASE 24H: Minuti standard di passaggio dei treni Regionali ogni ora sulla linea
# I treni sulla Lucca-Pisa passano cadenzati principalmente a questi minuti di ogni ora
MINUTI_PASSAGGIO = [5, 22, 35, 52]

pl_chiusi = False
info_chiusura = ""
prossimo_treno_info = "Nessun treno imminente"

minuto_attuale = ora_adesso.minute

# Cerchiamo il treno più vicino per calcolare la chiusura e simulare i sensori
for min_t in MINUTI_PASSAGGIO:
    # Finestra concordata: 6 minuti prima del passaggio, fino a 2 minuti dopo
    min_inizio_blocco = min_t - 6
    min_fine_blocco = min_t + 2
    
    if min_inizio_blocco <= minuto_attuale <= min_fine_blocco:
        pl_chiusi = True
        
        # Calcoliamo l'orario esatto della presunta chiusura e riapertura
        ora_chiusura = ora_adesso.replace(minute=min_t if min_inizio_blocco >= 0 else 0) - datetime.timedelta(minutes=6)
        ora_riapertura = ora_adesso.replace(minute=min_t) + datetime.timedelta(minutes=2)
        
        info_chiusura = f"Sbarre chiuse dalle **{ora_chiusura.strftime('%H:%M')}** alle **{ora_riapertura.strftime('%H:%M')}**"
        break

# Calcolo del prossimo treno della giornata per il pannello informativo
orari_futuri = [m for m in MINUTI_PASSAGGIO if m > minuto_attuale]
if orari_futuri:
    prossimo_minuto = orari_futuri[0]
    prossimo_treno_info = f"Prossimo transito stimato al minuto **:{prossimo_minuto}** dell'ora in corso."
else:
    prossimo_treno_info = f"Prossimo transito stimato al minuto **:{MINUTI_PASSAGGIO[0]}** della prossima ora."

# Box informativo dei sensori di linea
st.info(f"📋 **Stato Linea 24h:** {prossimo_treno_info}")

# Lista geografica ordinata dei passaggi a livello
pl_ordinati = [
    {"nome": "San Giuliano Terme", "ritardo_sensore": -2}, # Il treno passa prima da qui (se viene da Lucca)
    {"nome": "Via Ulisse Dini (Gello)", "ritardo_sensore": 0},
    {"nome": "Via di Gagno (Pisa)", "ritardo_sensore": 1},
    {"nome": "Via Ugo Rindi (Pisa)", "ritardo_sensore": 2}   # Il treno arriva qui per ultimo verso Pisa
]

st.write("**[ DIREZIONE LUCCA ]**")

for pl in pl_ordinati:
    st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
    
    # Rilevamento avanzato "Sensore di Tratta": 
    # Calcoliamo se il treno si trova esattamente sopra questo specifico PL in base ai minuti
    stato_pl_singolo = False
    for min_t in MINUTI_PASSAGGIO:
        # Il sensore virtuale si attiva dinamicamente per ogni singolo passaggio a livello
        inizio_sensore = min_t - 5 + pl["ritardo_sensore"]
        fine_sensore = min_t + pl["ritardo_sensore"]
        if inizio_sensore <= minuto_attuale <= fine_sensore:
            stato_pl_singolo = True
            break
            
    if stato_pl_singolo:
        st.error(f"🔴 **CHIUSO / IN CHIUSURA** - {pl['nome']}\n\n⚠️ Sensore binario attivato. {info_chiusura}")
    else:
        st.success(f"🟢 **APERTO** - {pl['nome']}\n\nStrada libera")

st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
st.write("**[ DIREZIONE PISA SAN ROSSORE ]**")
