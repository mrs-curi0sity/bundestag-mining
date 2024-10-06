import pandas as pd

from plotly import graph_objs as go
from src.config import LIST_OF_COLORS
from src.mapping_values import df_mdb, df_mdb_wp, MAX_WP, WP_START


def select_vis_data(df_mdb_wp, start_date, end_date, selected_parteien, dimension='GESCHLECHT', modus='count'):
    # Wahlperiode und Partei auswählen
    selected_df = df_mdb_wp[(df_mdb_wp['WP'] >= start_date) & (df_mdb_wp['WP'] <= end_date)]
    selected_df = selected_df[selected_df['PARTEI_KURZ'].isin(selected_parteien)]
    
    if dimension == 'START_AGE_IN_YEARS_MAPPED':
        # Alle Altersgruppen definieren
        age_groups = ['< 30', '30 - 40', '40 - 50', '50 - 60', '60 - 70', '70 - 80', '>= 80']
        
        def count_age_groups(group):
            counts = group['START_AGE_IN_YEARS_MAPPED'].value_counts()
            return pd.Series({ag: counts.get(ag, 0) for ag in age_groups})
        
        grouped = selected_df.groupby('WP').apply(count_age_groups)
        # Fülle fehlende Werte mit 0
        grouped = grouped.reindex(columns=age_groups, fill_value=0)
        # Normalisierung pro Jahr (WP)
        grouped = grouped.div(grouped.sum(axis=1), axis=0)
        # Ersetze NaN durch 0 (falls eine Spalte komplett 0 war)
        grouped = grouped.fillna(0)
        
    else:
        # Ursprüngliche Logik für andere Dimensionen
        if modus == 'count':
            grouped = selected_df.groupby(['WP', dimension]).size().unstack(fill_value=0)
        elif modus == 'mean':
            grouped = selected_df.groupby(['WP', dimension]).mean().unstack(fill_value=0)
        else:
            logging.error(f'Dieser Modus ist nicht bekannt: {modus}')
            return None
        
        # Normalisieren
        grouped = grouped.div(grouped.sum(axis=1), axis=0)
    
    return grouped


def compute_traces(grouped, start_date, end_date, values_to_keep, dimension='GESCHLECHT'):
    # only selecte non-empty WPs which is important e.g. for PDS or AFD
    #wps = sorted(list(set([WP_START[wp-1] for wp in grouped.WP])))
    #dim_values = list(set(grouped[dimension])) # e.g. ['männlich', 'weiblich']
    traces_values = []
    
    levels = [values_to_keep, range(start_date, end_date+1)]
    new_index = pd.MultiIndex.from_product(levels, names=[dimension, 'WP'])
    # create entries also for 0 values
    grouped = grouped.reindex(new_index, fill_value=0)
    grouped.reset_index(inplace=True)
    wps = sorted(list(set(grouped.WP)))
    years = [str(WP_START[wp]) for wp in wps]
    
    if values_to_keep =='all':
        trace = grouped.sort_values(by='WP').ID.values
        traces_values.append(trace)     
    
    else:
        # e.g. one trace for each party
        for value in values_to_keep:
            trace = grouped[grouped[dimension] == value].sort_values(by='WP').ID.values
            traces_values.append(trace)
    
    traces = [go.Bar(x=years, y=trace, xaxis='x2', yaxis='y2',
                marker=dict(color=color), #'#0099ff'),
                name=f'{value}') for trace, value, color in zip(traces_values, values_to_keep, LIST_OF_COLORS[:len(values_to_keep)])]
    
    return traces
