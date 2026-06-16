import streamlit as st
import datetime, pytz, requests

st.set_page_config(page_title="BinarioLibero", layout="centered")

st.markdown("""<style>
    .stApp { background-color: #0f172a !important; color: #ffffff !important; }
    h1, h2, h3, h4, p, span, div, li { color: #ffffff !important; }
    .stAlert p { color: #ffffff !important; }
    .stButton>button, .stLinkButton>a { background-color: #1e293b !important; color: #ffffff !important; border: 1px solid #475569 !important; text-align: center !important; }
</style>""", unsafe_allow_html=True)

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
if st.button("🔄 Aggiorna"): st.rerun()

try: ora_adesso = datetime.datetime.now(pytz.timezone('Europe/Rome'))
except: ora_adesso = datetime.datetime.now()

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
                    rit = max(0, int(t.get('ritardo', 0) or 0))
                    treni.append({"ora_p": h, "min_p": m, "ritardo": rit, "direzione": d_name, "num": t.get('numeroTreno'), "live": True})
    except: pass
    if not treni:
        for o, m, d, n in ORARI:
            if (o * 60 + m) > min_ora: treni.append({"ora_p": o, "min_p": m, "ritardo": 0, "direzione": d, "num": n, "live": False})
    return treni

lista_treni = prendi_treni()
ritardi = [t["ritardo"] for t in lista_treni if t["live"]]
est = min(max(ritardi), 12) if (ritardi and max(ritardi) >= 4) else 0

treni_futuri = []
for t in lista_treni:
    mt = t["ora_p"] * 60 + t["min_p"] + t["ritardo"]
    if (mt + 15) > min_ora: treni_futuri.append((mt, t))

if treni_futuri:
    _, prox = min(treni_futuri, key=lambda x: x[0])
    h_vis = prox["ora_p"] * 60 + prox["min_p"] + prox["ritardo"]
    st.info(f"📋 PROSSIMO TRENO: REG {prox['num']} ({prox['direzione']}) alle {h_vis//60:02d}:{h_vis%60:02d}")
else: st.info("📋 Servizio terminato.")

st.markdown("---")
st.write("### 🤝 I nostri Sponsor")
c1, c2, c3 = st.columns(3)
with c1: st.write("**Il Cappellaio Matto** 🎩\nPisa\n[Pagina FB](https://www.facebook.com/ilcappellaiomattopisa)")
with c2: st.write("**Spazio Libero** 🤝\nContattaci subito")
with c3: st.write("**Spazio Libero** 🤝\nContattaci subito")

st.write("")
st.link_button("💬 CLICCA QUI PER INFO PUBBLICITÀ (WHATSAPP)", "https://wa.me/393920275026?text=Ciao!%20Vorrei%20informazioni%20per%20lo%20sponsor")

st.markdown("---")
st.write("### 🚊 STATO VARCHI")
VARCHI = [("San Giuliano Terme", -13, 16, -3, 8), ("Via Ulisse Dini (Gello)", -15, 18, -1, 8), ("Via XXIV Maggio (Pisa)", -17, 20, 1, 8), ("Via di Gagno (Pisa)", -17, 20, 1, 8), ("Via Ugo Rindi (Pisa)", -18, 21, 2, 8)]

for nom, p_ant, p_dur, l_ant, l_dur in VARCHI:
    chiuso, msg, fut = False, "", []
    for mt, tr in treni_futuri:
        ini = (mt + p_ant) if tr["direzione"] == "LUCCA" else (mt + l_ant)
        fin = ini + (p_dur if tr["direzione"] == "LUCCA" else l_dur) + est
        if ini <= min_ora <= fin:
            chiuso = True
            msg = f"🛑 CHIUSO | Fino alle {fin//60:02d}:{fin%60:02d} (Treno dir. {tr['direzione']})"
            break
        if ini > min_ora: fut.append((ini, tr["direzione"]))
            
    if not chiuso:
        if fut:
            p_ch, dr = min(fut, key=lambda x: x[0])
            msg = f"🟢 APERTO | Preavviso: {p_ch//60:02d}:{p_ch%60:02d} ({p_ch - min_ora} min - Dir. {dr})"
        else: msg = "🟢 APERTO | Nessun transito"

    if chiuso: st.error(f"#### {nom}\n{msg}")
    else: st.success(f"#### {nom}\n{msg}")

st.markdown("---")
st.link_button("☕ Offri un caffè al server", "https://www.paypal.com/paypalme/rebolo73")
st.write("© 2026 BinarioLibero")
