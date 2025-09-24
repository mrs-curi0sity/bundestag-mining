import pandas as pd
from pathlib import Path
import os
import re
import json
from datetime import datetime


# Der Projektroot ist zwei Ebenen über config.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = PROJECT_ROOT / 'data'
PLOT_PATH = PROJECT_ROOT / 'plots'

CURRENT_YEAR = '2025'
WP_START = [1949, 1953, 1957, 1961, 1965, 1969, 1972, 1976, 1980, 1983, 1987, 1990, 1994, 1998, 2002, 2005, 2009, 2013, 2017, 2021, 2025, 2029]

MDB_XML_PATH = DATA_PATH / CURRENT_YEAR / 'input' / 'MDB_STAMMDATEN.XML'

#one row per individuum, one col per wp containing 0 / 1
DF_MDB_PATH = DATA_PATH / CURRENT_YEAR / 'output' / 'df_mdb.csv'

# one row per individuum per wp, containting e.g. 12. so one abgeordneter who has been in parliament for several wp will receive one row per wp
DF_MDB_WP_PATH = DATA_PATH / CURRENT_YEAR / 'output' / 'df_mdb_wp.csv' 

# startdaten der Wahlperioden
DF_MDB_WP_STARTDATEN_PATH = DATA_PATH / CURRENT_YEAR / 'output' / 'wp_startdaten.csv'

PLOTS_DIR = Path(__file__).parent.parent / 'plots'
PLOTS_DIR.mkdir(exist_ok=True)


# Kategorien-Metadaten laden
def load_categories():
    try:
        with open(DATA_PATH / CURRENT_YEAR / 'output' / 'categories_metadata.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback-Werte falls Datei nicht existiert
        print("Warning: categories_metadata.json nicht gefunden, verwende Fallback-Werte")
        return {
            'parteien': ['SPD', 'CDU', 'CSU', 'FDP', 'die Grünen', 'DIE LINKE.', 'AfD', 'sonstige'],
            'religion': ['evangelisch', 'katholisch', 'konfessionslos', 'unbekannt', 'sonstige'],
            'familienstand': ['verheiratet', 'ledig', 'geschieden', 'verwitwet', 'sonstige'],
            'kinder': ['ohne Kinder', 'mit einem Kind', 'mit zwei Kindern', '> zwei Kinder', 'keine Angaben'],
            'beruf': ['sonstige'],  # Wird durch echte Daten ersetzt
            'geschlecht': ['männlich', 'weiblich'],
            'altersklassen': ['< 30', '30 - 40', '40 - 50', '50 - 60', '> 60']
        }

# Kategorien laden
CATEGORIES = load_categories()

# Listen für die App
LIST_OF_PARTEIEN = CATEGORIES['parteien']
LIST_OF_RELIGION = CATEGORIES['religion'] 
LIST_OF_FAMILIENSTAND = CATEGORIES['familienstand']
LIST_OF_CHILDREN = CATEGORIES['kinder']
LIST_OF_BERUF = CATEGORIES['beruf']
LIST_OF_GESCHLECHT = CATEGORIES['geschlecht']
LIST_OF_ALTERSKLASSEN = CATEGORIES['altersklassen']


#rot SPD  # schwarz CDu #gelb FDP #blau CDU #grün grün #orange links #pink afd #lila sonstige
LIST_OF_COLORS = [
    '#ff0000',  # Rot (SPD)
    '#000000',  # Schwarz (CDU)
    '#ffcc00',  # Gelb (FDP)
    '#0066ff',  # Blau (CDU - alternative)
    '#008000',  # Grün (Grüne)
    '#ffa500',  # Orange (Linke)
    '#cc00cc',  # Pink (AfD)
    '#4b0082',  # Indigo (Sonstige)
    '#ee82ee',  # Violett (Sonstige)
    '#ff6600',  # Knalliges Orange (ersetzt Grau)
    '#8b4513',  # Braun
    '#00ffff',  # Cyan
    '#32cd32',  # Limettengrün
    '#ff69b4',  # Hot Pink
    '#1e90ff',  # Dodger Blue
    '#daa520'   # Goldenrod
]


# display List 
PAGE_SIZE = 8
COLUMNS_FOR_DISPLAY = ['NACHNAME', 'VORNAME', 'GESCHLECHT', 'GEBURTSDATUM', 'START_AGE_IN_YEARS_MAPPED', 'PARTEI_KURZ', 'FAMILIENSTAND', 'RELIGION', 'BERUF', 'BERUF_MAPPED', 'VITA_KURZ', 'WP']