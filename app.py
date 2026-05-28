import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Monitor PL Pisa-Lucca", layout="centered")

st.markdown("""
    <style>
    .pl-box { padding: 15px; border-radius: 10px; margin-bottom: 10px; color: white; font-weight: bold; }
    .aperto { background-color: #2e7d32; border-left: 8px solid #1b5e20; }
    .chiuso { background-color: #c62828; border-left: 8px solid #b71c1c; }
    .avviso { background-color: #ef6c00; border-left: 8px solid #e65100; }
    .freccia { text-align: center; font-size: 20px; color: #888; margin: 2px 0; }
    </style>
""", unsafe_allow_html=True)

PL_CONFIG = [
    {"nome": "San Giuliano Terme", "da_san_rossore": 7, "da_san_giuliano": 0},
    {"nome": "Via Ulisse Dini (Gello)", "da_san_rossore": 5, "da_san_giuliano": 2},
    {"nome": "Via di Gagno (Pisa)", "da_san_rossore": 2, "da_san_giuliano": 5},
    {"nome": "Via Ugo Rindi (Pisa)", "da_san_rossore": 1, "da_san_giuliano": 7}
]

STAZIONI = {"PISA_SR": "S00288", "SAN_GIULIANO": "S00216"}

def ottieni_treni_live(id_stazione):
    ora_ora = datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT+0200")
    url = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoMeteo/{id_stazione}/{ora_ora}"
    try:
        risposta = requests.get(url, timeout=4)
        if risposta.status_code == 200:
            return risposta.json().get('partenze', [])
    except:
        pass
    return []

st.title("Monitor Passaggi a Livello Live")
st.subheader("Tratta: San Giuliano Terme <-> Pisa S. Rossore")

if st.button("Aggiorna Stato Ora"):
    st.rerun()

ora_attuale = datetime.now()
st.write(f"Ultimo aggiornamento: **{ora_attuale.strftime('%H:%M:%S')}**")
st.write("---")

stato_pl_report = {pl["nome"]: {"stato": "APERTO", "classe": "aperto", "info": "Strada libera"} for pl in PL_CONFIG}

with st.spinner("Connessione ai server ferroviari..."):
    treni_da_pisa = ottieni_treni_live(STAZIONI["PISA_SR"])
    treni_da_lucca = ottieni_treni_live(STAZIONI["SAN_GIULIANO"])

for treno in treni_da_pisa[:2]:
    if treno.get('orarioPartenza'):
        try:
            ora_t = datetime.strptime(treno['orarioPartenza'], "%H:%M").replace(year=ora_attuale.year, month=ora_attuale.month, day=ora_attuale.day)
            ora_partenza_effettiva = ora_t + timedelta(minutes=treno.get('ritardo', 0))
            for pl in PL_CONFIG:
                ora_transito = ora_partenza_effettiva + timedelta(minutes=pl["da_san_rossore"])
                inizio_chiusura = ora_transito - timedelta(minutes=2)
                fine_chiusura = ora_transito + timedelta(minutes=2)
                if inizio_chiusura <= ora_attuale <= fine_chiusura:
                    stato_pl_report[pl["nome"]] = {"stato": "CHIUSO", "classe": "chiuso", "info": f"Reg. {treno['numeroTreno']} da Pisa (Ritardo: {treno.get('ritardo', 0)}m)"}
                elif ora_attuale < inizio_chiusura:
                    minuti_mancanti = int((inizio_chiusura - ora_attuale).total_seconds() / 60)
                    if minuti_mancanti <= 10 and stato_pl_report[pl["nome"]]["stato"] == "APERTO":
                        stato_pl_report[pl["nome"]] = {"stato": "IN CHIUSURA", "classe": "avviso", "info": f"Sbarre giu tra {minuti_mancanti} min (Reg. {treno['numeroTreno']})"}
        except:
            pass

for treno in treni_da_lucca[:2]:
    if treno.get('orarioPartenza'):
        try:
            ora_t = datetime.strptime(treno['orarioPartenza'], "%H:%M").replace(year=ora_attuale.year, month=ora_attuale.month, day=ora_attuale.day)
            ora_partenza_effettiva = ora_t + timedelta(minutes=treno.get('ritardo', 0))
            for pl in PL_CONFIG:
                ora_transito = ora_partenza_effettiva + timedelta(minutes=pl["da_san_giuliano"])
                inizio_chiusura = ora_transito - timedelta(minutes=2)
                fine_chiusura = ora_transito + timedelta(minutes=2)
                if inizio_chiusura <= ora_attuale <= fine_chiusura:
                    stato_pl_report[pl["nome"]] = {"stato": "CHIUSO", "classe": "chiuso", "info": f"Reg. {treno['numeroTreno']} da Lucca (Ritardo: {treno.get('ritardo', 0)}m)"}
                elif ora_attuale < inizio_chiusura:
                    minuti_mancanti = int((inizio_chiusura - ora_attuale).total_seconds() / 60)
                    if minuti_mancanti <= 10 and stato_pl_report[pl["nome"]]["stato"] == "APERTO":
                        stato_pl_report[pl["nome"]] = {"stato": "IN CHIUSURA", "classe": "avviso", "info": f"Sbarre giu tra {minuti_mancanti} min (Reg. {treno['numeroTreno']})"}
        except:
            pass

st.write("**[ DIREZIONE LUCCA ]**")
st.markdown('<div class="freccia">│<br>▼</div>', unsafe_allow_html=True)

for i, pl in enumerate(PL_CONFIG):
    dati = stato_pl_report[pl["nome"]]
    st.markdown(f"""
        <div class="pl-box {dati['classe']}">
            <div style="font-size: 20px;">{dati['stato']} - {pl['nome']}</div>
            <div style="font-size: 14px; font-weight: normal; opacity: 0.9;">{dati['info']}</div>
        </div>
    """, unsafe_allow_html=True)
    if i < len(PL_CONFIG) - 1:
        st.markdown('<div class="freccia">│<br>▼</div>', unsafe_allow_html=True)

st.markdown('<div class="freccia">│<br>▼</div>', unsafe_allow_html=True)
st.write("**[ DIREZIONE PISA SAN ROSSORE ]**")
