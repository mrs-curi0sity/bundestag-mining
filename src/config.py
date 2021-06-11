import pandas as pd
from pathlib import Path

#rot SPD  # schwarz CDu #gelb FDP #blau CDU #grün grün #orange links #pink afd #lila sonstige
LIST_OF_COLORS = ['#ff0000', '#000000', '#ffcc00', '#0066ff',  '#008000', '#ffa500', '#cc00cc', '#4b0082', '#ee82ee', '#999999']
LIST_OF_COLORS = LIST_OF_COLORS + LIST_OF_COLORS

DATA_PATH = Path('./data')
DF_MDB_PATH = DATA_PATH / 'df_mdb.csv'
DF_MDB_WP_PATH = DATA_PATH / 'df_mdb_wp.csv'
df_mdb = pd.read_csv(DF_MDB_PATH)
df_mdb_wp = pd.read_csv(DF_MDB_WP_PATH)


MAX_WP = df_mdb_wp.WP.max()
WP_START = [1949, 1953, 1957, 1961, 1965, 1969, 1972, 1976, 1980, 1983, 1987, 1990, 1994, 1998, 2002, 2005, 2009, 2013, 2017, 2021]

# display List 
PAGE_SIZE = 8
COLUMNS_FOR_DISPLAY = ['NACHNAME', 'VORNAME', 'GEBURTSDATUM', 'PARTEI_KURZ', 'FAMILIENSTAND', 'RELIGION', 'BERUF', 'BERUF_MAPPED', 'VEROEFFENTLICHUNGSPFLICHTIGES', 'VITA_KURZ'] #'GESCHLECHT'

def replace_sonstige(df_mdb, df_mdb_wp, dimension='PARTEI_KURZ', num_keep = 7):
    """
    keep num_keep most occurences, replace other values by "sonstige"
    """
    
    # e.g. 'CDU', 'SPD'
    values_to_keep = list(df_mdb_wp[['ID', dimension]].groupby(dimension).count().sort_values(by='ID', ascending=False)[:num_keep].index)
    values_to_discard = list(df_mdb[['ID', dimension]].groupby(dimension).count().sort_values(by='ID', ascending=False)[num_keep:].index)
    
    # logging.info(f'[{dimension}]. keeping {values_to_keep}. replacing {values_to_discard[:3]} ... with <sonstige>')
    df_mdb[dimension].replace(values_to_discard, 'sonstige', inplace=True)
    df_mdb_wp[dimension].replace(values_to_discard, 'sonstige', inplace=True)
    
    return values_to_keep, values_to_discard, df_mdb, df_mdb_wp

# TODO start move to objects or at least dict
list_of_parteien, list_of_parteien_discard, df_mdb, df_mdb_wp = replace_sonstige(df_mdb, df_mdb_wp, dimension='PARTEI_KURZ', num_keep = 7)
list_of_religion, list_of_religion_discard, df_mdb, df_mdb_wp = replace_sonstige(df_mdb, df_mdb_wp, dimension='RELIGION_MAPPED', num_keep = 6) 
list_of_familienstand, list_of_familienstand_discard, df_mdb, df_mdb_wp = replace_sonstige(df_mdb, df_mdb_wp, dimension='FAMILIENSTAND_MAPPED', num_keep = 7)
list_of_beruf, list_of_beruf_discard, df_mdb, df_mdb_wp = replace_sonstige(df_mdb, df_mdb_wp, dimension='BERUF_MAPPED', num_keep = 20)
list_of_altersklassen = ['< 30', '30 - 40', '40 - 50', '50 - 60', '70 - 80',  '>= 80']
                            
# append 'sonstige' to list of valid values
for list_of_values in [list_of_parteien, list_of_religion, list_of_familienstand, list_of_beruf]:
    list_of_values += ['sonstige']
# TODO End