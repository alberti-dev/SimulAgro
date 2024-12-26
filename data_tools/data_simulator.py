# data_simulator.py

# E' il motore di simulazione della dashboard
# Contiene le funzioni:
# - generate_random_data: genera dati casuali ambientali, di produzione e di performance. E' richiamata dalle callbacks
#   al caricamento dell'app e all'azione sul pulsante btn-random
# - calc_prod_indicators: calcola gli indicatori di produzione basandosi sui dati ambientali. E' richiamata dalla
#   funzione generate_custom_data(params) del modulo data_tools.data.py
# - calc_perf_indicators: calcola gli indicatori di performance economica basandosi sui dati di produzione ed ambientali.
#   E' richiamata dalla funzione load_initial_data() del modulo data_tools.data.py
# - yield_simulate: simula la resa della coltivazione in funzione dei parametri ambientali. E' una funzione interna
#   di questo modulo ed è richiamata dalla funzione generate_random_data

# Importazione delle librerie necessarie
import numpy as np  # per operazioni numeriche e generazione di valori casuali
import pandas as pd  # per la gestione dei DataFrame

# Impostazione parametri di riferimento
years = np.arange(2020, 2025) # Intervallo di tempo considerato
area_hectares = 25 # Area della superficie coltivata
temp_limits = [10, 35] # Intervallo di temperature media a Catania e provincia
humid_limits = [40, 75] # Intervallo di umidità media  a Catania e provincia
precip_limits = [300, 800] # Intervallo di precipitazioni medie a Catania e provincia
growth_limits = [180, 210] # Intervallo medio di giorni di crescita del prodotto agricolo
growth_average = sum(growth_limits)/len(growth_limits) # Giorni medi di crescita
waste_limits = [2, 10] # Percentuale di scarto nella raccolta (tra il 2% e il 10%)
waste_average = sum(waste_limits)/len(waste_limits) # Percentuale di scarto media

# Funzione che genera dati casuali ambientali, di produzione e di performance
def generate_random_data():
    # temperatura - viene previsto un aumento graduale a causa del progressivo surriscaldamento globale
    temperatures = np.random.uniform(temp_limits[0], temp_limits[1], size=len(years)) + np.linspace(0, 3, len(years))
    # umidità
    humidities = np.random.uniform(humid_limits[0], humid_limits[1], size=len(years))
    # precipitazioni - viene previsto un decremento graduale a causa del progressivo fenomeno di desertificazione
    precipitations = np.random.uniform(precip_limits[0], precip_limits[1], size=len(years)) - np.linspace(0, 100, len(years))

    # Creazione del DataFrame che raccoglie la temperatura, l'umidità e le precipitazioni per ogni anno
    df_env = pd.DataFrame({
        'Year': years,
        'Temperature': np.clip(temperatures, 5, 40),  # Temperatura limitata tra 5°C e 40°C
        'Humidity': humidities,
        'Precipitation': precipitations
    })
	
    # Calcolo dei dati di produzione basati sui dati ambientali generati randomicamente
    growth_days, total_yield, water_consumption, fertilizer_consumption = calc_prod_indicators(df_env)

    # Raccolta dei dati di produzione in un DataFrame
    df_prod = pd.DataFrame({
        'Year': df_env['Year'],
        'Growth_Days': growth_days,
        'Yield': total_yield,
        'Water_Consumption': water_consumption,
        'Fertilizer_Consumption': fertilizer_consumption
    })    

    # Calcolo dei dati di performance basati sui dati ambientali e di produzione generati randomicamente
    df_perf = calc_perf_indicators(df_prod, df_env)

    # I DataFrame vengono restituiti
    return df_env, df_prod, df_perf.round(3)

# Funzione che calcola gli indicatori di produzione in funzione dei dati ambientali
def calc_prod_indicators(df_env):
    # Giorni di crescita (tipicamente tra 180 e 210 giorni per le olive)
    growth_days = np.random.normal(growth_average, 10, len(df_env))
    # Percentuale di scarto nella raccolta, che può essere tra il 2% e il 10%
    waste_percentage = np.random.normal(waste_average, 1, size=len(df_env))
    # Calcolo della resa per ettaro in base alla temperatura
    yield_values = np.array([yield_simulate(temp, humidity, precip) for temp, humidity, precip in zip(df_env['Temperature'], df_env['Humidity'], df_env['Precipitation'])])
    # Resa totale considerando l'area e lo scarto
    total_yield = yield_values * area_hectares * (100 - waste_percentage) / 100
    # Stima del fabbisogno idrico in funzione delle variabili ambientali
    # Viene applicato un modello lineare e alcuni vincoli di modo che il consumo d'acqua (per l'irrigazione) venga calcolato 
    # con un incremento se le temperature sono più alte, con un decremento se aumentano le precipitazioni
    water_consumption = np.clip(100 + 0.3 * df_env['Temperature'] - 0.2 * df_env['Precipitation'], 30, 250) * area_hectares / 10
    # Consumo di fertilizzante, valore medio per ettaro tra 60 e 100 kg
    fertilizer_consumption = np.random.normal(80, 15, len(df_env))

    return growth_days, total_yield, water_consumption, fertilizer_consumption

# Funzione che calcola gli indicatori di performance economica basandosi sui dati di produzione ed ambientali
def calc_perf_indicators(df_prod, df_env):
    # Creazione di un DataFrame per gli indicatori
    df_perf = pd.DataFrame(index=df_env.index)
    
    # Prezzo per kg di prodotto (olive)
    prices_per_unit = np.random.uniform(1, 3, size=5)
    # Costi per unità di acqua e fertilizzante
    cost_per_water_unit = np.random.normal(loc=8, scale=2, size=5)  # Costo per m3 di acqua
    cost_per_fertilizer_unit = np.random.normal(loc=12, scale=3, size=5)  # Costo per kg di fertilizzante
    
    # Calcolo dei ricavi dalla vendita delle olive per un terreno coltivato di superficie data (area_hectares)
    # I ricavi sono basati sulla resa e sul prezzo casuale per kg di prodotto
    revenue = df_prod['Yield'] * prices_per_unit * area_hectares
    # Calcolo dei costi totali per acqua e fertilizzante
    costs = (df_prod['Water_Consumption'] * cost_per_water_unit) + (df_prod['Fertilizer_Consumption'] * cost_per_fertilizer_unit)
    # Calcolo del profitto
    profit = revenue - costs
    # Margine di profitto
    profit_margin = (profit / revenue) * 100
    # Efficienza produttiva (resa per unità di acqua consumate)
    efficiency = df_prod['Yield'] / df_prod['Water_Consumption']
    # Sostenibilità ambientale (rapporto tra resa e consumo di risorse)
    env_sustain = (df_prod['Yield'] * 100 / area_hectares) / (df_prod['Water_Consumption'] + df_prod['Fertilizer_Consumption'])

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
    # Il DataFrame viene restituito
    return df_perf.round(3)

# Funzione che simula la resa della coltivazione in funzione dei parametri ambientali
def yield_simulate(temp, humidity, precip):
    # Gli uilivi producono meno in climi molto freddi o molto caldi
    if temp < 10:
        yield_temp = np.random.normal(0.8, 0.2)  # resa bassa in condizioni fredde
    elif 10 <= temp <= 30:
        yield_temp = np.random.normal(3.0, 0.4)  # resa ottimale per la coltivazione
    else:
        yield_temp = np.random.normal(1.5, 0.3)  # resa più bassa in condizioni molto calde
    
    humidity_factor = 1 + 0.02 * (humidity - 60)  # L'effetto dell'umidità sulla resa
    precip_factor = 1 - 0.001 * (precip - 500)  # L'effetto delle precipitazioni sulla resa

    # Calcolo della resa in funzione di temperatura, umidità e precipitazioni
    yield_temp = yield_temp * humidity_factor * precip_factor
    
    return yield_temp