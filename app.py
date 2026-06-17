import streamlit as st
import datetime, pytz, requests

st.set_page_config(page_title="BinarioLibero", layout="centered")

# CSS Personalizzato per la modalità scura
st.markdown("""<style>
    .stApp { background-color: #0f172a !important; color: #ffffff !important; }
    h1, h2, h3, h4, p, span, div, li { color: #ffffff !important; }
    .stAlert p { color: #ffffff !important; }
    .stButton>button, .stLinkButton>a { background-color: #1e293b !important; color: #ffffff !important; border: 1px solid #475569 !important; width: 100% !important; text-align: center !important; }
</style>""", unsafe_allow_html=True)

# Auto-refresh invisibile (Ricarica la pagina ogni 10 secondi)
st.components.v1.html("""
    <script>
        setTimeout(function(){ window.parent.location.reload(); }, 10000);
    </script>
""", height=0, width=0)

# 1. TABELLA ORARIA VERIFICATA DA APP (Solo treni diretti 0 cambi)
ORARI_PISA = [
    (5,25), (6,13), (7,4), (7,50), (8,50), (9,3), (9,22), (9,50), (10,20), 
    (12,20), (12,50), (13,20), (13,43), (14,20), (14,50), (15,20), (15,50), 
    (16,19), (16,50), (17,20), (17,50), (18,20), (18,50), (19,20), (19,50), 
    (20,50), (21,20), (21,50)
]

ORARI_LUCCA = [
    (6,52), (7,8), (7,40), (7,53), (8,15), (9,10), (9,42), (10,12), (10,42), 
    (12,42), (13,12)
]

st.title("⚡ BinarioLibero Pisa")

# Gestione Orario Italiano
try: ora_adesso = datetime.datetime.now(pytz.timezone('Europe/Rome'))
except: ora_adesso = datetime.datetime.now()

min_ora = ora_adesso.hour * 60 + ora_adesso.minute
st.write(f"⏱️ Ora attuale: {ora_adesso.strftime('%H:%M:%S')} (Aggiornamento automatico)")

# 2. SCARICAMENTO DATI LIVE DA VIAGGIATRENO
@st.cache_data(ttl=5)
def prendi_treni():
    treni = []
    try:
        dt = ora_adesso.strftime('%Y-%m-%dT00:00:00')
        for v_id, d_name, f_key in [("S06411", "PISA", "PISA"), ("S06501", "LUCCA", "LUCCA")]:
            url = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/{v_id}/{dt}"
            res = requests.get(url, timeout=3).json().get('tabellone', [])
            for t in res:
                dest = t.get('destinazione', '').upper()
                # Filtra solo i treni della linea Pisa-Lucca escludendo Viareggio/costa
                if f_key in dest or "LIVORNO" in dest or "PISTOIA" in dest or "FIRENZE" in dest:
                    h, m = map(int, t.get('orarioProgrammato', '').split(':'))
                    rit = max(0, int(t.get('ritardo', 0) or 0))
                    treni.append({"ora_p": h, "min_p": m, "ritardo": rit, "direzione": d_name, "num": t.get('numeroTreno'), "live": True})
    except: pass
    
    # Se i server ViaggiaTreno non rispondono, usa gli orari programmati dell'app
    if not treni:
        for o, m in ORARI_PISA:
            if (o * 60 + m) > min_ora: treni.append({"ora_p": o, "min_p": m, "ritardo": 0, "direzione": "LUCCA", "num": "PROG", "live": False})
        for o, m in ORARI_LUCCA:
            if (o * 60 + m) > min_ora: treni.append({"ora_p": o, "min_p": m, "ritardo": 0, "direzione": "PISA", "num": "PROG", "live": False})
    return treni

lista_treni = prendi_treni()
ritardi = [t["ritardo"] for t in lista_treni if t["live"]]
est = min(max(ritardi), 12) if (ritardi and max(ritardi) >= 4) else 0

# Filtra i treni che passeranno nei prossimi minuti
treni_futuri = []
for t in lista_treni:
    mt = t["ora_p"] * 60 + t["min_p"] + t["ritardo"]
    if (mt + 25) > min_ora: treni_futuri.append((mt, t))

# Box prossimo treno in arrivo
if treni_futuri:
    _, prox = min(treni_futuri, key=lambda x: x[0])
    h_vis = prox["ora_p"] * 60 + prox["min_p"] + prox["ritardo"]
    st.info(f"📋 PROSSIMO TRENO: REG {prox['num']} (Dir. {prox['direzione']}) alle {h_vis//60:02d}:{h_vis%60:02d}")
else: 
    st.info("📋 Servizio terminato per oggi.")

st.markdown("---")
st.write("### 🤝 I nostri Sponsor")
c1, c2, c3 = st.columns(3)
with c1: st.write("**Il Cappellaio Matto** 🎩\nPisa\n[Pagina FB](https://www.facebook.com/ilcappellaiomattopisa)")
with c2: st.write("**Spazio Libero** 🤝\nContattaci subito")
with c3: st.write("**Spazio Libero** 🤝\nContattaci subito")

st.write("")
st.link_button("💬 CLICCA QUI PER INFO PUBBLICITÀ (WHATSAPP)", "https://wa.me/393920275026?text=Ciao!%20Vorrei%20informazioni%20per%20lo%20sponsor")

st.markdown("---")
st.write("### 🚊 STATO VARCHI (PASSAGGI A LIVELLO)")

# Configurazione millimetrica basata sui 5 minuti reali di viaggio del treno.
# Struttura: (Nome, offset_andata_minuti, durata_andata, offset_ritorno_minuti, durata_ritorno)
VARCHI_CONFIG = [
    ("Via Ugo Rindi (Pisa)", 7, 3, 17, 3),
    ("Via di Gagno (Pisa)", 7, 3, 17, 3),
    ("Via XXIV Maggio (Pisa)", 8, 3, 16, 3),
    ("Via Ulisse Dini (Gello)", 11, 3, 13, 3),
    ("San Giuliano Terme", 13, 4, 10, 3)
]

for nom, p_offset, p_dur, l_offset, l_dur in VARCHI_CONFIG:
    chiuso, msg, fut = False, "", []
    for mt, tr in treni_futuri:
        if tr["direzione"] == "LUCCA":
            ini = mt + p_offset
            fin = ini + p_dur + est
        else:
            ini = mt + l_offset
            fin = ini + l_dur + est
            
        # Controllo se il treno sta occupando il varco in questo momento
        if ini <= min_ora <= fin:
            chiuso = True
            msg = f"🛑 CHIUSO | Fino alle {fin//60:02d}:{fin%60:02d} (Treno dir. {tr['direzione']})"
            break
        if ini > min_ora: 
            fut.append((ini, tr["direzione"]))
            
    # Se non è chiuso, calcola il tempo rimanente al prossimo passaggio
    if not chiuso:
        if fut:
            p_ch, dr = min(fut, key=lambda x: x[0])
            msg = f"🟢 APERTO | Preavviso: {p_ch//60:02d}:{p_ch%60:02d} ({p_ch - min_ora} min - Dir. {dr})"
        else: 
            msg = "🟢 APERTO | Nessun transito imminente"

    if chiuso: st.error(f"#### {nom}\n{msg}")
    else: st.success(f"#### {nom}\n{msg}")

st.markdown("---")
st.link_button("☕ Offri un caffè al server", "https://www.paypal.com/paypalme/rebolo73")
st.write("© 2026 BinarioLibero")
