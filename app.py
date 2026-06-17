import re

# =====================================================================
# PROGETTO BASE: VARIABILE AGGIORNATA CON I NUOVI DATI DELLE TRATTE
# =====================================================================
dati_da_elaborare = """
83671
05:31
26min
05:57
Pisa S. Rossore
Lucca
CHIUDI
5:30
5:31
Pisa S. Rossore
Fermata: Pisa S. Rossore
Arrivo: 5:30
Partenza: 5:31
5:36
5:37
S. Giuliano Terme
Fermata: S. Giuliano Terme
Arrivo: 5:36
Partenza: 5:37
5:42
5:43
Rigoli
Fermata: Rigoli
Arrivo: 5:42
Partenza: 5:43
5:48
5:49
Ripafratta
Fermata: Ripafratta
Arrivo: 5:48
Partenza: 5:49
5:57
Lucca
CHIUDI

18553
07:10
26min
07:36
Pisa S. Rossore
Lucca
CHIUDI
7:09
7:10
Pisa S. Rossore
Fermata: Pisa S. Rossore
Arrivo: 7:09
Partenza: 7:10
7:15
7:16
S. Giuliano Terme
Fermata: S. Giuliano Terme
Arrivo: 7:15
Partenza: 7:16
7:24
7:25
Rigoli
Fermata: Rigoli
Arrivo: 7:24
Partenza: 7:25
7:28
7:29
Ripafratta
Fermata: Ripafratta
Arrivo: 7:28
Partenza: 7:29
7:36
Lucca
CHIUDI

83675
07:55
25min
08:20
Pisa S. Rossore
Lucca
CHIUDI
7:54
7:55
Pisa S. Rossore
Fermata: Pisa S. Rossore
Arrivo: 7:54
Partenza: 7:55
8:00
8:01
S. Giuliano Terme
Fermata: S. Giuliano Terme
Arrivo: 8:00
Partenza: 8:01
8:06
8:07
Rigoli
Fermata: Rigoli
Arrivo: 8:06
Partenza: 8:07
8:20
Lucca
CHIUDI

18555
08:55
22min
09:17
Pisa S. Rossore
Lucca
CHIUDI
8:54
8:55
Pisa S. Rossore
Fermata: Pisa S. Rossore
Arrivo: 8:54
Partenza: 8:55
9:00
9:01
S. Giuliano Terme
Fermata: S. Giuliano Terme
Arrivo: 9:00
Partenza: 9:01
9:07
9:08
Ripafratta
Fermata: Ripafratta
Arrivo: 9:07
Partenza: 9:08
9:17
Lucca
CHIUDI

18561
09:55
22min
10:17
Pisa S. Rossore
Lucca
CHIUDI
9:54
9:55
Pisa S. Rossore
Fermata: Pisa S. Rossore
Arrivo: 9:54
Partenza: 9:55
10:00
10:01
S. Giuliano Terme
Fermata: S. Giuliano Terme
Arrivo: 10:00
Partenza: 10:01
10:08
10:09
Ripafratta
Fermata: Ripafratta
Arrivo: 10:08
Partenza: 10:09
10:17
Lucca
CHIUDI
"""

# =====================================================================
# STRUTTURA DI ELABORAZIONE BASE
# =====================================================================
def analizza_tutti_i_treni(testo_completo):
    blocchi = re.split(r'(?i)CHIUDI', testo_completo)
    
    report_andata = []
    report_ritorno = []
    
    for blocco in blocchi:
        if not blocco.strip():
            continue
            
        num_treno_match = re.search(r'\b(\d{5})\b', blocco)
        num_treno = num_treno_match.group(1) if num_treno_match else "N/D"
        
        pos_pisa = blocco.find("Pisa S. Rossore")
        pos_lucca = blocco.find("Lucca")
        
        dettaglio_pisa = re.search(r'Pisa\s*S\.\s*Rossore', blocco, re.IGNORECASE)
        dettaglio_sg = re.search(r'S\.\s*Giuliano\s*Terme', blocco, re.IGNORECASE)
        
        if not dettaglio_pisa or not dettaglio_sg:
            continue
            
        direzione = "RITORNO" if pos_lucca < pos_pisa else "ANDATA"
        
        try:
            if direzione == "ANDATA":
                pisa_partenza = re.search(r'Pisa\s*S\.\s*Rossore.*?Partenza:\s*([0-2]\d:[0-5]\d)', blocco, re.DOTALL | re.IGNORECASE)
                sg_arrivo = re.search(r'S\.\s*Giuliano\s*Terme.*?Arrivo:\s*([0-2]\d:[0-5]\d)', blocco, re.DOTALL | re.IGNORECASE)
                
                if pisa_partenza and sg_arrivo:
                    ora_in, min_in = map(int, pisa_partenza.group(1).split(':'))
                    ora_fi, min_fi = map(int, sg_arrivo.group(1).split(':'))
                    str_partenza = f"Pisa S.R. ({pisa_partenza.group(1)})"
                    str_arrivo = f"S. Giuliano ({sg_arrivo.group(1)})"
                else:
                    continue
            else:
                sg_partenza = re.search(r'S\.\s*Giuliano\s*Terme.*?Partenza:\s*([0-2]\d:[0-5]\d)', blocco, re.DOTALL | re.IGNORECASE)
                pisa_arrivo = re.search(r'Pisa\s*S\.\s*Rossore.*?Arrivo:\s*([0-2]\d:[0-5]\d)', blocco, re.DOTALL | re.IGNORECASE)
                
                if not pisa_arrivo:
                    pisa_arrivo = re.search(r'Pisa\s*S\.\s*Rossore.*?([0-2]\d:[0-5]\d)$', blocco.strip(), re.DOTALL | re.IGNORECASE)
                
                if sg_partenza and pisa_arrivo:
                    ora_in, min_in = map(int, sg_partenza.group(1).split(':'))
                    ora_fi, min_fi = map(int, pisa_arrivo.group(1).split(':'))
                    str_partenza = f"S. Giuliano ({sg_partenza.group(1)})"
                    str_arrivo = f"Pisa S.R. ({pisa_arrivo.group(1)})"
                else:
                    continue
            
            m_tot_in = ora_in * 60 + min_in
            m_tot_fi = ora_fi * 60 + min_fi
            if m_tot_fi < m_tot_in:  
                m_tot_fi += 24 * 60
                
            durata = m_tot_fi - m_tot_in
            
            dati_treno = {
                "treno": num_treno,
                "chiave_tempo": m_tot_in,
                "partenza": str_partenza,
                "arrivo": str_arrivo,
                "durata": durata
            }
            
            if direzione == "ANDATA":
                report_andata.append(dati_treno)
            else:
                report_ritorno.append(dati_treno)
                
        except Exception:
            continue

    report_andata.sort(key=lambda x: x["chiave_tempo"])
    report_ritorno.sort(key=lambda x: x["chiave_tempo"])

    print("=== TRATTA: PISA S. ROSSORE --> LUCCA (ANDATA) ===")
    print(f"{'Treno':<8} | {'Partenza (Ora)':<20} | {'Arrivo (Ora)':<20} | {'Durata Tratto'}")
    print("-" * 75)
    for t in report_andata:
        print(f"{t['treno']:<8} | {t['partenza']:<20} | {t['arrivo']:<20} | {t['durata']} min")
        
    print("\n" + "="*60 + "\n")
    
    print("=== TRATTA: LUCCA --> PISA S. ROSSORE (RITORNO) ===")
    print(f"{'Treno':<8} | {'Partenza (Ora)':<20} | {'Arrivo (Ora)':<20} | {'Durata Tratto'}")
    print("-" * 75)
    for t in report_ritorno:
        print(f"{t['treno']:<8} | {t['partenza']:<20} | {t['arrivo']:<20} | {t['durata']} min")

# Esecuzione
analizza_tutti_i_treni(dati_da_elaborare)
