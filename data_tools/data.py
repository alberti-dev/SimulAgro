# data.py

# Modulo che gestisce il caricamento e la generazione di dati per la dashboard.
# Contiene le funzioni
# - load_initial_data: richiamata dalle callback e dal modulo layouts.layout.py, legge i dati ambientali e produttivi iniziali 
#   dai file .csv di backend e invoca la genearzione dei dati futuri per popolare la dashboard all'apertura o all'aggiornamento
#   della pagina
# - generate_custom_data(params): richiamata dalla callback che gestisce gli slider ambientali, calcola i dati futuri in funzione 
#   del valore di questi ultimi
# - predict_future_production(params): genera i dati previsionali ambientali e di produzione. E' richiamata dalle callback del pulsante
#   btn-random e del caricamento della pagina

# Importazione delle librerie necessarie
import os # per la gestione dei file
import pandas as pd # per la gestione e la manipolazione dei dati in formato tabellare (strutture dati)
import numpy as np # per la generazione di numeri casuali e le operazioni sugli array
from interface import labels # per importare le etichette di intestazione tabelle
from sklearn.linear_model import LinearRegression  # per creare modelli di regressione lineare
from data_tools.data_simulator import calc_prod_indicators, calc_perf_indicators # per calcolare i dati di produzione e performance

# Funzione che carica i dati iniziali (ambientali e di produzione) da due file .csv
def load_initial_data():
    # Impostazione path dei file
    env_file = os.path.join(os.getcwd(), "data_src", "data_env.csv")
    prod_file = os.path.join(os.getcwd(), "data_src", "data_prod.csv")
    # Lettura dei dati
    data_env = pd.read_csv(env_file)

    # Converti la colonna 'Precipitation' in centimetri
    # Il DataFrame sarà quello visualizzato sotto al grafico dei dati ambientali
    data_env['Precipitation'] = data_env['Precipitation'] / 10 

    data_prod = pd.read_csv(prod_file)
    
    # Popolamento dei DataFrame (vengono generati anche i dati "futuri")
    df_env = pd.DataFrame(data_env)
    df_prod = pd.DataFrame(data_prod)	
    df_perf = calc_perf_indicators(df_prod, df_env)
    df_future = predict_future_production(df_env, df_prod)
	
	# Importazione del dizionario per la traduzione delle intestazioni di colonna delle 
    # tabelle visualizzate sotto i grafici
    col_mapping = labels.col_mapping
	# Restituzione dei dati caricati, degli indicatori, delle previsioni e delle 
    # intestazioni di colonna
    return df_env, df_prod, df_perf, df_future, col_mapping

# Funzione che calcola i dati futuri in funzione dei valori impostati sugli slider di Temperatura, Umidità e Precipitazioni
def generate_custom_data(mynew_env):
    # DataFrame che raccoglie la temperatura, l'umidità e le precipitazioni
    df_env = mynew_env
    # Precipitazioni da cm a mm per i calcoli
    df_env['Precipitation'] = df_env['Precipitation'] * 10
    # Calcolo dei dati di produzione basati sui dati ambientali
    growth_days, total_yield, water_consumption, fertilizer_consumption = calc_prod_indicators(df_env)
	
    # Raccolta dei dati di produzione in un DataFrame
    df_prod = pd.DataFrame({
        'Year': df_env['Year'],
        'Growth_Days': growth_days,
        'Yield': total_yield,
        'Water_Consumption': water_consumption,
        'Fertilizer_Consumption': fertilizer_consumption
    })
    # Riporta le precipitazioni da mm a cm
    df_env['Precipitation'] = df_env['Precipitation'] / 10
    # Calcolo dei dati di perormance basati sui dati ambientali e di produzione generati randomicamente
    df_future = pd.merge(df_env, df_prod, on="Year")

    # I DataFrame vengono restituiti
    return df_future.round(3)

# Funzione che genera i dati previsionali ambientali e di produzione
# instability_factor (float): controlla l'intensità del "rumore" (default 0.1, corrisponde al 10% di deviazione rispetto al valore previsto)
def predict_future_production(df_env, df_prod, instability_factor=0.1):
    ### Preprocessing dei dati
    # Selezione dei dati ambientali come variabili indipendenti
    X = df_env[['Year']].values
    y_temp = df_env['Temperature'].values
    y_humidity = df_env['Humidity'].values
    y_precip = df_env['Precipitation'].values
    
    # Creazione dei modelli di regressione lineare per stimare temperatura, umidità e precipitazioni future
    model_temp = LinearRegression()
    model_humidity = LinearRegression()
    model_precip = LinearRegression()

    # Addestramento dei modelli sui dati selezionati
    model_temp.fit(X, y_temp)
    model_humidity.fit(X, y_humidity)
    model_precip.fit(X, y_precip)

    ### Previsione dei dati ambientali per i prossimi 5 anni
    future_years = np.arange(df_env['Year'].max() + 1, df_env['Year'].max() + 6)
    df_future_env = pd.DataFrame({'Year': future_years}) # Dataframe che raccoglierà i dati ambientali previsti

    # Calcolo dei valori futuri di Temperature, Humidity, Precipitation
    future_temp = model_temp.predict(future_years.reshape(-1, 1))
    future_humidity = model_humidity.predict(future_years.reshape(-1, 1))
    future_precip = model_precip.predict(future_years.reshape(-1, 1))
    
    # Aggiunta di un "rumore" casuale alle previsioni (simuliamo instabilità meteorologica)
    future_temp += np.random.normal(0, instability_factor * np.std(future_temp), len(future_temp))
    future_humidity += np.random.normal(0, instability_factor * np.std(future_humidity), len(future_humidity))
    future_precip += np.random.normal(0, instability_factor * np.std(future_precip), len(future_precip))
    
    # Aggiunta delle previsioni al dataframe dei dati futuri
    df_future_env['Temperature'] = future_temp
    df_future_env['Humidity'] = future_humidity
    df_future_env['Precipitation'] = future_precip

    ### Previsione della produzione e dei consumi
    # Selezione dei dati storici
    X_prod = df_env[['Temperature', 'Humidity', 'Precipitation']].values  # Dati ambientali storici
    y_growth_days = df_prod['Growth_Days'].values
    y_yield = df_prod['Yield'].values
    y_water_consumption = df_prod['Water_Consumption'].values
    y_fertilizer_consumption = df_prod['Fertilizer_Consumption'].values

    # Creazione di modelli di regressione lineare per stimare i parametri della produzione futura
    model_growth_days = LinearRegression()
    model_yield = LinearRegression()
    model_water_consumption = LinearRegression()
    model_fertilizer_consumption = LinearRegression()

    # Addestramento dei modelli sui dati storici
    model_growth_days.fit(X_prod, y_growth_days)
    model_yield.fit(X_prod, y_yield)
    model_water_consumption.fit(X_prod, y_water_consumption)
    model_fertilizer_consumption.fit(X_prod, y_fertilizer_consumption)

    # Calcolo della previsione dei dati di produzione e dei consumi
    future_env_values = df_future_env[['Temperature', 'Humidity', 'Precipitation']].values
    future_growth_days = model_growth_days.predict(future_env_values)
    future_yield = model_yield.predict(future_env_values)
    future_water_consumption = model_water_consumption.predict(future_env_values)
    future_fertilizer_consumption = model_fertilizer_consumption.predict(future_env_values)
    
    # Aggiunta di un "rumore" casuale alle previsioni di produzione e consumo
    future_growth_days += np.random.normal(0, instability_factor * np.std(future_growth_days), len(future_growth_days))
    future_yield += np.random.normal(0, instability_factor * np.std(future_yield), len(future_yield))
    future_water_consumption += np.random.normal(0, instability_factor * np.std(future_water_consumption), len(future_water_consumption))
    future_fertilizer_consumption += np.random.normal(0, instability_factor * np.std(future_fertilizer_consumption), len(future_fertilizer_consumption))

    ### Creazione del dataframe per la produzione futura
    df_future_prod = pd.DataFrame({
        'Year': future_years,
        'Growth_Days': future_growth_days,
        'Yield': future_yield,
        'Water_Consumption': future_water_consumption,
        'Fertilizer_Consumption': future_fertilizer_consumption
    })
    
    # Conversione dei valori delle precipitazioni da mm a cm
    df_future_env['Precipitation'] = df_future_env['Precipitation'] / 10

    # Merge dei due dataframe e restituzione
    future_data = pd.merge(df_future_env, df_future_prod, on="Year")
    return future_data