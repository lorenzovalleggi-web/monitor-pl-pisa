import streamlit as st
import datetime, pytz, requests

st.set_page_config(page_title="BinarioLibero", layout="centered")
st.markdown("<style>.stApp { background-color: #0f172a !important; color: #ffffff !important; } * { color: #ffffff !important; }</style>", unsafe_allow_html=True)
st.components.v1.html("<script>setTimeout(function(){ window.parent.location.reload(); }, 30000);</script>", height=0, width=0)

P_H = [5,7,7,8,9,5,6,7,7,8,9,9,9,10,12,12,13,13,14,14,15,15,16,16,17,17,18,18,19,19,20,21,21]
P_M = [31,10,55,55,55,25,13,4,50,50,3,22,50,20,20,50,20,43,20,50,20,50,19,50,20,50,20,50,20,50,50,20,50]
L_H = [6,7,7,7,8,9,9,10,10,12,13]
L_M = [52,8,40,53,15,10,42,12,42,42,12]

st.title("⚡ BinarioLibero Pisa")
try:
    ora = datetime.datetime.now(pytz.timezone('Europe/Rome'))
except:
    ora = datetime.datetime.now()

min_ora = ora.hour * 60 + ora.minute
st.write(f"⏱️ Ora attuale: {ora.strftime('%H:%M:%S')}")

tr_min, tr_dir, tr_num = [], [], []
dt = ora.strftime('%Y-%m-%dT00:00:00')
for staz, direz in [("S06411", "PISA"), ("S06501", "LUCCA")]:
    try:
        url = f"http://www.viaggiatreno.it/viaggiatrenonew/api/esitoPartenze/{staz}/{dt}"
        res = requests.get(url, timeout=2).json().get('tabellone', [])
        for t in res:
            prog = t.get('orarioProgrammato', '')
            if prog and ':' in prog:
                sp = prog.split(':')
                rit = max(0, int(t.get('ritardo', 0) or 0))
                tr_min.append(int(sp[0]) * 60 + int(sp[1]) + rit)
                tr_dir.append(direz)
                tr_num.append(str(t.get('numeroTreno', 'REG')))
    except:
        pass

if not tr_min:
    for i in range(len(P_H)):
        if (P_H[i]*60 + P_M[i]) > min_ora:
            tr_min.append(P_H[i]*60 + P_M[i]); tr_dir.append("LUCCA"); tr_num.append("PROG")
    for i in range(len(L_H)):
        if (L_H[i]*60 + L_M[i]) > min_ora:
            tr_min.append(L_H[i]*60 + L_M[i]); tr_dir.append("PISA"); tr_num.append("PROG")

f_min, f_dir, f_num = [], [], []
for i in range(len(tr_min)):
    if (tr_min[i] + 25) > min_ora:
        f_min.append(tr_min[i]); f_dir.append(tr_dir[i]); f_num.append(tr_num[i])

if f_min:
    idx_p = f_min.index(min(f_min))
    m_v = f_min[idx_p]
    st.info(f"📋 PROSSIMO: REG {f_num[idx_p]} (Dir. {f_dir[idx_p]}) alle {m_v//60:02d}:{m_v%60:02d}")
else:
    st.info("📋 Nessun treno.")

st.markdown("---")
st.write("### 🚊 STATO VARCHI")

N_PL = ["Via Ugo Rindi", "Via di Gagno", "Via XXIV Maggio", "Via U. Dini (Gello)", "Via Gigli (S. Giuliano)", "San Giuliano Terme"]
A_I, A_F = [-4, -4, -3, -1, 4, 5], [2, 2, 3, 5, 10, 11]
R_I, R_F = [15, 15, 14, 11, 11, 9], [21, 21, 20, 17, 17, 15]

for i in range(len(N_PL)):
    chiuso, v_fine, v_dir, p_ch = False, 0, "", 9999
    for j in range(len(f_min)):
        ini = f_min[j] + (A_I[i] if f_dir[j] == "LUCCA" else R_I[i])
        fin = f_min[j] + (A_F[i] if f_dir[j] == "LUCCA" else R_F[i])
        if ini <= min_ora <= fin:
            chiuso, v_fine, v_dir = True, fin, f_dir[j]
            break
        if ini > min_ora and ini < p_ch:
            p_ch = ini

    if chiuso:
        st.error(f"#### {N_PL[i]}\n🛑 CHIUSO | Fino alle {v_fine//60:02d}:{v_fine%60:02d} (Dir. {v_dir})")
    else:
        msg = f"🟢 APERTO | Chiusura: {p_ch//60:02d}:{p_ch%60:02d} (in {p_ch-min_ora} min)" if p_ch != 9999 else "🟢 APERTO | Libero"
        st.success(f"#### {N_PL[i]}\n{msg}")

st.markdown("---")
st.write("© 2026 BinarioLibero")
