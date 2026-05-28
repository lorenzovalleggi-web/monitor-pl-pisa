import streamlit as st
import datetime
import pytz
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Monitor PL Pisa Live", page_icon="🚦", layout="centered")

st.title("Monitor Passaggi a Livello Live")
st.subheader("Tratta: San Giuliano Terme ↔ Pisa S. Rossore")

# Aggiornamento automatico ogni 15 secondi per interrogare i server ferroviari
st_autorefresh(interval=15000, key="datarefresh")

if st.button("🔄 Forza Aggiornamento Real-Time"):
    st.rerun()

fuso_italia = pytz.timezone('Europe/Rome')
ora_adesso = datetime.datetime.now(fuso_italia)
st.write(f"Ultimo aggiornamento dai server FS: **{ora_adesso.strftime('%H:%M:%S')}**")

minuti_assoluti_ora = ora_adesso.hour * 60 + ora_adesso.minute

# ID Stazioni ufficiali ViaggiaTreno per monitorare i passaggi
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
            if "PISA" in t.get('destinazione', '').upper() or "LIVORNO" in t.get('destinazione', '').upper():
                orario_prog = t.get('orarioProgrammato', '') # Formato HH:MM
                if orario_prog:
                    h, m = map(int, orario_prog.split(':'))
                    ritardo = t.get('ritardo', 0)
                    if ritardo == "---" or ritardo is None: ritardo = 0
                    treni_attivi.append({
                        "ora_p": h, "min_p": m, "ritardo": int(ritardo), "direzione": "PISA",
                        "info": f"➔ **REG {t.get('numeroTreno')}** per {t.get('destinazione')}"
                    })
    except:
        pass

    # 2. Controlla partenze da Pisa S. Rossore (Verso Lucca)
    try:
        url_pr = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/{ID_PISA_ROSSORE}/{ora_adesso.strftime('%Y-%m-%dT00:00:00')}"
        res = requests.get(url_pr, timeout=5).json()
        for t in res.get('tabellone', []):
            if "LUCCA" in t.get('destinazione', '').upper() or "PISTOIA" in t.get('destinazione', '').upper() or "FIRENZE" in t.get('destinazione', '').upper():
                orario_prog = t.get('orarioProgrammato', '')
                if orario_prog:
                    h, m = map(int, orario_prog.split(':'))
                    ritardo = t.get('ritardo', 0)
                    if ritardo == "---" or ritardo is None: ritardo = 0
                    treni_attivi.append({
                        "ora_p": h, "min_p": m, "ritardo": int(ritardo), "direzione": "LUCCA",
                        "info": f"🡨 **REG {t.get('numeroTreno')}** per {t.get('destinazione')}"
                    })
    except:
        pass
    return treni_attivi

# Scarica lo stato della linea live
lista_treni_fs = recupera_treni_reali()

# --- TROVA PROSSIMO TRENO ---
prossimo_treno_testo = "Nessun transito imminente rilevato dai sistemi di stazione."
treni_futuri = []
for t in lista_treni_fs:
    min_ass_treno = t["ora_p"] * 60 + t["min_p"] + t["ritardo"]
    if min_ass_treno > minuti_assoluti_ora:
        treni_futuri.append((min_ass_treno, t))

if treni_futuri:
    _, prox = min(treni_futuri, key=lambda x: x[0])
    ora_effettiva = (prox["ora_p"] * 60 + prox["min_p"] + prox["ritardo"]) // 60
    min_effettiva = (prox["ora_p"] * 60 + prox["min_p"] + prox["ritardo"]) % 60
    nota_ritardo = f" (+{prox['ritardo']} min ritardo)" if prox['ritardo'] > 0 else " (In orario)"
    prossimo_treno_testo = f"Prossimo transito reale: {prox['info']} alle **{ora_eff
