import re

def analizza_tutti_i_treni(testo_completo):
    # Divide il testo usando la parola "CHIUDI" per isolare ogni treno
    blocchi = re.split(r'(?i)CHIUDI', testo_completo)
    
    report_andata = []  # Pisa -> Lucca
    report_ritorno = [] # Lucca -> Pisa
    
    for blocco in blocchi:
        if not blocco.strip():
            continue
            
        # 1. Estrazione Numero Treno
        num_treno_match = re.search(r'\b(\d{5})\b', blocco)
        num_treno = num_treno_match.group(1) if num_treno_match else "N/D"
        
        # 2. Rilevamento Direzione basato sulla sequenza delle fermate
        pos_pisa = blocco.find("Pisa S. Rossore")
        pos_lucca = blocco.find("Lucca")
        
        # Cerchiamo di capire l'ordine cronologico nel dettaglio fermate
        dettaglio_pisa = re.search(r'Pisa\s*S\.\s*Rossore', blocco, re.IGNORECASE)
        dettaglio_sg = re.search(r'S\.\s*Giuliano\s*Terme', blocco, re.IGNORECASE)
        
        if not dettaglio_pisa or not dettaglio_sg:
            continue
            
        direzione = "RITORNO" if pos_lucca < pos_pisa else "ANDATA"
        
        try:
            if direzione == "ANDATA":
                # PISA -> LUCCA (Tratto breve: Partenza Pisa S.R. -> Arrivo S. Giuliano)
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
                # LUCCA -> PISA (Tratto breve: Partenza S. Giuliano -> Arrivo Pisa S.R.)
                sg_partenza = re.search(r'S\.\s*Giuliano\s*Terme.*?Partenza:\s*([0-2]\d:[0-5]\d)', blocco, re.DOTALL | re.IGNORECASE)
                pisa_arrivo = re.search(r'Pisa\s*S\.\s*Rossore.*?Arrivo:\s*([0-2]\d:[0-5]\d)', blocco, re.DOTALL | re.IGNORECASE)
                
                # Fallback se a Pisa S. Rossore c'è solo l'orario senza la scritta "Arrivo:"
                if not pisa_arrivo:
                    pisa_arrivo = re.search(r'Pisa\s*S\.\s*Rossore.*?([0-2]\d:[0-5]\d)$', blocco.strip(), re.DOTALL | re.IGNORECASE)
                
                if sg_partenza and pisa_arrivo:
                    ora_in, min_in = map(int, sg_partenza.group(1).split(':'))
                    ora_fi, min_fi = map(int, pisa_arrivo.group(1).split(':'))
                    str_partenza = f"S. Giuliano ({sg_partenza.group(1)})"
                    str_arrivo = f"Pisa S.R. ({pisa_arrivo.group(1)})"
                else:
                    continue
            
            # Calcolo matematico della durata del tratto
            m_tot_in = ora_in * 60 + min_in
            m_tot_fi = ora_fi * 60 + min_fi
            if m_tot_fi < m_tot_in:  # Gestione superamento mezzanotte
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

    # Ordinamento cronologico dei passaggi
    report_andata.sort(key=lambda x: x["chiave_tempo"])
    report_ritorno.sort(key=lambda x: x["chiave_tempo"])

    # Output tabellare
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

# =====================================================================
# INCOLLA QUI SOTTO TUTTI I TUOI DATI (VECCHI E NUOVI) TRA LE TRE VIRGOLETTE
# =====================================================================
dati_da_elaborare = """

[INCOLLA QUI IL TESTO COPIATO DALL'APP]

"""

# Esecuzione del software
analizza_tutti_i_treni(dati_da_elaborare)
