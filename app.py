import streamlit as st
import datetime
import pytz
import requests

st.set_page_config(
    page_title="BinarioLibero",
    layout="centered"
)

# CSS compatto su righe corte
st.markdown(
    "<style>"
    ".stApp {"
    "background-color: #0f172a "
    "!important;"
    "color: #ffffff !important;"
    "}"
    "* { color: #ffffff "
    "!important; }"
    "</style>",
    unsafe_allow_html=True
)

# Auto-refresh 30s
st.components.v1.html(
    "<script>"
    "setTimeout(function(){"
    "window.parent.location"
    ".reload();"
    "}, 30000);"
    "</script>",
    height=0,
    width=0
)

# Tabelle Orarie flat
P_H = [5,7,7,8,9,5,6,7,7,8,9,9,9,10,
       12,12,13,13,14,14,15,15,16,16,
       17,17,18,18,19,19,20,21,21]
P_M = [31,10,55,55,55,25,13,4,50,50,
       3,22,50,20,20,50,20,43,20,50,
       20,50,19,50,20,50,20,50,20,50,
       50,20,50]
L_H = [6,7,7,7,8,9,9,10,10,12,13]
L_M = [52,8,40,53,15,10,42,12,42,42,
       12]

st.title("⚡ BinarioLibero Pisa")

try:
    tz = pytz.timezone(
        'Europe/Rome'
    )
    ora = datetime.datetime.now(tz)
except:
    ora = datetime.datetime.now()

min_ora = (
    ora.hour * 60 + ora.minute
)
st.write(
    f"⏱️ Ora attuale: "
    f"{ora.strftime('%H:%M:%S')}"
)

tr_min = []
tr_dir = []
tr_num = []

# Live Pisa righe ultra corte
try:
    dt = ora.strftime(
        '%Y-%m-%dT00:00:00'
    )
    url_p = (
        f"http://www.viaggiatreno.it"
        f"/viaggiatrenonew/api"
        f"/esitoPartenze/S06411/{dt}"
    )
    r_p = requests.get(
        url_p, timeout=2
    ).json()
    res_p = r_p.get(
        'tabellone', []
    )
    for t in res_p:
        prog = t.get(
            'orarioProgrammato', ''
        )
        if prog and ':' in prog:
            sp = prog.split(':')
            rit = int(
                t.get('ritardo', 0)
                or 0
            )
            rit = max(0, rit)
            m_calc = (
                int(sp[0]) * 60
                + int(sp[1])
                + rit
            )
            tr_min.append(m_calc)
            tr_dir.append("PISA")
            tr_num.append(
                str(t.get(
                    'numeroTreno',
                    'REG'
                ))
            )
except:
    pass

# Live Lucca righe ultra corte
try:
    url_l = (
        f"http://www.viaggiatreno.it"
        f"/viaggiatrenonew/api"
        f"/esitoPartenze/S06501/{dt}"
    )
    r_l = requests.get(
        url_l, timeout=2
    ).json()
    res_l = r_l.get(
        'tabellone', []
    )
    for t in res_l:
        prog = t.get(
            'orarioProgrammato', ''
        )
        if prog and ':' in prog:
            sp = prog.split(':')
            rit = int(
                t.get('ritardo', 0)
                or 0
            )
            rit = max(0, rit)
            m_calc = (
                int(sp[0]) * 60
                + int(sp[1])
                + rit
            )
            tr_min.append(m_calc)
            tr_dir.append("LUCCA")
            tr_num.append(
                str(t.get(
                    'numeroTreno',
                    'REG'
                ))
            )
except:
    pass

# Fallback
if not tr_min:
    for i in range(len(P_H)):
        m_c = (
            P_H[i] * 60 + P_M[i]
        )
        if m_c > min_ora:
            tr_min.append(m_c)
            tr_dir.append("LUCCA")
            tr_num.append("PROG")
    for i in range(len(L_H)):
        m_c = (
            L_H[i] * 60 + L_M[i]
        )
        if m_c > min_ora:
            tr_min.append(m_c)
            tr_dir.append("PISA")
            tr_num.append("PROG")

f_min = []
f_dir = []
f_num = []
for i in range(len(tr_min)):
    if (tr_min[i] + 25) > min_ora:
        f_min.append(tr_min[i])
        f_dir.append(tr_dir[i])
        f_num.append(tr_num[i])

if f_min:
    idx_p = f_min.index(
        min(f_min)
    )
    m_v = f_min[idx_p]
    st.info(
        f"📋 PROSSIMO: REG "
        f"{f_num[idx_p]} "
        f"(Dir. {f_dir[idx_p]}) "
        f"alle {m_v//60:02d}:"
        f"{m_v%60:02d}"
    )
else:
    st.info("📋 Nessun treno.")

st.markdown("---")
st.write("### 🚊 STATO VARCHI")

N_PL = ["Via Ugo Rindi",
        "Via di Gagno",
        "Via XXIV Maggio",
        "Via U. Dini (Gello)",
        "San Giuliano Terme"]
A_INI = [-4, -4, -3, -1, 1]
A_FIN
