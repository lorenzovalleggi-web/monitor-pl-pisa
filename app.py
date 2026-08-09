from datetime import datetime, timedelta
import zoneinfo
import streamlit as st

# ==========================================
# BINARIO LIBERO — Vista Unica Automatico
# ==========================================

st.set_page_config(page_title="Binario Libero", page_icon="🚧", layout="wide")

# Auto-refresh ogni 40 secondi
st.markdown('<meta http-equiv="refresh" content="40">', unsafe_allow_html=True)

st.markdown(
    """
<style>
    .pl-card {
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 16px;
        border: 1px solid #dee2e6;
        background: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .pl-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1a1d20;
        margin-bottom: 6px;
    }
    .stato-chiuso { color: #dc3545; font-size: 1.25rem; font-weight: 700; }
    .stato-chiude { color: #d97706; font-size: 1.25rem; font-weight: 700; }
    .stato-aperto { color: #28a745; font-size: 1.25rem; font-weight: 700; }
    .dir-box {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin-top: 8px;
        border-left: 4px solid #0d6efd;
    }
    .info-row { font-size: 0.9rem; color: #333; margin-top: 2px; }
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

# MOSTRA TUTTI I PASSAGGI A LIVELLO IN UN'UNICA SCHERMATA
for pl_name, cfg in PL_CONFIG.items():
    t_andata = get_prossimo_treno(cfg["offset_andata"], ORARI_ANDATA, oggi)
    t_ritorno = get_prossimo_treno(cfg["offset_ritorno"], ORARI_RITORNO, oggi)

    # Determina lo stato globale prioritario del PL (Chiuso > Chiude > Aperto)
    stati = [
        t[2] for t in [t_andata, t_ritorno] if t is not None
    ]
    if "chiuso" in stati:
        stato_globale = "chiuso"
        msg_globale = "🔴 PASSAGGIO A LIVELLO CHIUSO"
    elif "chiude" in stati:
        stato_globale = "chiude"
        msg_globale = "🟡 PASSAGGIO A LIVELLO IN CHIUSURA"
    else:
        stato_globale = "aperto"
        msg_globale = "🟢 PASSAGGIO LIBERO"

    html_card = f"""
    <div class="pl-card">
        <div class="pl-title">📍 {pl_name}</div>
        <div class="stato-{stato_globale}">{msg_globale}</div>
    """

    # Sezione Direzione San Giuliano -> Pisa
    if t_andata:
        num, transito, stato, msg, chiusura, apertura = t_andata
        html_card += f"""
        <div class="dir-box">
            <b>➡️ Verso Pisa:</b> Treno <b>{num}</b> (Transito {transito.strftime('%H:%M')})<br>
            <span class="info-row">Stato: <b>{msg}</b> | Chiusura: <b>{chiusura.strftime('%H:%M')}</b> ➜ Riapertura: <b>{apertura.strftime('%H:%M')}</b></span>
        </div>
        """

    # Sezione Direzione Pisa -> San Giuliano
    if t_ritorno:
        num, transito, stato, msg, chiusura, apertura = t_ritorno
        html_card += f"""
        <div class="dir-box">
            <b>⬅️ Verso San Giuliano:</b> Treno <b>{num}</b> (Transito {transito.strftime('%H:%M')})<br>
            <span class="info-row">Stato: <b>{msg}</b> | Chiusura: <b>{chiusura.strftime('%H:%M')}</b> ➜ Riapertura: <b>{apertura.strftime('%H:%M')}</b></span>
        </div>
        """

    html_card += "</div>"
    st.markdown(html_card, unsafe_allow_html=True)

# ==========================================
# PANNELLO LATERALE (SIDEBAR) - ORARI COMPLETI
# ==========================================
with st.sidebar:
    st.header("📋 Tabella Orari")
    pl_selezionato = st.selectbox(
        "Seleziona Passaggio a Livello:", list(PL_CONFIG.keys())
    )

    cfg = PL_CONFIG[pl_selezionato]

    st.markdown(f"### Prossimi passaggi per `{pl_selezionato}`")

    # Unifica e ordina tutti i prossimi treni per l'orario di transito
    prossimi_treni = []
    for num, hhmm in ORARI_ANDATA:
        transito = parse_hhmm(oggi, hhmm) + timedelta(
            minutes=cfg["offset_andata"]
        )
        if transito > now_ita - timedelta(minutes=2):
            prossimi_treni.append((transito, num, "➡️ Pisa"))

    for num, hhmm in ORARI_RITORNO:
        transito = parse_hhmm(oggi, hhmm) + timedelta(
            minutes=cfg["offset_ritorno"]
        )
        if transito > now_ita - timedelta(minutes=2):
            prossimi_treni.append((transito, num, "⬅️ San Giuliano"))

    prossimi_treni.sort(key=lambda x: x[0])

    for transito, num, dir_txt in prossimi_treni:
        st.write(
            f"🚆 **{transito.strftime('%H:%M')}** — {num} ({dir_txt})"
        )
