import streamlit as st
import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Monitor PL Pisa 24h", page_icon="🚊", layout="centered")

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

# DATABASE 24H CON NUMERO TRENO ASSOCIATO AI MINUTI DI PASSAGGIO
# Struttura: { minuto_di_passaggio: "Numero_Treno" }
TRENI_PISA = {5: "REG 18521", 35: "REG 18525"}    # Verso Pisa
TRENI_LUCCA = {22: "REG 18522", 52: "REG 18526"}  # Verso Lucca

minuto_attuale = ora_adesso.minute
ora_attuale_h = ora_adesso.hour

# Calcolo del ritardo statistico nelle ore di punta
ritardo_stimato = 3 if ((7 <= ora_attuale_h <= 9) or (17 <= ora_attuale_h <= 19)) else 0

# Lista dei Passaggi a Livello in un UNICO ORDINE GEOGRAFICO (Da Nord a Sud)
pl_lista = [
    {"nome": "San Giuliano Terme", "ind_pisa": 0, "ind_lucca": 3},
    {"nome": "Via Ulisse Dini (Gello)", "ind_pisa": 1, "ind_lucca": 2},
    {"nome": "Via di Gagno (Pisa)", "ind_pisa": 2, "ind_lucca": 1},
    {"nome": "Via Ugo Rindi (Pisa)", "ind_pisa": 3, "ind_lucca": 0}
]

st.write("### 🚊 UNICO BINARIO GEOGRAFICO")
st.caption("Visualizzazione sequenziale da Lucca (Nord) verso Pisa (Sud)")

# Generiamo l'unica mappa lineare senza sdoppiamenti
for pl in pl_lista:
    st.markdown("<div style='text-align: center; font-size: 16px; margin: 1px 0;'>│<br>▼</div>", unsafe_allow_html=True)
    
    stato_chiuso = False
    info_segnaletica = "Strada libera"
    
    # 1. Controllo treni verso PISA (il treno scende lungo la lista)
    for min_t, num_treno in TRENI_PISA.items():
        min_reale = min_t + ritardo_stimato + pl["ind_pisa"]
        if (min_reale - 6) <= minuto_attuale <= (min_reale + 2):
            stato_chiuso = True
            ora_c = ora_adesso.replace(minute=max(0, min_reale - 6)).strftime('%H:%M')
            ora_r = ora_adesso.replace(minute=min(59, min_reale + 2)).strftime('%H:%M')
            info_segnaletica = f"➔ **{num_treno}** da Lucca **[VERSO PISA]**\n\n⏱️ Chiusura: {ora_c} ↔ {ora_r}"
            break
            
    # 2. Controllo treni verso LUCCA (il treno risale la lista)
    if not stato_chiuso:
        for min_t, num_treno in TRENI_LUCCA.items():
            min_reale = min_t + ritardo_stimato + pl["ind_lucca"]
            if (min_reale - 6) <= minuto_attuale <= (min_reale + 2):
                stato_chiuso = True
                ora_c = ora_adesso.replace(minute=max(0, min_reale - 6)).strftime('%H:%M')
                ora_r = ora_adesso.replace(minute=min(59, min_reale + 2)).strftime('%H:%M')
                info_segnaletica = f"🡨 **{num_treno}** da Pisa **[VERSO LUCCA]**\n\n⏱️ Chiusura: {ora_c} ↔ {ora_r}"
                break

    # Mostriamo il box colorato finale (Singolo PL)
    if stato_chiuso:
        st.error(f"🔴 **CHIUSO / IN CHIUSURA** - {pl['nome']}\n\n{info_segnaletica}")
    else:
        st.success(f"🟢 **APERTO** - {pl['nome']}\n\n{info_segnaletica}")

st.markdown("---")
if ritardo_stimato > 0:
    st.warning(f"⚠️ **Fascia di punta:** Calcolati +{ritardo_stimato} min di tolleranza traffico.")
else:
    st.info("ℹ️ **Fascia regolare:** Monitoraggio basato su orari ufficiali 24h.")
