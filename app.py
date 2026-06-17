import re

def analizza_tutti_i_treni(testo_completo):
    # Divide il testo usando la parola "CHIUDI" (case-insensitive) per isolare i treni
    blocchi = re.split(r'(?i)CHIUDI', testo_completo)
    
    report_andata = []  # Pisa -> Lucca
    report_ritorno = [] # Lucca -> Pisa
    
    for blocco in blocchi:
        if not blocco.strip():
            continue
            
        # 1. Estrazione Numero Treno
        num_treno_match = re.search(r'\b(18\d{3}|83\d{3})\b', blocco)
        num_treno = num_treno_match.group(1) if num_treno_match else "N/D"
        
        # 2. Rilevamento Direzione (Guarda l'ordine delle stazioni principali nel blocco)
        # Se trova "Pisa S. Rossore" prima di "Lucca" nella testata è Andata, altrimenti Ritorno
        pos_pisa_gen = blocco.find("Pisa S. Rossore")
        pos_lucca_gen = blocco.find("Lucca")
        
        direzione = "RITORNO" # Default se non chiaro
        if pos_pisa_gen != -1 and pos_lucca_gen != -1:
            direzione = "ANDATA" if pos_pisa_gen < pos_lucca_gen else "RITORNO"

        # 3. Estrazione dati S. Giuliano Terme e Pisa S. Rossore nei dettagli delle fermate
        sg_match = re.search(r'S\.\s*Giuliano\s*Terme.*?(?:Arrivo|Partenza):\s*([0-2]\d:[0-5]\d).*?Partenza:\s*([0-2]\d:[0-5]\d)', blocco, re.DOTALL | re.IGNORECASE)
        # Se non trova sia arrivo che partenza (es. se c'è solo una voce), prova a prendere la partenza generica
        if not sg_match:
            sg_match = re.search(r'S\.\s*Giuliano\s*Terme.*?Partenza:\s*([0-2]\d:[0-5]\d)', blocco, re.DOTALL | re.IGNORECASE)
            
        pisa_match = re.search(r'Pisa\s*S\.\s*Rossore.*?(?:Arrivo|Partenza):\s*([0-2]\d:[0-5]\d)', blocco, re.DOTALL | re.IGNORECASE)

        if sg_match and pisa_match:
            # Per il calcolo dei minuti:
            # Se ANDATA (Pisa -> Lucca): il tratto è Pisa S. Rossore (Partenza) -> S. Giuliano (Arrivo)
            # Se RITORNO (Lucca -> Pisa): il tratto è S. Giuliano (Partenza) -> Pisa S. Rossore (Arrivo)
            
            try:
                if direzione == "ANDATA":
                    # Cerca l'orario di partenza da Pisa S. Rossore nei dettagli
                    orario_pisa = pisa_match.group(1)
                    # L'arrivo a San Giuliano è il primo orario catturato dal pattern esteso
                    orario_sg = re.search(r'S\.\s*Giuliano\s*Terme.*?Arrivo:\s*([0-2]\d:[0-5]\d)', blocco, re.DOTALL | re.IGNORECASE).group(1)
                    
                    h_in, m_in = map(int, orario_pisa.split(':'))
                    h_fi, m_fi = map(int, orario_sg.split(':'))
                    stazione_partenza = f"Pisa S.R. ({orario_pisa})"
                    stazione_arrivo = f"S. Giuliano ({orario_sg})"
                else:
                    # RITORNO
                    orario_sg_partenza = sg_match.group(2) if len(sg_match.groups()) > 1 else sg_match.group(1)
                    orario_pisa_arrivo = pisa_match.group(1)
                    
                    h_in, m_in = map(int, orario_sg_partenza.split(':'))
                    h_fi, m_fi = map(int, orario_pisa_arrivo.split(':'))
                    stazione_partenza = f"S. Giuliano ({orario_sg_partenza})"
                    stazione_arrivo = f"Pisa S.R. ({orario_pisa_arrivo})"
                
                # Calcolo effettivo dei minuti
                min_in = h_in * 60 + m_in
                min_fi = h_fi * 60 + m_fi
                if min_fi < min_in:  # Gestione cambio giorno/mezzanotte
                    min_fi += 24 * 60
                    
                durata = min_fi - min_in
                
                info_treno = {
                    "treno": num_treno,
                    "chiave_orario": min_in, # per ordinamento cronologico
                    "partenza": stazione_partenza,
                    "arrivo": stazione_arrivo,
                    "durata": durata
                }
                
                if direzione == "ANDATA":
                    report_andata.append(info_treno)
                else:
                    report_ritorno.append(info_treno)
            except Exception:
                continue

    # Ordinamento cronologico
    report_andata.sort(key=lambda x: x["chiave_orario"])
    report_ritorno.sort(key=lambda x: x["chiave_orario"])

    # Stampa i risultati
    print("=== TRATTA: PISA S. ROSSORE --> LUCCA (ANDATA) ===")
    print(f"{'Treno':<8} | {'Da Stazione (Ora)':<20} | {'A Stazione (Ora)':<20} | {'Durata Tratto Breve'}")
    print("-" * 75)
    for t in report_andata:
        print(f"{t['treno']:<8} | {t['partenza']:<20} | {t['arrivo']:<20} | {t['durata']} min")
        
    print("\n" + "="*50 + "\n")
    
    print("=== TRATTA: LUCCA --> PISA S. ROSSORE (RITORNO) ===")
    print(f"{'Treno':<8} | {'Da Stazione (Ora)':<20} | {'A Stazione (Ora)':<20} | {'Durata Tratto Breve'}")
    print("-" * 75)
    for t in report_ritorno:
        print(f"{t['treno']:<8} | {t['partenza']:<20} | {t['arrivo']:<20} | {t['durata']} min")

# --- INCOLLA I TUOI DATI QUI SOTTO ---
dati_completi = """
[Incolla qui tutto il testo dei treni che hai raccolto oggi]
"""

# Esegui l'analisi finale
# analizza_tutti_i_treni(dati_completi)
