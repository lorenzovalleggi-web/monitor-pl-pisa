import streamlit as st
import datetime
import pytz
import requests
from streamlit_autorefresh import st_autorefresh
import os
import base64

# 1. Configurazione della pagina
st.set_page_config(page_title="Pisa ⇄ Lucca RailFlow", page_icon="🚦", layout="centered")

# --- TITOLO MODERNO ---
st.title("Pisa ⇄ Lucca RailFlow")
st.subheader("Monitoraggio predittivo barriere in tempo reale")

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
    # Controlla partenze da San Giuliano (Verso Pisa)
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

    # Controlla partenze da Pisa S. Rossore (Verso Lucca)
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

lista_treni_fs = recupera_treni_reali()

# --- DETECTOR ANOMALIE LINEA ---
ritardo_rilevato_linea = False
minuti_estensione_blocco = 0
if lista_treni_fs:
    for t in lista_treni_fs:
        if t.get("ritardo", 0) >= 4:
            ritardo_rilevato_linea = True
            minuti_estensione_blocco = min(t["ritardo"], 12)

# --- TROVA PROSSIMO TRENO ---
prossimo_treno_testo = ""
treni_futuri = []
if lista_treni_fs:
    for t in lista_treni_fs:
        min_ass_treno = t["ora_p"] * 60 + t["min_p"] + t["ritardo"]
        if min_ass_treno > minuti_assoluti_ora:
            treni_futuri.append((min_ass_treno, t))

if treni_futuri:
    _, prox = min(treni_futuri, key=lambda x: x[0])
    min_totale = prox["ora_p"] * 60 + prox["min_p"] + prox["ritardo"]
    ora_effettiva = min_totale // 60
    min_effettiva = min_totale % 60
    stringa_ora = f"{ora_effettiva:02d}:{min_effettiva:02d}"
    nota_ritardo = f" (+{prox['ritardo']} min ritardo)" if prox['ritardo'] > 0 else " (In orario)"
    prossimo_treno_testo = "Prossimo transito reale: " + prox["info"] + " alle **" + stringa_ora + "**" + nota_ritardo
else:
    if ora_adesso.hour >= 22 or ora_adesso.hour < 5:
        prossimo_treno_testo = "Servizio giornaliero terminato. 🌅 Primo treno della mattina: **REG delle 05:30 per Lucca** / **05:51 per Pisa**."
    else:
        prossimo_treno_testo = "Nessun transito imminente rilevato dai sistemi di stazione."

st.info(f"📋 **STATO LINEA LIVE:** {prossimo_treno_testo}")

# --- NOTA FISSA SUI TRENI MERCI ---
st.caption("ℹ️ **Nota sul traffico merci:** I sistemi pubblici monitorano esclusivamente i treni passeggeri. I transiti di treni merci e convogli straordinari non sono programmati e potrebbero causare chiusure estemporanee non segnalate dall'app.")

if ritardo_rilevato_linea:
    st.warning("⚠️ **ANOMALIA TRAFFICO LIVE:** Rilevato rallentamento dinamico sulla tratta. I passaggi a livello potrebbero rimanere chiusi più a lungo per possibili incroci o treni merci non in orario.")

st.markdown("---")

# --- BANNER SPONSOR DIGITALE SICURO ---
LINK_FACEBOOK = "https://www.facebook.com/ilcappellaiomatto"

if os.path.exists("sponsor.jpg"):
    # Convertiamo l'immagine locale in formato sicuro per il browser
    with open("sponsor.jpg", "rb") as img_file:
        img_encoded = base64.b64encode(img_file.read()).decode()
    
    st.markdown(f"""
        <div style="text-align: center; margin: 5px 0 20px 0; background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #eaeaea; box-shadow: 0 4px 10px rgba(0,0,0,0.03);">
            <p style="color: #777777; font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; margin: 0 0 12px 0; font-weight: bold;">In collaborazione con lo Sponsor Ufficiale</p>
            <a href="{LINK_FACEBOOK}" target="_blank" style="text-decoration: none; display: inline-block; width: 100%; max-width: 500px;">
                <img src="data:image/jpeg;base64,{img_encoded}" alt="Il Cappellaio Matto" style="width: 100%; max-width: 450px; height: auto; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.08);">
                <div style="margin-top: 10px; text-align: center;">
                    <h4 style="margin: 0; color: #111; font-size: 16px; font-weight: bold;">Il Cappellaio Matto Pisa</h4>
                    <p style="margin: 4px 0 0 0; color: #555; font-size: 12.5px; line-height: 1.4;">
                        Progetti grafici loghi per attività, gruppi stadio e associazioni.<br>
                        Personalizzazioni di ogni genere: T-shirt, felpe, k-way, tazze, cappellini e allestimenti in palloncini.
                    </p>
                </div>
            </a>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div style="text-align: center; margin: 5px 0 20px 0; padding: 15px; border-radius: 10px; border: 1px solid #eaeaea; background-color: #ffffff;">
            <p style="color: #777777; font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; font-weight: bold;">
