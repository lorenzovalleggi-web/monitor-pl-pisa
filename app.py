import streamlit as st
import datetime, pytz, requests, os
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="BinarioLibero Pisa",
    page_icon="🚦",
    layout="centered"
)

try:
    st_autorefresh(interval=15000, key="datarefresh")
except:
    pass

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: #f8fafc; }
    h1, h2, h3, h4, p, span, div { color: #f8fafc !important; }
    a { color: #38bdf8 !important; text-decoration: underline; }
    .stAlert { border-radius: 12px !important; border: none !important; box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important; }
    .stButton>button { background-color: #334155 !important; color: white !important; border-radius: 8px !important; width: 100%; }
    .sponsor-box { background-color: #1e293b; border: 1px dashed #475569; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 10px; color: #94a3b8 !important; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ BinarioLibero")
st.subheader("Meteo passaggi a livello: Pisa - San Giuliano")

if st.button("🔄 Aggiorna Stato In Tempo Reale"):
    st.rerun()

try:
    fuso = pytz.timezone('Europe/Rome')
    ora_adesso = datetime.datetime.now(fuso)
except:
    ora_adesso = datetime.datetime.now()

st.write(f"Ultimo controllo: **{ora_adesso.strftime('%H:%M:%S')}**")
minuti_ora = ora_adesso.hour * 60 + ora_adesso.minute

# Orari scritti in modo ultracompatto contro i tagli di riga
ORARIO_TABELLA = [
    {"ora": 5, "min": 30, "dir": "LUCCA", "num": "18502"},
    {"ora": 5, "min": 51, "dir": "PISA", "num": "18501"},
    {"ora": 6, "min": 23, "dir": "LUCCA", "num": "18504"},
    {"ora": 6, "min": 35, "dir": "PISA", "num": "18503"},
    {"ora": 6, "min": 54, "dir": "LUCCA", "num": "18506"},
    {"ora": 7, "min": 17, "dir": "PISA", "num": "6915"},
    {"ora": 7, "min": 30, "dir": "LUCCA", "num": "18508"},
    {"ora": 7, "min": 47, "dir": "PISA", "num": "18505"},
    {"ora": 8, "min": 23, "dir": "LUCCA", "num": "18514"},
    {"ora": 8, "min": 51, "dir": "PISA", "num": "18511"},
    {"ora": 9, "min": 23, "dir": "LUCCA", "num": "18516"},
    {"ora": 9, "min": 51, "dir": "PISA", "num": "18515"},
    {"ora": 10, "min": 23, "dir": "LUCCA", "num": "18518"},
    {"ora": 10, "min": 51, "dir": "PISA", "num": "18517"},
    {"ora": 11, "min": 23, "dir": "LUCCA", "num": "18520"},
    {"ora": 11, "min": 51, "dir": "PISA", "num": "18519"},
    {"ora": 12, "min": 23, "dir": "LUCCA", "num": "18522"},
    {"ora": 12, "min": 43, "dir": "PISA", "num": "18521"},
    {"ora": 13, "min": 13, "dir": "LUCCA", "num": "18524"},
    {"ora": 13, "min": 36, "dir": "PISA", "num": "18523"},
    {"ora": 13, "min": 53, "dir": "LUCCA", "num": "18526"},
    {"ora": 14, "min": 13, "dir": "PISA", "num": "18525"},
    {"ora": 14, "min": 35, "dir": "LUCCA", "num": "18528"},
    {"ora": 14, "min": 43, "dir": "PISA", "num": "18527"},
    {"ora": 15, "min": 23, "dir": "LUCCA", "num": "18532"},
    {"ora": 15, "min": 51, "dir": "PISA", "num": "18531"},
    {"ora": 16, "min": 23, "dir": "LUCCA", "num": "18534"},
    {"ora": 16, "min": 51, "dir": "PISA", "num": "18533"},
    {"ora": 17, "min": 23, "dir": "LUCCA", "num": "18536"},
    {"ora": 17, "min": 46, "dir": "PISA", "num": "18535"},
    {"ora": 18, "min": 23, "dir": "LUCCA", "num": "18540"},
    {"ora": 18, "min": 51, "dir": "PISA", "num": "18537"},
    {"ora": 19, "min": 23, "dir": "LUCCA", "num": "18542"},
    {"ora": 19, "min": 51, "dir": "PISA", "num": "18541"},
    {"ora": 20, "min": 23, "dir": "LUCCA", "num": "18544"},
    {"ora": 20, "min": 46, "dir": "PISA", "num": "18543"},
    {"ora": 21, "min": 23, "dir": "LUCCA", "num": "18546"},
    {"ora": 21, "min": 58, "dir": "PISA", "num": "18545"}
]

@st.cache_data(ttl=10)
def recupera_treni():
    treni = []
    try:
        dt_str = ora_adesso.strftime('%Y-%m-%dT00:00:00')
        stazioni = [
            ("S06411", "PISA", "PISA"),
            ("S06501", "LUCCA", "LUCCA")
        ]
        for v_id, d_name, f_key in stazioni:
            try:
                url = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/{v_id}/{dt_str}"
                res = requests.get(url, timeout=3).json()
                for t in res.get('tabellone', []):
                    dest = t.get('destinazione', '').upper()
                    valido = f_key in dest or ("LIVORNO" in dest and f_key == "PISA") or (("PISTOIA" in dest or "FIRENZE" in dest) and f_key == "LUCCA")
                    if valido:
                        h, m = map(int, t.get('orarioProgrammato', '').split(':'))
                        rit = t.get('ritardo', 0)
                        rit = 0 if rit in ["---", None] else int(rit)
                        treni.append({"ora_p": h, "min_p": m, "ritardo": rit, "direzione": d_name, "num": t.get('numeroTreno'), "fonte": "LIVE"})
            except: pass
    except: pass
    return treni

lista_treni = recupera_treni()

if not lista_treni:
    for tp in ORARIO_TABELLA:
        if (tp["ora"] * 60 + tp["min"]) > minuti_ora:
            lista_treni.append({"ora_p": tp["ora"], "min_p": tp["min"], "ritardo": 0, "direzione": tp["dir"], "num": tp["num"], "fonte": "TABELLA"})

ritardo_rilevato = any(t.get("fonte") == "LIVE" and t.get("ritardo", 0) >= 4 for t in lista_treni)
ritardi_live = [t.get("ritardo", 0) for t in lista_treni if t.get("fonte") == "LIVE"]
estensione = min(max(ritardi_live), 12) if (ritardo_rilevato and ritardi_live) else 0

treni_futuri = []
for t in lista_treni:
    m_p = t["ora_p"] * 60 + t["min_p"] + t["ritardo"]
    if (m_p + 15) > minuti_ora:
        treni_futuri.append((m_p, t))

if treni_futuri:
    m_tot, prox = min(treni_futuri, key=lambda x: x[0])
    h_visualizza = (prox["ora_p"] * 60 + prox["min_p"] + prox["ritardo"])
    nota = f" (+{prox['ritardo']} min)" if prox.get("fonte") == "LIVE" and prox['ritardo'] > 0 else " (Da orario)"
    freccia_info = "➡️ LUCCA" if prox['direzione'] == "LUCCA" else "⬅️ PISA"
    
    st.info(f"📋 **PROSSIMO TRENO**: REG {prox['num']} ({freccia_info}) alle **{h_visualizza // 60:02d}:{h_visualizza % 60:02d}**{nota}")
    
    minuti_mancanti = h_visualizza - minuti_ora
    if minuti_mancanti > 15:
        st.success(f"⏱️ **PREVISIONE CHIUSURA PL**: Barriere aperte. Chiusura stimata tra **{minuti_mancanti - 15} minuti**.")
    elif 0 <= minuti_mancanti <= 15:
        st.warning(f"⏳ **PREVISIONE CHIUSURA PL**: Chiusura in corso o imminente. Il treno transita/parte tra **{minuti_mancanti} minuti**.")
    else:
        st.error(f"🛑 **PREVISIONE CHIUSURA PL**: Treno attualmente sui binari. Possibili code residue.")
else:
    st.info("📋 **Servizio passeggeri terminato.**")

if ritardo_rilevato:
    st.warning("⚠️ **RALLENTAMENTI SULLA LINEA.** Chiusure prolungate.")

st.markdown("---")
st.write("### 🤝 I nostri Sponsor")
c1, c2, c3 = st.columns(3)
mail_sponsor = "mailto:info.railflow@gmail.com?subject=Richiesta%20Sponsorizzazione"

with c1:
    st.markdown('<div class="sponsor-box">Il Cappellaio Matto<br>🎩</div>', unsafe_allow_html=True)
    st.link_button("🎩 Pagina FB", "https://www.facebook.com/ilcappellaiomattopisa")
with c2:
    st.markdown('<div class="sponsor-box">Spazio Disponibile<br>🤝</div>', unsafe_allow_html=True)
    st.link_button("📢 Diventa Sponsor", mail_sponsor)
with c3:
    st.markdown('<div class="sponsor-box">Spazio Disponibile<br>🤝</div>', unsafe_allow_html=True)
    st.link_button("📢 Info Email", mail_sponsor)

st.markdown("---")
st.write("### 🚊 STATO VARCHI")

varchi = [
    {"nome": "San Giuliano Terme",     "pisa_ant": -13, "pisa_dur": 16, "luc_ant": -3, "luc_dur": 8},
    {"nome": "Via Ulisse Dini (Gello)", "pisa_ant": -15, "pisa_dur": 18, "luc_ant": -1, "luc_dur": 8},
    {"nome": "Via XXIV Maggio (Pisa)",  "pisa_ant": -17, "pisa_dur": 20, "luc_ant": 1,  "luc_dur": 8},
    {"nome": "Via di Gagno (Pisa)",     "pisa_ant": -17, "pisa_dur": 20, "luc_ant": 1,  "luc_dur": 8},
    {"nome": "Via Ugo Rindi (Pisa)",    "pisa_ant": -18, "pisa_dur": 21, "luc_ant": 2,  "luc_dur": 8}
]

for i, pl in enumerate(varchi):
    if i > 0: st.write("⬇️")
    chiuso, info_pl = False, ""
    
    for tr in lista_treni:
        m_p = tr["ora_p"] * 60 + tr["min_p"] + tr["ritardo"]
        if tr["direzione"] == "LUCCA":
            ini, fin, senso = m_p + pl["pisa_ant"], m_p + pl["pisa_ant"] + pl["pisa_dur"] + estensione, "➡️ LUCCA"
        else:
            ini, fin, senso = m_p + pl["luc_ant"], m_p + pl["luc_ant"] + pl["luc_dur"] + estensione, "⬅️ PISA"
            
        if ini <= minuti_ora <= fin:
            chiuso = True
            info_pl = f"🛑 **CHIUSO** | Fino alle: **{fin//60:02d}:{fin%60:02d}**\n\n*Direzione: {senso}*"
            break
            
    if not chiuso and treni_futuri:
        prossimi = []
        for _, tr in treni_futuri:
            m_p = tr["ora_p"] * 60 + tr["min_p"] + tr["ritardo"]
            ini_f, senso_f = (m_p + pl["pisa_ant"]) if tr["direzione"] == "LUCCA" else (m_p + pl["luc_ant"]), "➡️ LUCCA" if tr["direzione"] == "LUCCA" else "⬅️ PISA"
            if ini_f > minuti_ora: prossimi.append((ini_f, senso_f))
        
        if prossimi:
            p_ini, p_senso = min(prossimi, key=lambda x: x[0])
            info_pl = f"🟢 **APERTO** | Chiusura: **{p_ini//60:02d}:{p_ini%60:02d}**\n\n*Direzione: {p_senso}*"
        else: info_pl = "🟢 **APERTO** | Nessun transito imminente."
    elif not chiuso:
        info_pl = "🟢 **APERTO** | Fine servizio."

    if chiuso: st.error(f"#### {pl['nome']}\n{info_pl}")
    else: st.success(f"#### {pl['nome']}\n{info_pl}")

st.markdown("---")
st.markdown('<div style="text-align: center;"><a href="https://www.paypal.com/paypalme/rebolo73" target="_blank"><button style="background-color: #FF813F; color: white; border: none; padding: 12px 24px; font-weight: bold; border-radius: 8px; cursor: pointer;">☕ Offri un caffè al server</button></a></div>', unsafe_allow_html=True)
st.write("© 2026 **BinarioLibero Pisa**.")
