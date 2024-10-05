import pandas as pd
import numpy as np
import re
import os
import sys
from datetime import datetime

# Pfad zum übergeordneten Verzeichnis des aktuellen Skripts
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from src.config import DF_MDB_PATH, DF_MDB_WP_PATH, DF_MDB_WP_STARTDATEN_PATH

df_mdb = pd.read_csv(DF_MDB_PATH)
df_mdb_wp = pd.read_csv(DF_MDB_WP_PATH)


MAX_WP = df_mdb_wp.WP.max()
WP_START = [1949, 1953, 1957, 1961, 1965, 1969, 1972, 1976, 1980, 1983, 1987, 1990, 1994, 1998, 2002, 2005, 2009, 2013, 2017, 2021, 2025]



def replace_sonstige(df_mdb, df_mdb_wp, dimension='PARTEI_KURZ', num_keep = 7):
    """
    keep num_keep most occurences, replace other values by "sonstige"
    """
    
    # e.g. 'CDU', 'SPD'
    # Die häufigsten `num_keep` Werte ermitteln
    values_to_keep = df_mdb_wp[dimension].value_counts().nlargest(num_keep).index.tolist()

    # Alle anderen Werte ermitteln
    values_to_discard = df_mdb[dimension].value_counts().index.difference(values_to_keep).tolist()
    
    # logging.info(f'[{dimension}]. keeping {values_to_keep}. replacing {values_to_discard[:3]} ... with <sonstige>')
    df_mdb[dimension].replace(values_to_discard, 'sonstige', inplace=True)
    df_mdb_wp[dimension].replace(values_to_discard, 'sonstige', inplace=True)
    
    return values_to_keep, values_to_discard, df_mdb, df_mdb_wp

# TODO start move to objects or at least dict
list_of_parteien, list_of_parteien_discard, df_mdb, df_mdb_wp = replace_sonstige(df_mdb, df_mdb_wp, dimension='PARTEI_KURZ', num_keep = 7)
list_of_religion, list_of_religion_discard, df_mdb, df_mdb_wp = replace_sonstige(df_mdb, df_mdb_wp, dimension='RELIGION_MAPPED', num_keep = 6) 
list_of_familienstand, list_of_familienstand_discard, df_mdb, df_mdb_wp = replace_sonstige(df_mdb, df_mdb_wp, dimension='FAMILIENSTAND_MAPPED', num_keep = 10)
list_of_beruf, list_of_beruf_discard, df_mdb, df_mdb_wp = replace_sonstige(df_mdb, df_mdb_wp, dimension='BERUF_MAPPED', num_keep = 18)
list_of_altersklassen = ['< 30', '30 - 40', '40 - 50', '50 - 60', '70 - 80',  '>= 80']
                            
# append 'sonstige' to list of valid values
for list_of_values in [list_of_parteien, list_of_religion, list_of_familienstand, list_of_beruf]:
    list_of_values += ['sonstige']
# TODO End


wp_startdaten = {
    1:datetime(1949, 9, 7), # Der 1. Deutsche Bundestag bestand zwischen dem 7. September 1949[1] und dem 7. September 1953
    2:datetime(1953, 10, 6), # Der 2. Deutsche Bundestag bestand zwischen dem 6. Oktober 1953[1] und dem 6. Oktober 1957
    3:datetime(1957, 10, 15), # Der 3. Deutsche Bundestag bestand zwischen dem 15. Oktober 1957[1] und dem 15. Oktober 1961
    4:datetime(1961, 10, 17), # Der 4. Deutsche Bundestag bestand zwischen dem 17. Oktober 1961[1] und dem 17. Oktober 196
    5:datetime(1965, 10, 19), # Der 5. Deutsche Bundestag bestand zwischen dem 19. Oktober 1965[1] und dem 19. Oktober 1969
    6:datetime(1969, 10, 20), # Der 6. Deutsche Bundestag bestand zwischen dem 20. Oktober 1969[1] und dem 13. Dezember 1972
    7:datetime(1972, 12, 13), #? Der 7. Deutsche Bundestag wurde am 19. November 1972 gewählt
    8:datetime(1976, 12, 14), # Der 8. Deutsche Bundestag bestand zwischen dem 14. Dezember 1976[1] und dem 4. November 1980
    9:datetime(1980, 11, 4),# Der 9. Deutsche Bundestag bestand zwischen dem 4. November 1980[1] und dem 29. März 1983
    10:datetime(1983, 3, 29), # Der 10. Deutsche Bundestag bestand zwischen dem 29. März 1983[1] und dem 18. Februar 1987
    11:datetime(1987, 2, 18), # Der 11. Deutsche Bundestag bestand zwischen dem 18. Februar 1987[1] und dem 20. Dezember 1990
    12:datetime(1990, 12, 20), # Der 12. Deutsche Bundestag bestand zwischen dem 20. Dezember 1990[1] und dem 10. November 1994
    13:datetime(1994, 11, 10), # Der 13. Deutsche Bundestag bestand zwischen dem 10. November 1994[1] und dem 26. Oktober 1998
    14:datetime(1998, 10, 26), # Der 14. Deutsche Bundestag bestand zwischen dem 26. Oktober 1998[1] und dem 17. Oktober 2002
    15:datetime(2002, 10, 17), # Der 15. Deutsche Bundestag bestand zwischen dem 17. Oktober 2002[1] und dem 18. Oktober 2005
    16:datetime(2005, 10, 18), # Der 16. Deutsche Bundestag bestand zwischen dem 18. Oktober 2005[1] und dem 27. Oktober 2009
    17:datetime(2009, 10, 27), # Der 17. Deutsche Bundestag bestand zwischen dem 27. Oktober 2009[1] und dem 22. Oktober 2013
    18:datetime(2013, 10, 22), # Der 18. Deutsche Bundestag bestand vom 22. Oktober 2013 bis zum 24. Oktober 2017
    19:datetime(2017, 10, 24), #  Seine konstituierende Sitzung fand am 24. Oktober 2017 statt,
    20:datetime(2021, 10, 26) #Die Wahlperiode begann mit der konstituierenden Sitzung am 26. Oktober 2021
}

df_wp_startdaten=pd.DataFrame(wp_startdaten, index=[0]).T
df_wp_startdaten.columns =[ 'START_DATE']
print(df_wp_startdaten.head())
df_wp_startdaten.to_csv(DF_MDB_WP_STARTDATEN_PATH) # TODO; move to NB


partei_mapping = {
    'BÜNDNIS 90/DIE GRÜNEN': 'die Grünen',
    'DIE GRÜNEN/BÜNDNIS 90': 'die Grünen',
    'GRÜNE': 'die Grünen',
}


def map_age_to_group(age):
    if age < 30:
        return '< 30'
    elif 30 <= age < 40:
        return '30 - 40'
    elif 40 <= age < 50:
        return '40 - 50'
    elif 50 <= age < 60:
        return '50 - 60'
    elif 60 <= age < 70:
        return '60 - 70'  # Diese Gruppe fehlte in Ihrer ursprünglichen Liste
    elif 70 <= age < 80:
        return '70 - 80'
    else:
        return '>= 80'

religion_mapping = {
    'ohne Angaben': 'unbekannt',
    'evangelisch': 'evangelisch',
    'katholisch': 'katholisch',
    'römisch-katholisch': 'katholisch',
    'UNBEKANNT': 'unbekannt',
    'evangelisch-lutherisch': 'evangelisch',
    'konfessionslos': 'konfessionslos',
    'evangelisch-reformiert': 'evangelisch',
    'religionslos': 'konfessionslos',
    'Atheistin': 'konfessionslos',
    'muslimisch': 'muslimisch',
    'evangelisch-freikirchlich': 'evangelisch',
    'freireligiös': 'sonstige',
    'Islam': 'muslimisch',
    'Atheist': 'konfessionslos',
    'neuapostolisch': 'sonstige',
    'protestantisch': 'evangelisch',
    'humanistisch': 'sonstige',
    'griechisch-orthodox': 'orthodox',
    'alevitisch': 'muslimisch',
    'alt-katholisch': 'katholisch',
    'orthodox': 'orthodox',
    'russisch-orthodox': 'orthodox'
}


family_status_mapping = {
    # Verheiratet
    'verheiratet': 'verheiratet_ohne_kinder',
    'verheiratet, 1 Kind': 'verheiratet_mit_1_kind',
    'verheiratet, 2 Kinder': 'verheiratet_mit_2_kindern',
    'verheiratet, 3 Kinder': 'verheiratet_mit_mehr_als_2_kindern',
    'verheiratet, 4 Kinder': 'verheiratet_mit_mehr_als_2_kindern',
    'verheiratet, 5 Kinder': 'verheiratet_mit_mehr_als_2_kindern',
    'verheiratet, 6 Kinder': 'verheiratet_mit_mehr_als_2_kindern',
    'verheiratet, 7 Kinder': 'verheiratet_mit_mehr_als_2_kindern',
    'verheiratet, 8 Kinder': 'verheiratet_mit_mehr_als_2_kindern',
    'verheiratet, 9 Kinder': 'verheiratet_mit_mehr_als_2_kindern',
    'verheiratet, 10 Kinder': 'verheiratet_mit_mehr_als_2_kindern',
    'verheiratet, 12 Kinder': 'verheiratet_mit_mehr_als_2_kindern',
    'verheiratet, 2 Kinder, 3 Pflegekinder': 'verheiratet_mit_mehr_als_2_kindern',
    'verheiratet, 1 Kinder, 3 Pflegekinder': 'verheiratet_mit_mehr_als_2_kindern',
    'verheiratet, 1 Adoptivkind': 'verheiratet_mit_1_kind',

    # Ledig
    'ledig': 'ledig_ohne_kinder',
    'ledig, 1 Kind': 'ledig_mit_1_kind',
    'ledig, 2 Kinder': 'ledig_mit_2_kindern',
    'ledig, 3 Kinder': 'ledig_mit_mehr_als_2_kindern',
    'ledig, 4 Kinder': 'ledig_mit_mehr_als_2_kindern',
    'ledig, in Lebensgemeinschaft lebend, 4 Kinder': 'ledig_mit_mehr_als_2_kindern',

    # Geschieden
    'geschieden': 'geschieden_ohne_kinder',
    'geschieden, 1 Kind': 'geschieden_mit_1_kind',
    'geschieden, 2 Kinder': 'geschieden_mit_2_kindern',
    'geschieden, 3 Kinder': 'geschieden_mit_mehr_als_2_kindern',
    'geschieden, 4 Kinder': 'geschieden_mit_mehr_als_2_kindern',
    'geschieden, 5 Kinder': 'geschieden_mit_mehr_als_2_kindern',

    # Verwitwet
    'verwitwet': 'verwitwet_ohne_kinder',
    'verwitwet, 1 Kind': 'verwitwet_mit_1_kind',
    'verwitwet, 2 Kinder': 'verwitwet_mit_2_kindern',
    'verwitwet, 3 Kinder': 'verwitwet_mit_mehr_als_2_kindern',
    'verwitwet, 4 Kinder': 'verwitwet_mit_mehr_als_2_kindern',
    'verwitwet, 5 Kinder': 'verwitwet_mit_mehr_als_2_kindern',
    'verwitwet, 6 Kinder': 'verwitwet_mit_mehr_als_2_kindern',

    # Getrennt lebend
    'getrennt lebend, 2 Kinder': 'getrennt_lebend_mit_2_kindern',
    'getrennt lebend, 3 Kinder': 'getrennt_lebend_mit_mehr_als_2_kindern',
    'getrennt lebend, 4 Kinder': 'getrennt_lebend_mit_mehr_als_2_kindern',

    # Unverheiratet
    'unverheiratet': 'unverheiratet_ohne_kinder',
    'unverheiratet, 1 Kind': 'unverheiratet_mit_1_kind',
    'unverheiratet, 2 Kinder': 'unverheiratet_mit_2_kindern',
    'unverheiratet, 1 Pflegekind': 'unverheiratet_mit_1_kind',

    # Partnerschaften
    'Lebensgemeinschaft': 'partnerschaft_ohne_kinder',
    'eheähnl. Lebensgemeinschaft, 1 Kind': 'partnerschaft_mit_1_kind',
    'eheähnl. Lebensgemeinschaft, 2 Kinder': 'partnerschaft_mit_2_kindern',
    'eingetragene Lebenspartnerschaft': 'partnerschaft_ohne_kinder',
    'verpartnert': 'partnerschaft_ohne_kinder',
    'verpartnert, 2 Kinder': 'partnerschaft_mit_2_kindern',
    'gleichgeschlechtliche Partnerschaft': 'partnerschaft_ohne_kinder',
    'lesbische Lebensgemeinschaft, 1 Kind': 'partnerschaft_mit_1_kind',

    # Sonstige
    'patchwork, 2 Kinder': 'sonstige_mit_2_kindern',
    'alleinerziehend, 3 Kinder': 'sonstige_mit_mehr_als_2_kindern',
    'verlobt': 'sonstige_ohne_kinder',

    # Nur Kinderzahl angegeben
    '1 Kind': 'mit_1_kind',
    '2 Kinder': 'mit_2_kindern',
    '3 Kinder': 'mit_mehr_als_2_kindern',
    '4 Kinder': 'mit_mehr_als_2_kindern',
    '5 Kinder': 'mit_mehr_als_2_kindern',

    # Keine Angaben
    'keine Angaben': 'unbekannt',
    'UNBEKANNT': 'unbekannt',
    'ohne Angaben': 'unbekannt'
}





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




# neu mit hilfe von claude
beruf_klassifizierung = {
    'Jurist*in': [
        'anwalt', 'jurist', 'richter', 'notar', re.compile('dr.*\s*jur.*'), 'syndikus', 'rechtsberater',
        'staatsanwalt', 'volljurist'
    ],
    'Land-/Forstwirt*in': [
        'landwirt', re.compile('^[a-z]bauer\s'), 'bauer', re.compile('agrar+'), 'forst', 'winzer', 'ökonomierat'
    ],
    'Unternehmer*in': [
        'unternehmer', 'fabrikant', 'geschäftsführer'
    ],
    'Ingenieur*in': [
        'ingenieur', 'maschinenbau', 'architekt', re.compile('dipl.*-ing'), 'bauingenieur', 'elektroingenieur'
    ],
    'Journalist*in': [
        'journalist', 'redakteur', 'publizist', 'schriftsteller', 'pressesprecher', 'chefredakteur'
    ],
    'Verleger*in': [
        'verleger', 'verlags'
    ],
    'Lehrer*in': [
        'erzieher', 'pädagog', 'lehrer', 'studienrat', 'studiendirektor', 'schulrat',
        'grundschul', 'hauptshul', 'sonderschul', 'waldorf', 'realschul', 'gymnasi',
        'volkshochschu', 'berufsschul', 'fremdsprachen', 'schul', 'rektor', 'konrektor'
    ],
    'Professor*in': [
        'dozent', 'professor', 'prof.', 'hochschull', 'hochschulpr', 'universitätsprofessor'
    ],
    'Kaufmann/-frau': [
        'kaufm', 'einzelhandel', 'großhandel', 'handelsfachwirt'
    ],
    'Volkswirt*in': [
        'volkswirt', re.compile('dipl.*-volkswirt')
    ],
    'Berufspolitiker*in': [
        'regierungsangestellt', 'stadtamtmann', 'stadtoberinspektor', 'landesgeschäftsführer',
        re.compile('landr(at|ätin)'), re.compile('ministerialr(a|ä)t'), 'staatssekret', 'bürgermeist', 
        'regierungsrat', re.compile('regierungs(vize)*präs'), 'regierung',
        'stadtdirektor', 'ministerialdirektor', 'regierungsdirektor', 'gemeindedirektor',
        'minister', 'bundeskanz', 'bundestagsp', re.compile('präsident(in)* d\.*b\.*t\.*'),
        'abgeordneter', 'parlamentarischer staatssekretär', 'staatsminister'
    ],
    'Arzt/Ärztin': [
        'arzt', 'psycholog', 'psychother', 'apotheker', 'mediziner', 'facharzt', 'zahnarzt', 'tierarzt'
    ],
    'Theolog*in': [
        'pfarrer', 'theolog', 'diakon', 'pastor', 'priester'
    ],
    'Betriebswirt*in': [
        'betriebswirt', 'verwaltungs', 'steuerberater', 'bankdirektor', re.compile('dipl.*-betriebswirt')
    ],
    'Wirtschaftswissenschaftler*in': [
        'wirtschaftsw', 'ökonom', 'prokurist', 'finanzwirt', 'wirtschaftsprüfer'
    ],
    'Geisteswissenschaftler*in': [
        'politolog', 'politikwiss', 'historik', 'philosoph', 'philolog', 'soziolog', 
        'sozialwissensch', 'kulturwissenschaft', 'sprachwissenschaftler'
    ],
    'Naturwissenschaftler*in': [
        'chemik', 'chemie', 'physik', 'geophysik', 'biolog', 'mathemat', 'informat',
        'geologe', 'biochemiker'
    ],
    'Handwerker*in': [
        'elektro', 'fahrzeug', 'handwerk', 'mechanik', 'schlosser', 'maurer', 'beton', 
        'maler', 'lackier', 'tischler', 'schreiner', 'bäcker', 'konditor', 'koch', 'köchin', 
        'müller', 'bergmann', 'werkzeugmacher', 'zimmermann', 'fleischer', 'metzger'
    ],
    'Militär': [
        'leutnant', re.compile('oberst(?!u)'), 'soldat', re.compile('general\s'), 'offizier', 
        'hauptmann', 'major'
    ],
    'Beamter': [
        'beamter', 'beamtin', 'verwaltungsbeamter', 'polizeibeamter'
    ],
    'Soziale Berufe': [
        'sozialarbeiter', 'sozialpädagoge', re.compile('dipl.*-sozi'), 'erzieher'
    ],
    'Medizinische Fachkräfte': [
        'krankenschwester', 'krankenpfleger', 'pflegekraft', 'hebamme', 'sanitäter',
        'medizinisch-technischer assistent'
    ],
    'Künstlerische Berufe': [
        'künstler', 'musiker', 'schauspieler', 'sänger', 'maler', 'bildhauer'
    ],
    'Technische Berufe': [
        'techniker', 'mechatroniker', 'elektroniker', re.compile('dipl.*-tech')
    ],
    'Sonstige': [
        'hausfrau', 'student', 'rentner', 'angestellter', 'arbeiter', 'selbständiger',
        re.compile('dipl.*'), 'freiberufler'
    ]
}

def klassifiziere_beruf(beruf):
    beruf_lower = beruf.lower()
    for kategorie, muster in beruf_klassifizierung.items():
        for m in muster:
            if isinstance(m, str) and m in beruf_lower:
                return kategorie
            elif isinstance(m, re.Pattern) and m.search(beruf_lower):
                return kategorie
    return 'Sonstige'





# alt, 2021
def get_dict_berufe():
    dict_berufe={}
    dict_berufe['Jurist*in'] = ['anwalt', 'jurist', 'richter', 'notar', re.compile('dr.*\s*jur.*'), 'syndikus', 'rechtsberater']
    dict_berufe['Land-/Forstwirt*in'] = ['landwirt', '^[a-z]bauer\s', 'bauer', re.compile('agrar+'), 'forst']
    dict_berufe['Unterehmer*in'] = ['unternehmer'] # 'geschäftsführer' passt leider nicht wegen z.B. Parl. Geschäftssführer
    dict_berufe['Ingenieur*in'] = ['ingenieur', 'maschinenbau', 'architekt']
    dict_berufe['Journalist*in'] = ['journalist', 'redakteur', 'publizist', 'schriftsteller']
    dict_berufe['Verleger*in'] = ['verleger', 'verlags']
    
    # direktor: nö, sonst bezirksdirektor museumsdirektor etc
    dict_berufe['Lehrer*in'] = ['erzieher', 'pädagog', 'lehrer', 'studienrat', 'studiendirektor', 'schulrat',
                                'grundschul', 'hauptshul', 'sonderschul', 'waldorf', 'realschul', 'gymnasi',
                                'volkshochschu', 'berufsschul', 'fremdsprachen',
                               'schul'] #evtl trennen Erzieher - Lehrer
    dict_berufe['Professor*in'] = ['dozent', 'professor', 'prof.', 'hochschull', 'hochschulpr']
    dict_berufe['Kaufmann/-frau'] = ['kaufm']
    dict_berufe['Volkswirt*in'] = ['volkswirt']
    dict_berufe['Berufspolitiker*in'] = ['regierungsangestellt', 'stadtamtmann', 'stadtoberinspektor', 'Landesgeschäftsführer',
                                        'landr(at|ätin)', re.compile('ministerialr(a|ä)t'), 'staatssekret', 'bürgermeist', 
                                         'regierungsrat', re.compile('regierungs(vize)*präs'), 'regierung',
                                         'stadtdirektor', 'ministerialdirektor', 'regierungsdirektor', 'gemeindedirektor', 'regierungsdirektor',
                                         'minister', 'bundeskanz', 'bundestagsp', re.compile('präsident(in)* d\.*b\.*t\.*')]
    dict_berufe['Arzt/Ärztin'] = ['arzt', 'psycholog', 'psychother', 'apotheker']
    dict_berufe['Theolog*in'] = ['pfarrer', 'theolog', 'diakon']
    dict_berufe['Betriebswirt*in'] = ['betriebswirt', 'verwaltungs', 'steuerberater', 'bankdirektor']
    dict_berufe['Wirtschaftswissenschaftler*in'] = ['wirtschaftsw', 'ökonom', 'prokurist']
    dict_berufe['Geisteswissenschaftler*in'] = ['politolog', 'politikwiss', 'historik', 'philosoph', 'philolog', 'soziolog', 'sozialwissensch', 'kulturwissenschaft']
    dict_berufe['Naturwissenschaftler*in'] = ['chemik', 'chemie', 'physik', 'geophysik', 'biolog', 'mathemat', 'informat']
    
    dict_berufe['Handwerker*in'] = ['elektro', 'fahrzeug', 'handwerk', 'mechanik',
                                   'schlosser', 'maurer', 'beton', 'maler', 'lackier', 'tischler', 'schreiner',
                                   'bäcker', 'konditor' 'koch', 'köchin', 'müller', 'bergmann', 'werkzeugmacher']
    dict_berufe['Militär'] = ['leutnant', 'oberst^u', 'soldat', re.compile('general\s')] # not oberstudienrat ;)
    return dict_berufe
    dict_berufe['Beamter'] = ['beamter']# problematisch: Berufspolitiker, Lehrer, Militär sind auch beamte

