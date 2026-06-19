import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="BinarioLibero", layout="wide")

st.title("⚡ BinarioLibero - Mappa Passaggi a Livello")

# Centro area Pisa - San Giuliano Terme
mappa = folium.Map(
    location=[43.7305, 10.4255],
    zoom_start=13
)

# Lista varchi (coordinate reali area Pisa–Lucca ferrovia)
varchi = [
    ("Via Ugo Rindi (Pisa)", 43.7219, 10.3972),
    ("Via di Gagno (Pisa)", 43.7228, 10.3899),
    ("Via XXIV Maggio (Pisa)", 43.7249, 10.3847),
    ("Via U. Dini (Gello)", 43.7468, 10.4096),
    ("Via Gigli (San Giuliano Terme)", 43.7627, 10.4412),
    ("San Giuliano Terme Stazione", 43.7642, 10.4448),
]

# Marker
for nome, lat, lon in varchi:
    folium.Marker(
        location=[lat, lon],
        popup=nome,
        tooltip=nome,
        icon=folium.Icon(color="blue", icon="train", prefix="fa")
    ).add_to(mappa)

st_folium(mappa, width=None, height=650)
