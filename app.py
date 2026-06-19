import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="BinarioLibero",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ BinarioLibero")
st.subheader("Mappa passaggi a livello Pisa - Lucca")

mappa = folium.Map(
    location=[43.74, 10.42],
    zoom_start=13
)

st_folium(
    mappa,
    width=None,
    height=600
)
