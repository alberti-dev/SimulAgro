# app.py

# Dashboard interattiva
# Basandosi sui dati generati dal simulatore "datacollection.py", fornisce una vista interattiva delle informazioni sotto forma
# di grafici e tabelle.
# Basandosi sui dati generati dal modulo "dataprediction-py", fornisce una vista interattiva delle previsioni di produzione


# Importazione delle librerie necessarie
import dash  # Per creare l'applicazione web interattiva
import dash_bootstrap_components as dbc  # Componenti di Dash basati su Bootstrap
from dash import Dash, dcc, html, dash_table, callback_context  # Componenti principali di Dash
from dash.dependencies import Input, Output, State  # Per gestire gli input, gli output e gli stati della dashboard
import datacollection  # Modulo personalizzato per la raccolta di dati random
import io  # Per gestire file in memoria
import numpy as np  # Per la generazione di numeri casuali e le operazioni sugli array
import pandas as pd  # Per la gestione e la manipolazione dei dataframe
import plotly.express as px  # Per la creazione di grafici
import plotly.graph_objects as go  # Per grafici avanzati
import dataprediction # Per il calcolo della produzione futura

# Caricamento dati iniziali (ambientali e di produzione)
#data_env = pd.read_csv("data_env.csv")
#data_prod = pd.read_csv("data_prod.csv")
from pathlib import Path
curr_folder = Path(__file__).parent.resolve()
data_env = pd.read_csv(curr_folder/"data_env.csv")
data_prod = pd.read_csv(curr_folder/"data_prod.csv")

# Creazione dei DataFrame
df_env = pd.DataFrame(data_env) # Dati ambientali
df_prod = pd.DataFrame(data_prod) # Dati di produzione
df_perf = datacollection.calc_perf_indicators(df_prod, df_env) # Dati di performance
df_future = datacollection.df_future  # Dati di previsione

# Dizionario per la traduzione delle intestazioni di colonna delle tabelle visualizzate sotto i grafici
col_mapping = {
    "Year": "Anno", "Temperature": "Temperatura (°C)", "Humidity": "Umidità (%)",
    "Precipitation": "Precipitazioni (mm)", "Growth_Days": "Giorni di Crescita",
    "Yield": "Raccolto (Kg)", "Water_Consumption": "Consumo Acqua (L/ha)",
    "Fertilizer_Consumption": "Consumo Fertilizzante (kg/ha)", "Efficiency": "Efficienza",
    "Env_Sustain": "Sostenibilità", "Total_Cost": "Totale Costi (€)",
    "Total_Price": "Totale Ricavi (€)", "Gain": "Profitto (€)", "Profit_Margin": "Margine di Profitto (%)"
}


#### Creazione dei grafici ####

# Creazione del grafico dei dati ambientali (df_env è il DataFrame contenente i dati da visualizzare)
def create_fig_env(df_env):
    # Inizializzazione del grafico
    fig = go.Figure()
    # Aggiunta al grafico dei tracciati basati sui dati di temperatura (asse y1), umidità e precipitazioni (asse y2)
    fig.add_trace(go.Scatter(x=df_env['Year'], y=df_env['Temperature'], mode='lines', name='Temperatura (°C)', yaxis='y1'))
    fig.add_trace(go.Scatter(x=df_env['Year'], y=df_env['Humidity'], mode='lines', name='Umidità (%)', yaxis='y2'))
    # I dati relativi alle precipitazioni vengono normailizzati
    fig.add_trace(go.Scatter(x=df_env['Year'], y=(df_env['Precipitation'])/10, mode='lines', name='Precipitazioni (mm)', yaxis='y2'))

    # Configurazione del layout del grafico
    fig.update_layout(
        # Impostazione titolo
        title="Andamento Annuale di Temperatura, Umidità e Precipitazioni",
        # Impostazione titoli degli assi
        xaxis=dict(title="Anno", tickformat=".0f", dtick=1),
        yaxis=dict(title="Temperatura (°C)", side='left'),
        # Le precipitazioni vengono contenute nel range 0-150
        yaxis2=dict(title="Umid.(%) e Prec.(mm)", side='right', overlaying='y', range=[0, 150]),
        # Impostazione tema grafico
        template="plotly_dark",
        # Impostazione posizionamento della legenda
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1.0)
    )
    # Restituzione del grafico creato
    return fig

# Creazione del grafico a barre raggruppate dei dati di produzione (df_prod è il DataFrame contenente i dati da visualizzare)
def create_fig_prod(df_prod):
    fig = px.bar(df_prod, x='Year', y=df_prod.columns[1:], barmode='group',
                 labels={'Year': 'Anno', 'value': 'Valore', 'variable': ''},
                 title='Confronto fra indicatori per anno', template="plotly_dark")
    # Aggiorna i nomi delle tracce in base al mapping predefinito nel dizionario col_mapping
    fig.for_each_trace(lambda trace: trace.update(name=col_mapping.get(trace.name, trace.name)))
    return fig

# Creazione dei grafici di performance 2D e 3D (df_perf è il DataFrame contenente i dati da visualizzare)
def create_fig_perf(df_perf):
    fig_3d = px.scatter_3d(df_perf, x='Total_Cost', y='Total_Price', z='Gain', color='Year',
                           title="Relazione tra Costi, Ricavi e Profitti", labels=col_mapping, template="plotly_dark")
    fig_2d = px.scatter(df_perf, x='Efficiency', y='Env_Sustain', color='Year',
                        title="Confronto tra Efficienza e Sostenibilità Ambientale", labels=col_mapping, template="plotly_dark")
    return fig_3d, fig_2d

# Creazione del grafico per i dati previsionali di produzione e ambientali (df_future è il DataFrame contenente i dati da visualizzare)
def create_fig_future(df_future):
    fig = go.Figure()

    # Aggiunta delle curve per i vari parametri
    fig.add_trace(go.Scatter(x=df_future['Year'], y=df_future['Growth_Days'], mode='lines', name='Giorni di Crescita'))
    fig.add_trace(go.Scatter(x=df_future['Year'], y=df_future['Yield'], mode='lines', name='Raccolto (Kg)'))
    fig.add_trace(go.Scatter(x=df_future['Year'], y=df_future['Water_Consumption'], mode='lines', name='Consumo Acqua (L/ha)'))
    fig.add_trace(go.Scatter(x=df_future['Year'], y=df_future['Fertilizer_Consumption'], mode='lines', name='Consumo Fertilizz. (kg/ha)'))
    
    # Dati ambientali (Temperature, Humidity, Precipitation) eventualmente da inserire nel grafico
    #fig.add_trace(go.Scatter(x=df_future['Year'], y=df_future['Temperature'], mode='lines', name='Temperatura (°C)', line=dict(dash='dot')))
    #fig.add_trace(go.Scatter(x=df_future['Year'], y=df_future['Humidity'], mode='lines', name='Umidità (%)', line=dict(dash='dot')))
    #fig.add_trace(go.Scatter(x=df_future['Year'], y=df_future['Precipitation'], mode='lines', name='Precipitazioni (mm)', line=dict(dash='dot')))
    
    # Configurazione del layout
    fig.update_layout(
        title="Previsione Futura di Produzione e Dati Ambientali",
        xaxis=dict(
            title="Anno",
            tickmode='array',  # Impostiamo i tick su valori discreti (anno per anno)
            tickvals=df_future['Year'],  # I tick dell'asse x saranno i valori presenti in df_future['Year']
            ticktext=df_future['Year'].astype(str),  # Visualizziamo gli anni come stringhe (interi senza decimali)
        ),
        yaxis=dict(title="Valore"),
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1.0)
    )

    return fig


#### Layout dell'applicazione ####

# Creazione dell'applicazione Dash con tema Bootstrap "Sandstone" e icone Font Awesome
app = Dash(__name__, title='Simul-Agro', external_stylesheets=[dbc.themes.SANDSTONE, dbc.icons.FONT_AWESOME])

# Layout della Dashboard interattiva
app.layout = html.Div(children=[
    # Aggiunta di un componente dcc.Location per gestire l'url dell'applicazione in funzione del callback che aggiorna i dati previsionali ad ogni caricamento della pagina
    dcc.Location(id='url', refresh=False), 
    # Container dell'applicazione
    dbc.Container([  
        # Intestazione
        dbc.Row([dbc.Col(html.H1('Monitoraggio delle Prestazioni Aziendali', className="text-center text-primary"), width=12)], className="my-4"),
        dbc.Row([dbc.Col(html.H2('- dashboard interattiva -', className="text-center text-primary"), width=12)], className="my-4"),
        # Aggiunta di un componente dcc.Store per memorizzare i dati futuri
        dcc.Store(id='store-future-data', data=None),
        # Sezione contenente il pulsante per la generazione di dati casuali e quello per effettuare il download
        html.Div(children=[
            dbc.Button('Genera Dati Casuali', id='btn-random', n_clicks=0, color="primary", size="sm", className="mt-3", style={'width': '180px'}),
            dbc.Button('Download Dati', id='btn-download', n_clicks=0, color="primary", size="sm", className="mt-3", style={'width': '180px'}),
            dcc.Download(id="download-data"),
            html.Div(id="output-div")
        ], className="d-flex flex-column justify-content-center align-items-end my-4"),
        
        # Sezione per i dati ambientali
        html.Div(children=[
            # Titolo della sezione
            html.H2("Dati Ambientali", className="my-4"),
            # Grafico
            dcc.Graph(id='fig_env', figure=create_fig_env(df_env)),
            # Tabella dati
            dash_table.DataTable(id='env-table', columns=[{"name": col_mapping[col], "id": col} for col in df_env.columns], data=df_env.to_dict('records'), sort_action='native', sort_by=[{'column_id': 'Year', 'direction': 'desc'}], style_table={'overflowX': 'auto'})
        ], className="my-4"),

        # Sezione per i dati di produzione
        html.Div(children=[
            # Titolo della sezione
            html.H2("Dati di Produzione", className="my-4"),
            # Grafico
            dcc.Graph(id='fig_prod', figure=create_fig_prod(df_prod)),
            # Tabella dati
            dash_table.DataTable(id='production-table', columns=[{"name": col_mapping[col], "id": col} for col in df_prod.columns], data=df_prod.to_dict('records'), sort_action='native', sort_by=[{'column_id': 'Year', 'direction': 'desc'}], style_table={'overflowX': 'auto'})
        ], className="my-4"),

        # Sezione per i dati di performance
        html.Div(className="row", children=[
            # Titolo della sezione
            html.H2("Dati di Performance", className="my-4"),
            # Grafici affiancati
            html.Div(children=[dcc.Graph(id="fig_perf2")], className="col-6"),
            html.Div(children=[dcc.Graph(id="fig_perf1")], className="col-6")
        ]),
        # Sezione che ospita la tabella dei dati performance
        html.Div(children=[
            html.H2("", className="my-4"),
            dash_table.DataTable(id='performance-table', columns=[{"name": col_mapping[col], "id": col} for col in df_perf.columns], data=df_perf.to_dict('records'), sort_action='native', sort_by=[{'column_id': 'Year', 'direction': 'desc'}], style_table={'overflowX': 'auto'})
        ], className="my-4"),

        # Sezione per i dati previsionali
        html.Div(children=[  
            # Titolo della sezione
            html.H2("Previsione di Produzione", className="my-4"),
            
            # Filtro per selezionare l'intervallo temporale
            html.Div([
                html.Label("Seleziona periodo:"),
                dcc.RangeSlider(
                    id='year-range-slider',
                    min=df_future['Year'].min(),  # Anno minimo
                    max=df_future['Year'].max(),  # Anno massimo
                    step=1,
                    marks={year: str(year) for year in range(df_future['Year'].min(), df_future['Year'].max() + 1)}, # Marks sulla linea dello slider
                    value=[df_future['Year'].min(), df_future['Year'].max()]  # Impostazione predefinita dell'intervallo
                )
            ], className="my-4"),

            # Grafico previsionale
            dcc.Graph(id='fig_future', figure={}),
                      
            # Tabella dati previsionali
            dash_table.DataTable(
                id='future-table',
                columns=[
                    {"name": "Anno", "id": "Year"},
                    {"name": "Temperatura (°C)", "id": "Temperature"},
                    {"name": "Umidità (%)", "id": "Humidity"},
                    {"name": "Precipitazioni (mm)", "id": "Precipitation"},
                    {"name": "Giorni di Crescita", "id": "Growth_Days"},
                    {"name": "Consumo Acqua (L/ha)", "id": "Water_Consumption"},
                    {"name": "Consumo Fertilizz. (kg/ha)", "id": "Fertilizer_Consumption"},
                    {"name": "Raccolto (Kg)", "id": "Yield"}
                ],
                data=[],
                sort_action='native',
                sort_by=[{'column_id': 'Year', 'direction': 'desc'}],
                style_table={'overflowX': 'auto'}
            )
        ], className="my-4"),

    # Footer della pagina
    html.Footer([
        dbc.Row([
            dbc.Col(html.P("Simul-Agro | Dashboard interattiva in Python per l'analisi delle prestazioni aziendali", className="text-center text-muted"), width=12),
            dbc.Col(html.P("Autore: Paolo Alberti | Email: alberti.paolo@gmail.com | a.a. 2024/2025 | Unipegaso Project Work - Traccia: 1.6", className="text-center text-muted"), width=12)
        ], className="py-3")
    ], className="bg-light mt-5")
    ])
])


#### Funzioni di callback invocate dalle interazioni con grafici, tabelle e pulsanti ####

# Callback per aggiornare le tabelle e i grafici quando viene premuto il pulsante btn-random
@app.callback(
    # Target delle azioni di callback
    Output('env-table', 'data'),  # Dati per la tabella ambientale
    Output('production-table', 'data'),  # Dati per la tabella di produzione
    Output('performance-table', 'data'),  # Dati per la tabella di performance
    Output('fig_env', 'figure'),  # Grafico dei dati ambientali
    Output('fig_prod', 'figure'),  # Grafico dei dati di produzione
    Output('fig_perf1', 'figure'),  # Grafico 3D dei dati di performance
    Output('fig_perf2', 'figure'),  # Grafico 2D dei dati di performance
    # Oggetti scatenanti le azioni di callback
    Input('btn-random', 'n_clicks')  # Input: numero di clic sul pulsante
)
# Funzione che aggiorna la dashboard in base a degli eventi specifici
def update_dashboard(n_clicks):
    ctx = callback_context

    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        # Se l'evento è il click del pulsante
        if triggered_id == 'btn-random' and n_clicks > 0:
            new_df_env = datacollection.get_env_data(np.arange(2020, 2025))
            new_df_prod = datacollection.get_prod_data(new_df_env, 50)
            new_df_perf = datacollection.calc_perf_indicators(new_df_prod, new_df_env)

            return (new_df_env.round(3).to_dict('records'),
                    new_df_prod.round(3).to_dict('records'),
                    new_df_perf.round(3).to_dict('records'),
                    create_fig_env(new_df_env),
                    create_fig_prod(new_df_prod),
                    *create_fig_perf(new_df_perf))

    return (df_env.to_dict('records'),
            df_prod.to_dict('records'),
            df_perf.to_dict('records'),
            create_fig_env(df_env),
            create_fig_prod(df_prod),
            *create_fig_perf(df_perf))

# Callback per il download dei dati filtrati in Excel
@app.callback(
    Output("download-data", "data"),
    Input("btn-download", "n_clicks"),
    dash.dependencies.State('env-table', 'data'), 
    dash.dependencies.State('production-table', 'data'),
    dash.dependencies.State('performance-table', 'data')
)
def download_data(n_clicks, env_data, prod_data, perf_data):
    if n_clicks > 0:
        df_env_download = pd.DataFrame(env_data)
        df_prod_download = pd.DataFrame(prod_data)
        df_perf_download = pd.DataFrame(perf_data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_env_download.to_excel(writer, sheet_name='Dati Ambientali', index=False)
            df_prod_download.to_excel(writer, sheet_name='Dati di Produzione', index=False)
            df_perf_download.to_excel(writer, sheet_name='Dati di Performance', index=False)

        output.seek(0)
        return dcc.send_bytes(output.getvalue(), "dati_completi.xlsx")
    
    return dash.no_update

# Callback che aggiorna grafico e tabella previsionali (richiamato dalla pressione del pulsante, dall'agire sugli slider#
# o al caricamento della pagina)
@app.callback(
    [Output('store-future-data', 'data'),       # Memorizza i dati futuri
     Output('fig_future', 'figure'),             # Grafico con i dati futuri
     Output('future-table', 'data')],            # Tabella con i dati futuri
    [Input('btn-random', 'n_clicks'),            # Clic del pulsante "Genera dati casuali"
     Input('url', 'pathname'),                  # Trigger per il caricamento della pagina
     Input('year-range-slider', 'value')],      # Trigger per il RangeSlider (anno selezionato)
    [State('store-future-data', 'data')]        # Stato dei dati futuri memorizzati
)
# Funzione che aggiorna grafico e tabella provisionali in base a degli eventi specifici
def update_future_data(n_clicks, pathname, year_range, stored_data):
    ctx = callback_context

    # Se la pagina è stata caricata (trigger al caricamento della pagina)
    if ctx.triggered_id == 'url' or (n_clicks is None and stored_data is None):
        # Se non ci sono dati memorizzati, li calcoliamo al caricamento
        new_df_env = datacollection.get_env_data(np.arange(2020, 2025))  # Ottieni i nuovi dati ambientali
        new_df_prod = datacollection.get_prod_data(new_df_env, 50)  # Ottieni i nuovi dati di produzione

        # Calcoliamo i nuovi dati futuri
        df_future = dataprediction.predict_future_production(new_df_env, new_df_prod)

        # Memorizziamo i nuovi dati futuri nel componente `dcc.Store`
        stored_data = df_future.to_dict('records')
    # Se viene premuto il pulsante btn-random
    elif ctx.triggered_id == 'btn-random' and n_clicks > 0:
        # Se il pulsante è stato cliccato, rigenera i nuovi dati casuali
        new_df_env = datacollection.get_env_data(np.arange(2020, 2025))  # Ottieni i nuovi dati ambientali
        new_df_prod = datacollection.get_prod_data(new_df_env, 50)  # Ottieni i nuovi dati di produzione

        # Calcoliamo i nuovi dati futuri
        df_future = dataprediction.predict_future_production(new_df_env, new_df_prod)

        # Memorizziamo i nuovi dati futuri nel componente `dcc.Store`
        stored_data = df_future.to_dict('records')
    else:
        # Se non ci sono trigger, usiamo i dati già memorizzati
        df_future = pd.DataFrame(stored_data)

    # Filtriamo i dati in base all'intervallo di anni selezionato nel RangeSlider
    filtered_df_future = df_future[(df_future['Year'] >= year_range[0]) & (df_future['Year'] <= year_range[1])]

    # Creiamo il grafico con i dati filtrati
    fig_future = create_fig_future(filtered_df_future)

    # Restituiamo i dati futuri, il grafico e la tabella
    return stored_data, fig_future, filtered_df_future.round(3).to_dict('records')


#### Avvio del server dell'applicazione Dash ####
if __name__ == '__main__':
    app.run_server(debug=True)