import datetime
import pandas as pd
import streamlit as st

# Configurazione pagina
st.set_page_config(
    page_title="Monitor PL Pisa", layout="wide", initial_sidebar_state="collapsed"
)

st.title("🚆 Monitor Passaggi a Livello - Pisa")
st.write("Stato in tempo reale e prossimi orari di chiusura/riapertura.")

# 1. Lista dei Passaggi a Livello e Orari
PL_DATA = [
    {
        "nome": "PL Via Rigattieri",
        "orari_chiusura": [
            ("07:30", "07:42"),
            ("08:15", "08:25"),
            ("12:40", "12:52"),
            ("14:10", "14:22"),
            ("18:30", "18:45"),
        ],
    },
    {
        "nome": "PL Via Putignano",
        "orari_chiusura": [
            ("07:40", "07:50"),
            ("08:30", "08:40"),
            ("13:00", "13:10"),
            ("17:50", "18:02"),
            ("19:15", "19:25"),
        ],
    },
    {
        "nome": "PL Via S. Marta",
        "orari_chiusura": [
            ("07:20", "07:32"),
            ("09:00", "09:12"),
            ("13:15", "13:28"),
            ("18:10", "18:22"),
        ],
    },
]


# 2. Calcolo dello stato
def calcola_stato(orari_list):
    ora_attuale = datetime.datetime.now().time()

    # Controlla se è CHIUSO adesso
    for inizio_str, fine_str in orari_list:
        inizio = datetime.datetime.strptime(inizio_str, "%H:%M").time()
        fine = datetime.datetime.strptime(fine_str, "%H:%M").time()
        if inizio <= ora_attuale <= fine:
            return "🔴 CHIUSO", inizio_str, fine_str

    # Se è APERTO, cerca la prossima chiusura
    for inizio_str, fine_str in orari_list:
        inizio = datetime.datetime.strptime(inizio_str, "%H:%M").time()
        if inizio > ora_attuale:
            return "🟢 APERTO", inizio_str, fine_str

    return "🟢 APERTO", "Nessuna", "-"


# 3. Visualizzazione con ICONE e SCHEDE GIGANTI
cols = st.columns(len(PL_DATA))

for i, pl in enumerate(PL_DATA):
    stato, pross_chiusura, pross_riapertura = calcola_stato(
        pl["orari_chiusura"]
    )

    with cols[i]:
        st.subheader(pl["nome"])
        if stato == "🔴 CHIUSO":
            st.error(f"### {stato}")
            st.write(f"⏰ **Riapertura prevista:** {pross_riapertura}")
        else:
            st.success(f"### {stato}")
            st.write(f"⏰ **Prossima chiusura:** {pross_chiusura}")
            st.write(f"🔓 **Riapertura:** {pross_riapertura}")

st.markdown("---")

# 4. Tabella Riassuntiva per una consultazione rapida
st.subheader("📋 Tabella Orari Completa")
tabella = []
for pl in PL_DATA:
    stato, p_chiusura, p_riapertura = calcola_stato(pl["orari_chiusura"])
    tabella.append(
        {
            "Passaggio a Livello": pl["nome"],
            "Stato": stato,
            "Prossima Chiusura": p_chiusura,
            "Prevista Riapertura": p_riapertura,
        }
    )

st.dataframe(pd.DataFrame(tabella), use_container_width=True)
