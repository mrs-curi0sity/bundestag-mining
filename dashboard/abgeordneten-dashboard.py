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

DATA_PATH = Path('../data')
DF_MDB_PATH = DATA_PATH / 'df_mdb.csv'
df_mdb = pd.read_csv(DF_MDB_PATH)
logging.info(f'df_mdb: {df_mdb.head()}')

# retrieve 8 most common parties (incl AFD and PDS, excluding DP, FU etc)
list_of_parteien = list(df_mdb[['ID', 'PARTEI_KURZ']].groupby('PARTEI_KURZ').count().sort_values(by='ID', ascending=False).head(8).index)
list_of_parteien.append('sonstige')
logging.info(f'Parteien: {list_of_parteien}')
list_of_excluded_parteien = list(df_mdb[['ID', 'PARTEI_KURZ']].groupby('PARTEI_KURZ').count().sort_values(by='ID', ascending=False)[8:].index)

# replace andere parteien with 'sonstige'
for excluded_partei in list_of_excluded_parteien:
    df_mdb['PARTEI_KURZ'].replace(excluded_partei, 'sonstige', inplace=True)

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
                     options=[{'label':x, 'value': x} for x in range(1, 18)],
                    value=2),
        
        dcc.Dropdown(id='wp_end',
                     options=[{'label':x, 'value': x} for x in range(1, 18)],
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
    [# num per topic
        dbc.Col(
            dcc.Graph(id='gender'), md=6
        ),

        dbc.Col(
            dcc.Graph(id='confession'), md=6
        )

    ]
)

# this is just test content to check callback functionality
content_second_row = html.Div([
        dcc.RangeSlider(
        id='my-slider',
        min=-10,
        max=+10,
        step=1,
        value=[-1, 1],
        marks={i:i for i in range(-10, 10)},
        updatemode='drag'
    ),
    html.Div(id='slider-output-container'),
    html.Div('ABC')
])



content_third_row = dbc.Row(
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
        content_third_row
    ],
    style=CONTENT_STYLE
)


# --------------------- app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([sidebar, content])


# --------------------- callbacksf
#TODO delete. just a test
@app.callback(Output('slider-output-container', 'children'),
             [Input('my-slider', 'value')])
def compute_product(value):
    return value[0] * value[1]
    



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
            
    

@app.callback(
    Output('gender', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('wp_start', 'value'),
     State('wp_end', 'value'),
     State('check_list', 'value')
     ])
def update_graph_gender(n_clicks, start_date, end_date, selected_parteien):    
    logging.info(f'entry of update_graph_gender, n_clicks: {n_clicks}')

    # select wahlperiode
    wps = range(start_date, end_date)
    selected_df = pd.concat([df_mdb[df_mdb[str(i)] == 1] for i in range(start_date,end_date+1)]).drop_duplicates()
    
    # selct partei
    selected_df = selected_df[selected_df['PARTEI_KURZ'].isin(selected_parteien)]
    logging.info(f'selected {selected_df.shape} many entries')
    
    
    fig = {
        'data': [{
            #'x': selected_df.groupby([selected_df['at'].dt.date])['pos'].sum().index,
            #'y': selected_df.groupby([selected_df['at'].dt.date])['pos'].sum().values
            'x': selected_df[['ID', 'GESCHLECHT']].groupby('GESCHLECHT').count().sort_values(by='ID', ascending=False).index,
            'y': selected_df[['ID', 'GESCHLECHT']].groupby('GESCHLECHT').count().sort_values(by='ID', ascending=False).values

        }],
        'layout':{
            'title':'Overall Number of Customer Feedback'
        }
    }
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
    
    logging.info(f'RECORDS: selected {selected_df.head()}')
    
    return selected_df.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ][COLUMNS_FOR_DISPLAY].to_dict('records')







if __name__ == '__main__':
    app.run_server()