import pandas as pd
from pathlib import Path
import os
import re
from datetime import datetime

#rot SPD  # schwarz CDu #gelb FDP #blau CDU #grün grün #orange links #pink afd #lila sonstige
LIST_OF_COLORS = ['#ff0000', '#000000', '#ffcc00', '#0066ff',  '#008000', '#ffa500', '#cc00cc', '#4b0082', '#ee82ee', '#999999']
LIST_OF_COLORS = LIST_OF_COLORS + LIST_OF_COLORS

# Pfad zum Hauptverzeichnis des Projekts
PROJECT_ROOT = Path(os.getcwd()).parent

DATA_PATH = PROJECT_ROOT / 'data'
PLOT_PATH = PROJECT_ROOT / 'plots'

CURRENT_YEAR = '2024'  # oder '2024' für aktuelle Daten

MDB_XML_PATH = DATA_PATH / CURRENT_YEAR / 'input' / 'MDB_STAMMDATEN.XML'

#one row per individuum, one col per wp containing 0 / 1
DF_MDB_PATH = DATA_PATH / CURRENT_YEAR / 'output' / 'df_mdb.csv'

# one row per individuum per wp, containting e.g. 12. so one abgeordneter who has been in parliament for several wp will receive one row per wp
DF_MDB_WP_PATH = DATA_PATH / CURRENT_YEAR / 'output' / 'df_mdb_wp.csv' 

# startdaten der Wahlperioden
DF_MDB_WP_STARTDATEN_PATH = DATA_PATH / CURRENT_YEAR / 'output' / 'wp_startdaten.csv'