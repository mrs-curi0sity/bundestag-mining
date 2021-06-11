import pandas as pd
import numpy as np
import re

def basic_cleaning_berufe(df, column = 'BERUF_MAPPED'):
    # leere einträge durch <unbekannt> ersetzen
    df[column].fillna('unbekannt', inplace=True)
    
    # lowercase everything
    df[column] = df[column].str.lower()

    # Geschäftsführer, Parl. Staatssekretär => Geschäftsführer, Rechtsanwalt, Parl. Staatssekretär a. D.' = 'Rechtsanwalt'
    df[column] = df[column].apply(lambda beruf: beruf.split(',')[0])

    #Bäckermeister und Konditor  => Bäckermeister, Rechtsanwalt und Fachanwalt für Steuerrecht  => Rechtsanwalt
    df[column] = df[column].apply(lambda beruf: beruf.split(' und ')[0])
    
    #Ingenieur für Maschinenbau => Ingenieur, Arzt für Allgemeinmedizin => Arzt
    df[column] = df[column].apply(lambda beruf: beruf.split(' für ')[0])

    # Kaufmann / Informatiker => Kaufmann
    df[column] = df[column].apply(lambda beruf: beruf.split(' / ')[0])

    # Dipl.-Kaufmann => Kaufmann, Dipl.-Ingenieur => Ingenieur usw
    df[column] = df[column].apply(lambda x: re.sub("dipl(om|\.*)", '', x))
    
    # Ingenieur (FH) => ingenieur
    df[column] = df[column].apply(lambda x: re.sub('\(*f\.*h\.*\)*', '', x))
    
    # Polotologe BA => Politologe
    df[column] = df[column].apply(lambda x: re.sub('\s\(*b\.*\s*a\.*\)*', '', x))
    
    # Philosoph M BA => 
    df[column] = df[column].apply(lambda x: re.sub('\s\(*m\.*\s*b\.*a\.*\)*', '', x))
    
    # Msc M.Sc.
    df[column] = df[column].apply(lambda x: re.sub('\s\(*m\.*\s*s\.*c\.*\)*', '', x))

    # a.D. a.d. ad
    df[column] = df[column].apply(lambda x: re.sub('\(*a\.*\s*d\.*\)*', '', x))
    
    # i.r.
    # df[column] = df[column].apply(lambda x: re.sub('\(*i\.*\s*r\.*\)*', '', x))
    
    # ärztin => artz, anwältin => anwalt. sonst klappt fast immer: in => ''
    df[column] = df[column].str.replace('ärztin', 'arzt', regex=False)
    df[column] = df[column].str.replace('anwältin', 'anwalt', regex=False)
    df[column] = df[column].str.replace('frau', 'mann', regex=False) # e.g. kauffrau => kaufmann
     
    # letztes 'in' weglassen (ends with in)
    df[column] = df[column].apply(lambda x: re.sub("in$", '', x))
    
    df[column] = df[column].apply(lambda x: x.strip())
    return df 


