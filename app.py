import streamlit as st
import datetime
import pytz
import requests
from streamlit_autorefresh import st_autorefresh
import os

st.set_page_config(page_title="RailFlow", page_icon="🚦", layout="centered")
st.title("Pisa - San Giuliano RailFlow")
st.subheader("Stato passaggi a livello")

st_autorefresh(interval=15000, key="datarefresh")

if st.button("🔄 Aggiorna"):
    st.rerun()

fuso = pytz.timezone('Europe/Rome')
ora_adesso = datetime.datetime.now(fuso)
st.write(f"Aggiornato: **{ora_adesso.strftime('%H:%M:%S')}**")

minuti_ora = ora_adesso.hour * 60 + ora_adesso.minute
ID_SG = "S06411"
ID_PR = "S06501"

ORARIO_TABELLA = [
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
    {"ora": 14, "min": 35, "dir": "LUCCA", "num": "18528"}, {"ora": 14, "min": 43, "dir": "PISA", "num": "18527"},
    {"ora": 15, "min": 23, "dir": "LUCCA", "num": "18532"}, {"ora": 15, "min": 51, "dir": "PISA", "num": "18531"},
    {"ora": 16, "min": 23, "dir": "LUCCA", "num": "18534"}, {"ora": 16, "min": 51, "dir": "PISA", "num": "18533"},
    {"ora": 17, "min": 23, "dir": "LUCCA", "num": "18536"}, {"ora": 17, "min": 46, "dir": "PISA", "num": "18535"},
    {"ora": 18, "min": 23, "dir": "LUCCA", "num": "18540"}, {"ora": 18, "min": 51, "dir": "PISA", "num": "18537"},
    {"ora": 19, "min": 23, "dir": "LUCCA", "num": "18542"}, {"ora": 19, "min": 51, "dir": "PISA", "num": "18541"},
    {"ora": 20, "min": 23, "dir": "LUCCA", "num": "18544"}, {"ora": 20, "min": 46, "dir": "PISA", "num": "18543"},
    {"ora": 21, "min": 23, "dir": "LUCCA", "num": "18546"}, {"ora": 21, "min": 58, "dir": "PISA", "num": "18545"}
]

@st.cache_data(ttl=10)
def recupera_treni():
    treni = []
    try:
        url = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/{ID_SG}/{ora_adesso.strftime('%Y-%m-%dT00:00:00')}"
        res = requests.get(url, timeout=5).json()
        for t in res.get('tabellone', []):
            dest = t.get('destinazione', '').upper()
            if "PISA" in dest or "LIVORNO" in dest:
                h, m = map(int, t.get('orarioProgrammato', '').split(':'))
                rit = t.get('ritardo', 0)
                if rit == "---" or rit is None: rit = 0
                treni.append({"ora_p": h, "min_p": m, "ritardo": int(rit), "direzione": "PISA", "num": t.get('numeroTreno'), "fonte": "LIVE"})
    except: pass

    try:
        url = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/{ID_PR}/{ora_adesso.strftime('%Y-%m-%dT00:00:00')}"
        res = requests.get(url, timeout=5).json()
        for t in res.get('tabellone', []):
            dest = t.get('destinazione', '').upper()
            if "LUCCA" in dest or "PISTOIA" in dest or "FIRENZE" in dest:
                h, m = map(int, t.get('orarioProgrammato', '').split(':'))
                rit = t.get('ritardo', 0)
                if rit == "---" or rit is None: rit = 0
                treni.append({"ora_p": h, "min_p": m, "ritardo": int(rit), "direzione": "LUCCA", "num": t.get('numeroTreno'), "fonte": "LIVE"})
    except: pass
    return treni

lista_treni = recupera_treni()
if not lista_treni:
    for tp in ORARIO_TABELLA:
        if (tp["ora"] * 60 + tp["min"]) > minuti_ora:
            lista_treni.append({"ora_p": tp["ora"], "min_p": tp["min"], "ritardo": 0, "direzione": tp["dir"], "num": tp["num"], "fonte": "TABELLA"})

ritardo_rilevato = False
estensione = 0
for t in lista_treni:
    if t.get("fonte") == "LIVE" and t.get("ritardo", 0) >= 4:
        ritardo_rilevato = True
        estensione = min(t["ritardo"], 12)

treni_futuri = []
for t in lista_treni:
    m_ass = t["ora_p"] * 60 + t["min_p"] + t["ritardo"]
    if m_ass > minuti_ora:
        treni_futuri.append((m_ass, t))

if treni_futuri:
    _, prox = min(treni_futuri, key=lambda x: x[0])
    m_tot = prox["ora_p"] * 60 + prox["min_p"] + prox["ritardo"]
    nota = f" (+{prox['ritardo']} min)" if prox.get("fonte") == "LIVE" and prox['ritardo'] > 0 else " (Da orario)"
    dir_t = "Pisa" if prox["direzione"] == "PISA" else "Lucca"
    txt_treno = f"Prossimo treno: **REG N. {prox['num']}** dir. {dir_t} alle **{m_tot // 60:02d}:{m_tot % 60:02d}**{nota}"
else:
    txt_treno = "Servizio terminato o nessun transito pianificato."

st.info(f"📋 {txt_treno}")
if ritardo_rilevato:
    st.warning("⚠️ Rallentamenti sulla linea. Chiusure prolungate.")

st.markdown("---")
c1, c2, c3 = st.columns(3)
with c1:
    if os.path.exists("sponsor1.jpg"): st.image("sponsor1.jpg", use_container_width=True)
    st.markdown("[Il Cappellaio Matto](https://www.facebook.com/ilcappellaiomatto)")
with c2:
    if os.path.exists("sponsor2.jpg"): st.image("sponsor2.jpg", use_container_width=True)
    st.markdown("[Sponsor 2]")
with c3:
    if os.path.exists("sponsor3.jpg"): st.image("sponsor3.jpg", use_container_width=True)
    st.markdown("[Sponsor 3]")

st.link_button("📩 Diventa Sponsor", "mailto:info.railflow@gmail.com?subject=Sponsor")
st.markdown("---")
st.write("### 🚊 STATO VARCHI")

varchi = [
    {"nome": "San Giuliano Terme", "pisa": 0, "lucca": 4},
    {"nome": "Via Ulisse Dini (Gello)", "pisa": 2, "lucca": 3},
    {"nome": "Via di Gagno (Pisa)", "pisa": 5, "lucca": 2},
    {"nome": "Via Ugo Rindi (Pisa)", "pisa": 7, "lucca": 0}
]

for i, pl in enumerate(varchi):
    if i > 0: 
        st.write("⬇️")
    
    chiuso = False
    info_pl = "Strada libera"
    
    for tr in lista_treni:
        m_p = tr["ora_p"] * 60 + tr["min_p"] + tr["ritardo"]
        durata = 10 if tr["ora_p"] == 21 and tr["min_p"] == 58 else 6
        
        if tr["direzione"] == "PISA":
            ini = m_p - 6 + pl["pisa"]
            fin = m_p + durata + 1 + estensione
            if ini <= minuti_ora <= fin:
                chiuso = True
                info_pl = f"REG {tr['num']} ⏱️ {ini//60:02d}:{ini%60:02d} - {fin//60:02d}:{fin%60:02d}"
                break
        elif tr["direzione"] == "LUCCA":
            ini = m_p - 6 + pl["lucca"]
            fin = m_p + 5 + 2 + estensione
            if ini <= minuti_ora <= fin:
                chiuso = True
                info_pl = f"REG {tr['num']} ⏱️ {ini//60:02d}:{ini%60:02d} - {fin//60:02d}:{fin%60:02d}"
                break
                
    if not chiuso and treni_futuri:
        _, p_tr = min(treni_futuri, key=lambda x: x[0])
        info_pl = f"Libero. Prossimo treno REG {p_tr['num']} alle ore {p_tr['ora_p']:02d}:{p_tr['min_p']:02d}"

    if chiuso: 
        st.error(f"🔴 **CHIUSO**
