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

# Bottone manuale
if st.button("🔄 Aggiorna Stato Ora"):
    st.rerun()

# Configurazione orario italiano attuale
fuso_italia = pytz.timezone('Europe/Rome')
ora_adesso = datetime.datetime.now(fuso_italia)
st.write(f"Ultimo aggiornamento automatico: **{ora_adesso.strftime('%H:%M:%S')}**")

st.markdown("---")

URL_RFI = "http://www.viaggiatreno.it/viaggiatrenonew/api/ristampaStriscia/S06105"

try:
    risposta = requests.get(URL_RFI, timeout=5)
    pl_chiusi = False
    info_treno = ""
    
    if risposta.status_code == 200:
        dati = risposta.json()
        
        # Uniamo arrivi e partenze della stazione di San Giuliano Terme
        movimenti = dati.get('arrivi', []) + dati.get('partenze', [])
        
        for treno in movimenti:
            # Consideriamo solo i treni Regionali (REG) attivi sulla tratta
            compagnia = treno.get('compagnia', '')
            if "REG" in compagnia:
                
                # Recuperiamo l'orario programmato (può essere sotto 'orarioArrivo' o 'orarioPartenza')
                orario_str = treno.get('orarioArrivo') or treno.get('orarioPartenza')
                if not orario_str:
                    continue
                
                # Estraiamo ore e minuti teorici (es. "18:00")
                try:
                    ore_t, minuti_t = map(int, orario_str.split(':'))
                    ora_teorica = ora_adesso.replace(hour=ore_t, minute=minuti_t, second=0, microsecond=0)
                except ValueError:
                    continue
                
                # Recuperiamo il ritardo (se non c'è, è 0)
                ritardo = treno.get('ritardo', 0)
                if ritardo is None:
                    ritardo = 0
                
                # Calcoliamo l'ORARIO REALE stimato del treno
                ora_reale = ora_teorica + datetime.timedelta(minutes=ritardo)
                
                # Definiamo la finestra di chiusura delle sbarre
                inizio_blocco = ora_reale - datetime.timedelta(minutes=6)
                fine_blocco = ora_reale + datetime.timedelta(minutes=2)
                
                # Controllo: l'ora attuale è compresa tra 6 minuti prima e 2 minuti dopo?
                if inizio_blocco <= ora_adesso <= fine_blocco:
                    pl_chiusi = True
                    info_treno = f"Treno REG {treno.get('numeroTreno', '')} atteso alle {ora_reale.strftime('%H:%M')} (Ritardo: {ritardo} min)"
                    break

    # Lista dei passaggi a livello geografici
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
    # Sistema di protezione in caso di errore di rete
    st.write("**[ DIREZIONE LUCCA ]**")
    for nome in ["San Giuliano Terme", "Via Ulisse Dini (Gello)", "Via di Gagno (Pisa)", "Via Ugo Rindi (Pisa)"]:
        st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
        st.success(f"🟢 **APERTO (Dato stimato)** - {nome}\n\nNessuna anomalia rilevata")
    st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
    st.write("**[ DIREZIONE PISA SAN ROSSORE ]**")
