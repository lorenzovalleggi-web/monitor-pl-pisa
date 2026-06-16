import streamlit as st
import datetime, pytz, requests, os
from streamlit_autorefresh import st_autorefresh

# 1. Configurazione Iniziale
st.set_page_config(page_title="BinarioLibero Pisa", page_icon="🚦", layout="centered")

try:
    st_autorefresh(interval=15000, key="datarefresh")
except:
    pass

# Stile CSS compatto
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: #f8fafc; }
    h1, h2, h3, h4, p, span, div { color: #f8fafc !important; }
    a { color: #38bdf8 !important; text-decoration: underline; }
    .stAlert { border-radius: 12px !important; border: none !important; box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important; }
    .stButton>button { background-color: #334155 !important; color: white !important; border-radius: 8px !important; width: 100%; }
    .sponsor-box { background-color: #1e293b; border: 1px dashed #475569; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 10px; color: #94a3b8 !important; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ BinarioLibero")
st.subheader("Meteo passaggi a livello: Pisa - San Giuliano")

if st.button("🔄 Aggiorna Stato In Tempo Reale"):
    st.rerun()

# Gestione Orario
try:
    fuso = pytz.timezone('Europe/Rome')
    ora_adesso = datetime.datetime.now(fuso)
except:
    ora_adesso = datetime.datetime.now()

st.write(f"Ultimo controllo: **{ora_adesso.strftime('%H:%M:%S')}**")
minuti_ora = ora_adesso.hour * 60 + ora_adesso.minute

ORARIO_TABELLA = [
    {"ora": 5, "min": 30, "dir": "LUCCA", "num": "18502"}, {"ora": 5, "min": 51, "dir": "PISA", "num": "18501"},
    {"ora": 6, "min": 23, "dir": "LUCCA", "num": "18504"}, {"ora": 6, "min": 35, "dir": "PISA", "num": "18503"},
    {"ora": 6, "min": 54, "dir": "LUCCA", "num": "18506"}, {"ora": 7, "min": 17, "dir": "PISA", "num": "6915"},
    {"ora": 7, "min": 30, "dir": "LUCCA", "num": "18508"}, {"ora": 7, "min": 47, "dir": "PISA", "num": "18505"},
    {"ora": 8, "min": 23, "dir": "LUCCA", "num": "18514"}, {"ora": 8, "min": 51, "dir": "PISA", "num": "18511"},
    {"ora": 9, "min": 23, "dir": "LUCCA", "num": "18516"}, {"ora": 9, "min": 51, "dir": "PISA", "num": "18515"},
    {"ora": 10, "min": 23, "dir": "LUCCA", "num": "18518"}, {"ora": 10, "min": 51, "dir": "PISA", "num": "18517"},
    {"ora": 11, "min": 23, "dir": "LUCCA", "num": "18520"}, {"ora": 11, "min": 51, "dir": "PISA", "num": "18519"},
    {"ora": 12, "min": 23, "dir": "LUCCA", "num": "18522"}, {"ora": 12, "min": 43, "dir": "PISA", "num": "18521"},
    {"ora": 13, "min": 13, "dir": "LUCCA", "num": "18524"}, {"ora": 13, "min": 36, "dir": "PISA", "num": "18523"},
    {"ora": 13, "min": 53, "dir": "LUCCA", "num": "18526"}, {"ora": 14, "min": 13, "dir": "PISA", "num": "18525"},
    {"ora": 14, "min": 35, "dir": "LUCCA", "num": "18528"}, {"ora": 14, "min": 43, "dir": "PISA", "num": "18527"},
    {"ora": 15, "min": 23, "dir": "LUCCA", "num": "18532"}, {"ora": 15, "min
