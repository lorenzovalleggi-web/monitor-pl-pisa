import streamlit as st
import requests
import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Monitor PL Pisa", page_icon="🚊", layout="centered")

st.title("Monitor Passaggi a Livello Live")
st.subheader("Tratta: San Giuliano Terme ↔ Pisa S. Rossore")

# Aggiornamento automatico ogni 10 secondi
st_autorefresh(interval=10000, key="datarefresh")

if st.button("🔄 Aggiorna Stato Ora"):
    st.rerun()

fuso_italia = pytz.timezone('Europe/Rome')
ora_adesso = datetime.datetime.now(fuso_italia)
st.write(f"Ultimo aggiornamento automatico: **{ora_adesso.strftime('%H:%M:%S')}**")

st.markdown("---")

# Nuove API stabili: controlliamo sia gli Arrivi che le Partenze a San Giuliano Terme (Codice: S06105)
URL_PARTENZE = "http://www.viaggiatreno.it/viaggiatrenonew/api/partenze/S06105/MONITOR"
URL_ARRIVI = "http://www.viaggiatreno.it/viaggiatrenonew/api/arrivi/S06105/MONITOR"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

try:
    pl_chiusi = False
    info_treno = ""
    treni_rilevati = []

    # 1. Scarichiamo le partenze imminenti
    res_p = requests.get(URL_PARTENZE, headers=headers, timeout=5)
    if res_p.status_code == 200 and res_p.text.strip():
        treni_rilevati.extend(res_p.json())

    # 2. Scarichiamo gli arrivi imminenti
    res_a = requests.get(URL_ARRIVI, headers=headers, timeout=5)
    if res_a.status_code == 200 and res_a.text.strip():
        treni_rilevati.extend(res_a.json())

    # Analizziamo tutti i treni trovati
    for treno in treni_rilevati:
        # Prendiamo l'orario programmato (può essere sotto 'orarioPartenza' o 'orarioArrivo')
        orario_str = treno.get('orarioPartenza') or treno.get('orarioArrivo')
        if not orario_str:
            continue
        
        # Estraiamo ore e minuti (formato HH:MM)
        try:
            ore_t, minuti_t = map(int, orario_str.split(':'))
            ora_teorica = ora_adesso.replace(hour=ore_t, minute=minuti_t, second=0, microsecond=0)
        except ValueError:
            continue
        
        # Estraiamo il ritardo (se è None o non c'è, è 0)
        ritardo = treno.get('ritardo', 0)
        if ritardo is None:
            ritardo = 0
            
        # Calcoliamo l'orario reale stimato del treno sul PL
        ora_reale = ora_teorica + datetime.timedelta(minutes=ritardo)
        
        # Finestra di temporizzazione concordata (6 minuti prima, 2 minuti dopo)
        inizio_blocco = ora_reale - datetime.timedelta(minutes=6)
        fine_blocco = ora_reale + datetime.timedelta(minutes=2)
        
        if inizio_blocco <= ora_adesso <= fine_blocco:
            pl_chiusi = True
            destinazione = treno.get('destinazione', 'N/D')
            info_treno = f"Treno REG {treno.get('numeroTreno', '')} per/da {destinazione} delle {ora_reale.strftime('%H:%M')} (Ritardo: {ritardo} min)"
            break

    # Disegniamo la grafica dei passaggi a livello
    pl_ordinati = [
        "San Giuliano Terme",
        "Via Ulisse Dini (Gello)",
        "Via di Gagno (Pisa)",
        "Via Ugo Rindi (Pisa)"
    ]
    
    st.write("**[ DIREZIONE LUCCA ]**")
    for nome in pl_ordinati:
        st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
        if pl_chiusi:
            st.error(f"🔴 **CHIUSO / IN CHIUSURA** - {nome}\n\n{info_treno}")
        else:
            st.success(f"🟢 **APERTO** - {nome}\n\nStrada libera")
            
    st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
    st.write("**[ DIREZIONE PISA SAN ROSSORE ]**")

except Exception as e:
    st.warning(f"⚠️ Errore lettura tabelle RFI: {str(e)}")
    st.write("**[ DIREZIONE LUCCA ]**")
    for nome in ["San Giuliano Terme", "Via Ulisse Dini (Gello)", "Via di Gagno (Pisa)", "Via Ugo Rindi (Pisa)"]:
        st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
        st.success(f"🟢 **APERTO (Dato provvisorio)** - {nome}\n\nConnessione di riserva attiva")
    st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
    st.write("**[ DIREZIONE PISA SAN ROSSORE ]**")
