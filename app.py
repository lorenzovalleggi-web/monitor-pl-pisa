import streamlit as st
from datetime import datetime, timedelta

# ==========================================
# BINARIO LIBERO - Monitor Passaggi a Livello
# Linea: San Giuliano Terme ↔ Pisa
# PL di riferimento: Via 24 Maggio
# Logica: chiusura 3 min prima del transito,
#         apertura 12 secondi dopo il transito
# ==========================================

st.set_page_config(
    page_title="Binario Libero",
    page_icon="🚧",
    layout="centered"
)

# CSS personalizzato per schede colorate
st.markdown("""
<style>
    .treno-card {
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
        border-left: 6px solid;
        background-color: #f8f9fa;
    }
    .stato-chiuso { border-left-color: #dc3545; background-color: #fff5f5; }
    .stato-chiude { border-left-color: #ffc107; background-color: #fffbeb; }
    .stato-aperto { border-left-color: #28a745; background-color: #f0fff4; }
    .stato-passato { border-left-color: #6c757d; background-color: #f1f3f5; }
    .num-treno { font-size: 1.3rem; font-weight: 700; }
    .orario-treno { font-size: 1.1rem; color: #495057; }
    .stato-text { font-size: 1rem; font-weight: 600; margin-top: 4px; }
    .info-pl { font-size: 0.85rem; color: #868e96; margin-top: 6px; }
</style>
""", unsafe_allow_html=True)

# Auto-refresh ogni 5 secondi per tenere i timer aggiornati
st.markdown('<meta http-equiv="refresh" content="5">', unsafe_allow_html=True)

# ==========================================
# ORARI (da aggiornare 2 volte l'anno)
# ==========================================
# Formato: ("Numero", "HH:MM", direzione)
# Direzione: "andata" = San Giuliano → Pisa
#            "ritorno" = Pisa → San Giuliano

ORARI = [
    # San Giuliano Terme → Pisa Centrale (andata)
    ("R 19122", "06:14", "andata"),
    ("R 19124", "06:44", "andata"),
    ("R 19126", "07:14", "andata"),
    ("R 19128", "07:44", "andata"),
    ("R 19130", "08:14", "andata"),
    ("R 19132", "08:44", "andata"),
    ("R 19134", "09:14", "andata"),
    ("R 19136", "09:44", "andata"),
    ("R 19138", "10:14", "andata"),
    ("R 19140", "10:44", "andata"),
    ("R 19142", "11:14", "andata"),
    ("R 19144", "11:44", "andata"),
    ("R 19146", "12:14", "andata"),
    ("R 19148", "12:44", "andata"),
    ("R 19150", "13:14", "andata"),
    ("R 19152", "13:44", "andata"),
    ("R 19154", "14:14", "andata"),
    ("R 19156", "14:44", "andata"),
    ("R 19158", "15:14", "andata"),
    ("R 19160", "15:44", "andata"),
    ("R 19162", "16:14", "andata"),
    ("R 19164", "16:44", "andata"),
    ("R 19166", "17:14", "andata"),
    ("R 19168", "17:44", "andata"),
    ("R 19170", "18:14", "andata"),
    ("R 19172", "18:44", "andata"),
    ("R 19174", "19:14", "andata"),
    ("R 19176", "19:44", "andata"),
    ("R 19178", "20:14", "andata"),
    ("R 19180", "20:44", "andata"),
    ("R 19182", "21:14", "andata"),
    ("R 19184", "21:44", "andata"),
    ("R 19186", "22:14", "andata"),

    # Pisa Centrale → San Giuliano Terme (ritorno)
    ("R 19101", "05:35", "ritorno"),
    ("R 19103", "06:05", "ritorno"),
    ("R 19105", "06:35", "ritorno"),
    ("R 19107", "07:05", "ritorno"),
    ("R 19109", "07:35", "ritorno"),
    ("R 19111", "08:05", "ritorno"),
    ("R 19113", "08:35", "ritorno"),
    ("R 19115", "09:05", "ritorno"),
    ("R 19117", "09:35", "ritorno"),
    ("R 19119", "10:05", "ritorno"),
    ("R 19121", "10:35", "ritorno"),
    ("R 19123", "11:05", "ritorno"),
    ("R 19125", "11:35", "ritorno"),
    ("R 19127", "12:05", "ritorno"),
    ("R 19129", "12:35", "ritorno"),
    ("R 19131", "13:05", "ritorno"),
    ("R 19133", "13:35", "ritorno"),
    ("R 19135", "14:05", "ritorno"),
    ("R 19137", "14:35", "ritorno"),
    ("R 19139", "15:05", "ritorno"),
    ("R 19141", "15:35", "ritorno"),
    ("R 19143", "16:05", "ritorno"),
    ("R 19145", "16:35", "ritorno"),
    ("R 19147", "17:05", "ritorno"),
    ("R 19149", "17:35", "ritorno"),
    ("R 19151", "18:05", "ritorno"),
    ("R 19153", "18:35", "ritorno"),
    ("R 19155", "19:05", "ritorno"),
    ("R 19157", "19:35", "ritorno"),
    ("R 19159", "20:05", "ritorno"),
    ("R 19161", "20:35", "ritorno"),
    ("R 19163", "21:05", "ritorno"),
    ("R 19165", "21:35", "ritorno"),
    ("R 19167", "22:05", "ritorno"),
]

# ==========================================
# LOGICA DI CALCOLO
# ==========================================
PL_CHIUSURA_ANTICIPO = 3       # minuti prima del transito
PL_APERTURA_POST = 12          # secondi dopo il transito
PREAVVISO_MINUTI = 5           # quando inizia l'alert giallo


def parse_orario(oggi, hhmm):
    h, m = map(int, hhmm.split(":"))
    return oggi.replace(hour=h, minute=m, second=0, microsecond=0)


def calcola_stato(treno_ora):
    """Restituisce (stato, css_class, messaggio, countdown_sec)"""
    now = datetime.now()
    chiusura = treno_ora - timedelta(minutes=PL_CHIUSURA_ANTICIPO)
    apertura = treno_ora + timedelta(seconds=PL_APERTURA_POST)

    if now < chiusura - timedelta(minutes=PREAVVISO_MINUTI):
        return "aperto", "stato-aperto", "🟢 Passaggio libero", 0

    if chiusura - timedelta(minutes=PREAVVISO_MINUTI) <= now < chiusura:
        diff = chiusura - now
        sec = int(diff.total_seconds())
        return "chiude", "stato-chiude", f"🟡 Si chiude tra {sec//60}m {sec%60}s", sec

    if chiusura <= now <= apertura:
        diff = apertura - now
        sec = int(diff.total_seconds())
        return "chiuso", "stato-chiuso", f"🔴 CHIUSO - si apre tra {sec//60}m {sec%60}s", sec

    return "passato", "stato-passato", "⚫ Treno passato", 0


def mostra_lista(direzione, titolo, icona):
    st.subheader(f"{icona} {titolo}")
    oggi = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    trovato = False

    for numero, hhmm, dir in ORARI:
        if dir != direzione:
            continue
        treno_ora = parse_orario(oggi, hhmm)
        stato, css, msg, _ = calcola_stato(treno_ora)

        # Mostra solo treni non ancora passati da troppo (ultime 2h)
        if stato == "passato" and (datetime.now() - treno_ora).total_seconds() > 7200:
            continue

        trovato = True
        st.markdown(f"""
        <div class="treno-card {css}">
            <div class="num-treno">{numero}</div>
            <div class="orario-treno">🕐 Transito alle {hhmm}</div>
            <div class="stato-text">{msg}</div>
            <div class="info-pl">PL Via 24 Maggio — chiusura {PL_CHIUSURA_ANTICIPO} min prima, apertura {PL_APERTURA_POST} sec dopo</div>
        </div>
        """, unsafe_allow_html=True)

    if not trovato:
        st.info("Nessun treno in programma per questa fascia oraria.")


# ==========================================
# INTERFACCIA
# ==========================================
st.title("🚧 Binario Libero")
st.caption("Monitor passaggi a livello in tempo reale — San Giuliano Terme ↔ Pisa")

st.markdown(f"""
<div style="text-align:center; font-size:1.1rem; margin-bottom:20px;">
    🕒 <b>Ora attuale:</b> {datetime.now().strftime("%H:%M:%S")}
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🚂 San Giuliano → Pisa", "🚂 Pisa → San Giuliano"])

with tab1:
    mostra_lista("andata", "San Giuliano Terme → Pisa Centrale", "🚂")

with tab2:
    mostra_lista("ritorno", "Pisa Centrale → San Giuliano Terme", "🚂")

st.divider()
st.markdown("""
<small>
<b>Nota:</b> i tempi sono stimati in base agli orari ufficiali. Il passaggio a livello si chiude circa 3 minuti prima del transito del treno e si riapre 12 secondi dopo (dato rilevato sul PL Via 24 Maggio).<br>
Aggiornamento orari: 2ª domenica di giugno e 2ª domenica di dicembre.
</small>
""", unsafe_allow_html=True)
