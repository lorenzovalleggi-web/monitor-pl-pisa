import streamlit as st
import datetime
import pytz
import requests
from streamlit_autorefresh import st_autorefresh
import os

st.set_page_config(page_title="RailFlow", page_icon="🚦", layout="centered")

st.title("Pisa ⇄ San Giuliano Terme RailFlow")
st.subheader("Stato varchi in tempo reale")

st_autorefresh(interval=15000, key="datarefresh")

if st.button("🔄 Aggiorna"):
    st.rerun()

fuso = pytz.timezone('Europe/Rome')
ora_adesso = datetime.datetime.now(fuso)
st.write(f"Ultimo aggiornamento: **{ora_adesso.strftime('%H:%M:%S')}**")

minuti_assoluti_ora = ora_adesso.hour * 60 + ora_adesso.minute
ID_SG = "S06411"
ID_PR = "S06501"

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
                treni.append({"ora_p": h, "min_p": m, "ritardo": int(rit), "direzione": "PISA", "info": f"➔ **REG {t.get('numeroTreno')}**"})
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
                treni.append({"ora_p": h, "min_p": m, "ritardo": int(rit), "direzione": "LUCCA", "info": f"🡨 **REG {t.get('numeroTreno')}**"})
    except: pass
    return treni

lista_treni_fs = recupera_treni()
minuti_estensione_blocco = 0
if lista_treni_fs:
    for t in lista_treni_fs:
        if t.get("ritardo", 0) >= 4:
            minuti_estensione_blocco = min(t["ritardo"], 12)

prossimo_treno_testo = ""
treni_futuri = []
if lista_treni_fs:
    for t in lista_treni_fs:
        min_ass = t["ora_p"] * 60 + t["min_p"] + t["ritardo"]
        if min_ass > minuti_assoluti_ora:
            treni_futuri.append((min_ass, t))

if treni_futuri:
    _, prox = min(treni_futuri, key=lambda x: x[0])
    m_tot = prox["ora_p"] * 60 + prox["min_p"] + prox["ritardo"]
    prossimo_treno_testo = f"Prossimo: {prox['info']} alle **{m_tot // 60:02d}:{m_tot % 60:02d}**"
else:
    prossimo_treno_testo = "Nessun transito imminente rilevato."

st.info(f"📋 {prossimo_treno_testo}")
st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    if os.path.exists("sponsor1.jpg"): st.image("sponsor1.jpg", use_container_width=True)
    st.markdown("**[Il Cappellaio Matto](https://www.facebook.com/ilcappellaiomatto)**")
with col2:
    if os.path.exists("sponsor2.jpg"): st.image("sponsor2.jpg", use_container_width=True)
    st.markdown("**[Sponsor 2]**")
with col3:
    if os.path.exists("sponsor3.jpg"): st.image("sponsor3.jpg", use_container_width=True)
    st.markdown("**[Sponsor 3]**")

st.link_button("📩 Diventa Sponsor", "mailto:info.railflow@gmail.com?subject=Sponsor")
st.markdown("---")

pl_lista = [
    {"nome": "San Giuliano Terme", "ind_pisa": 0, "ind_lucca": 4},
    {"nome": "Via Ulisse Dini (Gello)", "ind_pisa": 2, "ind_lucca": 3},
    {"nome": "Via di Gagno (Pisa)", "ind_pisa": 5, "ind_lucca": 2},
    {"nome": "Via Ugo Rindi (Pisa)", "ind_pisa": 7, "ind_lucca": 0}
]

for i, pl in enumerate(pl_lista):
    if i > 0: st.write("### :arrow_down:")
    chiuso = False
    info = "Strada libera"
    if lista_treni_fs:
        for tr in lista_treni_fs:
            m_p = tr["ora_p"] * 60 + tr["min_p"] + tr["ritardo"]
            durata = 10 if (tr["ora_p"] == 21 and tr["min_p"] == 58) else 6
            if tr["direzione"] == "PISA":
                ini = m_p - 6 + pl["ind_pisa"]
                fin = m_p + durata + 1 + minuti_estensione_blocco
                if ini <= minuti_assoluti_ora <= fin:
                    chiuso = True
                    info = f"{tr['info']} ⏱️ {ini//60:02d}:{ini%60:02d} ↔ {fin//60:02d}:{fin%60:02d}"
                    break
            elif tr["direzione"] == "LUCCA":
                ini = m_p - 6 + pl["ind_lucca"]
                fin = m_p + 5 + 2 + minuti_estensione_blocco
                if ini <= minuti_assoluti_ora <= fin:
                    chiuso = True
                    info = f"{tr['info']} ⏱️ {ini//60:02d}:{ini%60:02d} ↔ {fin//60:02d}:{fin%60:02d}"
                    break
    if chiuso: st.error(f"🔴 **CHIUSO** - {pl['nome']}\n\n{info}")
    else: st.success(f"🟢 **APERTO** - {pl['nome']}\n\n{info}")

st.markdown("---")
st.markdown('<div style="text-align: center;"><a href="https://www.paypal.com/paypalme/rebolo73" target="_blank"><button style="background-color: #FF813F; color: white; border: none; padding: 10px 20px; font-weight: bold; border-radius: 8px; cursor: pointer;">☕ Offrimi un caffè (PayPal)</button></a></div>', unsafe_allow_html=True)
st.write("© 2026 RailFlow. [info.railflow@gmail.com](mailto:info.railflow@gmail.com)")
