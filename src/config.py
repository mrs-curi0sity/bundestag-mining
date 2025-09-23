import pandas as pd
from pathlib import Path
import os
import re
from datetime import datetime

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

# Pfad zum Hauptverzeichnis des Projekts
#PROJECT_ROOT = Path(os.getcwd()).parent 
#PROJECT_ROOT = Path("/app") #<= due to docker + dash
#PROJECT_ROOT = Path(os.getenv('PROJECT_ROOT', os.getcwd()))

# Der Projektroot ist zwei Ebenen über config.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent


DATA_PATH = PROJECT_ROOT / 'data'
PLOT_PATH = PROJECT_ROOT / 'plots'

CURRENT_YEAR = '2025'

MDB_XML_PATH = DATA_PATH / CURRENT_YEAR / 'input' / 'MDB_STAMMDATEN.XML'

#one row per individuum, one col per wp containing 0 / 1
DF_MDB_PATH = DATA_PATH / CURRENT_YEAR / 'output' / 'df_mdb.csv'

# one row per individuum per wp, containting e.g. 12. so one abgeordneter who has been in parliament for several wp will receive one row per wp
DF_MDB_WP_PATH = DATA_PATH / CURRENT_YEAR / 'output' / 'df_mdb_wp.csv' 

# startdaten der Wahlperioden
DF_MDB_WP_STARTDATEN_PATH = DATA_PATH / CURRENT_YEAR / 'output' / 'wp_startdaten.csv'

# display List 
PAGE_SIZE = 8
COLUMNS_FOR_DISPLAY = ['NACHNAME', 'VORNAME', 'GESCHLECHT', 'GEBURTSDATUM', 'START_AGE_IN_YEARS_MAPPED', 'PARTEI_KURZ', 'FAMILIENSTAND', 'RELIGION', 'BERUF', 'BERUF_MAPPED', 'VITA_KURZ', 'WP']