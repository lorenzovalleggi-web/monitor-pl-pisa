import re

# =====================================================================
# INCOLLA QUI I PROSSIMI DATI DEL SITO
# =====================================================================
dati_da_elaborare = """
[INCOLLA QUI]
"""

def calcola_passaggi_a_livello(testo_completo):
    blocchi = re.split(r'(?i)CHIUDI', testo_completo)
    
    print(f"{'Treno':<8} | {'Partenza':<10} | {'Arrivo SG':<10} | {'🚧 CHIUSURA PL':<18} | {'🟢 APERTURA PL'}")
    print("-" * 75)
    
    for blocco in blocchi:
        if not blocco.strip():
            continue
            
        num_treno = re.search(r'\b(\d{5})\b', blocco)
        num = num_treno.group(1) if num_treno else "N/D"
        
        orari_pisa = re.findall(r'Pisa\s*S\.\s*Rossore.*?([0-2]?\d:[0-5]\d)', blocco, re.DOTALL | re.IGNORECASE)
        orari_sg = re.findall(r'S\.\s*Giuliano\s*Terme.*?([0-2]?\d:[0-5]\d)', blocco, re.DOTALL | re.IGNORECASE)
        
        if orari_pisa and orari_sg:
            # Andata
            if blocco.find("Pisa S. Rossore") < blocco.find("S. Giuliano Terme"):
                ora_partenza = orari_pisa[-1]
                ora_arrivo = orari_sg[0]
            # Ritorno
            else:
                ora_partenza = orari_sg[-1]
                ora_arrivo = orari_pisa[0]
                
            h_p, m_p = map(int, ora_partenza.split(':'))
            h_a, m_a = map(int, ora_arrivo.split(':'))
            
            # Calcolo tempi PL (Chiusura 4 minuti prima, Apertura 1 minuto dopo l'arrivo/transito)
            min_chiusura = (h_p * 60 + m_p) - 4
            min_apertura = (h_a * 60 + m_a) + 1
            
            ora_ch = f"{min_chiusura // 60:02d}:{min_chiusura % 60:02d}"
            ora_ap = f"{min_apertura // 60:02d}:{min_apertura % 60:02d}"
            
            print(f"{num:<8} | {ora_partenza:<10} | {ora_arrivo:<10} | {ora_ch:<18} | {ora_ap}")

# Per testarlo subito sul tuo PC con i dati vecchi basta attivarlo
