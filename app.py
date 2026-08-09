from datetime import datetime, timedelta
import zoneinfo
import streamlit as st

# ==========================================
# BINARIO LIBERO — Con PL San Giuliano
# ==========================================

st.set_page_config(page_title="Binario Libero", page_icon="🚧", layout="wide")

# Auto-refresh ogni 40 secondi
st.markdown('<meta http-equiv="refresh" content="40">', unsafe_allow_html=True)

st.markdown(
    """
<style>
    .pl-card {
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid #e9ecef;
        background: #ffffff;
    }
    .pl-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1a1d20;
    }
    .stato-chiuso { color: #dc3545; font-size: 1.25rem; font-weight: 700; }
    .stato-chiude { color: #d97706; font-size: 1.25rem; font-weight: 700; }
    .stato-aperto { color: #28a745; font-size: 1.25rem; font-weight: 700; }
    .info-row { font-size: 0.9rem; color: #495057; margin-top: 4px; }
    .ora-box {
        font-size: 1.2rem;
        font-weight: 600;
        text-align: center;
        padding: 8px;
        background: #212529;
        color: #fff;
        border-radius: 8px;
        margin-bottom: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

TZ_ITALIA = zoneinfo.ZoneInfo("Europe/Rome")

PL_CONFIG = {
    "San Giuliano Terme": {"offset_andata": 0, "offset_ritorno": 6},
    "Via Cave": {"offset_andata": 1, "offset_ritorno": 5},
    "Via Ulisse Dini": {"offset_andata": 2, "offset_ritorno": 4},
    "Via 24 Maggio": {"offset_andata": 3, "offset_ritorno": 3},
    "Via di Gagno": {"offset_andata": 4, "offset_ritorno": 2},
    "Via Ugo Rindi": {"offset_andata": 5, "offset_ritorno": 1},
}

CHIUSURA_ANTICIPO = 3
APERTURA_POST = 12

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
    now = datetime.now(TZ_ITALIA)
    chiusura = transito_ora - timedelta(minutes=CHIUSURA_ANTICIPO)
    apertura = transito_ora + timedelta(seconds=APERTURA_POST)

    if now < chiusura:
        sec = int((chiusura - now).total_seconds())
        if sec <= 300:
            return (
                "chiude",
                f"🟡 Chiude tra {sec//60}m {sec%60}s",
                chiusura,
                apertura,
            )
        return "aperto", "🟢 Passaggio libero", chiusura, apertura
    if chiusura <= now <= apertura:
        sec = int((apertura - now).total_seconds())
        return (
            "chiuso",
            f"🔴 CHIUSO — riapre tra {sec//60}m {sec%60}s",
            chiusura,
            apertura,
        )
    return "passato", "⚫ Treno passato", chiusura, apertura


def get_prossimo_treno(offset, orari_list, oggi):
    now = datetime.now(TZ_ITALIA)
    for num, hhmm in orari_list:
        partenza = parse_hhmm(oggi, hhmm)
        transito = partenza + timedelta(minutes=offset)
        stato, msg, chiusura, apertura = calcola_stato(transito)
        if stato != "passato" or (now - apertura).total_seconds() <= 60:
            return num, transito, stato, msg, chiusura, apertura
    return None


# ==========================================
# INTERFACCIA PRINCIPALE
# ==========================================
now_ita = datetime.now(TZ_ITALIA)
oggi = now_ita.replace(hour=0, minute=0, second=0, microsecond=0)

col_title, col_time = st.columns([2, 1])
with col_title:
    st.title("🚧 Binario Libero")
    st.caption("Pisa S. Rossore ↔ San Giuliano Terme")
with col_time:
    st.markdown(
        f'<div class="ora-box">🕐 {now_ita.strftime("%H:%M:%S")}</div>',
        unsafe_allow_html=True,
    )
    if st.button("🔄 Aggiorna Ora", use_container_width=True):
        st.rerun()

st.markdown("---")

tab1, tab2 = st.tabs(["🚂 San Giuliano → Pisa", "🚂 Pisa → San Giuliano"])

# ─── TAB ANDATA ───
with tab1:
    st.subheader("Stato PL imminente (San Giuliano → Pisa)")
    for pl_name, cfg in PL_CONFIG.items():
        treno = get_prossimo_treno(cfg["offset_andata"], ORARI_ANDATA, oggi)
        if treno:
            num, transito, stato, msg, chiusura, apertura = treno
            st.markdown(
                f"""
            <div class="pl-card">
                <div class="pl-title">📍 {pl_name}</div>
                <div class="stato-{stato}">{msg}</div>
                <div class="info-row"><b>Treno:</b> {num} | <b>Transito:</b> {transito.strftime('%H:%M')}</div>
                <div class="info-row">⏰ Chiusura: <b>{chiusura.strftime('%H:%M')}</b> &nbsp;|&nbsp; 🔓 Riapertura: <b>{apertura.strftime('%H:%M')}</b></div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.info(f"📍 {pl_name}: Nessun altro treno previsto per oggi.")

# ─── TAB RITORNO ───
with tab2:
    st.subheader("Stato PL imminente (Pisa → San Giuliano)")
    for pl_name, cfg in PL_CONFIG.items():
        treno = get_prossimo_treno(cfg["offset_ritorno"], ORARI_RITORNO, oggi)
        if treno:
            num, transito, stato, msg, chiusura, apertura = treno
            st.markdown(
                f"""
            <div class="pl-card">
                <div class="pl-title">📍 {pl_name}</div>
                <div class="stato-{stato}">{msg}</div>
                <div class="info-row"><b>Treno:</b> {num} | <b>Transito:</b> {transito.strftime('%H:%M')}</div>
                <div class="info-row">⏰ Chiusura: <b>{chiusura.strftime('%H:%M')}</b> &nbsp;|&nbsp; 🔓 Riapertura: <b>{apertura.strftime('%H:%M')}</b></div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.info(f"📍 {pl_name}: Nessun altro treno previsto per oggi.")

# ==========================================
# PANNELLO LATERALE (SIDEBAR) - PROSSIMI ORARI
# ==========================================
with st.sidebar:
    st.header("📋 Tabella Orari Completa")
    st.write("Consulta i passaggi successivi della giornata.")

    pl_selezionato = st.selectbox(
        "Seleziona Passaggio a Livello:", list(PL_CONFIG.keys())
    )
    direzione = st.radio(
        "Direzione:", ["San Giuliano → Pisa", "Pisa → San Giuliano"]
    )

    cfg = PL_CONFIG[pl_selezionato]
    offset = (
        cfg["offset_andata"]
        if direzione == "San Giuliano → Pisa"
        else cfg["offset_ritorno"]
    )
    lista_orari = (
        ORARI_ANDATA
        if direzione == "San Giuliano → Pisa"
        else ORARI_RITORNO
    )

    st.markdown(f"### Prossimi treni per `{pl_selezionato}`")

    trovati = 0
    for num, hhmm in lista_orari:
        partenza = parse_hhmm(oggi, hhmm)
        transito = partenza + timedelta(minutes=offset)
        chiusura = transito - timedelta(minutes=CHIUSURA_ANTICIPO)
        apertura = transito + timedelta(seconds=APERTURA_POST)

        if now_ita < apertura:
            st.write(
                f"🚆 **{num}** — Transito: `{transito.strftime('%H:%M')}`"
            )
            st.caption(
                f"Chiusura: {chiusura.strftime('%H:%M')} ➜ Riapertura:"
                f" {apertura.strftime('%H:%M')}"
            )
            st.markdown("---")
            trovati += 1

    if trovati == 0:
        st.write("Nessun altro treno in programma per oggi.")
