
import streamlit as st
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# ==========================================
# BINARIO LIBERO
# Monitor PL e Stazione — Pisa S. Rossore ↔ San Giuliano Terme
# 6 punti monitorati:
#   1. San Giuliano Terme (stazione)
#   2. Via Cave
#   3. Via Ulisse Dini
#   4. Via 24 Maggio
#   5. Via di Gagno
#   6. Via Ugo Rindi
# Chiusura: 3 min prima del transito
# Apertura: 12 secondi dopo il transito (dato reale Via 24 Maggio)
# ==========================================

st.set_page_config(
    page_title="Binario Libero",
    page_icon="🚧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Auto-refresh ogni 20 secondi
st.markdown('<meta http-equiv="refresh" content="20">', unsafe_allow_html=True)

TZ_ITALIA = ZoneInfo("Europe/Rome")

# ==========================================
# CONFIGURAZIONE PL e Stazione
# Offset = minuti dopo la partenza dalla stazione di origine
# ==========================================
PL_CONFIG = {
    "San Giuliano Terme": {"offset_andata": 0, "offset_ritorno": 6},
    "Via Cave":           {"offset_andata": 1, "offset_ritorno": 5},
    "Via Ulisse Dini":    {"offset_andata": 2, "offset_ritorno": 4},
    "Via 24 Maggio":      {"offset_andata": 3, "offset_ritorno": 3},
    "Via di Gagno":       {"offset_andata": 4, "offset_ritorno": 2},
    "Via Ugo Rindi":      {"offset_andata": 5, "offset_ritorno": 1},
}

CHIUSURA_ANTICIPO_MINUTI = 3
APERTURA_POST_SECONDI = 12

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
    now = datetime.now(TZ_ITALIA)
    chiusura = transito_ora - timedelta(minutes=CHIUSURA_ANTICIPO_MINUTI)
    apertura = transito_ora + timedelta(seconds=APERTURA_POST_SECONDI)

    if now < chiusura:
        sec = int((chiusura - now).total_seconds())
        if sec <= 300:
            return (
                "chiude",
                f"🟡 CHIUDE TRA {sec//60}m {sec%60}s",
                chiusura,
                apertura,
            )
        return "aperto", "🟢 PASSAGGIO LIBERO", chiusura, apertura
    if chiusura <= now <= apertura:
        sec = int((apertura - now).total_seconds())
        return (
            "chiuso",
            f"🔴 CHIUSO — RIAPRE TRA {sec//60}m {sec%60}s",
            chiusura,
            apertura,
        )
    return "passato", "⚫ TRENO PASSATO", chiusura, apertura


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
# TESTATA
# ==========================================
now_ita = datetime.now(TZ_ITALIA)
oggi = now_ita.replace(hour=0, minute=0, second=0, microsecond=0)

col1, col2 = st.columns([3, 1])
with col1:
    st.title("🚧 Binario Libero")
    st.caption("Pisa S. Rossore ↔ San Giuliano Terme")
with col2:
    st.metric(label="Ora attuale", value=now_ita.strftime("%H:%M:%S"))

st.divider()

# ==========================================
# LISTA PASSAGGI A LIVELLO
# ==========================================
for pl_name, cfg in PL_CONFIG.items():
    t_andata = get_prossimo_treno(cfg["offset_andata"], ORARI_ANDATA, oggi)
    t_ritorno = get_prossimo_treno(cfg["offset_ritorno"], ORARI_RITORNO, oggi)

    stati = [t[2] for t in [t_andata, t_ritorno] if t is not None]

    if "chiuso" in stati:
        stato_header = "🔴 PASSAGGIO A LIVELLO CHIUSO"
    elif "chiude" in stati:
        stato_header = "🟡 PASSAGGIO A LIVELLO IN CHIUSURA"
    else:
        stato_header = "🟢 PASSAGGIO LIBERO"

    with st.container(border=True):
        st.subheader(f"📍 {pl_name}")
        st.markdown(f"### {stato_header}")

        col_a, col_b = st.columns(2)

        # Verso Pisa
        with col_a:
            st.markdown("#### ➡️ Verso Pisa")
            if t_andata:
                num, transito, stato, msg, chiusura, apertura = t_andata
                st.write(
                    f"🚆 Treno: **{num}** (Transito: **{transito.strftime('%H:%M')}**)"
                )
                st.write(f"Stato: **{msg}**")
                st.caption(
                    f"⏰ Chiusura: **{chiusura.strftime('%H:%M:%S')}** ➜"
                    f" Riapertura: **{apertura.strftime('%H:%M:%S')}**"
                )
            else:
                st.info("Nessun altro treno previsto oggi.")

        # Verso San Giuliano
        with col_b:
            st.markdown("#### ⬅️ Verso San Giuliano")
            if t_ritorno:
                num, transito, stato, msg, chiusura, apertura = t_ritorno
                st.write(
                    f"🚆 Treno: **{num}** (Transito: **{transito.strftime('%H:%M')}**)"
                )
                st.write(f"Stato: **{msg}**")
                st.caption(
                    f"⏰ Chiusura: **{chiusura.strftime('%H:%M:%S')}** ➜"
                    f" Riapertura: **{apertura.strftime('%H:%M:%S')}**"
                )
            else:
                st.info("Nessun altro treno previsto oggi.")

# ==========================================
# PANNELLO LATERALE (SIDEBAR)
# ==========================================
with st.sidebar:
    st.header("📋 Tabella Orari")
    pl_selezionato = st.selectbox(
        "Seleziona Passaggio a Livello:", list(PL_CONFIG.keys())
    )

    cfg = PL_CONFIG[pl_selezionato]
    st.markdown(f"### Prossimi treni per `{pl_selezionato}`")

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
