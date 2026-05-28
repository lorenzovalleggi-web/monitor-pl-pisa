import streamlit as st
import datetime
import pytz
import requests
from streamlit_autorefresh import st_autorefresh
import os
import streamlit_analytics2 as streamlit_analytics

# 1. Configurazione della pagina
st.set_page_config(page_title="Pisa ⇄ San Giuliano Terme RailFlow", page_icon="🚦", layout="centered")

# Attiviamo il contatore di visite interno e sicuro
with streamlit_analytics.track():

    # --- TITOLO SEMPLIFICATO ---
    st.title("Pisa ⇄ San Giuliano Terme RailFlow")
    st.subheader("Stato dei passaggi a livello in tempo reale")

    # Aggiornamento automatico ogni 15 secondi
    st_autorefresh(interval=15000, key="datarefresh")

    if st.button("🔄 Aggiorna Stato Ora"):
        st.rerun()

    fuso_italia = pytz.timezone('Europe/Rome')
    ora_adesso = datetime.datetime.now(fuso_italia)
    st.write(f"Ultimo aggiornamento automatico: **{ora_adesso.strftime('%H:%M:%S')}**")

    minuti_assoluti_ora = ora_adesso.hour * 60 + ora_adesso.minute

    ID_SAN_GIULIANO = "S06411"
    ID_PISA_ROSSORE = "S06501"

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
                            "ora_p": h, "min_p": m, "ritardo": int(ritardo), "direzione": "PISA",
                            "info": f"➔ **REG {t.get('numeroTreno')}** per {t.get('destinazione')}"
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
                            "ora_p": h, "min_p": m, "ritardo": int(ritardo), "direzione": "LUCCA",
                            "info": f"🡨 **REG {t.get('numeroTreno')}** per {t.get('destinazione')}"
                        })
        except: pass
        return treni_attivi

    lista_treni_fs = recupera_treni_reali()

    ritardo_rilevato_linea = False
    minuti_estensione_blocco = 0
    if lista_treni_fs:
        for t in lista_treni_fs:
            if t.get("ritardo", 0) >= 4:
                ritardo_rilevato_linea = True
                minuti_estensione_blocco = min(t["ritardo"], 12)

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
        stringa_ora = f"{min_totale // 60:02d}:{min_totale % 60:02d}"
        nota_ritardo = f" (+{prox['ritardo']} min ritardo)" if prox['ritardo'] > 0 else " (In orario)"
        prossimo_treno_testo = f"Prossimo transito reale: {prox['info']} alle **{stringa_ora}**{nota_ritardo}"
    else:
        if ora_adesso.hour >= 22 or ora_adesso.hour < 5:
            prossimo_treno_testo = "Servizio giornaliero terminato. 🌅 Primo treno della mattina: **REG delle 05:30 per Lucca** / **05:51 per Pisa**."
        else:
            prossimo_treno_testo = "Nessun transito imminente rilevato dai sistemi di stazione."

    st.info(f"📋 **STATO LINEA LIVE:** {prossimo_treno_testo}")

    st.caption("ℹ️ **Nota sul traffico merci:** I sistemi pubblici monitorano esclusivamente i treni passeggeri. I transiti di treni merci e convogli straordinari non sono programmati e potrebbero causare chiusure estemporanee non segnalate dall'app.")

    if ritardo_rilevato_linea:
        st.warning("⚠️ **ANOMALIA TRAFFICO LIVE:** Rilevato rallentamento dinamico sulla tratta. I passaggi a livello potrebbero rimanere chiusi più a lungo per possibili incroci o treni merci non in orario.")

    st.markdown("---")

    # --- SEZIONE SPONSOR MULTIPLI (IN ORIZZONTALE) ---
    st.caption("✨ IN COLLABORAZIONE CON GLI SPONSOR UFFICIALI")

    col_sp1, col_sp2, col_sp3 = st.columns(3)

    with col_sp1:
        LINK_FB1 = "https://www.facebook.com/ilcappellaiomatto"
        if os.path.exists("sponsor1.jpg"):
            st.image("sponsor1.jpg", use_container_width=True)
        st.markdown(f"**[Il Cappellaio Matto]({LINK_FB1})**")
        st.caption("Personalizzazioni, abbigliamento e grafica.")

    with
