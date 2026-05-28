import streamlit as st
import requests
import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Monitor PL Pisa", page_icon="🚊", layout="centered")

st.title("Monitor Passaggi a Livello Live")
st.subheader("Tratta: San Giuliano Terme ↔ Pisa S. Rossore")

# AGGIORNAMENTO AUTOMATICO: Rinfresca la pagina da solo ogni 10 secondi
# (10000 millisecondi = 10 secondi)
st_autorefresh(interval=10000, key="datarefresh")

# Bottone di aggiornamento manuale (se vuoi forzarlo tu)
if st.button("🔄 Aggiorna Stato Ora"):
    st.rerun()

# Configurazione fuso orario italiano
fuso_italia = pytz.timezone('Europe/Rome')
ora_attuale = datetime.datetime.now(fuso_italia).strftime("%H:%M:%S")
st.write(f"Ultimo aggiornamento automatico: **{ora_attuale}**")

st.markdown("---")

# Interroghiamo Viaggiatreno (RFI) sulla situazione della linea Lucca-Pisa
URL_RFI = "http://www.viaggiatreno.it/viaggiatrenonew/api/ristampaStriscia/S06105"

try:
    risposta = requests.get(URL_RFI, timeout=5)
    pl_chiusi = False
    
    if risposta.status_code == 200:
        dati = risposta.json()
        for treno in dati.get('arrivi', []) + dati.get('partenze', []):
            compagnia = treno.get('compagnia', '')
            if "REG" in compagnia or treno.get('orarioArrivo', '') != '':
                pl_chiusi = True
                break

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
            st.error(f"🔴 **CHIUSO / IN CHIUSURA** - {nome}\n\nTreno in transito.")
        else:
            st.success(f"🟢 **APERTO** - {nome}\n\nStrada libera")
            
    st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
    st.write("**[ DIREZIONE PISA SAN ROSSORE ]**")

except Exception as e:
    st.write("**[ DIREZIONE LUCCA ]**")
    for nome in ["San Giuliano Terme", "Via Ulisse Dini (Gello)", "Via di Gagno (Pisa)", "Via Ugo Rindi (Pisa)"]:
        st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
        st.success(f"🟢 **APERTO** - {nome}\n\nStrada libera")
    st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
    st.write("**[ DIREZIONE PISA SAN ROSSORE ]**")
