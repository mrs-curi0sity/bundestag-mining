import pandas as pd
import matplotlib.pyplot as plt
from plotly import graph_objs as go

import plotly.express as px
from plotly.subplots import make_subplots

from src.config import LIST_OF_COLORS
from src.mapping_values import WP_START
import seaborn as sns
from src.config import PLOTS_DIR  # Annahme: du hast PLOTS_DIR in config definiert

def create_barplot_with_values(data, title, xlabel, ylabel, filename, 
                              figsize=(14, 8), show_values=True, grid=True):
    """
    Erstellt ein Balkendiagramm mit Werten über den Balken
    
    Args:
        data: pandas Series oder dict mit Index/Keys als x-Werte und Values als y-Werte
        title: Titel des Plots
        xlabel: Label für x-Achse
        ylabel: Label für y-Achse
        filename: Dateiname (ohne Endung, wird als SVG gespeichert)
        figsize: Tuple für Figur-Größe
        show_values: Bool, ob Werte über Balken angezeigt werden
        grid: Bool, ob Grid angezeigt wird
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Balkendiagramm erstellen
    if hasattr(data, 'index') and hasattr(data, 'values'):
        # pandas Series
        x_data, y_data = data.index, data.values
    else:
        # dict oder andere iterables
        x_data, y_data = list(data.keys()), list(data.values())
    
    sns.barplot(x=x_data, y=y_data, ax=ax)
    
    # Beschriftungen
    ax.set_title(title, fontsize=20)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    
    # Werte über Balken
    if show_values:
        for i, v in enumerate(y_data):
            ax.text(i, v + max(y_data) * 0.01, f'{int(v)}', ha='center', va='bottom')
    
    # Y-Achse anpassen
    y_max = max(y_data)
    ax.set_ylim(0, y_max * 1.1)
    
    # Grid
    if grid:
        ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Layout und speichern
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f'{filename}.svg', format='svg', dpi=300, bbox_inches='tight')
    plt.show()



def create_animated_barplot(data, title, xlabel, ylabel, filename):
    """Animated Plotly-Version mit Übergangseffekten"""
    
    fig = px.bar(
        x=data.index.astype(str),
        y=data.values,
        title=title,
        labels={'x': xlabel, 'y': ylabel},
        color=data.values,
        color_continuous_scale='Blues',
        text=data.values
    )
    
    # Text-Formatierung
    fig.update_traces(
        texttemplate='%{text}',
        textposition='outside',
        textfont_size=12,
        hovertemplate='<b>Wahlperiode %{x}</b><br>' +
                     'Anzahl: %{y}<br><extra></extra>'
    )
    
    # Erweiterte Layout-Optionen
    fig.update_layout(
        title_x=0.5,
        title_font_size=24,
        font_family="Arial",
        plot_bgcolor='rgba(240,240,240,0.3)',
        coloraxis_showscale=False,
        height=600,
        transition_duration=500
    )
    
    fig.write_html(PLOTS_DIR / f'{filename}.html')
    fig.show()
    return fig


def select_vis_data(df_mdb_wp, start_date, end_date, selected_parteien, dimension='GESCHLECHT', modus='count'):

    # Wahlperiode und Partei auswählen
    selected_df = df_mdb_wp[(df_mdb_wp['WP'] >= start_date) & (df_mdb_wp['WP'] <= end_date)]
    selected_df = selected_df[selected_df['PARTEI_MAPPED'].isin(selected_parteien)]

    print(selected_df.groupby('PARTEI_MAPPED').value_counts())
    
    if dimension == 'START_AGE_IN_YEARS_MAPPED':
        # Alle Altersgruppen definieren
        age_groups = ['< 30', '30 - 40', '40 - 50', '50 - 60', '> 60']
        
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
