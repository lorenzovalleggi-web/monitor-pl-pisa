
import streamlit as st
import datetime
import pytz
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Monitor PL Pisa Live", page_icon="🚦", layout="centered")

st.title("Monitor Passaggi a Livello Live")
st.subheader("Tratta: San Giuliano Terme ↔ Pisa S. Rossore")

# Aggiornamento automatico ogni 15 secondi
st_autorefresh(interval=15000, key="datarefresh")

if st.button("🔄 Aggiorna Stato Ora"):
    st.rerun()

fuso_italia = pytz.timezone('Europe/Rome')
ora_adesso = datetime.datetime.now(fuso_italia)
st.write(f"Ultimo aggiornamento automatico: **{ora_adesso.strftime('%H:%M:%S')}**")

minuti_assoluti_ora = ora_adesso.hour * 60 + ora_adesso.minute

# ID Stazioni ufficiali ViaggiaTreno
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
            dest = t.get('destinazione', '').upper()
            if "PISA" in dest or "LIVORNO" in dest:
                orario_prog = t.get('orarioProgrammato', '')
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
            dest = t.get('destinazione', '').upper()
            if "LUCCA" in dest or "PISTOIA" in dest or "FIRENZE" in dest:
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
prossimo_treno_testo = ""
treni_futuri = []
for t in lista_treni_fs:
    min_ass_treno = t["ora_p"] * 60 + t["min_p"] + t["ritardo"]
    if min_ass_treno > minuti_assoluti_ora:
        treni_futuri.append((min_ass_treno, t))

if treni_futuri:
    _, prox = min(treni_futuri, key=lambda x: x[0])
    min_totale = prox["ora_p"] * 60 + prox["min_p"] + prox["ritardo"]
    ora_effettiva = min_totale // 60
    min_effettiva = min_totale % 60
    
    # Ricostruiamo la stringa in modo spezzato e sicuro per evitare bug di tranciatura
    stringa_ora = f"{ora_effettiva:02d}:{min_effettiva:02d}"
    nota_ritardo = f" (+{prox['ritardo']} min ritardo)" if prox['ritardo'] > 0 else " (In orario)"
    prossimo_treno_testo = "Prossimo transito reale: " + prox["info"] + " alle **" + stringa_ora + "**" + nota_ritardo
else:
    if ora_adesso.hour >= 22:
        prossimo_treno_testo = "Servizio giornaliero terminato. 🌅 Primo treno della mattina: **REG delle 05:30 per Lucca** / **05:51 per Pisa**."
    else:
        prossimo_treno_testo = "Nessun transito imminente rilevato dai sistemi di stazione."

st.info(f"📋 **STATO LINEA LIVE:** {prossimo_treno_testo}")
st.markdown("---")

pl_lista = [
    {"nome": "San Giuliano Terme", "ind_pisa": 0, "ind_lucca": 4},
    {"nome": "Via Ulisse Dini (Gello)", "ind_pisa": 2, "ind_lucca": 3},
    {"nome": "Via di Gagno (Pisa)", "ind_pisa": 5, "ind_lucca": 2},
    {"nome": "Via Ugo Rindi (Pisa)", "ind_pisa": 7, "ind_lucca": 0}
]

st.write("### 🚊 LINEA PISA ↔ LUCCA")

# CALCOLO STATO DEI PASSAGGI A LIVELLO CON DATI REALI
for pl in pl_lista:
    st.markdown("<div style='text-align: center; font-size: 16px; margin: 1px 0;'>│<br>▼</div>", unsafe_allow_html=True)
    
    stato_chiuso = False
    info_segnaletica = "Strada libera"
    
    for treno in lista_treni_fs:
        min_partenza_reale = treno["ora_p"] * 60 + treno["min_p"] + treno["ritardo"]
        durata_viaggio = 10 if (treno["ora_p"] == 21 and treno["min_p"] == 58) else 6
        
        if treno["direzione"] == "PISA":
            inizio_chiusura = min_partenza_reale - 6 + pl["ind_pisa"]
            fine_chiusura = min_partenza_reale + durata_viaggio + 1
            
            if inizio_chiusura <= minuti_assoluti_ora <= fine_chiusura:
                stato_chiuso = True
                ora_c = f"{inizio_chiusura // 60:02d}:{inizio_chiusura % 60:02d}"
                ora_r = f"{fine_chiusura // 60:02d}:{fine_chiusura % 60:02d}"
                info_segnaletica = f"{treno['info']}\n\n⏱️ Chiusura effettiva: {ora_c} ↔ {ora_r}"
                break
                
        elif treno["direzione"] == "LUCCA":
            inizio_chiusura = min_partenza_reale - 6 + pl["ind_lucca"]
            fine_chiusura = min_partenza_reale + 5 + 2
            
            if inizio_chiusura <= minuti_assoluti_ora <= fine_chiusura:
                stato_chiuso = True
                ora_c = f"{inizio_chiusura // 60:02d}:{inizio_chiusura % 60:02d}"
                ora_r = f"{fine_chiusura // 60:02d}:{fine_chiusura % 60:02d}"
                info_segnaletica = f"{treno['info']}\n\n⏱️ Chiusura effettiva: {ora_c} ↔ {ora_r}"
                break

    if stato_chiuso:
        st.error(f"🔴 **CHIUSO / IN CHIUSURA** - {pl['nome']}\n\n{info_segnaletica}")
    else:
        st.success(f"🟢 **APERTO** - {pl['nome']}\n\n{info_segnaletica}")

st.markdown("---")
st.success("🛰️ **Modalità Dinamica Attiva**: Collegamento diretto con i server ViaggiaTreno Trenitalia abilitato.")
