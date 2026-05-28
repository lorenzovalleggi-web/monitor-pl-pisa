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

# DATABASE 24H (Orari di linea cadenzati e numeri treno)
TRENI_PISA = {5: "REG 18521", 35: "REG 18525"}    # Verso Pisa
TRENI_LUCCA = {22: "REG 18522", 52: "REG 18526"}  # Verso Lucca

minuto_attuale = ora_adesso.minute
ora_attuale_h = ora_adesso.hour

# Calcolo del ritardo statistico nelle ore di punta
ritardo_stimato = 3 if ((7 <= ora_attuale_h <= 9) or (17 <= ora_attuale_h <= 19)) else 0

# --- NUOVA LOGICA: CALCOLO DEL PROSSIMO TRENO IN ARRIVO ---
prossimo_treno_testo = ""
minuti_tutti = []

# Uniamo tutti i treni pianificati nell'ora con la loro direzione e codice
for m, n in TRENI_PISA.items():
    minuti_tutti.append({"minuto": m + ritardo_stimato, "info": f"➔ **{n}** [VERSO PISA]"})
for m, n in TRENI_LUCCA.items():
    minuti_tutti.append({"minuto": m + ritardo_stimato, "info": f"🡨 **{n}** [VERSO LUCCA]"})

# Ordiniamo i passaggi cronologicamente (0-59 minuti)
minuti_tutti = sorted(minuti_tutti, key=lambda x: x["minuto"])

# Cerchiamo il primo treno che passerà dopo il minuto attuale
trovato = False
for t inGrid in minuti_tutti:
    if t["minuto"] > minuto_attuale:
        ora_prevista = ora_adesso.replace(minute=t["minuto"]).strftime('%H:%M')
        prossimo_treno_testo = f"Prossimo transito: {t['info']} stimato alle ore **{ora_prevista}**"
        trovato = True
        break

# Se non troviamo treni nel resto di questa ora, prendiamo il primo della prossima ora
if not trovato:
    primo_treno = minuti_tutti[0]
    prossima_ora = (ora_adesso + datetime.timedelta(hours=1))
    # Gestione del cambio d'ora per i minuti bassi
    try:
        ora_prevista = prossima_ora.replace(minute=primo_treno["minuto"]).strftime('%H:%M')
    except:
        ora_prevista = "--:--"
    prossimo_treno_testo = f"Prossimo transito: {primo_treno['info']} stimato alle ore **{ora_prevista}**"

# Mostriamo il box informativo in evidenza
st.info(f"📋 **INFO LINEA:** {prossimo_treno_testo}")
st.markdown("---")

# Lista dei Passaggi a Livello in un UNICO ORDINE GEOGRAFICO (Da Nord a Sud)
pl_lista = [
    {"nome": "San Giuliano Terme", "ind_pisa": 0, "ind_lucca": 3},
    {"nome": "Via Ulisse Dini (Gello)", "ind_pisa": 1, "ind_lucca": 2},
    {"nome": "Via di Gagno (Pisa)", "ind_pisa": 2, "ind_lucca": 1},
    {"nome": "Via Ugo Rindi (Pisa)", "ind_pisa": 3, "ind_lucca": 0}
]

st.write("### 🚊 LINEA PISA ↔ LUCCA")
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
