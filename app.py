import streamlit as st
import requests
import datetime
import pytz

st.set_page_config(page_title="Monitor PL Pisa", page_icon="🚊", layout="centered")

st.title("Monitor Passaggi a Livello Live")
st.subheader("Tratta: San Giuliano Terme ↔ Pisa S. Rossore")

# Bottone di aggiornamento manuale
if st.button("🔄 Aggiorna Stato Ora"):
    st.rerun()

# Configurazione fuso orario italiano
fuso_italia = pytz.timezone('Europe/Rome')
ora_attuale = datetime.datetime.now(fuso_italia).strftime("%H:%M:%S")
st.write(f"Ultimo aggiornamento: **{ora_attuale}**")

st.markdown("---")

# Link della sorgente dati (Open Data Pisa/Toscana)
URL_API = "https://www.move-it.toscana.it/api/v1/pl/pisa-lucca"

try:
    # Richiesta dati reali
    risposta = requests.get(URL_API, timeout=5)
    dati = risposta.json()
    
    # Lista dei passaggi a livello nell'ordine corretto da San Giuliano a Pisa
    pl_ordinati = [
        {"id": "PL_SG", "nome": "San Giuliano Terme"},
        {"id": "PL_GD", "nome": "Via Ulisse Dini (Gello)"},
        {"id": "PL_VG", "nome": "Via di Gagno (Pisa)"},
        {"id": "PL_UR", "nome": "Via Ugo Rindi (Pisa)"}
    ]
    
    st.write("**[ DIREZIONE LUCCA ]**")
    
    for pl in pl_ordinati:
        st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
        
        # Cerchiamo lo stato del PL nei dati della regione (default: APERTO per sicurezza)
        stato = dati.get(pl["id"], {}).get("status", "APERTO")
        
        if stato == "CHIUSO":
            st.error(f"🔴 **CHIUSO** - {pl['nome']}\n\nAttesa passaggio treno.")
        else:
            st.success(f"🟢 **APERTO** - {pl['nome']}\n\nStrada libera")
            
    st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
    st.write("**[ DIREZIONE PISA SAN ROSSORE ]**")

except Exception as e:
    # Se il server della regione ha un problema, mostriamo un avviso generico funzionante
    st.warning("⚠️ Impossibile ricevere i dati in tempo reale. Mostro lo stato teorico:")
    st.write("**[ DIREZIONE LUCCA ]**")
    pl_ordinati = ["San Giuliano Terme", "Via Ulisse Dini (Gello)", "Via di Gagno (Pisa)", "Via Ugo Rindi (Pisa)"]
    for nome in pl_ordinati:
        st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
        st.success(f"🟢 **APERTO** - {nome}\n\nStrada libera")
    st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
    st.write("**[ DIREZIONE PISA SAN ROSSORE ]**")
