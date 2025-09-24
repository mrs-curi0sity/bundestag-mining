import logging
import sys
import os
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px


# Add parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.config import (
    LIST_OF_COLORS, PAGE_SIZE, COLUMNS_FOR_DISPLAY,
    DF_MDB_PATH, DF_MDB_WP_PATH, WP_START,
    LIST_OF_PARTEIEN as list_of_parteien,
    LIST_OF_RELIGION as list_of_religion,
    LIST_OF_CHILDREN as list_of_children, 
    LIST_OF_FAMILIENSTAND as list_of_familienstand,
    LIST_OF_BERUF as list_of_beruf,
    LIST_OF_ALTERSKLASSEN as list_of_altersklassen
)
from src.visualization import select_vis_data, compute_traces

from src.mapping_values import (
    get_color_for_party, 
    get_color_for_age_group, 
    get_color_palette 
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

df_mdb = pd.read_csv(DF_MDB_PATH)
df_mdb_wp = pd.read_csv(DF_MDB_WP_PATH)
MAX_WP = df_mdb_wp.WP.max()

# Globale Variable für gefilterte Daten
filtered_df = pd.DataFrame()

CONTENT_STYLE = {
    'margin-left': '4%',  # reduziert von 25%
    'margin-right': '4%', # reduziert von 5%
    'padding': '20px 10px'
}

# Neue Style für die unterschiedlichen Plot-Größen
PLOT_STYLE_HALF = {
    'height': 550  # für die 2-spaltigen Plots
}

PLOT_STYLE_FULL = {
    'height': 700  # für Berufe-Plot
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970',  # Dunkles Marineblau
    'marginBottom': '20px',
    'marginTop': '10px',
    'fontFamily': 'Arial, sans-serif',
    'fontSize': '24px',
    'fontWeight': 'bold'
}


# Helper functions
def create_dropdown(id, options, value):
    return dcc.Dropdown(
        id=id,
        options=[
            {'label': f"{WP_START[x-1]} - {WP_START[x]}", 'value': x} 
            for x in range(1, len(WP_START))  # Bis len(WP_START) statt MAX_WP+1
        ],
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

def create_button(id, label, color='primary'):
    return dbc.Button(
        id=id,
        children=label,
        color=color,
        className='w-100',
    )

filter_panel = dbc.Card([
    dbc.CardHeader("Filter"),
    dbc.CardBody([
        html.Div([
            html.Label("Wahlperioden:"),
            dbc.Row([
                dbc.Col([
                    html.Label("von:", className="mr-2"),
                    create_dropdown('wp_start', [], 1)
                ], md=6),
                dbc.Col([
                    html.Label("bis:", className="mr-2"),
                    create_dropdown('wp_end', [], MAX_WP)
                ], md=6)
            ]),
        ], className="mb-3"),
        html.Div([
            html.Label("Parteien:"),
            create_checklist('check_list_parteien', list_of_parteien, list_of_parteien),
            create_button('select_all_parteien', 'Alle auswählen/abwählen'),
        ], className="mb-3"),
        create_button('submit_button', 'Anwenden', color='warning')
    ])
])



# Initialize app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([
    html.H2('Bundestagsmining', style=TEXT_STYLE),
    html.Hr(),
    
    # Erste Zeile: Filter und Partei
    dbc.Row([
        dbc.Col(filter_panel, md=6),
        dbc.Col(dcc.Graph(id='party', config={'displayModeBar': False}), md=6)
    ], className="mb-4"),
    
    # Zweite Zeile: Geschlecht und Religion
    dbc.Row([
        dbc.Col(dcc.Graph(id='gender', config={'displayModeBar': False}), md=6),
        dbc.Col(dcc.Graph(id='religion', config={'displayModeBar': False}), md=6)
    ], className="mb-4"),
    
    # Dritte Zeile: Alter und Bleibedauer
    dbc.Row([
        dbc.Col(dcc.Graph(id='alter', config={'displayModeBar': False}), md=6),
        dbc.Col(dcc.Graph(id='num_years_in_bt', config={'displayModeBar': False}), md=6)
    ], className="mb-4"),
    
    # Vierte Zeile: Familienstand und Kinder
    dbc.Row([
        dbc.Col(dcc.Graph(id='familienstand', config={'displayModeBar': False}), md=6),
        dbc.Col(dcc.Graph(id='kinder', config={'displayModeBar': False}), md=6)
    ], className="mb-4"),
    
    # Fünfte Zeile: Berufe (volle Breite)
    dbc.Row([
        dbc.Col(dcc.Graph(id='beruf', config={'displayModeBar': False}), md=12)
    ], className="mb-4"),
    
    # Sechste Zeile: Datentabelle
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='selected_records',
                columns=[
                    {
                        'name': 'ALTER' if colname == 'START_AGE_IN_YEARS_MAPPED' else colname,
                        'id': colname,
                        'presentation': 'markdown' if colname == 'VITA_KURZ' else 'input',
                        'type': 'text',
                    } for colname in COLUMNS_FOR_DISPLAY
                ],
                page_size=20,
                page_current=0,
                page_action='custom',
                filter_action='custom',
                filter_query='',
                sort_action='custom',
                sort_mode='multi',
                sort_by=[{'column_id': 'WP', 'direction': 'desc'}],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '14px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': 0,
                    'minWidth': '120px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'textAlign': 'left'
                },
                style_cell_conditional=[
                    {
                        'if': {'column_id': 'VITA_KURZ'},
                        'maxWidth': '700px',
                        'minWidth': '600px',
                    },
                ] + [
                    {
                        'if': {'column_id': colname},
                        'maxWidth': '150px',
                    } for colname in COLUMNS_FOR_DISPLAY if colname != 'VITA_KURZ'
                ],
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'padding': '5px'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                css=[{
                    'selector': '.dash-spreadsheet td div',
                    'rule': '''
                        line-height: 15px;
                        max-height: 250px;
                        min-height: 30px;
                        height: auto;
                        white-space: normal;
                        overflow-y: auto;
                    '''
                }],
            ),
            html.Div(id='pagination-info')
        ], md=12)
    ])
], style=CONTENT_STYLE)


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


def update_graph(n_clicks, start_date, end_date, selected_parteien, dimension, values_to_keep, title):
    grouped = select_vis_data(df_mdb_wp, start_date, end_date, selected_parteien, dimension)
    
    # Konvertiere den Index zu Startdaten
    grouped.index = [WP_START[wp-1] for wp in grouped.index]
    
    # Filter info für Annotation
    if sorted(selected_parteien) == sorted(list_of_parteien):
       filter_text = "Gefiltert nach: allen Parteien"
    elif len(selected_parteien) == 1:
       filter_text = f"Gefiltert nach Partei: {', '.join(sorted(selected_parteien))}"
    else:
       filter_text = f"Gefiltert nach Parteien: {', '.join(sorted(selected_parteien))}"
    
    # Initialize traces list
    traces = []
    
    # Gemeinsame Layout-Parameter
    layout_params = dict(
        title=title,
        height=600 if dimension == 'BERUF_MAPPED' else 550,
        margin=dict(b=150),
        xaxis=dict(
            title='Jahr',
            ticktext=[f"{year}" for wp, year in enumerate(grouped.index, 1)],
            tickvals=list(range(len(grouped.index))),
            type='category'
        ),
        annotations=[dict(
            text=filter_text,
            xref="paper",
            yref="paper",
            x=0,
            y=-0.3,
            showarrow=False,
            align="left",
            font=dict(size=10)
        )],
        hovermode='x unified'
    )
    
    # Spezielle Layout-Parameter für den Berufe-Plot
# Spezielle Layout-Parameter für den Berufe-Plot
    if dimension == 'BERUF_MAPPED':
        layout_params.update(dict(
            height=700,  # oder welche Höhe du gewählt hast
            legend=dict(
                traceorder="normal",
                font=dict(size=10),
                yanchor="top",
                y=1,
                xanchor="left",
                x=1,
                bgcolor="white",
                bordercolor="gray",
                borderwidth=1,
                nrow=7,     # 7 Zeilen pro Spalte
                ncol=2      # 3 Spalten
            )
        ))

    if dimension == 'START_AGE_IN_YEARS_MAPPED':
        age_groups = list_of_altersklassen
        for age_group in age_groups:
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
        
        layout_params.update(dict(
            yaxis=dict(title='Anteil der Altersgruppen', tickformat=',.0%'),
            legend=dict(title='Altersgruppen')
        ))
        
    elif dimension == 'PARTEI_MAPPED':
        for party in values_to_keep:
            if party in grouped.columns:
                trace = go.Bar(
                    x=grouped.index,
                    y=grouped[party],
                    name=party,
                    marker_color=get_color_for_party(party)
                )
                traces.append(trace)
        
        layout_params.update(dict(
            yaxis=dict(title='Anteil der Parteien', tickformat=',.0%'),
            barmode='stack',
            legend=dict(title='Parteien')
        ))
        
    else:
        color_palette = get_color_palette(len(values_to_keep))
        
        traces.extend([go.Bar(
            x=grouped.index, 
            y=grouped[value] if value in grouped.columns else [0] * len(grouped.index), 
            name=value,
            marker_color=color_palette[i]
        ) for i, value in enumerate(reversed(values_to_keep))])
        
        layout_params.update(dict(
            yaxis=dict(title='Anteil', tickformat=',.0%'),
            barmode='stack',
            legend=dict(title=dimension)
        ))
    
    layout = go.Layout(**layout_params)
    return {'data': traces, 'layout': layout}


for graph_id, dimension, values_to_keep, title in [
    ('gender', 'GESCHLECHT', ['männlich', 'weiblich'], 'Geschlecht'),
    ('party', 'PARTEI_MAPPED', list_of_parteien, 'Partei'),
    ('religion', 'RELIGION_MAPPED', list_of_religion, 'Religion'),
    ('familienstand', 'FAMILIENSTAND_MAPPED', list_of_familienstand, 'Familienstand'),
    ('kinder', 'KINDER_MAPPED', list_of_children, 'Anzahl Kinder'), 
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
    selected_df = selected_df[selected_df['PARTEI_MAPPED'].isin(selected_parteien)]
    
    grouped = selected_df[['ID', 'START_DATE', 'NUM_YEARS_IN_BT', 'PARTEI_MAPPED']].groupby(['START_DATE', 'PARTEI_MAPPED']).mean()
    
    new_index = pd.MultiIndex.from_product([grouped.index.levels[0], grouped.index.levels[1]], names=['START_DATE', 'PARTEI_MAPPED'])
    grouped_reindexed = grouped.reindex(new_index, fill_value=0)
    grouped_reindexed.reset_index(inplace=True)
    
    # Erstelle Figure manuell statt px.line zu verwenden
    fig = go.Figure()
    
    # Füge für jede Partei eine separate Linie hinzu mit korrekter Farbe
    for partei in selected_parteien:
        partei_data = grouped_reindexed[grouped_reindexed['PARTEI_MAPPED'] == partei]
        fig.add_trace(go.Scatter(
            x=partei_data['START_DATE'],
            y=partei_data['NUM_YEARS_IN_BT'],
            mode='lines',
            name=partei,
            line=dict(
                color=get_color_for_party(partei),
                width=3
            )
        ))
    
    fig.update_layout(
        title='Bleibedauer der Abgeordneten im Bundestag',
        xaxis_title='',
        yaxis_title='Jahre im BT bei Beginn der WP',
        hovermode='x unified'
    )
    return fig

@app.callback(
    [Output('selected_records', 'data'),
     Output('selected_records', 'page_count'),
     Output('pagination-info', 'children')],
    [Input('submit_button', 'n_clicks'),
     Input('selected_records', 'page_current'),
     Input('selected_records', 'page_size'),
     Input('selected_records', 'sort_by'),
     Input('selected_records', 'filter_query')],
    [State('wp_start', 'value'),
     State('wp_end', 'value'), 
     State('check_list_parteien', 'value')]
)
def update_table(n_clicks, page_current, page_size, sort_by, filter_query, start_date, end_date, selected_parteien):
    global filtered_df
    
    ctx = dash.callback_context
    if not ctx.triggered:
        logger.info("Initial load")
        filtered_df = df_mdb_wp[(df_mdb_wp['WP'] >= 1) & (df_mdb_wp['WP'] <= MAX_WP)]
        filtered_df = filtered_df[filtered_df['PARTEI_MAPPED'].isin(list_of_parteien)][COLUMNS_FOR_DISPLAY].drop_duplicates()
        # Sort by WP in descending order initially
        filtered_df = filtered_df.sort_values('WP', ascending=False)
    elif ctx.triggered[0]['prop_id'] == 'submit_button.n_clicks':
        logger.info("Submit button clicked")
        filtered_df = df_mdb_wp[(df_mdb_wp['WP'] >= start_date) & (df_mdb_wp['WP'] <= end_date)]
        filtered_df = filtered_df[filtered_df['PARTEI_MAPPED'].isin(selected_parteien)][COLUMNS_FOR_DISPLAY].drop_duplicates()
        # Sort by WP in descending order after filtering
        filtered_df = filtered_df.sort_values('WP', ascending=False)
    
    working_df = filtered_df.copy()
    
    # Anwenden der Filter
    if filter_query:
        try:
            working_df = apply_filters(working_df, filter_query)
            logger.info(f"Number of rows after filtering: {len(working_df)}")
        except Exception as e:
            logger.error(f"Error applying filters: {str(e)}")
            logger.error(f"Filter query: {filter_query}")
    
    # Anwenden der Sortierung
    if sort_by:
        try:
            working_df = working_df.sort_values(
                [col['column_id'] for col in sort_by],
                ascending=[col['direction'] == 'asc' for col in sort_by],
                inplace=False
            )
        except Exception as e:
            logger.error(f"Error applying sort: {str(e)}")
    
    # Paginierung
    total_records = len(working_df)
    page_count = -(-total_records // page_size)  # Aufrunden
    page_current = 0 if page_current is None else page_current
    start = page_current * page_size
    end = (page_current + 1) * page_size
    
    page_data = working_df.iloc[start:end].to_dict('records')
    
    # Pagination Info
    pagination_info = f"Showing {start+1} to {min(end, total_records)} of {total_records} entries"
    
    logger.info(f"Returning {len(page_data)} records")
    
    return page_data, page_count, pagination_info

def apply_filters(df, filter_query):
    filtering_expressions = filter_query.split(' && ')
    dff = df.copy()
    
    for filter_part in filtering_expressions:
        col_name, op, filter_value = split_filter_part(filter_part)
        
        if not col_name:
            continue
            
        logger.info(f"Applying filter: column={col_name}, operator={op}, value={filter_value}")
        
        # Convert column to string for text-based operations
        if op in ('contains', 'scontains'):
            dff[col_name] = dff[col_name].astype(str)
        
        if op in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            try:
                filter_value = float(filter_value)
                dff = dff.loc[getattr(dff[col_name], op)(filter_value)]
            except ValueError:
                dff = dff.loc[getattr(dff[col_name], op)(filter_value)]
        elif op == 'contains':
            # Case-insensitive partial string match
            filter_value = str(filter_value).lower()
            dff = dff[dff[col_name].str.lower().str.contains(filter_value, regex=False, na=False)]
        elif op == 'scontains':
            # Case-sensitive contains (falls noch benötigt)
            dff = dff[dff[col_name].str.contains(filter_value, regex=False, na=False)]
        elif op == 'datestartswith':
            dff = dff[dff[col_name].str.startswith(filter_value, na=False)]
        
        logger.info(f"Rows remaining after filter: {len(dff)}")
    
    return dff

def split_filter_part(filter_part):
    for operator_type in ['eq', 'ne', 'lt', 'le', 'gt', 'ge', 'contains', 'scontains', 'datestartswith']:
        if operator_type in filter_part:
            name_part, value_part = filter_part.split(operator_type, 1)
            name = name_part[name_part.find('{') + 1: name_part.rfind('}')]
            value = value_part.strip()
            if value.startswith('{') and value.endswith('}'):
                value = value[1:-1]
            return name, operator_type, value
    return [None] * 3



def update_selected_cell(active_cell):
    if active_cell:
        return [{
            'if': {
                'row_index': active_cell['row'],
                'column_id': active_cell['column_id']
            },
            'maxHeight': 'none',
            'height': 'auto',
            'whiteSpace': 'normal',
            'textOverflow': 'clip',
            'overflow': 'auto'
        }]
    return []

if __name__ == '__main__':
    import os
    # Cloud Run setzt PORT automatisch, lokal verwende 8050
    port = int(os.environ.get("PORT", 8050))
    # Debug=False für Production
    debug = os.environ.get("ENVIRONMENT", "development") == "development"
    app.run_server(host="0.0.0.0", port=port, debug=debug)

server = app.server