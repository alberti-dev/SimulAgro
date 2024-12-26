# charts.py

# Modulo che definisce le funzioni di creazione dei grafici
# Ogni funzione accetta come input un DataFrame e restituisce uno o più grafici (e relative tabelle) basandosi su di esso
# Le funzioni vengono richiamate dal modulo layouts.layout per "disegnare" i grafici all'interno della dashboard

# Importazione delle librerie necessarie
import plotly.express as px # modulo per creare grafici interattivi
import plotly.graph_objects as go # modulo per creare grafici interattivi
from interface import labels # modulo che fornisce un dizionario per tradurre le etichette di colonna in grafici e tabelle

# Dizionario per la traduzione delle etichette di colonna di grafici e tabelle
col_mapping = labels.col_mapping

# Funzione che crea un grafico a linee per rappresentare i parametri ambientali
def create_fig_env(df_env):
    # Inizializzazione del grafico
    fig = go.Figure()
    # Aggiunta al grafico dei tracciati basati sui dati di temperatura (asse y1), umidità e precipitazioni (asse y2)
    fig.add_trace(go.Scatter(x=df_env['Year'], y=df_env['Temperature'], \
                             mode='lines', name='Temperatura (°C)', yaxis='y1'))
    fig.add_trace(go.Scatter(x=df_env['Year'], y=df_env['Humidity'], \
                             mode='lines', name='Umidità (%)', yaxis='y2'))
    # I dati relativi alle precipitazioni vengono riportati in cm per evitare che dominino visivamente 
    # il grafico rispetto agli altri parametri
    fig.add_trace(go.Scatter(x=df_env['Year'], y=(df_env['Precipitation'])/10, \
                             mode='lines', name='Precipitazioni (cm)', yaxis='y2'))

    # Configurazione del layout del grafico
    fig.update_layout(
        # Impostazione titolo
        title="Andamento Annuale di Temperatura, Umidità e Precipitazioni",
        # Impostazione titoli degli assi
        xaxis=dict(title="Anno", tickformat=".0f", dtick=1),
        yaxis=dict(title="Temperatura (°C)", side='left'),
        # Le precipitazioni vengono contenute nel range 0-100
        yaxis2=dict(title="Umid.(%) e Prec.(cm)", side='right', overlaying='y', range=[0, 100]),
        # Impostazione del tema grafico
        template="plotly_dark",
        # Impostazione del posizionamento della legenda
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1.0)
    )
    # Restituzione del grafico creato
    return fig

# Funzione che crea un grafico a barre raggruppate per rappresentare i dati di produzione per anno
def create_fig_prod(df_prod):
    fig = px.bar(df_prod, x='Year', y=df_prod.columns[1:], barmode='group',
                 labels={'Year': 'Anno', 'value': 'Valore', 'variable': ''},
                 # Impostazione titolo e scelta del tema grafico
                 title='Confronto fra indicatori per anno', template="plotly_dark")
    # Aggiorna i nomi delle tracce in base al mapping predefinito nel dizionario col_mapping 
    # importato dal modulo layouts.labels
    fig.for_each_trace(lambda trace: trace.update(name=col_mapping.get(trace.name, trace.name)))
    # Modifica della legenda per renderla orizzontale
    # Modifica della legenda per renderla orizzontale e su una sola riga
    fig.update_layout(
        # Impostazioni della legenda
        legend=dict(
            orientation="h",  # Legenda orizzontale
            yanchor="bottom",  # Ancoraggio alla parte inferiore
            y=1.02,  # Posizionamento sopra il grafico
            xanchor="center",  # Posizionamento centrale orizzontale
            x=0.5,
            itemwidth=60,  # Aumenta la larghezza degli item per evitare l'andare a capo
            traceorder='normal',  # Ordine tracce (normale)
            font=dict(size=11)  # dimensione del font
        ),
        margin=dict(t=120, b=85, l=50, r=50),  # Aggiusta i margini per dare più spazio alla legenda
    )
    # Restituisce il grafico creato
    return fig

# Funzione che crea due grafici (uno 2D e uno 3D), per rappresentare rispettivamente il confronto 
# tra efficienza e sostenibilità ambientale e la relazione tra costi, ricavi e profitti.
# In entrambi i grafici i punti sono colorati per anno
def create_fig_perf(df_perf):
    fig_3d = px.scatter_3d(df_perf, x='Total_Cost', y='Total_Price', z='Gain', color='Year',
                           title="Relazione tra Costi, Ricavi e Profitti", labels=col_mapping, template="plotly_dark")
    fig_2d = px.scatter(df_perf, x='Efficiency', y='Env_Sustain', color='Year',
                        title="Confronto tra Efficienza e Sostenibilità Ambientale", labels=col_mapping, template="plotly_dark")
    # Restituzione dei grafici creati
    return fig_3d, fig_2d

# Funzione che crea un grafico a linee per rappresentare previsioni relative al quinquennio successivo 
# su raccolto, consumi e giorni di crescita
def create_fig_future(df_future):
    fig = go.Figure()

    # Aggiunta delle curve per i vari parametri
    fig.add_trace(go.Scatter(x=df_future['Year'], y=df_future['Growth_Days'], \
                             mode='lines', name='Giorni di Crescita'))
    fig.add_trace(go.Scatter(x=df_future['Year'], y=df_future['Yield'], \
                             mode='lines', name='Raccolto (q)'))
    fig.add_trace(go.Scatter(x=df_future['Year'], y=df_future['Water_Consumption'], \
                             mode='lines', name='Consumo Acqua (dm3)'))
    fig.add_trace(go.Scatter(x=df_future['Year'], y=df_future['Fertilizer_Consumption'], \
                             mode='lines', name='Consumo Fertilizz. (q)'))
    
    # Configurazione del layout
    fig.update_layout(
        title="Previsione Futura di Produzione e Dati Ambientali",
        xaxis=dict(
            title="Anno",
            tickmode='array',  
            tickvals=df_future['Year'],  # Impostazione dei tick su valori discreti (anno per anno)
            ticktext=df_future['Year'].astype(str),  # Visualizzazione degli anni come stringhe (interi senza decimali)
        ),
        yaxis=dict(title="Valore"),
        # Impostazione del tema grafico e del posizionamento della legenda
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1.0)
    )
    # Restituzione del grafico creato
    return fig

def create_fig_nextyear(df_future, temperature, humidity, precipitation):
    # Filtra i dati per l'anno minore
    min_year = df_future['Year'].min()
    # Filtra il DataFrame selezionando l'anno più piccolo (il prossimo)
    filtered_data = df_future[df_future['Year'] == min_year].copy()

    fig = px.bar(
        filtered_data,
        x='Year',
        y=['Temperature', 'Humidity', 'Precipitation', 'Water_Consumption', 'Fertilizer_Consumption', 'Yield'],
        barmode='group',
        labels={'value': 'Valore', 'variable': 'Parametro', 'Year': 'Anno'},
        title=f"Dati dell'Anno {min_year}",
        template="plotly_dark"
    )
    # Aggiorna i nomi delle tracce in base al mapping predefinito nel dizionario col_mapping importato dal modulo layouts.labels
    fig.for_each_trace(lambda trace: trace.update(name=col_mapping.get(trace.name, trace.name)))
    
    # Restituisce il grafico e i dati per la tabella
    return fig, filtered_data.to_dict('records')