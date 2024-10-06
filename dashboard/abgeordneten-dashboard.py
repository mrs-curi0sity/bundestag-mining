import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import logging
import sys
import os

# Add parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.mapping_values import (
    df_mdb_wp, MAX_WP, WP_START, list_of_parteien, list_of_religion,
    list_of_familienstand, list_of_beruf, list_of_altersklassen
)
from src.visualization import select_vis_data, compute_traces
from src.config import LIST_OF_COLORS, PAGE_SIZE, COLUMNS_FOR_DISPLAY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Styles
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa'
}

CONTENT_STYLE = {
    'margin-left': '25%',
    'margin-right': '5%',
    'padding': '20px 10px'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970'
}

# Helper functions
def create_dropdown(id, options, value):
    return dcc.Dropdown(
        id=id,
        options=[{'label': f"{WP_START[x-1]} - {WP_START[x]}", 'value': x} for x in range(1, MAX_WP+1)],
        value=value
    )

def create_checklist(id, options, value):
    return dbc.Card([
        dbc.Checklist(
            id=id,
            options=[{'label': option, 'value': option} for option in options],
            value=value,
        )
    ])

def create_button(id, label):
    return dbc.Button(
        id=id,
        children=label,
        color='primary',
        className='w-100',
    )

# Layout components
sidebar = html.Div([
    html.H2('Filter', style=TEXT_STYLE),
    html.Hr(),
    html.P('Wahlperioden', style={'textAlign': 'center'}),
    create_dropdown('wp_start', [], 1),
    create_dropdown('wp_end', [], MAX_WP),
    html.Br(),
    html.P('Parteien', style={'textAlign': 'center'}),
    create_checklist('check_list_parteien', list_of_parteien, list_of_parteien),
    create_button('select_all_parteien', 'Select All'),
    html.Br(),
    create_button('submit_button', 'Submit'),
], style=SIDEBAR_STYLE)

content = html.Div([
    html.H2('Bundestagsmining', style=TEXT_STYLE),
    html.Hr(),
    dbc.Row([
        dbc.Col(dcc.Graph(id='party'), md=6),
        dbc.Col(dcc.Graph(id='gender'), md=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='familienstand'), md=6),
        dbc.Col(dcc.Graph(id='religion'), md=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='alter'), md=6),
        dbc.Col(dcc.Graph(id='num_years_in_bt'), md=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='beruf'), md=12)
    ]),
    dbc.Row([
        dash_table.DataTable(
            id='selected_records',
            columns=[
                {
                    'name': 'ALTER' if colname == 'START_AGE_IN_YEARS_MAPPED' else colname,
                    'id': colname,
                    **(({'presentation': 'markdown'} if colname == 'VITA_KURZ' else {}))#,
                    #'sortable': True
                } for colname in COLUMNS_FOR_DISPLAY
            ],
            
            page_current=0,
            page_size=PAGE_SIZE,
            page_action='custom',
            sort_action='custom',
            sort_mode='single',
            sort_by=[],
            style_table={'overflowX': 'auto'},
            style_cell={
                'whiteSpace': 'normal',
                'height': 'auto',
                'textAlign': 'left',
                'padding': '10px',
                'font-family': 'Arial, sans-serif',
                'minWidth': '100px',
                'width': '150px',
                'maxWidth': '300px',
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': 'VITA_KURZ'},
                    'width': '40%',
                    'minWidth': '500px',
                    'maxWidth': '800px',
                }
            ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold',
                'border': '1px solid black'
            },
            style_data={
                'border': '1px solid lightgrey'
            },
            markdown_options={'html': True}
        )

    ])
], style=CONTENT_STYLE)

# Initialize app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([sidebar, content])

# Callbacks
@app.callback(
    Output('check_list_parteien', 'value'),
    [Input('select_all_parteien', 'n_clicks')],
    [State('check_list_parteien', 'options'),
     State('check_list_parteien', 'value')]
)
def set_check_list_values(n_clicks, options, values):
    logger.info(f'N-CLICKS: {n_clicks}')
    if n_clicks is None:
        return values  # Return current values if button hasn't been clicked
    return [i['value'] for i in options] if n_clicks % 2 == 0 else []
"""
def update_graph(n_clicks, start_date, end_date, selected_parteien, dimension, values_to_keep, title):
    grouped = select_vis_data(df_mdb_wp, start_date, end_date, selected_parteien, dimension)
    traces = compute_traces(grouped, start_date, end_date, values_to_keep, dimension)
    return {'data': traces, 'layout': go.Layout(title=title)}"""
def get_color_for_age_group(age_group):
    color_map = {
        '< 30': '#66c2a5',  # Hellgrün
        '30 - 40': '#fc8d62',  # Orange
        '40 - 50': '#8da0cb',  # Hellblau
        '50 - 60': '#e78ac3',  # Rosa
        '60 - 70': '#a6d854',  # Gelbgrün
        '70 - 80': '#ffd92f',  # Gelb
        '>= 80': '#e5c494'   # Beige
    }
    return color_map.get(age_group, '#CCCCCC')  # Standardfarbe, falls keine Zuordnung gefunden wird

def update_graph(n_clicks, start_date, end_date, selected_parteien, dimension, values_to_keep, title):
    grouped = select_vis_data(df_mdb_wp, start_date, end_date, selected_parteien, dimension)
    
    if dimension == 'START_AGE_IN_YEARS_MAPPED':
        age_groups = ['< 30', '30 - 40', '40 - 50', '50 - 60', '60 - 70', '70 - 80', '>= 80']
        traces = []
        for age_group in age_groups:  # Nicht mehr umgekehrt, um die gewünschte Reihenfolge zu erhalten
            trace = go.Scatter(
                x=grouped.index,
                y=grouped[age_group],
                mode='lines',
                stackgroup='one',
                name=age_group,
                line=dict(width=0),
                fillcolor=get_color_for_age_group(age_group)
            )
            traces.append(trace)
        
        layout = go.Layout(
            title=title,
            xaxis=dict(title='Wahlperiode'),
            yaxis=dict(title='Anteil der Altersgruppen', tickformat=',.0%'),
            legend=dict(title='Altersgruppen', traceorder='reversed'),  # Umgekehrte Reihenfolge in der Legende
            hovermode='x unified'
        )
        
        return {'data': traces, 'layout': layout}
    else:
        # Logik für andere Dimensionen bleibt unverändert
        traces = [go.Bar(x=grouped.index, y=grouped[value], name=value) 
                  for value in reversed(values_to_keep) if value in grouped.columns]
        layout = go.Layout(title=title, barmode='stack', yaxis=dict(tickformat=',.0%'))
        return {'data': traces, 'layout': layout}


for graph_id, dimension, values_to_keep, title in [
    ('gender', 'GESCHLECHT', ['männlich', 'weiblich'], 'Geschlecht'),
    ('party', 'PARTEI_KURZ', list_of_parteien, 'Partei'),
    ('religion', 'RELIGION_MAPPED', list_of_religion, 'Religion'),
    ('familienstand', 'FAMILIENSTAND_MAPPED', list_of_familienstand, 'Familienstand'),
    ('alter', 'START_AGE_IN_YEARS_MAPPED', list_of_altersklassen, 'Alter'),
    ('beruf', 'BERUF_MAPPED', list_of_beruf, 'Beruf')
]:
    app.callback(
        Output(graph_id, 'figure'),
        [Input('submit_button', 'n_clicks')],
        [State('wp_start', 'value'),
         State('wp_end', 'value'),
         State('check_list_parteien', 'value')]
    )(lambda n_clicks, start_date, end_date, selected_parteien, 
       dim=dimension, values=values_to_keep, t=title: 
       update_graph(n_clicks, start_date, end_date, selected_parteien, dim, values, t))

@app.callback(
    Output('num_years_in_bt', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('wp_start', 'value'),
     State('wp_end', 'value'),
     State('check_list_parteien', 'value')]
)
def update_graph_num_years_in_bt(n_clicks, start_date, end_date, selected_parteien):
    selected_df = df_mdb_wp[(df_mdb_wp['WP'] >= 1) & (df_mdb_wp['WP'] <= 19)]
    selected_df = selected_df[selected_df['PARTEI_KURZ'].isin(selected_parteien)]
    grouped = selected_df[['ID', 'START_DATE', 'NUM_YEARS_IN_BT', 'PARTEI_KURZ']].groupby(['START_DATE', 'PARTEI_KURZ']).mean()
    
    new_index = pd.MultiIndex.from_product([grouped.index.levels[0], grouped.index.levels[1]], names=['START_DATE', 'PARTEI_KURZ'])
    grouped_reindexed = grouped.reindex(new_index, fill_value=0)
    grouped_reindexed.reset_index(inplace=True)
    
    grouped_reindexed['PARTEI_KURZ'] = pd.Categorical(grouped_reindexed['PARTEI_KURZ'], selected_parteien)
    grouped_reindexed.sort_values(by=['START_DATE', 'PARTEI_KURZ'], inplace=True)
    
    fig = px.line(grouped_reindexed, x='START_DATE', y='NUM_YEARS_IN_BT', color='PARTEI_KURZ', color_discrete_sequence=LIST_OF_COLORS)
    fig.update_traces(line=dict(width=3))
    fig.update_layout(
        title='Bleibedauer der Abgeordneten im Bundestag',
        xaxis_title='',
        yaxis_title='Jahre im BT bei Beginn der WP'
    )
    return fig
    

# Aktualisierte Callback-Funktion für Sortierung und Paginierung
@app.callback(
    Output('selected_records', 'data'),
    [Input('submit_button', 'n_clicks'),
     Input('selected_records', 'page_current'),
     Input('selected_records', 'page_size'),
     Input('selected_records', 'sort_by')],
    [State('wp_start', 'value'),
     State('wp_end', 'value'), 
     State('check_list_parteien', 'value')]
)
def update_table(n_clicks, page_current, page_size, sort_by, start_date, end_date, selected_parteien):
    selected_df = df_mdb_wp[(df_mdb_wp['WP'] >= start_date) & (df_mdb_wp['WP'] <= end_date)]
    selected_df = selected_df[selected_df['PARTEI_KURZ'].isin(selected_parteien)][COLUMNS_FOR_DISPLAY].drop_duplicates()
    
    if sort_by:
        selected_df = selected_df.sort_values(
            sort_by[0]['column_id'],
            ascending=sort_by[0]['direction'] == 'asc',
            inplace=False
        )
    
    return selected_df.iloc[page_current*page_size:(page_current + 1)*page_size].to_dict('records')


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8050, debug=True)

server = app.server