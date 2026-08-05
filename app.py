import datetime
import folium
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Configurazione pagina
st.set_page_config(page_title="Monitor PL Pisa", layout="wide")
st.title("🚆 Monitor Passaggi a Livello - Pisa")

# 1. Database Passaggi a Livello di Pisa (Coordinate e Finestre Orarie)
# NOTA: Puoi modificare gli orari indicativi nella lista 'orari_chiusura'
PL_DATA = [
    {
        "nome": "PL Via Rigattieri",
        "lat": 43.70812,
        "lon": 10.40125,
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
        "lat": 43.69950,
        "lon": 10.42150,
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
        "lat": 43.71520,
        "lon": 10.41010,
        "orari_chiusura": [
            ("07:20", "07:32"),
            ("09:00", "09:12"),
            ("13:15", "13:28"),
            ("18:10", "18:22"),
        ],
    },
]


# 2. Calcolo dello stato attuale (Aperto/Chiuso)
def calcola_stato_pl(orari_list):
    ora_attuale = datetime.datetime.now().time()

    for inizio_str, fine_str in orari_list:
        inizio = datetime.datetime.strptime(inizio_str, "%H:%M").time()
        fine = datetime.datetime.strptime(fine_str, "%H:%M").time()

        if inizio <= ora_attuale <= fine:
            return "🔴 CHIUSO", inizio_str, fine_str

    # Se non è in fascia di chiusura, cerca la prossima chiusura
    for inizio_str, fine_str in orari_list:
        inizio = datetime.datetime.strptime(inizio_str, "%H:%M").time()
        if inizio > ora_attuale:
            return "🟢 APERTO", inizio_str, fine_str

    # Se la giornata è finita
    return "🟢 APERTO", "Domani", "-"


# 3. Preparazione dati per la tabella e la mappa
tabella_dati = []
m = folium.Map(location=[43.708, 10.405], zoom_start=13)

for pl in PL_DATA:
    stato, pross_chiusura, pross_riapertura = calcola_stato_pl(
        pl["orari_chiusura"]
    )

    # Dati Tabella
    tabella_dati.append(
        {
            "Passaggio a Livello": pl["nome"],
            "Stato Attuale": stato,
            "Prossima Chiusura": pross_chiusura,
            "Prevista Riapertura": pross_riapertura,
        }
    )

    # Colore Marker Mappa
    color = "red" if stato == "🔴 CHIUSO" else "green"

    # Inserimento Marker sulla Mappa
    folium.Marker(
        location=[pl["lat"], pl["lon"]],
        popup=f"<b>{pl['nome']}</b><br>Stato: {stato}",
        tooltip=pl["nome"],
        icon=folium.Icon(color=color, icon="info-sign"),
    ).add_to(m)

# 4. Visualizzazione nell'interfaccia Streamlit
st.subheader("📋 Tabella Orari e Stato In Tempo Reale")
st.dataframe(pd.DataFrame(tabella_dati), use_container_width=True)

st.subheader("🗺️ Mappa Passaggi a Livello")
st_folium(m, width=900, height=450)
