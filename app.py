import streamlit as st
import datetime
import pytz
import requests
from streamlit_autorefresh import st_autorefresh
import os

st.set_page_config(page_title="Pisa ⇄ San Giuliano Terme RailFlow", page_icon="🚦", layout="centered")

st.title("Pisa ⇄ San Giuliano Terme RailFlow")
st.subheader("Stato dei passaggi a livello in tempo reale")

st_autorefresh(interval=15000, key="datarefresh")

if st.button("🔄 Aggiorna Stato Ora"):
    st.rerun()

fuso_italia = pytz.timezone('Europe/Rome')
ora_adesso = datetime.datetime.now(fuso_italia)
st.write(f"Ultimo aggiornamento automatico: **{ora_adesso.strftime('%H:%M:%S')}**")

minuti_assoluti_ora = ora_adesso.hour * 60 + ora_adesso.minute
ID_SAN_GIULIANO = "S06411"
ID_PISA_ROSSORE = "S06501"

# --- TABELLA ORARIA UFFICIALE PROGRAMMATA (ORARIO TEORICO DI RISERVA) ---
ORARIO_PROGRAMMATO = [
    {"ora": 5, "min": 30, "dir": "LUCCA", "num": "18502"}, {"ora": 5, "min": 51, "dir": "PISA", "num": "18501"},
    {"ora": 6, "min": 23, "dir": "LUCCA", "num": "18504"}, {"ora": 6, "min": 35, "dir": "PISA", "num": "18503"},
    {"ora": 6, "min": 54, "dir": "LUCCA", "num": "18506"}, {"ora": 7, "min": 17, "dir": "PISA", "num": "6915"},
    {"ora": 7, "min": 30, "dir": "LUCCA", "num": "18508"}, {"ora": 7, "min": 47, "dir": "PISA", "num": "18505"},
    {"ora": 8, "min": 23, "dir": "LUCCA", "num": "18514"}, {"ora": 8, "min": 51, "dir": "PISA", "num": "18511"},
    {"ora": 9, "min": 23, "dir": "LUCCA", "num": "18516"}, {"ora": 9, "min": 51, "dir": "PISA", "num": "18515"},
    {"ora": 10, "min": 23, "dir": "LUCCA", "num": "18518"}, {"ora": 10, "min": 51, "dir": "PISA", "num": "18517"},
    {"ora": 11, "min": 23, "dir": "LUCCA", "num": "18520"}, {"ora": 11, "min": 51, "dir": "PISA", "num": "18519"},
    {"ora": 12, "min": 23, "dir": "LUCCA", "num": "18522"}, {"ora": 12, "min": 43, "dir": "PISA", "num": "18521"},
    {"ora": 13, "min": 13, "dir": "LUCCA", "num": "18524"}, {"ora": 13, "min": 36, "dir": "PISA", "num": "18523"},
    {"ora": 13, "min": 53, "dir": "LUCCA", "num": "18526"}, {"ora": 14, "min": 13, "dir": "PISA", "num": "18525"},
    {"ora": 14, "min": 35, "dir": "LUCCA", "num": "18528"}, {"ora": 14, "min": 51, "dir": "PISA", "num": "18527"},
    {"ora": 15, "min": 23, "dir": "LUCCA", "num": "18532"}, {"ora": 15, "min": 51, "dir": "PISA", "num": "18531"},
    {"ora": 16, "min": 23, "dir": "LUCCA", "num": "18534"}, {"ora": 16, "min": 51, "dir": "PISA", "num": "18533"},
    {"ora": 17, "min": 23, "dir": "LUCCA", "num": "18536"}, {"ora": 17, "min": 46, "dir": "PISA", "num": "18535"},
    {"ora": 18, "min": 23, "dir": "LUCCA", "num": "18540"}, {"ora": 18, "min": 51, "dir": "PISA", "num": "18537"},
    {"ora": 19, "min": 23, "dir": "LUCCA", "num": "18542"}, {"ora": 19, "min": 51, "dir": "PISA", "num": "18541"},
    {"ora": 20, "min": 23, "dir": "LUCCA", "num": "18544"}, {"ora": 20, "min": 46, "dir": "PISA", "num": "18543"},
    {"ora": 21, "min": 23, "dir": "LUCCA", "num": "18546"}, {"ora": 21, "min": 58, "dir": "PISA", "num": "18545"}
]

@st.cache_data(ttl=10)
def recupera_treni_reali():
    treni_attivi = []
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
                        "ora_p": h, "min_p": m, "ritardo": int(ritardo), "direzione": "PISA", "num": t.get('numeroTreno'),
                        "info": f"➔ **REG {t.get('numeroTreno')}** per {t.get('destinazione')}", "fonte": "LIVE"
                    })
    except: pass

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
                        "ora_p": h, "min_p": m, "ritardo": int(ritardo), "direzione": "LUCCA", "num": t.get('numeroTreno'),
                        "info": f"🡨 **REG {t.get('numeroTreno')}** per {t.get('destinazione')}", "fonte": "LIVE"
                    })
    except: pass
    return treni_attivi

lista_treni_fs = recupera_treni_reali()

# SE I SISTEMI LIVE SONO VUOTI, CARICA IL PROSSIMO TRENO DA ORARIO PROGRAMMATO DA ADESSO IN POI
usa_programmati_di_riserva = False
if not lista_treni_fs:
    usa_programmati_di_riserva = True
    for tp in ORARIO_PROGRAMMATO:
        min_tp = tp["ora"] * 60 + tp["min"]
        if min_tp > minuti_assoluti_ora:
            freccia = "➔" if tp["dir"] == "PISA" else "🡨"
            lista_treni_fs.append({
                "ora_p": tp["ora"], "min_p": tp["min"], "ritardo": 0, "direzione": tp["dir"], "num": tp["num"],
                "info": f"{freccia} **REG {tp['num']}** (Orario Programmato)", "fonte": "TABELLA"
            })

ritardo_rilevato_linea = False
minuti_estensione_blocco = 0
for t in lista_treni_fs:
    if t.get("fonte") == "LIVE" and t.get("ritardo", 0) >= 4:
        ritardo_rilevato_linea = True
        minuti_estensione_blocco = min(t["ritardo"], 12)

prossimo_treno_testo = ""
treni_futuri = []
for t in lista_treni_fs:
    min_ass_treno = t["ora_p"] * 60 + t["min_p"] + t["ritardo"]
    if min_ass_treno > minuti_assoluti_ora:
        treni_futuri.append((min_ass_treno, t))

if treni_futuri:
    _, prox = min(treni_futuri, key=lambda x: x[0])
    min_totale = prox["ora_p"] * 60 + prox["min_p"] + prox["ritardo"]
    stringa_ora = f"{min_totale // 60:02d}:{min_totale % 60:02d}"
    
    if prox.get("fonte") == "LIVE":
        nota_ritardo = f" (+{prox['ritardo']} min ritardo)" if prox['ritardo'] > 0 else " (In orario)"
    else:
        nota_ritardo = " (Da orario ufficiale)"
        
    dir_t = "direzione Pisa" if prox["direzione"] == "PISA" else "direzione Lucca"
    prossimo_treno_testo = f"Prossimo treno previsto: **REG N. {prox['num']}** ({dir_t}) alle **{stringa_ora}**{nota_ritardo}"
else:
    if ora_adesso.hour >= 22 or ora_adesso.hour < 5:
        prossimo_treno_testo = "Servizio giornaliero terminato. 🌅 Primo treno della mattina: **REG delle 05:30 per Lucca** / **05:51 per Pisa**."
    else:
        prossimo_treno_testo = "Nessun transito pianificato nelle prossime ore."

st.info(f"📋 **STATO LINEA LIVE:** {prossimo_treno_testo}")
st.caption("ℹ️ **Nota sul traffico merci:** I sistemi pubblici monitorano esclusivamente i treni passeggeri. I transiti di treni merci e convogli straordinari non sono programmati e potrebbero causare chiusure estemporanee non segnalate dall'app.")

if ritardo_rilevato_linea:
    st.warning("⚠️ **ANOMALIA TRAFFICO LIVE:** Rilevato rallentamento dinamico sulla tratta. I passaggi a livello potrebbero rimanere chiusi più a lungo per possibili incroci o treni merci non in orario.")

st.markdown("---")
st.caption("✨ IN COLLABORAZIONE
