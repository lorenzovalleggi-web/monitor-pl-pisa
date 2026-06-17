import re

# =====================================================================
# I TUOI DATI DEL SITO (INSERITI E PRONTI)
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

def analizza_tutti_i_treni(testo_completo):
    blocchi = testo_completo.split("CHIUDI")
    report_andata = []
    
    for blocco in blocchi:
        linee = [l.strip() for l in blocco.split("\n") if l.strip()]
        if not linee:
            continue
            
        # Trova il numero del treno nella prima riga utile
        num_treno = "N/D"
        for linea in linee:
            if linea.isdigit() and len(linea) == 5:
                num_treno = linea
                break
        
        ora_pisa = None
        ora_sg = None
        
        # Scansiona le righe per trovare gli orari precisi di Pisa e San Giuliano
        for i, linea in enumerate(linee):
            if "Pisa S. Rossore" in linea:
                # Cerca la riga "Partenza:" subito sotto
                for j in range(i, min(i+5, len(linee))):
                    if "Partenza:" in linee[j]:
                        ora_pisa = linee[j].split("Partenza:")[-1].strip()
                        break
            
            if "S. Giuliano Terme" in linea:
                # Cerca la riga "Arrivo:" subito sotto
                for j in range(i, min(i+5, len(linee))):
                    if "Arrivo:" in linee[j]:
                        ora_sg = linee[j].split("Arrivo:")[-1].strip()
                        break
                        
        # Se abbiamo trovato entrambi gli orari, calcoliamo la durata
        if ora_pisa and ora_sg:
            try:
                h_in, m_in = map(int, ora_pisa.split(':'))
                h_fi, m_fi = map(int, ora_sg.split(':'))
                
                min_in = h_in * 60 + m_in
                min_fi = h_fi * 60 + m_fi
                
                durata = min_fi - min_in
                
                report_andata.append({
                    "treno": num_treno,
                    "chiave": min_in,
                    "partenza": f"Pisa S.R. ({ora_pisa})",
                    "arrivo": f"S. Giuliano ({ora_sg})",
                    "durata": f"{durata} min"
                })
            except Exception:
                continue

    # Ordina cronologicamente
    report_andata.sort(key=lambda x: x["chiave"])
    
    # Stampa finale pulita
    print("=== TRATTA: PISA S. ROSSORE --> LUCCA (ANDATA) ===")
    print(f"{'Treno':<8} | {'Partenza (Ora)':<20} | {'Arrivo (Ora)':<20} | {'Durata Tratto'}")
    print("-" * 75)
    for t in report_andata:
        print(f"{t['treno']:<8} | {t['partenza']:<20} | {t['arrivo']:<20} | {t['durata']}")

# Esecuzione
analizza_tutti_i_treni(dati_da_elaborare)
