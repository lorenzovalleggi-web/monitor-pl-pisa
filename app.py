import streamlit as st
import datetime, pytz, requests, os
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="BinarioLibero Pisa", page_icon="🚦", layout="centered")
st.title("⚡ BinarioLibero")
st.subheader("Meteo passaggi a livello: Pisa - San Giuliano")
st_autorefresh(interval=15000, key="datarefresh")

if st.button("🔄 Aggiorna"):
    st.rerun()

fuso = pytz.timezone('Europe/Rome')
ora_adesso = datetime.datetime.now(fuso)
st.write(f"Aggiornato: **{ora_adesso.strftime('%H:%M:%S')}**")
minuti_ora = ora_adesso.hour * 60 + ora_adesso.minute

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
    dt_str = ora_adesso.strftime('%Y-%m-%dT00:00:00')
    for v_id, d_name, f_key in [("S06411", "PISA", "PISA"), ("S06501", "LUCCA", "LUCCA")]:
        try:
            res = requests.get(f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/{v_id}/{dt_str}", timeout=5).json()
            for t in res.get('tabellone', []):
                dest = t.get('destinazione', '').upper()
                if f_key in dest or ("LIVORNO" in dest and f_key == "PISA") or (("PISTOIA" in dest or "FIRENZE" in dest) and f_key == "LUCCA"):
                    h, m = map(int, t.get('orarioProgrammato', '').split(':'))
                    rit = t.get('ritardo', 0)
                    rit = 0 if rit in ["---", None] else int(rit)
                    treni.append({"ora_p": h, "min_p": m, "ritardo": rit, "direzione": d_name, "num": t.get('numeroTreno'), "fonte": "LIVE"})
        except: pass
    return treni

lista_treni = recupera_treni()
if not lista_treni:
    for tp in ORARIO_TABELLA:
        if (tp["ora"] * 60 + tp["min"]) > minuti_ora:
            lista_treni.append({"ora_p": tp["ora"], "min_p": tp["min"], "ritardo": 0, "direzione": tp["dir"], "num": tp["num"], "fonte": "TABELLA"})

ritardo_rilevato = any(t.get("fonte") == "LIVE" and t.get("ritardo", 0) >= 4 for t in lista_treni)
estensione = min(max([t.get("ritardo", 0) for t in lista_treni if t.get("fonte") == "LIVE"] + [0]), 12) if ritardo_rilevato else 0

treni_futuri = []
for t in lista_treni:
    m_p = t["ora_p"] * 60 + t["min_p"] + t["ritardo"]
    m_riferimento = (m_p - 3) if t["direzione"] == "LUCCA" else (m_p + 6)
    if m_riferimento > minuti_ora:
        treni_futuri.append((m_riferimento, t))

if treni_futuri:
    m_tot, prox = min(treni_futuri, key=lambda x: x[0])
    h_visualizza = (prox["ora_p"] * 60 + prox["min_p"] + prox["ritardo"])
    nota = f" (+{prox['ritardo']} min)" if prox.get("fonte") == "LIVE" and prox['ritardo'] > 0 else " (Da orario)"
    freccia_info = "➡️ LUCCA" if prox['direzione'] == "LUCCA" else "⬅️ PISA"
    st.info(f"📋 Prossimo treno: **REG N. {prox['num']}** ({freccia_info}) previsto alle **{h_visualizza // 60:02d}:{h_visualizza % 60:02d}**{nota}\n\n*⚠️ Nota: Eventuali transiti di treni merci o di manutenzione non sono tracciati.*")
else:
    st.info("""📋 Servizio passeggeri terminato o nessun transito imminente.

*⚠️ Nota: I passaggi a livello potrebbero chiudersi fuori orario per transiti straordinari di treni merci o di manutenzione.*""")

if ritardo_rilevato:
    st.warning("⚠️ Rallentamenti sulla linea. Chiusure prolungate.")

st.markdown("---")
c1, c2, c3 = st.columns(3)
mail_sponsor = "mailto:info.railflow@gmail.com?subject=Richiesta%20Sponsorizzazione"

with c1:
    if os.path.exists("sponsor1.jpg"): st.image("sponsor1.jpg", use_container_width=True)
    st.link_button("🎩 Il Cappellaio Matto", "https://www.facebook.com/ilcappellaiomattopisa")
with c2:
    if os.path.exists("sponsor2.jpg"): st.image("sponsor2.jpg", use_container_width=True)
    st.link_button("🤝 Spazio Libero", mail_sponsor)
with c3:
    if os.path.exists("sponsor3.jpg"): st.image("sponsor3.jpg", use_container_width=True)
    st.link_button("🤝 Spazio Libero", mail_sponsor)

st.markdown("---")
st.link_button("📩 Diventa Sponsor", mail_sponsor)
st.markdown("---")
st.write("### 🚊 STATO VARCHI")

varchi = [
    {"nome": "San Giuliano Terme",     "pisa_ant": 2, "pisa_dur": 4, "luc_ant": 6,  "luc_dur": 4},
    {"nome": "Via Ulisse Dini (Gello)", "pisa_ant": 0, "pisa_dur": 4, "luc_ant": 8,  "luc_dur": 4},
    {"nome": "Via XXIV Maggio (Pisa)",  "pisa_ant": -2, "pisa_dur": 4, "luc_ant": 10, "luc_dur": 4},
    {"nome": "Via di Gagno (Pisa)",     "pisa_ant": -2, "pisa_dur": 4, "luc_ant": 10, "luc_dur": 4},
    {"nome": "Via Ugo Rindi (Pisa)",    "pisa_ant": -3, "pisa_dur": 4, "luc_ant": 11, "luc_dur": 4}
]

for i, pl in enumerate(varchi):
    if i > 0: st.write("⬇️")
    chiuso, info_pl = False, ""
    
    for tr in lista_treni:
        m_p = tr["ora_p"] * 60 + tr["min_p"] + tr["ritardo"]
        if tr["direzione"] == "LUCCA":
            ini = m_p + pl["pisa_ant"]
            fin = ini + pl["pisa_dur"] + estensione
            senso = "➡️ LUCCA"
        else:
            ini = m_p + pl["luc_ant"]
            fin = ini + pl["luc_dur"] + estensione
            senso = "⬅️ PISA"
            
        if ini <= minuti_ora <= fin:
            t_ini = f"{ini//60:02d}:{ini%60:02d}"
            t_fin = f"{fin//60:02d}:{fin%60:02d}"
            chiuso = True
            info_pl = f"🛑 **CHIUSO** | Inizio: **{t_ini}** ➡️ Riapertura prevista: **{t_fin}**\n\n*Senso di marcia: {senso} (REG {tr['num']})*"
            break
            
    if not chiuso and treni_futuri:
        prossimi_blocchi = []
        for _, tr in treni_futuri:
            m_p = tr["ora_p"] * 60 + tr["min_p"] + tr["ritardo"]
            if tr["direzione"] == "LUCCA":
                ini = m_p + pl["pisa_ant"]
                fin = ini + pl["pisa_dur"] + estensione
                senso = "➡️ LUCCA"
            else:
                ini = m_p + pl["luc_ant"]
                fin = ini + pl["luc_dur"] + estensione
                senso = "⬅️ PISA"
            if ini > minuti_ora:
                prossimi_blocchi.append((ini, fin, tr["num"], senso))
        
        if prossimi_blocchi:
            p_ini, p_fin, p_num, p_senso = min(prossimi_blocchi, key=lambda x: x[0])
            t_ini = f"{p_ini//60:02d}:{p_ini%60:02d}"
            t_fin = f"{p_fin//60:02d}:{p_fin%60:02d}"
            info_pl = f"🟢 **APERTO** | Prossima chiusura: **{t_ini}** (Riapre alle **{t_fin}**)\n\n*Senso di marcia previsto: {p_senso} (REG {p_num})*"
        else:
            info_pl = "🟢 **APERTO** | Nessun transito imminente rilevato."
            
    elif not chiuso and not treni_futuri:
        info_pl = "🟢 **APERTO** | Servizio passeggeri terminato."

    if chiuso: 
        st.error(f"### {pl['nome']}\n{info_pl}")
    else: 
        st.success(f"### {pl['nome']}\n{info_pl}")

# --- SEZIONE DONAZIONI AGGIORNATA ED EMOTIVA ---
st.markdown("---")
with st.container():
    st.write("### ☕ Sostieni BinarioLibero")
    st.write(
        "BinarioLibero è un servizio indipendente, gratuito e privo di pubblicità invasiva. "
        "L'infrastruttura richiede costi vivi mensili per server, traffico dati e interrogazione in tempo reale dei sistemi ferroviari. "
        "Se l'applicazione ti ha aiutato a evitare una coda e a risparmiare tempo prezioso, considera una piccola donazione libera per mantenerla attiva!"
    )
    
    # Pulsante centrato e accattivante
    st.markdown(
        '<div style="text-align: center; margin-top: 15px; margin-bottom: 15px;">'
        '<a href="https://www.paypal.com/paypalme/rebolo73" target="_blank">'
        '<button style="background-color: #FF813F; color: white; border: none; padding: 12px 28px; '
        'font-weight: bold; border-radius: 8px; cursor: pointer; font-size: 16px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1);">'
        '☕ Offri un caffè per supportare il server'
        '</button></a></div>', 
        unsafe_allow_html=True
    )
st.markdown("---")
st.write("© 2026 BinarioLibero Pisa. info.railflow@gmail.com")
