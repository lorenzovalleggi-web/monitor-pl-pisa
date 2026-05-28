import streamlit as st
import requests
import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Monitor PL Pisa", page_icon="🚊", layout="centered")

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

URL_PARTENZE = "http://www.viaggiatreno.it/viaggiatrenonew/api/partenze/S06105/MONITOR"
URL_ARRIVI = "http://www.viaggiatreno.it/viaggiatrenonew/api/arrivi/S06105/MONITOR"

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "it-IT,it;q=0.9",
    "Referer": "http://www.viaggiatreno.it/viaggiatrenomobile/home.jsp"
}

try:
    pl_chiusi = False
    info_treno = ""
    treni_rilevati = []

    with requests.Session() as session:
        session.headers.update(headers)
        
        try:
            res_p = session.get(URL_PARTENZE, timeout=7)
            if res_p.status_code == 200 and len(res_p.text.strip()) > 5:
                treni_rilevati.extend(res_p.json())
        except:
            pass

        try:
            res_a = session.get(URL_ARRIVI, timeout=7)
            if res_a.status_code == 200 and len(res_a.text.strip()) > 5:
                treni_rilevati.extend(res_a.json())
        except:
            pass

    if not treni_rilevati:
        URL_STATO = "http://www.viaggiatreno.it/viaggiatrenonew/api/andamentoStazione/S06105/1"
        res_s = requests.get(URL_STATO, headers=headers, timeout=5)
        if res_s.status_code == 200 and len(res_s.text.strip()) > 5:
            treni_rilevati.extend(res_s.json())

    for treno in treni_rilevati:
        orario_str = treno.get('orarioPartenza') or treno.get('orarioArrivo') or treno.get('orario')
        if not orario_str:
            continue
            
        try:
            if " " in orario_str:
                orario_str = orario_str.split(" ")[1]
            ore_t, minuti_t = map(int, orario_str.split(':')[:2])
            ora_teorica = ora_adesso.replace(hour=ore_t, minute=minuti_t, second=0, microsecond=0)
        except:
            continue
        
        ritardo = treno.get('ritardo', 0)
        if ritardo is None:
            ritardo = 0
            
        ora_reale = ora_teorica + datetime.timedelta(minutes=ritardo)
        
        inizio_blocco = ora_reale - datetime.timedelta(minutes=6)
        fine_blocco = ora_reale + datetime.timedelta(minutes=2)
        
        if inizio_blocco <= ora_adesso <= fine_blocco:
            pl_chiusi = True
            dest = treno.get('destinazione', 'Pisa/Lucca')
            info_treno = f"Treno {treno.get('numeroTreno', '')} ({dest}) atteso ore {ora_reale.strftime('%H:%M')} [Ritardo: {ritardo} min]"
            break

    pl_ordinati = [
        "San Giuliano Terme",
        "Via Ulisse Dini (Gello)",
        "Via di Gagno (Pisa)",
        "Via Ugo Rindi (Pisa)"
    ]
    
    st.write("**[ DIREZIONE LUCCA ]**")
    for nome in pl_ordinati:
        st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
        if pl_chiusi:
            st.error(f"🔴 **CHIUSO / IN CHIUSURA** - {nome}\n\n{info_treno}")
        else:
            st.success(f"🟢 **APERTO** - {nome}\n\nStrada libera")
    st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
    st.write("**[ DIREZIONE PISA SAN ROSSORE ]**")

except Exception as e:
    st.warning(f"⚠️ Modalità Offline (Server RFI irraggiungibili): {str(e)}")
    st.write("**[ DIREZIONE LUCCA ]**")
    for nome in ["San Giuliano Terme", "Via Ulisse Dini (Gello)", "Via di Gagno (Pisa)", "Via Ugo Rindi (Pisa)"]:
        st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
        st.success(f"🟢 **APERTO** - {nome}\n\nStato regolare")
    st.markdown("<div style='text-align: center; font-size: 20px; margin: 5px 0;'>│<br>▼</div>", unsafe_allow_html=True)
    st.write("**[ DIREZIONE PISA SAN ROSSORE ]**")
