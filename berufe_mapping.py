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
    df[column] = df[column].str.replace('dipl.-', '')
    df[column] = df[column].str.replace('diplom-', '')
    df[column] = df[column].str.replace('diplom ', '')
    df[column] = df[column].str.replace(' (fh)', '')
    df[column] = df[column].str.replace(' (ba)', '')
    df[column] = df[column].str.replace(' (b. a.)', '')
    df[column] = df[column].str.replace(' (b.a.)', '')
    df[column] = df[column].str.replace(' (mba)', '')
    df[column] = df[column].str.replace(' (m. sc.)', '')
    df[column] = df[column].str.replace(' (msc)', '')

    df[column] = df[column].str.replace(' a. d.', '')
    df[column] = df[column].str.replace(' i. r.', '')
    
    # ärztin => artz, anwältin => anwalt. sonst klappt fast immer: in => ''
    df[column] = df[column].str.replace('ärztin', 'arzt')
    df[column] = df[column].str.replace('anwältin', 'anwalt')
    
    # letztes 'in' weglassen wenn mindestens 3 andere Buchstaben vorher
    df[column] = df[column].str.replace(r"\+{3,}in", '')
    
    return df 



class Beruf:
    def __init__(self, male='lehrer', female='lehrerin'):
        self.male=male
        self.female=female


class Berufsklasse:
    
    def __init__(self, primary=Beruf('lehrer', 'lehrerin'), substitutes={Beruf('studienrat', 'studienrätin'), Beruf('oberstudienrat', 'oberstudienrätin')}):
        self.primary=primary
        self.substitutes=substitutes
        
    
    def belongs_to(self, beruf=Beruf('grundschullehrer', 'grundschullehrerin')):
        for substitute in self.substitutes:
            if (another_beruf.male in substitute.male) or (substitute.male in another_beruf.male):
                return True
        return False