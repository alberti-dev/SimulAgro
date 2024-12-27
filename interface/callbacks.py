# dashboard_callbacks.py

# Modulo che definisce le callback che gestiscono eventi e interazioni con i componenti della dashboard 
# (clic sui pulsanti, modifica dei valori tramite slider, etc.)

# Importazione delle librerie necessarie
import pandas as pd # per la manipolazione e all'analisi dei dati
from dash import Input, Output, State, callback_context, dcc # per la gestione delle callback
from data_tools.data import generate_custom_data, load_initial_data, calc_future_production # per la gestione dei dati (iniziali, custom e futuri)
from data_tools.data_simulator import  generate_random_data # per la generazione di dati casuali
from data_tools.data_export import save_to_excel, create_pdf_report, format_table_data # per l'esportazione dei dati
from interface.charts import create_fig_env, create_fig_prod, create_fig_perf, create_fig_future, create_fig_nextyear # per la creazione dei grafici

# Funzione che registra tutte le callback necessarie
# Ogni callback è associata a specifici componenti della dashboard e risponde agli input utente
def register_callbacks(app):
    # Dati iniziali generati al caricamento dell'app
    initial_env, initial_prod, initial_perf = generate_random_data()

    # Quando il pulsante btn-random viene cliccato, si avvia la funzione che genera nuovi dati casuali
    @app.callback(
        [Output('env-table', 'data'),
         Output('production-table', 'data'),
         Output('performance-table', 'data'),
         Output('fig_env', 'figure'),
         Output('fig_prod', 'figure'),
         Output('fig_perf1', 'figure'),
         Output('fig_perf2', 'figure')],
        [Input('btn-random', 'n_clicks'), # Trigger per la generazione di dati casuali
         Input('url', 'pathname')]  # Trigger per il caricamento della pagina
    )
    def update_dashboard(n_clicks, pathname): 
        ctx = callback_context
        if ctx.triggered_id == 'url':
            # Usa i dati iniziali da load_initial_data
            df_env, df_prod, df_perf, df_future, col_mapping = load_initial_data()        
        # Se il pulsante è stato cliccato almeno una volta
        elif n_clicks and n_clicks > 0:
            df_env, df_prod, df_perf = generate_random_data()
            return (
                df_env.round(3).to_dict('records'),
                df_prod.round(3).to_dict('records'),
                df_perf.round(3).to_dict('records'),
                create_fig_env(df_env),
                create_fig_prod(df_prod),
                *create_fig_perf(df_perf)
            )
        # Se il pulsante non è stato ancora cliccato, usa i dati iniziali (l'arrotondamento a 3 decimali serve ad una migliore leggibilità)
        else:
            df_env, df_prod, df_perf = initial_env.round(3), initial_prod.round(3), initial_perf.round(3)

        # Restituisce i dati iniziali se non si opera nessun clic sul pulsante
        return (df_env.round(3).to_dict('records'),
                df_prod.round(3).to_dict('records'),
                df_perf.round(3).to_dict('records'),
                create_fig_env(df_env),
                create_fig_prod(df_prod),
                *create_fig_perf(df_perf))

    # Quando il pulsante btn-download viene cliccato, si avvia la funzione che genera un file Excel e lo invia all'utente
    @app.callback(
        Output("download-data", "data"),
        [Input("btn-download", "n_clicks")],
        [State('env-table', 'data'),
         State('production-table', 'data'),
         State('performance-table', 'data')]
    )
    def download_data(n_clicks, env_data, prod_data, perf_data):
        if n_clicks > 0:
            return save_to_excel(env_data, prod_data, perf_data)
        #return dash.no_update

    # Callback che aggiorna grafico e tabella previsionale (richiamato dalla pressione del pulsante, dall'agire sulla slider
    # o al caricamento della pagina)
    @app.callback(
        [Output('store-future-data', 'data'),      # Memorizza i dati futuri
        Output('store-global-df-future', 'data'),
        Output('fig_future', 'figure'),            # Grafico con i dati futuri
        Output('future-table', 'data')],           # Tabella con i dati futuri
        [Input('btn-random', 'n_clicks'),          # Clic del pulsante "Genera dati casuali"
        Input('url', 'pathname'),                  # Trigger per il caricamento della pagina
        Input('year-range-slider', 'value')],      # Trigger per il RangeSlider (anno selezionato)
        [State('store-future-data', 'data')]       # Stato dei dati futuri memorizzati
    )
    # Funzione richiamata dagli eventi previsti nella callback
    def update_future_data(n_clicks, pathname, year_range, stored_data):
        ctx = callback_context
        global global_df_future
        # Se la pagina è stata caricata (trigger al caricamento della pagina)
        if ctx.triggered_id == 'url' or (n_clicks is None and stored_data is None):
            # Se non ci sono dati memorizzati, li calcoliamo al caricamento
            df_env, df_prod = initial_env.round(3), initial_prod.round(3)
            new_df_env = df_env  # Ottieni i nuovi dati ambientali
            new_df_prod = df_prod  # Ottieni i nuovi dati di produzione

            # Calcoliamo i nuovi dati futuri
            df_future = calc_future_production(new_df_env, new_df_prod)

            # Memorizziamo i nuovi dati futuri nel componente `dcc.Store`
            stored_data = df_future.to_dict('records')
        # Se viene premuto il pulsante btn-random
        elif ctx.triggered_id == 'btn-random' and n_clicks > 0:
            # Se il pulsante è stato cliccato, rigenera i nuovi dati casuali
            df_env, df_prod = initial_env.round(3), initial_prod.round(3)
            new_df_env = df_env  # Ottieni i nuovi dati ambientali
            new_df_prod = df_prod  # Ottieni i nuovi dati di produzione

            # Calcoliamo i nuovi dati futuri
            df_future = calc_future_production(new_df_env, new_df_prod)

            # Memorizziamo i nuovi dati futuri nel componente `dcc.Store`
            stored_data = df_future.to_dict('records')
        else:
            # Se non ci sono trigger, usiamo i dati già memorizzati
            df_future = pd.DataFrame(stored_data)
            stored_data = df_future.to_dict('records')
        
        # Filtriamo i dati in base all'intervallo di anni selezionato nel RangeSlider
        filtered_df_future = df_future[(df_future['Year'] >= year_range[0]) & (df_future['Year'] <= year_range[1])]
        
        # Conserva df_future in una variabile globale che serve per alimentare correttamente grafico e tabella "Anno Prossimo"
        global_df_future_data = df_future[(df_future['Year'] == df_future['Year'].min())].round(3).to_dict('records')
        
        # Creiamo il grafico con i dati filtrati
        fig_future = create_fig_future(filtered_df_future)

        # Restituiamo i dati futuri, il grafico e la tabella
        return stored_data, global_df_future_data, fig_future, filtered_df_future.round(3).to_dict('records')
    
    # Callback che aggiorna grafico e tabella delle previsioni per l'anno prossimo (richiamato dalla pressione del pulsante, dall'agire sulle slider
    # o al caricamento della pagina)    
    @app.callback(
    [Output('fig_nextyear', 'figure'),
     Output('grouped-bar-table', 'data'),
     Output('store-global-df-future', 'data', allow_duplicate=True)],  # Aggiungi Output per memorizzare i dati futuri],
    [Input('btn-random', 'n_clicks'), # Trigger al clic del pulsante "Genera dati casuali"
     #Input('url', 'pathname'), # Trigger per il caricamento della pagina
     Input('store-global-df-future', 'data'),
     Input('temperature-slider', 'value'), # Trigger allo spostamento della slider della temperatura
     Input('humidity-slider', 'value'), # Trigger allo spostamento della slider dell'umidità
     Input('precipitation-slider', 'value')], # Trigger allo spostamento della slider delle precipitazioni
    [State('store-global-df-future', 'data')], prevent_initial_call=True
    )
    # Funzione richiamata dagli eventi previsti nella callback
    def update_nextyear_data(n_clicks, pathname, temp, humid, precip, global_df_future_data):
        ctx = callback_context  
        df_future = pd.DataFrame(global_df_future_data)

        # Se viene modificato il valore della temperatura
        if ctx.triggered_id in ['temperature-slider']:
            # Estrai i dati che servono e imposta un nuovo DataFrame dati ambientali
            mynew_env = df_future.iloc[:, [0, 1, 2, 3]].copy()
            # In questo nuovo DataFrame, sostituisci il valore della temperatura con quello della slider
            mynew_env['Temperature'] = temp
            # Ricalcola i dati futuri
            df_future = generate_custom_data(mynew_env).round(3)
        # Se viene modificato il valore dell'umidità'
        elif ctx.triggered_id in ['humidity-slider']:
            # Estrai i dati che servono e imposta un nuovo DataFrame dati ambientali
            mynew_env = df_future.iloc[:, [0, 1, 2, 3]].copy()
            # In questo nuovo DataFrame, sostituisci il valore dell'umidità' con quello della slider
            mynew_env['Humidity'] = humid
            # Ricalcola i dati futuri
            df_future = generate_custom_data(mynew_env).round(3)
        # Se viene modificato il valore delle precipitazioni
        elif ctx.triggered_id in ['precipitation-slider']:
            # Estrai i dati che servono e imposta un nuovo DataFrame dati ambientali
            mynew_env = df_future.iloc[:, [0, 1, 2, 3]].copy()
            # In questo nuovo DataFrame, sostituisci il valore delle precipitazioni con quello della slider
            mynew_env['Precipitation'] = precip            
            # Ricalcola i dati futuri
            df_future = generate_custom_data(mynew_env).round(3)
        # Se viene cliccato il pulsante di generazione dati casuali            
        elif ctx.triggered_id == 'btn-random' and n_clicks > 0:
            df_future = pd.DataFrame(global_df_future_data)
        else:
            df_future = pd.DataFrame(global_df_future_data)
        
        # Salva i nuovi dati futuri nel dcc.Store
        stored_data = df_future.to_dict('records')
        # Modifica grafico e tabella coi dati aggiornati
        fig, table_data = create_fig_nextyear(df_future, temp, humid, precip)

        return fig, table_data, stored_data

    # Callback che, alla pressione sul pulsante di generazione report, recupera i dati relativi
    # ai grafici e alle tabelle visualizzate in quel momento sulla dashboard e li passa alla
    # funzione create_pdf_report del modulo data_tools.data_export.py per la generazione del PDF
    @app.callback(
        Output('download-report', 'data'),
        Input('btn-generate-report', 'n_clicks'),
        State('env-table', 'data'),
        State('production-table', 'data'),
        State('performance-table', 'data'),
        State('future-table', 'data'),
        State('grouped-bar-table', 'data'),
        State('fig_env', 'figure'),
        State('fig_prod', 'figure'),
        State('fig_perf1', 'figure'),
        State('fig_perf2', 'figure'),
        State('fig_future', 'figure'),
        State('fig_nextyear', 'figure')
    )
    def generate_report(n_clicks, env_table_data, prod_table_data, perf_table_data, future_table_data,
                        global_df_future_data, fig_env, fig_prod, fig_perf1, fig_perf2, fig_future, fig_nextyear):
        if not n_clicks:
            return None

        # Converti i dati delle tabelle in DataFrame
        df_env = pd.DataFrame(env_table_data)
        df_prod = pd.DataFrame(prod_table_data)
        df_perf = pd.DataFrame(perf_table_data)
        df_future = pd.DataFrame(future_table_data)
        df_filtered = pd.DataFrame(global_df_future_data)

        # Genera il PDF dinamicamente
        # I dati nelle tabelle vengono passate ad una funzione che li restituisce formattati correttamente 
        # per la visualizzazione nel PDF
        pdf_buffer = create_pdf_report(
            [fig_env, fig_prod, fig_perf1, fig_perf2, fig_future, fig_nextyear],
            [format_table_data(df_env), format_table_data(df_prod), format_table_data(df_perf), format_table_data(df_future), format_table_data(df_filtered)]
        )

        return dcc.send_bytes(pdf_buffer.getvalue(), "report_dashboard.pdf")