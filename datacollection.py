# datacollection.py

# Simulatore di dati ambientali e di produzione
# Questo codice, richiamato dalla Dashboard interattiva, simula vari aspetti della produzione agricola, tra cui la resa di olive, 
# i consumi di acqua e fertilizzante, e calcola alcuni indicatori di performance come efficienza e sostenibilità.
# Il tutto è basato su modelli statistici e distribuzioni casuali.
# I dati generati saranno passati alla Dashboard per essere visualizzati ed esplorati in modo interattivo

# Importazione delle librerie necessarie
import pandas as pd # Per la gestione e la manipolazione dei dataframe
import numpy as np # Per la generazione di numeri casuali e le operazioni sugli array
import dataprediction # Per il calcolo della produzione futura

# Funzione che genera i dati ambientali
def get_env_data(years):
    # temperatura per la coltivazione di olive, tra 10°C e 35°C con un aumento graduale
    temperatures = np.random.uniform(10, 35, size=len(years)) + np.linspace(0, 3, len(years)) 
    # umidità tra 40% e 75% (tipica per l'area siciliana)
    humidities = np.random.uniform(40, 75, size=len(years))
    # precipitazioni tra 300 e 800 mm (in Sicilia le precipitazioni sono generalmente basse)
    precipitations = np.random.uniform(300, 800, size=len(years)) - np.linspace(0, 100, len(years))

    # Creazione del DataFrame che raccoglie la temperatura, l'umidità e le precipitazioni per ogni anno
    df_env = pd.DataFrame({
        'Year': years,
        'Temperature': np.clip(temperatures, 5, 40),  # Temperatura limitata tra 5°C e 40°C
        'Humidity': humidities,
        'Precipitation': precipitations
    })
    
    return df_env

# Funzione che calcola la resa in base alla temperatura per le olive
def yield_based_on_temperature(temp):
    # Le olive producono meno in climi molto freddi o molto caldi
    if temp < 10:
        return np.random.normal(0.8, 0.2)  # resa bassa in condizioni fredde
    elif 10 <= temp <= 30:
        return np.random.normal(3.0, 0.4)  # resa ottimale per la coltivazione
    else:
        return np.random.normal(1.5, 0.3)  # resa più bassa in condizioni molto calde

# Funzione che fornisce i dati produttivi per le olive
def get_prod_data(df_env, area_hectares=50):
    # Giorni di crescita (tipicamente tra 150 e 180 giorni per le olive)
    growth_days = np.random.normal(160, 10, len(df_env))
    # Percentuale di scarto nella raccolta, che può essere tra il 2% e il 10%
    waste_percentage = np.random.normal(5, 1, size=len(df_env))
    # Calcolo della resa per ettaro in base alla temperatura
    yield_values = np.array([yield_based_on_temperature(temp) for temp in df_env['Temperature']])
    # Resa totale considerando l'area e lo scarto
    total_yield = yield_values * area_hectares * (100 - waste_percentage) / 100
    # Consumo d'acqua
    water_consumption = np.clip(100 + 0.3 * df_env['Temperature'] - 0.2 * df_env['Precipitation'], 30, 250) * area_hectares / 10
    # Consumo di fertilizzante, valore medio per ettaro tra 60 e 100 kg
    fertilizer_consumption = np.random.normal(80, 15, len(df_env))

    # Raccolta dei dati in un DataFrame
    df_prod = pd.DataFrame({
        'Year': df_env['Year'],
        'Growth_Days': growth_days,
        'Yield': total_yield,
        'Water_Consumption': water_consumption,
        'Fertilizer_Consumption': fertilizer_consumption
    })

    return df_prod

# Funzione che calcola gli indicatori di performance
def calc_perf_indicators(df_prod, df_env):
    # Creazione di un DataFrame per gli indicatori
    df_perf = pd.DataFrame(index=df_env.index)
    
    # Prezzi per unità di prodotto (le olive in Sicilia possono avere un prezzo più variabile)
    prices_per_unit = np.random.uniform(1, 3, size=5)  # Prezzo per kg di olive
    # Costi per unità di acqua e fertilizzante
    cost_per_water_unit = np.random.normal(loc=8, scale=2, size=5)  # Costo per m3 di acqua
    cost_per_fertilizer_unit = np.random.normal(loc=12, scale=3, size=5)  # Costo per kg di fertilizzante
    
    # Calcolo dei ricavi dalla vendita delle olive
    revenue = df_prod['Yield'] * prices_per_unit * 50
    # Calcolo dei costi totali per acqua e fertilizzante
    costs = (df_prod['Water_Consumption'] * cost_per_water_unit) + (df_prod['Fertilizer_Consumption'] * cost_per_fertilizer_unit)
    # Calcolo del profitto
    profit = revenue - costs
    # Margine di profitto
    profit_margin = (profit / revenue) * 100
    # Efficienza produttiva
    efficiency = df_prod['Yield'] / df_prod['Water_Consumption']
    # Sostenibilità ambientale
    env_sustain = (df_prod['Yield'] * 100 / 50) / (df_prod['Water_Consumption'] + df_prod['Fertilizer_Consumption'])

    # Popolamento del DataFrame con gli indicatori
    df_perf = pd.DataFrame({
        'Year': df_prod['Year'],
        'Total_Cost': costs,
        'Total_Price': revenue,
        'Gain': profit,
        'Profit_Margin': profit_margin,
        'Efficiency': efficiency,
        'Env_Sustain': env_sustain,
    })

    return df_perf.round(3)

# Funzione principale per creare i dati simulati
def create_simulation_data():
    years = np.arange(2020, 2025)
    
    # Creazione dei dati ambientali e produttivi
    df_env = get_env_data(years)
    df_prod = get_prod_data(df_env)
    df_future = dataprediction.predict_future_production(df_env, df_prod)

    # Restituisce i DataFrame con i dati generati
    return df_env, df_prod, df_future

# Eseguiamo la simulazione
df_env, df_prod, df_future = create_simulation_data()