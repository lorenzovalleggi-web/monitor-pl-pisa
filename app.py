import streamlit as st
import datetime, pytz, requests

st.set_page_config(page_title="BinarioLibero", layout="centered")

ORARI = [
    (5,30,"LUCCA","18502"),(5,51,"PISA","18501"),(6,23,"LUCCA","18504"),(6,35,"PISA","18503"),
    (6,54,"LUCCA","18506"),(7,17,"PISA","6915"),(7,30,"LUCCA","18508"),(7,47,"PISA","18505"),
    (8,23,"LUCCA","18514"),(8,51,"PISA","18511"),(9,23,"LUCCA","18516"),(9,51,"PISA","18515"),
    (10,23,"LUCCA","18518"),(10,51,"PISA","18517"),(11,23,"LUCCA","18520"),(11,51,"PISA","18519"),
    (12,23,"LUCCA","18522"),(12,43,"PISA","18521"),(13,13,"LUCCA","18524"),(13,36,"PISA","18523"),
    (13,53,"LUCCA","18526"),(14,13,"PISA","18525"),(14,35,"LUCCA","18528"),(14,43,"PISA","18527"),
    (15,23,"LUCCA","18532"),(15,51,"PISA","18531"),(16,23,"LUCCA","18534"),(16,51,"PISA","18533"),
    (17,23,"LUCCA","18536"),(17,46,"PISA","18535"),(18,23,"LUCCA","18540"),(18,51,"PISA","18537"),
    (19,23,"LUCCA","18542"),(19,51,"PISA","18541"),(20,23,"LUCCA","18544"),(20,46,"PISA","18543"),
    (21,23,"LUCCA","18546"),(21,58,"PISA","18545")
]

st.title("⚡ BinarioLibero Pisa")
if st.button("🔄 Aggiorna"):
    st.rerun()

try:
    ora_adesso = datetime.datetime.now(pytz.timezone('Europe/Rome'))
except:
    ora_adesso = datetime.datetime.now()

min_ora = ora_adesso.hour * 60 + ora_adesso.minute
st.write(f"Ultimo controllo: {ora_adesso.strftime('%H:%M:%S')}")

@st.cache_data(ttl=15)
def prendi_treni():
    treni = []
    try:
        dt = ora_adesso.strftime('%Y-%m-%dT00:00:00')
        for v_id, d_name, f_key in [("S06411", "PISA", "PISA"), ("S06501", "LUCCA", "LUCCA")]:
            url = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/{v_id}/{dt}"
            res = requests.get(url, timeout=3).json().get('tabellone', [])
            for t in res:
                dest = t.get('destinazione', '').upper()
                if f_key in dest or "LIVORNO" in dest or "PISTOIA" in dest or "FIRENZE" in dest:
                    h, m = map(int, t.get('orarioProgrammato', '').split(':'))
                    rit = t.get('ritardo', 0)
                    rit = 0 if rit in ["---", None] else int(rit)
                    treni.append({"ora_p": h, "min_p": m, "ritardo": rit, "direzione": d_name, "num": t.get('numeroTreno'), "live": True})
    except: pass
    if not treni:
        for o, m, d, n in ORARI:
            if (o * 60 + m) > min_ora:
                treni.append({"ora_p": o, "min_p": m, "ritardo": 0, "direzione": d, "num": n, "live": False})
    return treni

lista_treni = prendi_treni()
ritardi = [t["ritardo"] for t in lista_treni if t["live"]]
estensione = min(max(ritardi), 12) if (ritardi and max(ritardi) >= 4) else 0

treni_futuri = []
for t in lista_treni:
    m_t = t["ora_p"] * 60 + t["min_p"] + t["ritardo"]
    if (m_t + 15) > min_ora:
        treni_futuri.append((m_t, t))

if treni_futuri:
    _, prox = min(treni_futuri, key=lambda x: x[0])
    h_vis = prox["ora_p"] * 60 + prox["min_p"] + prox["ritardo"]
    st.info(f"📋 PROSSIMO TRENO: REG {prox['num']} ({prox['direzione']}) alle {h_vis//60:02d}:{h_vis%60:02d}")
else:
    st.info("📋 Servizio terminato.")

# --- NUOVA SEZIONE SPONSOR COMPATTA ---
st.markdown("---")
st.write("### 🤝 I nostri Sponsor")
c1, c2, c3 = st.columns(3)
ml_sp = "mailto:info.railflow@gmail.com?subject=Sponsor"
box_html = '<div style="background:#1e293b;border:1px dashed #475569;border-radius:6px;padding:8px;text-align:center;font-size:13px;color:#94a3b8!important;">'

with c1:
    st.markdown(f'{box_html}Il Cappellaio Matto<br>🎩</div>', unsafe_allow_html=True)
    st.link_button("🎩 Pagina FB", "https://www.facebook.com/ilcappellaiomattopisa")
with c2:
    st.markdown(f'{box_html}Spazio Disponibile<br>🤝</div>', unsafe_allow_html=True)
    st.link_button("📢 Diventa Sponsor", ml_sp)
with c3:
    st.markdown(f'{box_html}Spazio Disponibile<br>🤝</div>', unsafe_allow_html=True)
    st.link_button("📢 Info Email", ml_sp)

# --- STATO VARCHI ---
st.markdown("---")
st.write("### 🚊 STATO VARCHI")
varchi = [
    {"n": "San Giuliano Terme", "p_ant": -13, "p_dur": 16, "l_ant": -3, "l_dur": 8},
    {"n": "Via Ulisse Dini (Gello)", "p_ant": -15, "p_dur": 18, "l_ant": -1, "l_dur": 8},
    {"n": "Via XXIV Maggio (Pisa)", "p_ant": -17, "p_dur": 20, "l_ant": 1, "l_dur": 8},
    {"n": "Via di Gagno (Pisa)", "p_ant": -17, "p_dur": 20, "l_ant": 1, "l_dur": 8},
    {"n": "Via Ugo Rindi (Pisa)", "p_ant": -18, "p_dur": 21, "l_ant": 2, "l_dur": 8}
]

for pl in varchi:
    chiuso, info = False, ""
    for tr in lista_treni:
        m_p = tr["ora_p"] * 60 + tr["min_p"] + tr["ritardo"]
        ini = (m_p + pl["p_ant"]) if tr["direzione"] == "LUCCA" else (m_p + pl["l_ant"])
        dur = pl["p_dur"] if tr["direzione"] == "LUCCA" else pl["l_dur"]
        fin = ini + dur + estensione
        if ini <= min_ora <= fin:
            chiuso = True
            info = f"🛑 CHIUSO | Fino alle {fin//60:02d}:{fin%60:02d}"
            break
    if not chiuso and treni_futuri:
        prossimi = []
        for _, tr in treni_futuri:
            m_p = tr["ora_p"] * 60 + tr["min_p"] + tr["ritardo"]
            ini_f = (m_p + pl["p_ant"]) if tr["direzione"] == "LUCCA" else (m_p + pl["l_ant"])
            if ini_f > min_ora: prossimi.append(ini_f)
        if prossimi:
            p_ini = min(prossimi)
            info = f"🟢 APERTO | Preavviso Chiusura: {p_ini//60:02d}:{p_ini%60:02d} (tra {p_ini - min_ora} min)"
        else: info = "🟢 APERTO | Nessun transito"
    elif not chiuso: info = "🟢 APERTO | Fine servizio"

    if chiuso: st.error(f"#### {pl['n']}\n{info}")
    else: st.success(f"#### {pl['n']}\n{info}")

# --- DONAZIONI ---
st.markdown("---")
st.markdown('<div style="text-align:center;"><a href="https://www.paypal.com/paypalme/rebolo73" target="_blank"><button style="background:#FF813F;color:white;border:none;padding:10px 20px;font-weight:bold;border-radius:6px;cursor:pointer;">☕ Offri un caffè al server</button></a></div>', unsafe_allow_html=True)
st.write("© 2026 BinarioLibero")
