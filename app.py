
import streamlit as st
from datetime import datetime, timedelta

# ==========================================
# BINARIO LIBERO
# Monitor PL sulla tratta Pisa S. Rossore ↔ San Giuliano Terme
# Auto-refresh ogni 20 secondi
# ==========================================

st.set_page_config(page_title="Binario Libero", page_icon="🚧", layout="centered")

# Auto-refresh ogni 20 secondi (affidabile in Streamlit)
st.markdown('<meta http-equiv="refresh" content="20">', unsafe_allow_html=True)

st.markdown("""
<style>
    .pl-card {
        padding: 18px;
        border-radius: 14px;
        margin-bottom: 14px;
        border: 1px solid #e9ecef;
        background: #ffffff;
    }
    .pl-name {
        font-size: 1.15rem;
        font-weight: 600;
        color: #212529;
        margin-bottom: 6px;
    }
    .stato-chiuso { color: #dc3545; font-size: 1.4rem; font-weight: 700; }
    .stato-chiude { color: #ffc107; font-size: 1.4rem; font-weight: 700; }
    .stato-aperto { color: #28a745; font-size: 1.4rem; font-weight: 700; }
    .info-row { font-size: 0.95rem; color: #495057; margin-top: 6px; }
    .totale-box {
        margin-top: 18px;
        padding: 14px;
        border-radius: 10px;
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        text-align: center;
        font-size: 1.05rem;
        font-weight: 500;
    }
    .ora-box {
        font-size: 1.3rem;
        font-weight: 600;
        text-align: center;
        padding: 10px;
        background: #212529;
        color: #fff;
        border-radius: 10px;
        margin-bottom: 12px;
    }
    .refresh-note {
        font-size: 0.8rem;
        color: #868e96;
        text-align: center;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CONFIGURAZIONE PL
# ==========================================
PL_CONFIG = {
    "Via Ugo Rindi":   {"offset_andata": 5,  "offset_ritorno": 1},
    "Via di Gagno":    {"offset_andata": 4,  "offset_ritorno": 2},
    "Via 24 Maggio":   {"offset_andata": 3,  "offset_ritorno": 3},
    "Via Ulisse Dini": {"offset_andata": 2,  "offset_ritorno": 4},
    "Via Cave":        {"offset_andata": 1,  "offset_ritorno": 5},
}

CHIUSURA_ANTICIPO = 3
APERTURA_POST = 12

# ==========================================
# ORARI REALI — ANDATA (San Giuliano Terme → Pisa S. Rossore)
# ==========================================
ORARI_ANDATA = [
    ("R 32829", "07:58"),
    ("R 34146", "08:15"),
    ("R 18556", "08:58"),
    ("R 18562", "09:58"),
    ("R 83571", "11:44"),
    ("R 18570", "13:28"),
    ("R 18490", "13:58"),
    ("R 18574", "14:27"),
    ("R 34098", "14:57"),
    ("R 18578", "15:28"),
    ("R 18494", "15:58"),
    ("R 18584", "16:27"),
    ("R 18588", "16:58"),
    ("R 18592", "17:28"),
    ("R 18594", "17:58"),
    ("R 18598", "18:29"),
    ("R 83691", "18:58"),
    ("R 18602", "19:28"),
    ("R 83663", "20:20"),
    ("R 18606", "20:58"),
    ("R 83665", "21:32"),
]

# ==========================================
# ORARI REALI — RITORNO (Pisa S. Rossore → San Giuliano Terme)
# ==========================================
ORARI_RITORNO = [
    ("R 83671", "05:31"),
    ("R 18553", "07:10"),
    ("R 83675", "07:55"),
    ("R 18555", "08:55"),
    ("R 18561", "09:55"),
    ("R 18573", "12:55"),
    ("R 18575", "13:25"),
    ("R 83679", "13:48"),
    ("R 18577", "14:24"),
    ("R 18493", "14:55"),
    ("R 18581", "15:25"),
    ("R 18583", "15:55"),
    ("R 18497", "16:23"),
    ("R 18585", "16:55"),
    ("R 18591", "17:25"),
    ("R 83681", "17:55"),
    ("R 18593", "18:25"),
    ("R 18595", "18:55"),
    ("R 83683", "19:25"),
    ("R 18597", "19:55"),
    ("R 18605", "21:55"),
]


def parse_hhmm(oggi, hhmm):
    h, m = map(int, hhmm.split(":"))
    return oggi.replace(hour=h, minute=m, second=0, microsecond=0)


def calcola_stato(transito_ora):
    now = datetime.now()
    chiusura = transito_ora - timedelta(minutes=CHIUSURA_ANTICIPO)
    apertura = transito_ora + timedelta(seconds=APERTURA_POST)

    if now < chiusura:
        sec = int((chiusura - now).total_seconds())
        if sec <= 300:
            return "chiude", f"🟡 Si chiude tra {sec//60}m {sec%60}s", chiusura, apertura
        return "aperto", "🟢 Passaggio libero", chiusura, apertura
    if chiusura <= now <= apertura:
        sec = int((apertura - now).total_seconds())
        return "chiuso", f"🔴 CHIUSO — si apre tra {sec//60}m {sec%60}s", chiusura, apertura
    return "passato", "⚫ Treno passato", chiusura, apertura


def mostra_pl(pl_name, offset, orari_list, oggi):
    st.markdown(f"<div style='font-size:1.1rem;font-weight:600;margin-top:16px;'>📍 {pl_name}</div>", unsafe_allow_html=True)
    visto = False
    for num, hhmm in orari_list:
        partenza = parse_hhmm(oggi, hhmm)
        transito = partenza + timedelta(minutes=offset)
        stato, msg, chiusura, apertura = calcola_stato(transito)
        if stato == "passato" and (datetime.now() - apertura).total_seconds() > 7200:
            continue
        visto = True
        st.markdown(f"""
        <div class="pl-card">
            <div class="pl-name">{num} — transito {transito.strftime('%H:%M')}</div>
            <div class="stato-{stato}">{msg}</div>
            <div class="info-row">⏰ Chiusura: {chiusura.strftime('%H:%M')} &nbsp;|&nbsp; 🔓 Apertura: {apertura.strftime('%H:%M')}</div>
        </div>
        """, unsafe_allow_html=True)
    if not visto:
        st.info("Nessun treno in questa fascia oraria.")


# ==========================================
# INTERFACCIA
# ==========================================
st.title("🚧 Binario Libero")
st.caption("Monitor PL — Pisa S. Rossore ↔ San Giuliano Terme")

# Orologio grande e visibile
now = datetime.now()
st.markdown(f'<div class="ora-box">🕐 {now.strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
st.markdown('<div class="refresh-note">⏳ Aggiornamento automatico ogni 20 secondi</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🔄 Aggiorna ora", use_container_width=True):
        st.rerun()
with col2:
    if st.button("⏸️ Ferma auto-refresh", use_container_width=True):
        st.info("Per fermare l\'auto-refresh, chiudi e riapri l\'app.")

st.markdown("---")

tab1, tab2 = st.tabs(["🚂 San Giuliano → Pisa", "🚂 Pisa → San Giuliano"])

# ─── ANDATA ───
with tab1:
    st.subheader("🚂 San Giuliano Terme → Pisa S. Rossore")
    oggi = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for pl_name, cfg in PL_CONFIG.items():
        mostra_pl(pl_name, cfg["offset_andata"], ORARI_ANDATA, oggi)

    aperti, chiusi = 0, 0
    for pl_name, cfg in PL_CONFIG.items():
        for num, hhmm in ORARI_ANDATA:
            partenza = parse_hhmm(oggi, hhmm)
            transito = partenza + timedelta(minutes=cfg["offset_andata"])
            stato, _, _, _ = calcola_stato(transito)
            if stato in ("aperto", "chiude"):
                aperti += 1
            elif stato == "chiuso":
                chiusi += 1
            break

    st.markdown(f"<div class='totale-box'>🟢 {aperti} PL aperti &nbsp;|&nbsp; 🔴 {chiusi} PL chiusi</div>", unsafe_allow_html=True)

# ─── RITORNO ───
with tab2:
    st.subheader("🚂 Pisa S. Rossore → San Giuliano Terme")
    oggi = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for pl_name, cfg in PL_CONFIG.items():
        mostra_pl(pl_name, cfg["offset_ritorno"], ORARI_RITORNO, oggi)

    aperti, chiusi = 0, 0
    for pl_name, cfg in PL_CONFIG.items():
        for num, hhmm in ORARI_RITORNO:
            partenza = parse_hhmm(oggi, hhmm)
            transito = partenza + timedelta(minutes=cfg["offset_ritorno"])
            stato, _, _, _ = calcola_stato(transito)
            if stato in ("aperto", "chiude"):
                aperti += 1
            elif stato == "chiuso":
                chiusi += 1
            break

    st.markdown(f"<div class='totale-box'>🟢 {aperti} PL aperti &nbsp;|&nbsp; 🔴 {chiusi} PL chiusi</div>", unsafe_allow_html=True)

st.divider()
st.markdown("""
<small>
<b>Binario Libero</b> — Monitor passaggi a livello in tempo reale.<br>
5 PL monitorati: Via Ugo Rindi, Via di Gagno, Via 24 Maggio, Via Ulisse Dini, Via Cave.<br>
Chiusura ~3 min prima del transito, apertura 12 sec dopo.<br>
<b>Aggiornamento orari:</b> 2ª domenica di giugno e dicembre.
</small>
""", unsafe_allow_html=True)
