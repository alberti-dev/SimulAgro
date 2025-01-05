# layout.py

# E' il modulo che gestisce l'aspetto della dashboard, creando nella pagina una serie di elementi
# html al cui interno posizionerà pulsanti, grafici, tabelle, slider, etc.
# Per questi elementi sono previste indicazioni circa le specifiche di visualizzazione (dimensione, ordinamento, 
# allineamento, etc.)

# Importazione delle librerie necessarie
# Componenti principali di Dash:
# - dcc: Per aggiungere componenti interattivi come grafici, dropdown, slider, etc.
# - html: Per creare elementi HTML (come div, paragrafi, titoli) direttamente in Python
# - dash_table: Per creare tabelle interattive, utili per visualizzare e modificare dati tabellari
from dash import dcc, html, dash_table
# Libreria Dash Bootstrap Components che consente di utilizzare componenti 
# pre-stilizzati quali pulsanti, card, etc.
import dash_bootstrap_components as dbc
# Funzioni personalizzate dal package "data_tools":
from data_tools.data import load_initial_data # per caricare e pre-elaborare i dati iniziali richiesti dall'app
from interface.charts import create_fig_env, create_fig_prod # per creare i grafici relativi ai dati ambientali e di produzione

# Caricamento dati iniziali
# Unpacking della funzione load_initial_data del modulo data.py del package data_tools:
# gli elementi restituiti vengono assegnati a delle variabili che popoleranno i grafici creati in seguito
df_env, df_prod, df_perf, df_future, col_mapping = load_initial_data()

# Si crea una copia di df_env con le precipitazioni riportate in cm invece che in mm
# Copia df_env per evitare modifiche indesiderate all'originale
df_env_table = df_env.copy()
# Converti la colonna 'Precipitation' in centimetri
# Il DataFrame sarà quello visualizzato sotto al grafico dei dati ambientali
df_env_table['Precipitation'] = df_env_table['Precipitation'] / 10

# Layout della dashboard
# Viene creato un Div principale e al suo interno vengono inseriti in puro stile html gli elementi costituenti la pagina
def create_layout(app):
    return html.Div(children=[
        dcc.Location(id='url', refresh=False),
        dbc.Container([
            # Intestazione
            html.Header([
            dbc.Row([
                dbc.Col(html.H1('Monitoraggio delle Prestazioni Aziendali', className="text-center text-primary"), width=12),
                dbc.Col(html.H2('- dashboard interattiva -', className="text-center text-primary"), width=12)
            ], className="my-4")
			]),
            
			# Inizializzazione del componente deputato a memorizzare temporaneamente i dati previsionali (lato client) 
			# all'interno della dashboard.
            # Verrà alimentato ed aggiornato dalla callback che aggiorna grafico e tabella previsionali ogni volta che 
			# si clicca sul pulsante che genera dati casuali, ogni volta che si sposta la slider per filtrare il periodo 
			# desiderato e ogni volta che si aggiorna la pagina
            dcc.Store(id='store-future-data', data=None),
            dcc.Store(id='store-global-df-future', data=None),  # Store per df_future

            # Barra di navigazione (Menubar)
            dbc.Navbar(
                dbc.Container([
                    # Spaziatura sinistra
                    html.Div([], style={"flex": 1}),
                    
                    # Pulsanti centrali
                    dbc.Nav([
                        dbc.NavItem(dbc.Button('Genera Dati Casuali', id='btn-random', n_clicks=0, color="primary", size="sm", \
                                               className="me-2", style={'width': '180px'})),
                        dbc.Tooltip("Genera un set di dati casuali per la dashboard", target="btn-random", placement="bottom"),
                        dbc.NavItem(dbc.Button('Download Dati', id='btn-download', n_clicks=0, color="primary", size="sm", \
                                               className="me-2", style={'width': '180px'})),
                        dbc.Tooltip("Scarica i dati generati in formato Excel", target="btn-download", placement="bottom"),
						# Incapsula il pulsante "Genera Report" in dcc.Loading per visualizzare uno spinner durante la generazione del PDF                    
						dbc.NavItem(dcc.Loading(id="spinner-container",	type="circle", color="#0d6efd",  # Tipo e colore dello spinner
								children=dbc.Button('Genera Report', id='btn-generate-report', n_clicks=0, color="primary", size="sm",
													className="me-2", style={'width': '180px'}))),
                        dbc.Tooltip("Crea un report in PDF basato sui dati visualizzati", target="btn-generate-report", placement="bottom"),
                        dcc.Download(id="download-data"),
                        dcc.Download(id="download-report"),
                    ], className="d-flex justify-content-center"),

                    # Spaziatura destra
                    html.Div([], style={"flex": 1}),
                ]),
                color="light",  # Colore chiaro per abbinarsi all'header
                dark=False,
                className="shadow-sm my-2"  # Leggera ombra e margine verticale
            ),
			dbc.CardGroup([
				# Grafico e tabella relativi ai dati ambientali
				dbc.Card([
					dbc.CardBody([
						html.H4("Dati Ambientali", className="my-4"),
						dcc.Graph(id='fig_env', figure=create_fig_env(df_env), config={'locale': 'it'}),
						html.Div(
							className="custom-table-container",  # Classe CSS specifica per il contenitore delle tabelle
							children=[
								dash_table.DataTable(
									id='env-table',
									# le intestazioni di colonna vengono "tradotte" utilizzando il dizionario importato 
									columns=[{"name": col_mapping[col], "id": col} for col in df_env.columns],
									data=df_env_table.to_dict('records'),
									# viene scelto un ordinamento discendente per anno
									sort_action='native', sort_by=[{'column_id': 'Year', 'direction': 'desc'}],
									# la tabella si ridimensiona in base alla dimensione della pagina
									style_table={'overflowX': 'auto'}
								)
							])
					]),
				]),
				
				# Grafico e tabella relativi ai dati di produzione
				dbc.Card([
					dbc.CardBody([
						# Titolo della sezione
						html.H4("Dati di Produzione", className="my-4"),
						# Grafico
						dcc.Graph(id='fig_prod', figure=create_fig_prod(df_prod), config={'locale': 'it'}),
						# Tabella dati
						html.Div(
							className="custom-table-container",  # Classe CSS specifica per il contenitore delle tabelle
							children=[                
								# Così come per la tabella dei dati ambientali, si traducono le intestazioni di colonna e si ordinano 
								# i dati per anno (discendente)
								dash_table.DataTable(id='production-table', columns=[{"name": col_mapping[col], "id": col} for col in df_prod.columns], \
                             			data=df_prod.to_dict('records'), sort_action='native', sort_by=[{'column_id': 'Year', 'direction': 'desc'}], \
                                            style_table={'overflowX': 'auto'})
							]
						)
					])
				]),
			]),

			dbc.Card([
				dbc.CardBody([
					# Grafici relativi ai dati di performance
					html.Div(className="row", children=[
						# Titolo della sezione
						html.H4("Dati di Performance", className="my-4"),
						# Con "col-6", entrambi i grafici occupano il 50% della larghezza della riga ciascuna, posizionandosi affiancati
						html.Div(children=[dcc.Graph(id="fig_perf2", config={'locale': 'it'})], className="col-6"),
						html.Div(children=[dcc.Graph(id="fig_perf1", config={'locale': 'it'})], className="col-6")
					]),
					# Tabella dei dati performance
					html.Div(children=[
						html.H2("", className="my-4"),
						html.Div(
							className="custom-table-container",  # Classe CSS specifica per il contenitore delle tabelle
							children=[                
								# si traducono le intestazioni di colonna e si ordinano i dati per anno (discendente)
								dash_table.DataTable(id='performance-table', columns=[{"name": col_mapping[col], "id": col} for col in df_perf.columns], \
										data=df_perf.to_dict('records'), sort_action='native', sort_by=[{'column_id': 'Year', 'direction': 'desc'}], \
                                            style_table={'overflowX': 'auto'})
							]
						)
					], className="my-4"),
				])
			]),


			dbc.Card([
				dbc.CardBody([
				# Grafico e tabella relativi ai dati previsionali
					# Titolo della sezione
					html.H4("Previsione di Produzione", className="my-4"),
					
					# Slider che consente di filtrare i dati selezionando l'intervallo temporale
					html.Div([
						html.Label("Seleziona periodo:"),
						dcc.RangeSlider(
							id='year-range-slider',
							min=df_future['Year'].min(),  # Anno minimo
							max=df_future['Year'].max(),  # Anno massimo
							step=1,
							marks={year: str(year) for year in range(df_future['Year'].min(), df_future['Year'].max() + 1)}, # Marks sulla linea dello slider
							value=[df_future['Year'].min(), df_future['Year'].max()]  # Impostazione predefinita dell'intervallo
						),
						dbc.Tooltip(
							"Usa le maniglie dello slider per impostare un range temporale e filtrare i dati",  # Testo del tooltip
							target="year-range-slider",  # Associa il tooltip allo slider
							placement="top"  # Posizione del tooltip sopra lo slider
						),                        
					], className="my-4"),

					# Grafico previsionale
					dcc.Graph(id='fig_future', figure={}, config={'locale': 'it'}),
							
					# Tabella dati previsionali
					html.Div(
						className="custom-table-container",  # Classe CSS specifica per il contenitore delle tabelle
						children=[                
							dash_table.DataTable(
								id='future-table',
								columns=[
									{"name": "Anno", "id": "Year"},
									{"name": "Temperatura (°C)", "id": "Temperature"},
									{"name": "Umidità (%)", "id": "Humidity"},
									{"name": "Precipitazioni (cm)", "id": "Precipitation"},
									{"name": "Giorni di Crescita", "id": "Growth_Days"},
									{"name": "Consumo Acqua (dm3)", "id": "Water_Consumption"},
									{"name": "Consumo Fertilizz. (q)", "id": "Fertilizer_Consumption"},
									{"name": "Raccolto (q)", "id": "Yield"}
								],
								# Si inizializza la tabella vuota
								# I dati saranno aggiunti tramite callback azionata dal caricamento della pagina, dal clic 
								# sul pulsante btn-random o dalla slider
								data=[],
								sort_action='native',
								sort_by=[{'column_id': 'Year', 'direction': 'desc'}],
								style_table={'overflowX': 'auto'}
							)
						]
					)
				])
			]),

			dbc.Card([
				dbc.CardBody([
					# Sezione per il grafico e la tabella per l'anno prossimo
					html.H4("Previsioni per l'anno prossimo in funzione delle condizioni ambientali", className="my-4"),
					dbc.Row([
						# Colonna del grafico
						dbc.Col(
							dcc.Graph(id='fig_nextyear', figure={}, style={"margin-bottom": "0px"}, config={'locale': 'it'}),
							width=10,  # Il grafico occupa l'80% dello spazio orizzontale
						),
						# Colonna per le slider
						dbc.Col(
							html.Div(
								[
									
									html.Div(
										[
											# Slider per Temperatura
											html.Div([
												html.Label("T (°C)", className="slider-label"),  # Etichetta orizzontale sopra la slider
												dcc.Slider(
													id='temperature-slider',
													min=0, max=50, step=1, value=25,
													marks={i: str(i) for i in range(0, 51, 5)},
													vertical=True
												)
											], className="slider-div"),

											# Slider per Umidità
											html.Div([
												html.Label("U (%)", className="slider-label"),  # Etichetta orizzontale sopra la slider
												dcc.Slider(
													id='humidity-slider',
													min=0, max=100, step=5, value=50,
													marks={i: str(i) for i in range(0, 101, 10)},
													vertical=True
												)
											],  className="slider-div"),

											# Slider per Precipitazioni
											html.Div([
												html.Label("P (mm)", className="slider-label"),  # Etichetta orizzontale sopra la slider
												dcc.Slider(
													id='precipitation-slider',
													#min=200, max=800, step=10, value=350,
													#marks={i: str(i) for i in range(200, 801, 50)},
                                                    min=20, max=80, step=5, value=35,
													marks={i: str(i) for i in range(20, 81, 5)},
													vertical=True
												)
											],  className="slider-div")
										],
										style={
											'display': 'flex', 
											'flex-direction': 'row', 
											'align-items': 'center', 
										}
									),
								],
							),
							width=2,  # La colonna slider occupa il 20% dello spazio orizzontale
                            id="sliders", # Impostazione di un id per associare un tooltip
						),
                        dbc.Tooltip(
							"Modificando i valori ambientali, grafico e tabella si aggiorneranno in tempo reale",  # Testo del tooltip
							target="sliders",  # Associa il tooltip alla colonna con id="sliders"
							placement="top"  # Posizione del tooltip sopra la colonna
						),
					], style={"margin-bottom": "0px"}), 

					dbc.Row([
                        dbc.Col(
							# Tabella con i dati dell'anno prossimo
							html.Div(
								className="custom-table-container",  # Classe CSS specifica per il contenitore delle tabelle
								children=[
									dash_table.DataTable(
										id='grouped-bar-table',
										columns=[
											{"name": "Anno", "id": "Year"},
											{"name": "Temperatura (°C)", "id": "Temperature"},
											{"name": "Umidità (%)", "id": "Humidity"},
											{"name": "Precipitazioni (cm)", "id": "Precipitation"},
											{"name": "Giorni di Crescita", "id": "Growth_Days"},
											{"name": "Consumo Acqua (dm3)", "id": "Water_Consumption"},
											{"name": "Consumo Fertilizzanti (q)", "id": "Fertilizer_Consumption"},
											{"name": "Raccolto (q)", "id": "Yield"}
										],
										data=df_future.to_dict('records'),
										style_table={'overflowX': 'auto'},
										sort_action='native',
										sort_by=[{'column_id': 'Year', 'direction': 'desc'}]
									)
								]
							), width=10,
						),
                        
						dbc.Col(
                            html.Div([
                				html.Div(" ", style={"height": "100%"})  # Colonna vuota
            				]), width=2  # Stessa larghezza della colonna slider
						)
					]),
				])
			]),


		# Footer della pagina
		html.Footer([
			dbc.Row([
				dbc.Col(html.P("Simul-Agro | Dashboard interattiva in Python per l'analisi delle prestazioni aziendali | \
                   Autore: Paolo Alberti (alberti.paolo@gmail.com) | Unipegaso Project Work - Traccia: 1.6 | a.a. 2024/2025", \
                    className="text-center text-muted"), width=12),
			], className="py-3")
		], className="bg-light mt-5")
	
        ])
    ])