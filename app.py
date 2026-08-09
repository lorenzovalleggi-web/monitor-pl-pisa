import streamlit as st
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# ==========================================
# BINARIO LIBERO
# Monitor PL Pisa S. Rossore ↔ San Giuliano Terme
# 5 PL: Via Ugo Rindi, Via di Gagno, Via 24 Maggio, Via Ulisse Dini, Via Cave
# ==========================================

st.set_page_config(page_title="Binario Libero", page_icon="🚧", layout="centered")

st.markdown('<meta http-equiv="refresh" content="20">', unsafe_allow_html=True)

st.markdown("""
<style>
    .pl-card {
        padding: 16px;
        border-radius: 14px;
        margin-bottom: 12px;
        border: 1px solid #e9ecef;
        background: #ffffff;
    }
    .pl-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #212529;
        margin-bottom: 4px;
    }
    .stato-chiuso { color: #dc3545; font-size: 1.3rem; font-weight: 700; }
    .stato-chiude { color: #f59f00; font-size: 1.3rem; font-weight: 700; }
    .stato-aperto { color: #2b8a3e; font-size: 1.3rem; font-weight: 700; }
    .info-row { font-size: 0.9rem; color: #495057; margin-top: 4px; }
    .totale-box {
        margin-bottom: 16px;
        padding: 12px;
        border-radius: 10px;
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        text-align: center;
        font-size: 1rem;
        font-weight: 500;
    }
    .ora-box {
        font-size: 1.3rem;
        font-weight: 700;
        text-align: center;
        padding: 10px;
        background: #212529;
        color: #fff;
        border-radius: 10px;
        margin-bottom: 8px;
        letter-spacing: 2px;
    }
    .refresh-note {
        font-size: 0.75rem;
        color: #868e96;
        text-align: center;
        margin-bottom: 10px;
    }
    .tabella-header {
        font-weight: 600;
        background: #e9ecef;
        padding: 6px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
    }
    .tabella-riga {
        padding: 6px 10px;
        border-bottom: 1px solid #f1f3f5;
        font-size: 0.85rem;
    }
    .badge-andata { color: #1864ab; font-weight: 600; }
    .badge-ritorno { color: #c92a2a; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

TZ_ITALIA = ZoneInfo("Europe/Rome")

PL_CONFIG = {
    "Via Ugo Rindi":   {"offset_andata": 5,  "offset_ritorno": 1},
    "Via di Gagno":    {"offset_andata": 4,  "offset_ritorno": 2},
    "Via 24 Maggio":   {"offset_andata": 3,  "offset_ritorno": 3},
    "Via Ulisse Dini": {"offset_andata": 2,  "offset_ritorno": 4},
    "Via Cave":        {"offset_andata": 1,  "offset_ritorno": 5},
}

CHIUSURA_ANTICIPO = 3
APERTURA_POST = 12

ORARI_ANDATA = [
    ("R 32829", "07:58"), ("R 34146", "08:15"), ("R 18556", "08:58"),
    ("R 18562", "09:58"), ("R 83571", "11:44"), ("R 18570", "13:28"),
    ("R 18490", "13:58"), ("R 18574", "14:27"), ("R 34098", "14:57"),
    ("R 18578", "15:28"), ("R 18494", "15:58"), ("R 18584", "16:27"),
    ("R 18588", "16:58"), ("R 18592", "17:28"), ("R 18594", "17:58"),
    ("R 18598", "18:29"), ("R 83691", "18:58"), ("R 18602", "19:28"),
    ("R 83663", "20:20"), ("R 18606", "20:58"), ("R 83665", "21:32"),
]

ORARI_RITORNO = [
    ("R 83671", "05:31"), ("R 18553", "07:10"), ("R 83675", "07:55"),
    ("R 18555", "08:55"), ("R 18561", "09:55"), ("R 18573", "12:55"),
    ("R 18575", "13:25"), ("R 83679", "13:48"), ("R 18577", "14:24"),
    ("R 18493", "14:55"), ("R 18581", "15:25"), ("R 18583", "15:55"),
    ("R 18497", "16:23"), ("R 18585", "16:55"), ("R 18591", "17:25"),
    ("R 83681", "17:55"), ("R 18593", "18:25"), ("R 18595", "18:55"),
    ("R 83683", "19:25"), ("R 18597", "19:55"), ("R 18605", "21:55"),
]


def parse_hhmm(oggi, hhmm):
    h, m = map(int, hhmm.split(":"))
    return oggi.replace(hour=h, minute=m, second=0, microsecond=0)


def calcola_stato(transito_ora):
    now = datetime.now(TZ_ITALIA)
    chiusura = transito_ora - timedelta(minutes=CHIUSURA_ANTICIPO)
    apertura = transito_ora + timedelta(seconds=APERTURA_POST)

    if now < chiusura:
        sec = int((chiusura - now).total_seconds())
        if sec <= 300:
            return "chiude", f"🟡 Si chiude tra {sec//60}m {sec%60}s", chiusura, apertura
        return "aperto", "🟢 Aperto", chiusura, apertura
    if chiusura <= now <= apertura:
        sec = int((apertura - now).total_seconds())
        return "chiuso", f"🔴 CHIUSO — apre tra {sec//60}m {sec%60}s", chiusura, apertura
    return "passato", "⚫ Passato", chiusura, apertura


def prossimo_treno_per_pl(pl_name, offset_a, offset_r, oggi):
    """Restituisce il prossimo treno (andata o ritorno) che non è ancora passato per questo PL."""
    now = datetime.now(TZ_ITALIA)
    candidati = []

    # Andata
    for num, hhmm in ORARI_ANDATA:
        partenza = parse_hhmm(oggi, hhmm)
        transito = partenza + timedelta(minutes=offset_a)
        apertura = transito + timedelta(seconds=APERTURA_POST)
        if now <= apertura:
            candidati.append((transito, num, "andata", offset_a))

    # Ritorno
    for num, hhmm in ORARI_RITORNO:
        partenza = parse_hhmm(oggi, hhmm)
        transito = partenza + timedelta(minutes=offset_r)
        apertura = transito + timedelta(seconds=APERTURA_POST)
        if now <= apertura:
            candidati.append((transito, num, "ritorno", offset_r))

    if not candidati:
        return None

    candidati.sort(key=lambda x: x[0])
    return candidati[0]


def tutti_prossimi_per_pl(pl_name, offset_a, offset_r, oggi):
    """Restituisce tutti i treni futuri per questo PL, ordinati."""
    now = datetime.now(TZ_ITALIA)
    lista = []

    for num, hhmm in ORARI_ANDATA:
        partenza = parse_hhmm(oggi, hhmm)
        transito = partenza + timedelta(minutes=offset_a)
        chiusura = transito - timedelta(minutes=CHIUSURA_ANTICIPO)
        apertura = transito + timedelta(seconds=APERTURA_POST)
        if now <= apertura:
            lista.append((transito, num, "andata", chiusura, apertura))

    for num, hhmm in ORARI_RITORNO:
        partenza = parse_hhmm(oggi, hhmm)
        transito = partenza + timedelta(minutes=offset_r)
        chiusura = transito - timedelta(minutes=CHIUSURA_ANTICIPO)
        apertura = transito + timedelta(seconds=APERTURA_POST)
        if now <= apertura:
            lista.append((transito, num, "ritorno", chiusura, apertura))

    lista.sort(key=lambda x: x[0])
    return lista


# ==========================================
# HEADER
# ==========================================
st.title("🚧 Binario Libero")
st.caption("Monitor PL — Pisa S. Rossore ↔ San Giuliano Terme")

now = datetime.now(TZ_ITALIA)
st.markdown(f'<div class="ora-box">🕐 {now.strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
st.markdown('<div class="refresh-note">⏳ Aggiornamento automatico ogni 20 secondi</div>', unsafe_allow_html=True)

c1, c2 = st.columns([1, 1])
with c1:
    if st.button("🔄 Aggiorna ora", use_container_width=True):
        st.rerun()
with c2:
    if st.button("⏸️ Ferma auto-refresh", use_container_width=True):
        st.info("Chiudi e riapri l\'app per fermare.")

st.markdown("---")

# ==========================================
# TABS
# ==========================================
tab1, tab2 = st.tabs(["🚨 Stato Attuale", "📅 Prossimi Orari"])

# ─── TAB 1: STATO ATTUALE ───
with tab1:
    st.subheader("🚨 Stato Attuale dei PL")
    oggi = datetime.now(TZ_ITALIA).replace(hour=0, minute=0, second=0, microsecond=0)

    aperti = 0
    chiusi = 0
    in_chiusura = 0

    for pl_name, cfg in PL_CONFIG.items():
        prossimo = prossimo_treno_per_pl(pl_name, cfg["offset_andata"], cfg["offset_ritorno"], oggi)

        if prossimo is None:
            st.markdown(f"""
            <div class="pl-card">
                <div class="pl-name">📍 {pl_name}</div>
                <div class="stato-aperto">🟢 Nessun treno in programma</div>
            </div>
            """, unsafe_allow_html=True)
            aperti += 1
            continue

        transito, num, direzione, offset = prossimo
        stato, msg, chiusura, apertura = calcola_stato(transito)
        dir_label = "→ Pisa" if direzione == "andata" else "→ S. Giuliano"
        dir_badge = f'<span class="badge-andata">{dir_label}</span>' if direzione == "andata" else f'<span class="badge-ritorno">{dir_label}</span>'

        if stato == "aperto":
            aperti += 1
        elif stato == "chiuso":
            chiusi += 1
        elif stato == "chiude":
            in_chiusura += 1

        st.markdown(f"""
        <div class="pl-card">
            <div class="pl-name">📍 {pl_name} {dir_badge}</div>
            <div class="stato-{stato}">{msg}</div>
            <div class="info-row">🚂 <b>{num}</b> — transito PL alle {transito.strftime('%H:%M')}</div>
            <div class="info-row">⏰ Chiusura: <b>{chiusura.strftime('%H:%M')}</b> &nbsp;|&nbsp; 🔓 Apertura: <b>{apertura.strftime('%H:%M')}</b></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="totale-box">
        🟢 {aperti} aperti &nbsp;|&nbsp; 🟡 {in_chiusura} in chiusura &nbsp;|&nbsp; 🔴 {chiusi} chiusi
    </div>
    """, unsafe_allow_html=True)

# ─── TAB 2: PROSSIMI ORARI ───
with tab2:
    st.subheader("📅 Prossimi Orari per PL")
    oggi = datetime.now(TZ_ITALIA).replace(hour=0, minute=0, second=0, microsecond=0)

    for pl_name, cfg in PL_CONFIG.items():
        prossimi = tutti_prossimi_per_pl(pl_name, cfg["offset_andata"], cfg["offset_ritorno"], oggi)

        with st.expander(f"📍 {pl_name} ({len(prossimi)} treni)", expanded=False):
            if not prossimi:
                st.info("Nessun treno in programma.")
                continue

            # Header tabella
            cols = st.columns([1.2, 1, 1.3, 1.3, 1.3])
            cols[0].markdown('<div class="tabella-header">Treno</div>', unsafe_allow_html=True)
            cols[1].markdown('<div class="tabella-header">Direzione</div>', unsafe_allow_html=True)
            cols[2].markdown('<div class="tabella-header">Transito PL</div>', unsafe_allow_html=True)
            cols[3].markdown('<div class="tabella-header">Chiusura</div>', unsafe_allow_html=True)
            cols[4].markdown('<div class="tabella-header">Apertura</div>', unsafe_allow_html=True)

            for transito, num, direzione, chiusura, apertura in prossimi[:10]:  # max 10 per PL
                dir_label = "→ Pisa" if direzione == "andata" else "→ S. Giuliano"
                cols = st.columns([1.2, 1, 1.3, 1.3, 1.3])
                cols[0].markdown(f'<div class="tabella-riga">{num}</div>', unsafe_allow_html=True)
                cols[1].markdown(f'<div class="tabella-riga">{dir_label}</div>', unsafe_allow_html=True)
                cols[2].markdown(f'<div class="tabella-riga">{transito.strftime("%H:%M")}</div>', unsafe_allow_html=True)
                cols[3].markdown(f'<div class="tabella-riga">{chiusura.strftime("%H:%M")}</div>', unsafe_allow_html=True)
                cols[4].markdown(f'<div class="tabella-riga">{apertura.strftime("%H:%M")}</div>', unsafe_allow_html=True)

st.divider()
st.markdown("""
<small>
<b>Binario Libero</b> — Monitor passaggi a livello in tempo reale.<br>
5 PL: Via Ugo Rindi, Via di Gagno, Via 24 Maggio, Via Ulisse Dini, Via Cave.<br>
Chiusura ~3 min prima, apertura 12 sec dopo il transito.<br>
<b>Aggiornamento orari:</b> 2ª domenica di giugno e dicembre.
</small>
""", unsafe_allow_html=True)
