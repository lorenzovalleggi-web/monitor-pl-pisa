import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="BinarioLibero", layout="wide")

st.title("⚡ BinarioLibero - Passaggi a Livello Pisa–Lucca")
st.caption("Mappa in tempo reale dei passaggi a livello")

# Centro zona reale linea ferroviaria Pisa–Lucca
mappa = folium.Map(
    location=[43.7378, 10.4090],
    zoom_start=13,
    tiles="OpenStreetMap"
)

# 🔴 VARCHI (più allineati alla linea ferroviaria reale)
varchi = [
    ("Via Ugo Rindi", 43.7199, 10.3948),
    ("Via di Gagno", 43.7222, 10.3892),
    ("Via XXIV Maggio", 43.7246, 10.3841),
    ("Via U. Dini (Gello)", 43.7475, 10.4092),
    ("Via Gigli", 43.7620, 10.4405),
    ("San Giuliano Terme", 43.7638, 10.4440),
]

# aggiunta marker
for nome, lat, lon in varchi:
    folium.Marker(
        location=[lat, lon],
        popup=f"<b>{nome}</b>",
        tooltip=nome,
        icon=folium.Icon(color="blue", icon="train", prefix="fa")
    ).add_to(mappa)

st_folium(mappa, width=None, height=700)
