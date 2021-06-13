import pandas as pd
from datetime import datetime
import logging
import random

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
from dash.dependencies import Input, Output, State
import dash_table
import plotly.express as px

from src.berufe_mapping import basic_cleaning_berufe
from src.visualization import select_vis_data, compute_traces
from src.config import LIST_OF_COLORS, df_mdb, df_mdb_wp, MAX_WP, WP_START, PAGE_SIZE, COLUMNS_FOR_DISPLAY, list_of_parteien, list_of_religion, list_of_familienstand, list_of_beruf, list_of_altersklassen

# set loglevel to INFO. could also be DEBUG or WARNING or ERROR
logging.getLogger().setLevel(logging.INFO)

num_reloads = 0

logging.info('columns : ' + df_mdb_wp.columns)


# ----------------- style. TODO => move to assets
# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa'
}

# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '25%',
    'margin-right': '5%',
    'padding': '20px 10p'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970'
}

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#0074D9'
}



# ---------------- sidebar
controls = dbc.FormGroup(
    [
        
        html.P('Wahlperioden', style={
            'textAlign': 'center'
        }),
        dcc.Dropdown(id='wp_start',
                     options=[{'label':str(WP_START[x-1]) + ' - ' + str(WP_START[x]), 'value': x} for x in range(1, MAX_WP+1)],
                    value=1),
        
        dcc.Dropdown(id='wp_end',
                     options=[{'label':str(WP_START[x-1]) + ' - ' + str(WP_START[x]), 'value': x} for x in range(1, MAX_WP+1)],
                    value=MAX_WP),
        
        html.Br(),
        
        
        # checkbox list parteien
        html.P('Partien', style={
            'textAlign': 'center'
        }),
        dbc.Card([dbc.Checklist(
            id='check_list_parteien',
            options=[{
            'label': partei,
            'value': partei
                } for partei in list_of_parteien],
            value=[partei for partei in list_of_parteien],
            # inline=True
        )]),
        
        dbc.Button(
            id='select_all_parteien',
            n_clicks=0,
            children='Select All',
            color='primary',
            block=True
        ),
        html.Br(),
        
        dbc.Button(
            id='submit_button',
            n_clicks=0,
            children='Submit',
            color='primary',
            block=True
        ),
        
    ]
)

sidebar = html.Div(
    [
        html.H2('Filter', style=TEXT_STYLE),
        html.Hr(),
        controls
    ],
    style=SIDEBAR_STYLE,
)    

# -------------------- content

content_first_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='party'), md=6
        ),
        dbc.Col(
            dcc.Graph(id='gender'), md=6
        )

    ]
)


content_second_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='familienstand'), md=6
        ),
        
        dbc.Col(
            dcc.Graph(id='religion'), md=6
        )

    ]
)


content_third_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='alter'), md=6
        ),

        dbc.Col(
            dcc.Graph(id='num_years_in_bt'), md=6
        )

    ]
)



content_fourth_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='beruf'), md=12
        )

    ]
)


content_fifth_row = dbc.Row(
    [
        # dbc.Col(
        dash_table.DataTable(
            style_cell={
                'whiteSpace': 'normal',
                'height': 'auto',
                'textAlign': 'left',
                'maxWidth': 900
            },
            id='selected_records',
            columns = [{'name': colname, 'id': colname} for colname in COLUMNS_FOR_DISPLAY],
            page_current=0,
            page_size=PAGE_SIZE,
            page_action='custom'
            )#, md = 8
       #  )
    ]
)


content = html.Div(
    [
        html.H2(f'Bundestag Dashboard', style=TEXT_STYLE),
        html.Hr(),
        content_first_row,
        content_second_row,
        content_third_row,
        content_fourth_row,
        content_fifth_row
    ],
    style=CONTENT_STYLE
)

    

# --------------------- app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([sidebar, content])


# --------------------- callbacksf
# click all parties
@app.callback(
    Output('check_list_parteien', 'value'),
    [Input('select_all_parteien', 'n_clicks')],
    [State('check_list_parteien', 'options'),
     State('check_list_parteien', 'value')])
def set_check_list_values(n_clicks, options, values):
    logging.info(f'N-CLICKS: {n_clicks}')
    if n_clicks%2 == 0:
        return [i['value'] for i in options]
    else:
        return []
    

    
    
# gender
@app.callback(
    Output('gender', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('wp_start', 'value'),
     State('wp_end', 'value'),
     State('check_list_parteien', 'value')
     ])
def update_graph_gender(n_clicks, start_date, end_date, selected_parteien):
    grouped = select_vis_data(df_mdb_wp, start_date, end_date, selected_parteien, dimension='GESCHLECHT')
    traces = compute_traces(grouped, start_date, end_date, ['männlich', 'weiblich'], dimension='GESCHLECHT')
    
    fig = {'data': traces,
        'layout': go.Layout(title = 'Geschlecht')}
    
    return fig



# party
@app.callback(
    Output('party', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('wp_start', 'value'),
     State('wp_end', 'value'),
     State('check_list_parteien', 'value')
     ])
def update_graph_party(n_clicks, start_date, end_date, selected_parteien): 

    grouped = select_vis_data(df_mdb_wp, start_date, end_date,  selected_parteien, dimension='PARTEI_KURZ')
    traces = compute_traces(grouped, start_date, end_date, list_of_parteien, dimension='PARTEI_KURZ')
    
    fig = {'data': traces,
        'layout': go.Layout(title = 'Partei')}
    
    # this is nice and clean but did not find a possibility to order
    #fig = go.Figure()
    #fig.add_trace(go.Histogram(histfunc="count",  x=selected_df['PARTEI_KURZ']))
    return fig


# religion
@app.callback(
    Output('religion', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('wp_start', 'value'),
     State('wp_end', 'value'),
     State('check_list_parteien', 'value')
     ])
def update_graph_religion(n_clicks, start_date, end_date, selected_parteien):
    
    grouped = select_vis_data(df_mdb_wp, start_date, end_date,  selected_parteien, dimension='RELIGION_MAPPED')
    traces = compute_traces(grouped, start_date, end_date, list_of_religion, dimension='RELIGION_MAPPED')
    fig = {'data': traces,
        'layout': go.Layout(title = 'Religion')}
    return fig


# familienstand
@app.callback(
    Output('familienstand', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('wp_start', 'value'),
     State('wp_end', 'value'),
     State('check_list_parteien', 'value')
     ])
def update_graph_familienstand(n_clicks, start_date, end_date,  selected_parteien):
    grouped = select_vis_data(df_mdb_wp, start_date, end_date,  selected_parteien, dimension='FAMILIENSTAND_MAPPED')
    traces = compute_traces(grouped, start_date, end_date, list_of_familienstand, dimension='FAMILIENSTAND_MAPPED')
    fig = {'data': traces,
        'layout': go.Layout(title = 'Familienstand')}
    return fig



# alter
@app.callback(
    Output('alter', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('wp_start', 'value'),
     State('wp_end', 'value'),
     State('check_list_parteien', 'value')
     ])
def update_graph_familienstand(n_clicks, start_date, end_date,  selected_parteien):
    grouped = select_vis_data(df_mdb_wp, start_date, end_date,  selected_parteien, dimension='START_AGE_IN_YEARS_MAPPED')
    traces = compute_traces(grouped, start_date, end_date, values_to_keep=list_of_altersklassen, dimension='START_AGE_IN_YEARS_MAPPED')
    fig = {'data': traces,
        'layout': go.Layout(title = 'Alter')}
    return fig


#num_years_in_bp
@app.callback(
    Output('num_years_in_bt', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('wp_start', 'value'),
     State('wp_end', 'value'),
     State('check_list_parteien', 'value')
     ])
def update_graph_familienstand(n_clicks, start_date, end_date,  selected_parteien):
    selected_df = df_mdb_wp[(df_mdb_wp['WP']>= 1) & (df_mdb_wp['WP']<= 19)]
    selected_df = selected_df[selected_df['PARTEI_KURZ'].isin(selected_parteien)]
    grouped = selected_df[['ID', 'START_DATE', 'NUM_YEARS_IN_BT', 'PARTEI_KURZ']].groupby(['START_DATE', 'PARTEI_KURZ']).mean()
    #grouped.reset_index(inplace=True)
    
    # make double index: START_DATE, PARTEI_KURZ and fill with zeros
    new_index = pd.MultiIndex.from_product([grouped.index.levels[0], grouped.index.levels[1]], names=['START_DATE', 'PARTEI_KURZ'])
    grouped_reindexed = grouped.reindex(new_index, fill_value=0)
    grouped_reindexed.reset_index(inplace=True)
    
    # make it orderable in order guarantee order of legend / order of colors 
    grouped_reindexed['PARTEI_KURZ'] = pd.Categorical(grouped_reindexed['PARTEI_KURZ'], selected_parteien)
    grouped_reindexed.sort_values(by=['START_DATE', 'PARTEI_KURZ'], inplace=True)
  
    
    #fig = px.scatter(x=grouped['NUM_YEARS_IN_BT'].index, y= grouped['NUM_YEARS_IN_BT'])
    fig = go.Figure(data=px.line(grouped_reindexed, x='START_DATE', y= 'NUM_YEARS_IN_BT', color='PARTEI_KURZ', color_discrete_sequence=LIST_OF_COLORS))
    fig.update_layout(title='Bleibedauer der Abgeordneten im Bundestag',
                   xaxis_title='',
                   yaxis_title='Jahre im BT bei Beginn der WP')
    return fig


#beruf

@app.callback(
    Output('beruf', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('wp_start', 'value'),
     State('wp_end', 'value'),
     State('check_list_parteien', 'value')
     ])
def update_graph_beruf(n_clicks, start_date, end_date, selected_parteien):  
    grouped = select_vis_data(df_mdb_wp, start_date, end_date, selected_parteien, dimension='BERUF_MAPPED')
    traces = compute_traces(grouped, start_date, end_date, list_of_beruf, dimension='BERUF')

    fig = {'data': traces,
        'layout': go.Layout(title = 'Beruf')}
    return fig





@app.callback(
    Output('selected_records', 'data'),
    [Input('submit_button', 'n_clicks'),
     Input('selected_records', 'page_current'),
     Input('selected_records', 'page_size')],
    [State('wp_start', 'value'),
     State('wp_end', 'value'), 
     State('check_list_parteien', 'value'),
     ])
def update_feedback_records(n_clicks, page_current, page_size, start_date, end_date, selected_parteien):#, selected_berufe):
    
    # select wahlperiode
    selected_df = df_mdb_wp[(df_mdb_wp['WP']>= start_date) & (df_mdb_wp['WP']<= end_date)]
    
    # selct partei
    selected_df = selected_df[selected_df['PARTEI_KURZ'].isin(selected_parteien)][COLUMNS_FOR_DISPLAY].drop_duplicates().sort_values(by='NACHNAME')#VEROEFFENTLICHUNGSPFLICHTIGES

    
    logging.info(f'selected {selected_df.shape} many entries')
    
    return selected_df.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')



if __name__ == '__main__':
    app.run_server(host="0.0.0.0",  port=8051, debug=True)