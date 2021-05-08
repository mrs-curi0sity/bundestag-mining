import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
from dash.dependencies import Input, Output, State
import dash_table

# set loglevel to INFO. could also be DEBUG or WARNING or ERROR
logging.getLogger().setLevel(logging.INFO)

#app = dash.Dash()


num_reloads = 0

# define list of colors for traces here 
LIST_OF_COLORS = ['#0ea46b', '#0e7da4', '#8bb5da', '#708292', '#1e61a0', '#101cb8', '#4e14c2', '#6d0ea4']

DATA_PATH = Path('../data')
DF_MDB_PATH = DATA_PATH / 'df_mdb.csv'
DF_MDB_WP_PATH = DATA_PATH / 'df_mdb_wp.csv'
df_mdb = pd.read_csv(DF_MDB_PATH)
df_mdb_wp = pd.read_csv(DF_MDB_WP_PATH)

MAX_WP = df_mdb_wp.WP.max()
WP_START = [1949, 1953, 1957, 1961, 1965, 1969, 1972, 1976, 1980, 1983, 1987, 1990, 1994, 1998, 2002, 2005, 2009, 2013, 2017, 2021]

# retrieve 8 most common parties (incl AFD and PDS, excluding DP, FU etc)
list_of_parteien = list(df_mdb_wp[['ID', 'PARTEI_KURZ']].groupby('PARTEI_KURZ').count().sort_values(by='ID', ascending=False).head(8).index)
list_of_parteien.append('sonstige')
logging.info(f'Parteien: {list_of_parteien}')
list_of_excluded_parteien = list(df_mdb[['ID', 'PARTEI_KURZ']].groupby('PARTEI_KURZ').count().sort_values(by='ID', ascending=False)[8:].index)

# replace andere parteien with 'sonstige'
for excluded_partei in list_of_excluded_parteien:
    df_mdb['PARTEI_KURZ'].replace(excluded_partei, 'sonstige', inplace=True)
    df_mdb_wp['PARTEI_KURZ'].replace(excluded_partei, 'sonstige', inplace=True)

# display List 
PAGE_SIZE = 8
COLUMNS_FOR_DISPLAY = ['NACHNAME', 'VORNAME', 'GEBURTSDATUM', 'PARTEI_KURZ', 'GESCHLECHT', 'FAMILIENSTAND', 'RELIGION', 'BERUF', 'VITA_KURZ']
    
    

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
                    value=2),
        
        dcc.Dropdown(id='wp_end',
                     options=[{'label':str(WP_START[x-1]) + ' - ' + str(WP_START[x]), 'value': x} for x in range(1, MAX_WP+1)],
                    value=7),
        
        html.Br(),
        
        
        # checkbox list parteien
        html.P('Partien', style={
            'textAlign': 'center'
        }),
        dbc.Card([dbc.Checklist(
            id='check_list',
            options=[{
            'label': partei,
            'value': partei
                } for partei in list_of_parteien],
            value=[partei for partei in list_of_parteien],
            # inline=True
        )]),
        
        dbc.Button(
            id='select_all',
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
            dcc.Graph(id='beruf'), md=12
        )

    ]
)

content_fourth_row = dbc.Row(
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
        content_fourth_row
    ],
    style=CONTENT_STYLE
)


# --------------------- app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([sidebar, content])


# --------------------- callbacksf
# click all parties
@app.callback(
    Output('check_list', 'value'),
    [Input('select_all', 'n_clicks')],
    [State('check_list', 'options'),
     State('check_list', 'value')])
def set_check_list_values(n_clicks, options, values):
    logging.info(f'N-CLICKS: {n_clicks}')
    logging.info(f'Options: {options}')
    logging.info(f'Options: {values}')
    if n_clicks%2 == 0:
        logging.info(print('TRUE'))
        return [i['value'] for i in options]
    else:
        return []


def select_data(start_date, end_date, selected_parteien, dimension='GESCHLECHT'):
    # select wahlperiode
    logging.info(f'+++++ starting evaluation of {dimension}')
    selected_df = df_mdb_wp[(df_mdb_wp['WP']>= start_date) & (df_mdb_wp['WP']<= end_date)]
    logging.info(f'fitting wp: {selected_df.shape}')
    
    # selct partei
    selected_df = selected_df[selected_df['PARTEI_KURZ'].isin(selected_parteien)]
    logging.info(f'fitting parteien: {selected_df.shape}')
    
    grouped = selected_df[['ID', 'WP', dimension]].groupby([dimension, 'WP']).count()
    grouped.reset_index(inplace=True)
    return grouped


def compute_traces(grouped, start_date, end_date, selected_parteien, dimension='GESCHLECHT'):
    # only selecte non-empty WPs which is important e.g. for PDS or AFD
    wps = sorted(list(set([WP_START[wp-1] for wp in grouped.WP])))
    dim_values = list(set(grouped[dimension])) # e.g. ['männlich', 'weiblich']
    traces_values = []

    # TODO: mit 0en 'auffüllen', sonst kommen z.B. bei AFD seltsame Dinge raus, weil die meisten WPs nicht präsent
    for dim_value in dim_values:
        trace = grouped[grouped[dimension] == dim_value].sort_values(by='WP').ID.values
        traces_values.append(trace)
    
    traces = [go.Bar(x=wps, y=trace, xaxis='x2', yaxis='y2',
                marker=dict(color=color), #'#0099ff'),
                name=f'{dim_value}') for trace, dim_value, color in zip(traces_values, dim_values, LIST_OF_COLORS[:len(dim_values)])]
    
    return traces

    
    
# gender
@app.callback(
    Output('gender', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('wp_start', 'value'),
     State('wp_end', 'value'),
     State('check_list', 'value')
     ])
def update_graph_gender(n_clicks, start_date, end_date, selected_parteien):    
    grouped = select_data(start_date, end_date, selected_parteien, dimension='GESCHLECHT')
    traces = compute_traces(grouped, start_date, end_date, selected_parteien, dimension='GESCHLECHT')
    
    fig = {'data': traces,
        'layout': go.Layout(title = 'Gender')}
    
    return fig



# party
@app.callback(
    Output('party', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('wp_start', 'value'),
     State('wp_end', 'value'),
     State('check_list', 'value')
     ])
def update_graph_party(n_clicks, start_date, end_date, selected_parteien):    

    grouped = select_data(start_date, end_date, selected_parteien, dimension='PARTEI_KURZ')
    traces = compute_traces(grouped, start_date, end_date, selected_parteien, dimension='PARTEI_KURZ')
    
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
     State('check_list', 'value')
     ])
def update_graph_religion(n_clicks, start_date, end_date, selected_parteien):    
    
    grouped = select_data(start_date, end_date, selected_parteien, dimension='RELIGION')
    traces = compute_traces(grouped, start_date, end_date, selected_parteien, dimension='RELIGION')
    fig = {'data': traces,
        'layout': go.Layout(title = 'Religion')}
    return fig


# familienstand
@app.callback(
    Output('familienstand', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('wp_start', 'value'),
     State('wp_end', 'value'),
     State('check_list', 'value')
     ])
def update_graph_religion(n_clicks, start_date, end_date, selected_parteien):    
    grouped = select_data(start_date, end_date, selected_parteien, dimension='FAMILIENSTAND')
    traces = compute_traces(grouped, start_date, end_date, selected_parteien, dimension='FAMILIENSTAND')
    fig = {'data': traces,
        'layout': go.Layout(title = 'Familienstand')}
    return fig



#beruf
@app.callback(
    Output('beruf', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('wp_start', 'value'),
     State('wp_end', 'value'),
     State('check_list', 'value')
     ])
def update_graph_religion(n_clicks, start_date, end_date, selected_parteien):    
    grouped = select_data(start_date, end_date, selected_parteien, dimension='BERUF')
    traces = compute_traces(grouped, start_date, end_date, selected_parteien, dimension='BERUF')
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
     State('check_list', 'value')
     ])
def update_feedback_records(n_clicks, page_current, page_size, start_date, end_date, selected_parteien):
    
    # select wahlperiode
    wps = range(start_date, end_date)
    selected_df = pd.concat([df_mdb[df_mdb[str(i)] == 1] for i in range(start_date,end_date+1)]).drop_duplicates()
    
    # selct partei
    selected_df = selected_df[selected_df['PARTEI_KURZ'].isin(selected_parteien)]
    logging.info(f'selected {selected_df.shape} many entries')
    
    return selected_df.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ][COLUMNS_FOR_DISPLAY].to_dict('records')







if __name__ == '__main__':
    app.run_server(debug=True)