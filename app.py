st.markdown("---")
st.write("### 🚊 STATO VARCHI")

# Liste sincronizzate al minuto con le tabelle sopra
N_PL = [
    "Via Ugo Rindi", 
    "Via di Gagno", 
    "Via XXIV Maggio", 
    "Via U. Dini (Gello)", 
    "Via Gigli (S. Giuliano)", 
    "San Giuliano Terme"
]

# Direzione LUCCA (Andata): minuti rispetto a partenza da Pisa
A_I = [-4, -4, -3, -1,  4,  5]
A_F = [ 2,  2,  3,  5, 10, 11]

# Direzione PISA (Ritorno): minuti rispetto a passaggio da S. Giuliano
R_I = [15, 15, 14, 11, 11,  9]
R_F = [21, 21, 20, 17, 17, 15]

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
