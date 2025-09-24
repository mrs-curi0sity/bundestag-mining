import pandas as pd
import numpy as np
import re
import os
import sys
from datetime import datetime
import colorsys

# Pfad zum übergeordneten Verzeichnis des aktuellen Skripts
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
from src.config import DF_MDB_PATH, DF_MDB_WP_PATH, DF_MDB_WP_STARTDATEN_PATH

from src.config import (
    LIST_OF_PARTEIEN as list_of_parteien,
    LIST_OF_RELIGION as list_of_religion, 
    LIST_OF_FAMILIENSTAND as list_of_familienstand,
    LIST_OF_CHILDREN as list_of_children,
    LIST_OF_BERUF as list_of_beruf,
    LIST_OF_ALTERSKLASSEN as list_of_altersklassen
)




def replace_sonstige(df, dimension, num_keep=7):
    """
    Behält maximal num_keep der am häufigsten vorkommenden Werte,
    ersetzt andere Werte durch "sonstige".
    Wenn weniger als num_keep verschiedene Werte vorhanden sind,
    werden alle vorhandenen Werte behalten.
    """
    df = df.copy()
    
    # Häufigkeiten aus dem Wide-Format berechnen
    # (berücksichtigt Mehrfachmitgliedschaften automatisch)
    unique_values = df[dimension].nunique()
    actual_num_keep = min(num_keep, unique_values)
    
    values_to_keep = df[dimension].value_counts().nlargest(actual_num_keep).index.tolist()
    values_to_discard = df[dimension].value_counts().index.difference(values_to_keep).tolist()
    
    if values_to_discard:
        df[dimension].replace(values_to_discard, 'sonstige', inplace=True)
    
    return values_to_keep, values_to_discard, df

list_of_altersklassen = ['< 30', '30 - 40', '40 - 50', '50 - 60', '> 60']


# Neue Liste für Kinder
list_of_children = [
    'ohne Kinder', 
    'mit einem Kind', 
    'mit zwei Kindern', 
    '> zwei Kinder', 
    'keine Angaben'
]


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
    20:datetime(2021, 10, 26), #Die Wahlperiode begann mit der konstituierenden Sitzung am 26. Oktober 2021
    21:datetime(2025, 2, 23)
}


partei_mapping = {
    'BÜNDNIS 90/DIE GRÜNEN': 'die Grünen',
    'DIE GRÜNEN/BÜNDNIS 90': 'die Grünen',
    'GRÜNE': 'die Grünen',
    'PDS': 'DIE LINKE.',           # Parteifusion 2007
    'PDS/LL': 'DIE LINKE.',        # Übergangsbezeichnung vor Fusion
}


religion_mapping = {
    # Evangelisch/Protestantisch (~1400 nach Mapping)
    'evangelisch': 'evangelisch',
    'evangelisch-lutherisch': 'evangelisch',
    'evangelisch-reformiert': 'evangelisch',
    'evangelisch-freikirchlich': 'evangelisch',
    'protestantisch': 'evangelisch',
    'evangelisch-altreformiert': 'evangelisch',
    'christlich-freikirchlich': 'evangelisch',
    'evangelisch-protestantisch': 'evangelisch',
    
    # Katholisch (~1300 nach Mapping)
    'katholisch': 'katholisch',
    'römisch-katholisch': 'katholisch',
    'alt-katholisch': 'katholisch',

    # Unbekannt/Keine Angaben (~1600 nach Mapping)
    'ohne Angaben': 'unbekannt',
    'UNBEKANNT': 'unbekannt',
    
    # Konfessionslos (~250 nach Mapping)
    'konfessionslos': 'konfessionslos',
    'religionslos': 'konfessionslos',
    'Atheist': 'konfessionslos',
    'Atheistin': 'konfessionslos',
    
    # Muslimisch (~16 nach Mapping)
    'muslimisch': 'muslimisch',
    'Islam': 'muslimisch',
    'alevitisch': 'muslimisch',
    
    # Orthodox (~4 nach Mapping)
    'griechisch-orthodox': 'orthodox',
    'russisch-orthodox': 'orthodox',
    
    # Kleine Kategorien (jeweils 2-3)
    'freireligiös': 'freireligiös',
    'neuapostolisch': 'neuapostolisch',
    'humanistisch': 'humanistisch',
}

def map_family_status(status):
    """
    Maps detailed family status to both relationship status and number of children.
    
    Args:
        status (str): Original family status string
        
    Returns:
        tuple: (relationship status, children category)
    """

    if pd.isna(status):
        return 'keine Angaben', 'keine Angaben'
    
    status = str(status).lower().strip()
    
    # Initialisierung
    relationship_status = 'keine Angaben'
    children_status = 'ohne Kinder'
    
    # Kinderanzahl extrahieren (verbessert)
    num_children = 0
    if any(word in status for word in ['kind', 'pflege', 'adoptiv']):
        # Alle Zahlen finden und summieren
        numbers = re.findall(r'\b(\d+)\s*(?:kind|pflege|adoptiv)', status)
        if numbers:
            num_children = sum(int(num) for num in numbers)
        elif any(word in status for word in ['kind', 'pflege', 'adoptiv']):
            # Falls "kind" erwähnt aber keine Zahl: mindestens 1
            num_children = 1
    
    # Kinderanzahl kategorisieren
    if num_children == 1:
        children_status = 'mit einem Kind'
    elif num_children == 2:
        children_status = 'mit zwei Kindern'
    elif num_children > 2:
        children_status = '> zwei Kinder'
    
    # Beziehungsstatus mapping (unverändert)
    if status in ['nan', 'keine angaben', 'ohne angaben', 'unbekannt', '']:
        relationship_status = 'keine Angaben'
        children_status = 'keine Angaben'
    elif 'verheiratet' in status:
        relationship_status = 'verheiratet'
    elif 'ledig' in status:
        relationship_status = 'ledig'
    elif 'geschieden' in status:
        relationship_status = 'geschieden'
    elif 'verwitwet' in status:
        relationship_status = 'verwitwet'
    elif any(x in status for x in ['lebensgemeinschaft', 'verpartnert', 'eingetragene lebenspartnerschaft']):
        relationship_status = 'Lebenspartnerschaft'
    elif 'getrennt lebend' in status:
        relationship_status = 'getrennt lebend'
    elif 'alleinerziehend' in status:
        relationship_status = 'alleinerziehend'
    elif 'verlobt' in status:
        relationship_status = 'ledig'
    else:
        relationship_status = 'sonstige'
    
    return relationship_status, children_status



def map_age_to_group(age):
    if age < 30:
        return '< 30'
    elif age < 40:
        return '30 - 40'
    elif age < 50:
        return '40 - 50'
    elif age < 60:
        return '50 - 60'
    else:
        return '> 60'


def basic_cleaning_berufe(df, column='BERUF_MAPPED'):
    """
    Bereinigt Berufsbezeichnungen für bessere Kategorisierung.
    Entfernt Titel, Zusätze und normalisiert Gender-Formen.
    """
    df = df.copy()
    
    # SCHRITT 1: Grundbereinigung
    # PANDAS FIX: Nicht inplace auf Series, sondern auf DataFrame
    df[column] = df[column].fillna('unbekannt')  # Statt .fillna('unbekannt', inplace=True)
    df[column] = df[column].str.lower()

    # SCHRITT 2: Klammern-Inhalte entfernen
    # Regex: \( = öffnende Klammer, [^)]* = alles außer schließender Klammer, \) = schließende Klammer
    # Beispiel: "Ingenieur (FH)" -> "Ingenieur "
    df[column] = df[column].apply(lambda x: re.sub(r'\([^)]*\)', '', x))
    
    # SCHRITT 3: Mehrfachberufe aufteilen - nur ersten Teil behalten
    df[column] = df[column].apply(lambda beruf: beruf.split(',')[0])
    df[column] = df[column].apply(lambda beruf: beruf.split(' und ')[0])
    df[column] = df[column].apply(lambda beruf: beruf.split(' für ')[0])
    df[column] = df[column].apply(lambda beruf: beruf.split(' / ')[0])

    # SCHRITT 4: Titel und Abschlüsse entfernen
    # Regex: dipl(om|\.*-*) = "dipl" gefolgt von "om" ODER beliebigen Punkten und Bindestrichen
    # Beispiele: "dipl.-kaufmann", "diplom-ingenieur" -> "kaufmann", "ingenieur"
    df[column] = df[column].apply(lambda x: re.sub(r'dipl(om|\.*-*)', '', x))
    
    # Regex: \s* = beliebige Leerzeichen, \(* = optionale Klammern
    # [fm] = f oder m (für FH/MA), [hasbc] = h,a,s,b,c (für verschiedene Abschlüsse)
    # Entfernt: "FH", "MA", "MSc", "BA", etc.
    #df[column] = df[column].apply(lambda x: re.sub(r'\s*\(*[fm]\.*\s*[hasbc]\.*[asc]*\.*\)*', '', x))
    
    # Regex: \s = Leerzeichen, \(* = optionale Klammern, b\.*\s*a\.* = "B.A." in verschiedenen Schreibweisen
    df[column] = df[column].apply(lambda x: re.sub(r'\s\(*b\.*\s*a\.*\)*', '', x))
    
    # Regex für Master-Abschlüsse: M.A., M.Sc., M.B.A., etc.
    df[column] = df[column].apply(lambda x: re.sub(r'\s\(*m\.*\s*[abs]\.*[asc]*\.*\)*', '', x))
    
    # Regex: \(* = optionale Klammern, a\.*\s*d\.* = "a.D." (außer Dienst)
    df[column] = df[column].apply(lambda x: re.sub(r'\(*a\.*\s*d\.*\)*', '', x))
    
    # Regex: i\.*\s*r\. = "i.R." (im Ruhestand)
    df[column] = df[column].apply(lambda x: re.sub(r'i\.*\s*r\.', '', x))
    
    # SCHRITT 5: Gender-Normalisierung 
    # Nur explizite Zuordnungen - kein generisches Ersetzen!
    gender_replacements = {
        'ärztin': 'arzt', 
        'anwältin': 'anwalt', 
        'lehrerin': 'lehrer',
        'professorin': 'professor', 
        'ingenieurin': 'ingenieur',
        'juristin': 'jurist',
        'redakteurin': 'redakteur',
        'geschäftsführerin': 'geschäftsführer',
        'kauffrau': 'kaufmann',
        'industriekauffrau': 'industriekaufmann',
        'bankkauffrau': 'bankkaufmann',
        'politikwissenschaftlerin':'politikwissenschaftler',
        'pädagogin':'pädagoge'
    }
    
    for female, male in gender_replacements.items():
        df[column] = df[column].str.replace(female, male, regex=False)
    
    # SCHRITT 6: Whitespace-Bereinigung
    # Regex: \s+ = ein oder mehr aufeinanderfolgende Whitespace-Zeichen
    # Ersetzt durch ein einzelnes Leerzeichen, dann strip() für Ränder
    df[column] = df[column].apply(lambda x: re.sub(r'\s+', ' ', x.strip()))
    
    return df


beruf_klassifizierung = {
    'Professor*in & Wissenschaft': [
        'dozent', 'professor', 'prof.', 'hochschull', 'hochschulpr', 'universitätsprofessor',
        'wissenschaftlicher assistent', 'wissenschaftlicher mitarbeiter', 'wissenschaftliche mitarbeiterin',
        'wissenschaftlicher referent', 'wissenschaftliche referentin', 'institutsleiter', 
        'wissenschaftsmanager', 'lehrbeauftragter', 'forschungsbeauftragter', 'akademischer oberrat', 'akademischer rat',
        'akademieleiter', 'studienleiter', 'studienleiterin', 'konservator', 'wiss. mitarbeiter', 'lehrbeaufttagte'
    ],
    
    'Jurist*in': [
        'anwalt', 'anwäl', 'jurist', 'richter', 'notar', re.compile('dr.*\s*jur.*'), 'syndikus', 'rechtsberater',
        'staatsanwalt', 'volljurist', 'wirtschaftsjurist', 'völkerrechtler', 'rechtsreferendar',
        'rechtsassessor', 'rechtswissenschaftler', 'oberlandesgerichtsrat', 'steuerrechtler'
    ],
    
    'Ärzt*in & Psycholog*in': [
        'arzt', 'ärzt', 'psycholog', 'psychlogin', 'psychother', 'mediziner', 'facharzt', 'zahnarzt', 'tierarzt',
        'internist', 'chirurg', 'kieferorthopäde', 'kreisveterrinärrat'
    ],
    
    'Volkswirt*in': [
        'volkswirt', re.compile('dipl.*-volkswirt'), 'diplom-volkswirt', 'dipl. volkswirt'
    ],
    
    'Betriebswirt*in': [
        'betriebswirt', 'steuerberater', 'bankdirektor', re.compile('dipl.*-betriebswirt'),
        'betriebsleiter', 'wirtschaftsassessor', 'wirtschaftsberater', 'finanzwirt', 'finanzberater',
        'finanzbuchhalter', 'finanzcontroller', 'wirtschaftssachverständiger', 'vermögensberater'
    ],
    
    'Wirtschaftswissenschaftler*in': [
        'ökonom', re.compile('dipl.*-ökonom'), 'wirtschaftswissenschaftler', 'wirtschaftsprüfer',
        'ing.-ökonom', 'sozialökonom', 'staatswissenschaftler', 'statistiker'
    ],
    
    'Geisteswissenschaftler*in': [
        'politolog', 'politikwiss', 'historik', 'philosoph', 'philolog', 'soziolog', 
        'sozialwissensch', 'kulturwissenschaft', 'sprachwissenschaftler', 'asienwissenschaft',
        'islamwissenschaft', 'literaturwissenschaft', 'gesellschaftswissenschaft', 'kommunikationswissenschaft',
        'medienwissenschaftler', 'kunstwissenschaftler', 'friedens- und konfliktforscher',
        'sozial- und kulturanthropologe', 'internationale beziehungen', 'ethnolog', 'umweltwissenschaft',
        'geograph', 'magister artium', 'geopolitik', 'system-analytiker'
    ],
    
    'Naturwissenschaftler*in': [
        'chemik', 'chemie', 'physik', 'geophysik', 'biolog', 'mathemat',
        'geologe', 'biochemiker', 'biotechnolog', 'ernährungswissenschaft', 'geowissenschaftler', 'geologe',
        'milchindustrielaborant', 
    ],
    
    'Ingenieur*in': [
        'ingenieur', 'maschinenbau', 'architekt', re.compile('dipl.*-ing'), 'bauingenieur', 'elektroingenieur',
        'wirtschaftsingenieur', 'maschinenschlosser', 'baumeister', 'technischer zeichner'
    ],

    'Informatik & IT': [
        'informatik', 'software', 'programm', 'entwickler', 'developer', 'data scientist',
        'datenanalyst', 'systemadministrator', 'netzwerk', 'datenbankadministrator',
        'it-berater', 'it berater', 'it-consultant', 'it-architekt', 'it-spezialist',
        'webentwickler', 'web-entwickler', 'fullstack', 'backend', 'frontend',
        'künstliche intelligenz', 'machine learning', 'ki-experte', 'ki experte',
        'it-sicherheit', 'cybersicherheit', 'security', 'system engineer',
        'cto', 'chief technical officer', 'cio', 'edv', 'computertechnik',
        'wirtschaftsinformatik', 'bioinformatik', 'informationstechnik',
        'fachinformatiker', 'datenbank'
    ],
    
    'Lehrer*in': [
        'erzieher', 'pädagog', 'lehrer', 'studienr', 'studiendirektor', 'schulrat',
        'grundschul', 'hauptshul', 'sonderschul', 'waldorf', 'realschul', 'gymnasi',
        'volkshochschu', 'berufsschul', 'fremdsprachen', 'schul', 'rektor', 'konrektor',
        'oberstudienrat', 'oberstudiendirektor', 'seminarleiter', 'studienassessor',
        'verbandsbildungsleiter', 'unterrichtsschwester'
    ],
    
    'Theolog*in': [
        'pfarrer', 'theolog', 'diakon', 'pastor', 'priester', 'militärseelsorger', 'diözesansekretär',
        'oberkirchenrat', 'diakonin'
    ],
    
    'Berufspolitiker*in': [
        'regierungsangestellt', 'stadtamtmann', 'stadtoberinspektor', 'landesgeschäftsführer',
        re.compile('landr(at|ätin)'), re.compile('ministerialr(a|ä)t'), 'staatssekret', 'bürgermeist', 
        'regierungsrat', re.compile('regierungs(vize)*präs'), 'regierung', 'stadtrat', 'stadträt', 'senator',
        'stadtdirektor', 'ministerialdirektor', 'regierungsdirektor', 'gemeindedirektor',
        'minister', 'bundeskanz', 'bundestagsp', re.compile('präsident(in)* d\.*b\.*t\.*'),
        'abgeordnete', 'parlamentarischer staatssekretär', 'staatsminister', 'ministerpräsident',
        'oberbürgermeister', 'politiker', 'poltiker','mdb', 'mdep', 'bezirksstadtrat', 'kreisbeigeordnet',
        'beigeordnet', 'mitglied des landtages', 'staatsrat', 'migrantenbeauftragte',
        'landespräsident', 'eg-kommissar', 'parteisekretä', 'parteifunktionär', 
        'vorsitzender der spd', 'präsident des deutschen bundestages', 'präsident des bundesverfassungsgericht',
        'bundesmin. f. besond. aufgaben'
    ],
    
    'Verwaltungsberufe': [
        'beamter', 'beamtin', 'verwaltungsbeamter', 'verwaltungsoberinspek', 'verwaltungsangestellte',
        'regierungsdirektor', 'ministerialrat', 'stadtoberinspektor', 'oberregierungsrat',
        'oberpostrat', 'polizeipräsident', 'bundesbahnoberinspektor', 'bundesbahnbetriebsinspektor',
        'obertelegrafensekretär', 'referent', 'referatsleiter', 'hauptreferent', 'kreisinspektorin',
        'postoberinspektor', 'polizeioberrat', 'kriminaloberrat', 'kriminaloberkommissar',
        'bezirksamtsleiter', re.compile('dipl.*-verwaltungswirt'), 'verwaltungswirt', 'verwaltungswiss', 'amtsrat',
        'stadtinspektor', 'stadtkämmerer', 'verwaltungsrat', 'verwaltungsamtmann', 'verwaltungsinspektor',
        'polizeihauptkommissar', 'bundesbankamtsinspektor', 'steueramtmann', 'oberamtsrat',
        'knappschaftsamtmann', 'postrat', 'bundesbahnamtmann', 'polizist', 'polizeibeamter', 'City-Managerin', 'gemeinderat', 'gemeinderät'
    ],

    'Diplomat*in': [
        'diplomat', 'vortragender legationsrat', 'botschafter'
    ],
    
    'Unternehmer*in': [
        'unternehmer', 'fabrikant', 'geschäftsführer', 'hauptgeschäftsführer', 'unternehmensberater', 
        'selbständiger kaufmann', 'geschäftsführender gesellschafter', 'freiberuflicher planer',
        'selbständig', 'selbstständig', 'organisationsberater', 'personalberater', 'industrieberater',
        'vorstandsvorsitzender', 'generalbevollmächtigter', 'persönlich haftender gesellschafter',
        'gutsbesitzer', 'vorstand', 'geschäftsleiter', 'baustoffgroßhändler'
    ],
    
    'Kaufmännische Berufe': [
        'kaufm', 'kauff', 'einzelhandel', 'großhandel', 'handelsfachwirt', 'bankkaufmann', 'bankier', 
        'bankfachwirt', 'finanzfachwirt','fachwirt im gastgewerbe', 'versicherungsfachwirt', 'sparkassenfachwirt', 
        'versicherungskaufmann', 'industriekaufmann', 'kaufmännische angestellte', 'prokurist',
        'account manager', 'vertriebsleiter', 'vertriebsmanager', 'marketing- und kommunikationsmanager',
        'projektmanager', 'produktmanager', 'geschäftsstellenleiter', 'hotelfachfrau', 'marktforscher',
        'verkaufsleiter', 'handelsvertreter', 'einzelhändler', 'ecommerce manager',
        'immobilienmakler', 'grundstücksmakler',  'buchhalter', 'finanzbuchhalter'
    ],
    

    'Journalist*in & Medien': [
        'journalist', 'redakteur', 'publizist', 'schriftsteller', 'pressesprecher', 'chefredakteur',
        'buchhändler', 'auslandskorrespond', 'autor', 'pressefotograf', 'moderator', 'dramaturg',
        'kulturmanager', 'pr-berater', 'kommunikationswirt', 'hauptschriftleiter', 'kommunikationsberater',
        'fundraiser', 'verlags', 'verleger'
    ],
    
    'Handwerker*in': [
        'elektro', 'fahrzeug', 'handwerk', 'mechanik', 'schlosser', 'maurer', 'beton', 
        'maler', 'lackier', 'tischler', 'schreiner', 'bäcker', 'konditor', 'koch', 'köchin', 
        'müller', 'bergmann', 'werkzeugmacher', 'zimmermann', 'fleischer', 'metzger',
        'schriftsetzer', 'buchdrucker', 'glasermeister', 'bezirksschornsteinfegermeister',
        'schuhmachermeister', 'zimmermeister', 'setzer', 'former', 'friseurmeister',
        'zerspanungsfacharbeiter', 'goldschmied', 'drucker', 'elektrikerin', 'restaurantfachmann',
        'lagerist', 'installateurmeister', 'schmiedemeister', 'kartonagenmeister', 'schweißer',
        'dreher', 'klempner', 'starkstromelektriker', 'glasschmelzer', 'fliesenleger',
        'tapeziermeister', 'karosseriebaumeister', 'metallarbeiter', 'werkzeugdreher',
        'hochdruckschweißer', 'polsterer', 'optiker', 'stukkateurmeister', 'stellmacher',
        'fotografenmeister', 'hafenfacharbeiter', 'installateur', 'stukkteurmeister'
    ],
    
   # 'Technische Berufe': [
   #     'techniker', 'mechatroniker', 'elektroniker', re.compile('dipl.*-tech'),
   #     'werkmeister', 'lokomotivführer', 'facharbeiter für eisenbahntransporttechnik',
   #     'technischer angestellter', 'abwassermeister', 'pilot', 'betriebsmeister',
   #     'baustofftechnolog'
   # ],
    
    'Land-/Forstwirt*in': [
        'landwirt', re.compile('^[a-z]bauer\s'), 'bauer', re.compile('agrar+'), 'forst', 'winzer', 'ökonomierat',
        'land- und forstwirt', 'agraringenieur', 'ökologischer gärtner', 'gärtnermeister', 'revierförster',
        'landliche hauswirtschaft', 'bäuerin', 'landfrau', 'meisterin der ländlichen hauswirtschaft'
    ],
    
    'Pflege- & Sozialberufe': [
        'krankenschwester', 'krankenpfleger', 'pflegekraft', 'hebamme', 'sanitäter',
        'medizinisch-technischer assistent', 'heilpraktiker', 'fachassistent für röntgendiagnostik',
        'kinderpfleger', 'sozialarbeiter', 'sozialpädagoge', re.compile('dipl.*-sozi'), 'erzieher',
        'fürsorgerin', 'sozialversicherungsfachangestellt', 'apotheker', 'apothekenhelferin',
        'krankengymnast', 'physiotherapeut', 'sporttherapeut', 'pflegedienstleitung',
        'qualif. kindertagespflegeperson', 'altenpfleger', 'wohlfahrtpfleger', 'logopäde',
        'gesundheitsberater', 'familienmanager', 'stadtaltenpfleger', 'angehörigenpfleger', 'päd. mitarbeiter'
    ],
    
    'Militär': [
        'leutnant', re.compile('oberst(?!u)'), 'soldat', re.compile('general\s'), 'offizier', 
        'hauptmann', 'major', 'oberstleutnant', 'fregattenkapitän', 'kapitän', 'vizeadmiral'
    ],
    
    'Gewerkschaftsberufe': [
        'gewerkschaftssekretär', 'arbeitersekretär', 'gewerkschaftsvorsitzender',
        'gewerkschaftskreisvorsitzender', 'gesamtbetriebsratvorsitzender', 'gewerkschafter',
        'betriebsrat', 'gewerkschaftlicher politikberater', 'landesbezirksvorsitzender des dgb',
        'vorsitzender der gewerkschaft', 'landesvorsitzender des dgb'
    ],
    
    'Künstlerische Berufe': [
        'künstler', 'musiker', 'schauspieler', 'sänger', 'maler', 'bildhauer',
        'regisseur', 'mediengestalter', re.compile('dipl.*-designer'), 'pr-manager',
        'harfenist', 'diplom-musiker', 'modedesigner'
    ],
    
    'Angestellte': [
        'angestellt', 'sachbearbeiter', 'bürokraft', 'büroangestellte', 'sekretär',
        'leitender angestellter', 'assistent', 'übersetzer', 'referent', 'sprachmittler',
        'bibliothekarin', 'büroleiter', 'vorarbeiter', 'helferin in steuersachen',
        'freier mitarbeiter'
    ],
    
    'Hausfrau/Hausmann': [
        'hausfrau', 'hausmann', 'siedlerfrau'
    ],
    
    'Student*in': [
        'student', 'studentin'
    ],
    
    'Sonstige': [
        'rentner', 'seemann', 'spediteur', 'gästeführer', 'feuerwehrmann', 'ohne angaben',
        'keine angaben', 'unbekannt', 'bestatter', 'ohne beruf', 'ohne angabe', 'vorkalkulator',
        'bergbauinvalide', 'gastwirt'
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
    return 'sonstige'


# TODO duplicate to colorlist in config?
def get_color_for_party(party):
    color_map = {
        'SPD': '#E3000F',           # Rot
        'CDU': '#000000',           # Schwarz
        'CSU': '#0080C8',           # Hellblau
        'FDP': '#FFED00',           # Gelb
        'die Grünen': '#64A12D',  # Grün
        'DIE LINKE.': '#BE3075',    # Dunkelrot/Magenta
        'AfD': '#009EE0',           # Hellblau
        'sonstige': '#808080'       # Grau für sonstige Parteien
    }
    return color_map.get(party, '#808080')  # Standardfarbe Grau, falls keine Zuordnung gefunden wird



def get_color_palette(num_colors):
    golden_ratio_conjugate = 0.618033988749895
    hue_start = 0.27  # Startpunkt angepasst für bessere Verteilung
    saturation_range = (0.65, 0.85)
    value_range = (0.65, 0.85)

    colors = []
    for i in range(num_colors):
        hue = (hue_start + i * golden_ratio_conjugate) % 1
        saturation = saturation_range[0] + (saturation_range[1] - saturation_range[0]) * (i / num_colors)
        value = value_range[1] - (value_range[1] - value_range[0]) * (i / num_colors)
        
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        colors.append(f'rgb({int(r*255)}, {int(g*255)}, {int(b*255)})')

    return colors




def get_color_for_age_group(age_group):
    color_map = {
        '< 30': 'rgb(0, 255, 0)',    
        '30 - 40': 'rgb(255, 127, 0)',  
        '40 - 50': 'rgb(255, 0, 0)',    
        '50 - 60': 'rgb(152, 0, 152)',   
        '> 60': 'rgb(100, 100, 100)' 
    }
    return color_map.get(age_group, 'rgb(128, 128, 128)')




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

