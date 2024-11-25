# Simulatore di dati ambientali e di produzione
# Questo codice, richiamato dalla Dashboard interattiva, simula vari aspetti della produzione agricola, tra cui la resa dei pomodori, 
# i consumi di acqua e fertilizzante, e calcola indicatori di performance come efficienza e sostenibilità.
# Inoltre, effettua una stima della produzione futura sulla base delle condizioni ambientali.
# Il tutto è basato su modelli statistici e distribuzioni casuali.
# I dati generati saranno passati alla Dashboard per essere visualizzati ed esplorati in modo interattivo

import pandas as pd # per la gestione e la manipolazione dei dataframe
import numpy as np # per la generazione di numeri casuali e le operazioni sugli array
from sklearn.linear_model import LinearRegression # modello di regressione lineare usato per fare previsioni sulla produzione futura

# Funzione che genera i dati ambientali
def get_env_data(years):
    # genera una sequenza di temperature random tra 20°C e 35°C gradi Celsius e aggiunge una variazione lineare crescente
    # (da 0 a 5 gradi) per simulare un aumento della temperatura negli anni
    temperatures = np.random.uniform(20, 35, size=len(years)) + np.linspace(0, 5, len(years)) 
    # genera valori random di umidità compresi nell'intervallo 40%-80%
    humidities = np.random.uniform(40, 80, size=len(years))
    # genera valori random di precipitazioni tra 500 e 1000 mm che decrescono linearmente per simulare una riduzione delle precipitazioni negli anni
    precipitations = np.random.uniform(500, 1000, size=len(years)) - np.linspace(0, 200, len(years))

    # Creazione del DataFrame che raccoglie la temperatura, l'umidità e le precipitazioni per ogni anno
    df_env = pd.DataFrame({
        'Year': years,
        'Temperature': np.clip(temperatures, 4, 44), # la temperatura deve rimanere entro certi limiti
        'Humidity': humidities,
        'Precipitation': precipitations
    })
    
    return df_env

# Funzione che calcola la resa in base alla temperatura
def yield_based_on_temperature(temp):
    # Se la temperatura è inferiore a 15°C, la resa è bassa (distribuzione normale centrata su 1 e deviazione standard di 0.3)
    if temp < 15:
        return np.random.normal(1, 0.3)
    # Se la temperatura è nell'intervallo 15°C e 30°C, la resa ha una distribuzione normale centrata su 1 e deviazione standard di 0,3 
    elif 15 <= temp <= 30:
        return np.random.normal(3.5, 0.5)
    # Se è più alta di 30°C la resa diminuisce (2 con deviazione 0.5)
    else:
        return np.random.normal(2, 0.5)

# Funzione che fornisce i dati produttivi: giorni di crescita, percentuale di scarto, raccolto in funzione della temperatura, consumo d'acqua
# Questi dati vengono raccolti in un dataframe che viene poi restituito dalla funzione quando richiamata
def get_prod_data(df_env, area_hectares=50):
    # Calcolo dei giorni di crescita (valore random centrato su 95 giorni con deviazione standard di 5)
    growth_days = np.random.normal(95, 5, len(df_env))
    # Calcolo della percentuale di scarto nella raccolta (valore random con media 5% e deviazione di 1%)
    waste_percentage = np.random.normal(5, 1, size=len(df_env))
    # Calcolo della resa per ettaro per mezzo di una funzione alla quale viene passato ogni valore di temperatura
    yield_values = np.array([yield_based_on_temperature(temp) for temp in df_env['Temperature']])
    # Resa totale in funzione dell'area dell'appezzamento di terreno e dello scarto
    total_yield = yield_values * area_hectares * (100 - waste_percentage) / 100
    # Consumo d'acqua calcolato in funzione della temperatura e delle precipitazioni
    # Il valore è limitato tra 50 e 400 e scalato per l'area in ettari
    water_consumption = np.clip(250 + 0.4 * df_env['Temperature'] - 0.3 * df_env['Precipitation'], 50, 400) * area_hectares / 10
    # I dati vengono raccolti in un dataframe che la funzione restituisce tutte le volte che viene invocata
    df_prod = pd.DataFrame({
        'Year': df_env['Year'],
        'Growth_Days': growth_days,
        'Yield': total_yield,
        'Water_Consumption': water_consumption,
        'Fertilizer_Consumption': np.random.normal(100, 20, len(df_env)) # Fertilizzante consumato (valore random centrato su 100 con deviazione di 20)
    })

    return df_prod

# Funzione calcola vari indicatori di performance (costi, ricavi, redditività, efficienza e sostenibilità ambientale)
# Prezzi per unità di prodotto, costi per unità di acqua e fertilizzante vengono generati casualmente
def calc_perf_indicators(df_prod, df_env):
    # Istanzia il dataframe che raccoglierà gli indicatori
    df_perf = pd.DataFrame(index=df_env.index)
    # Generazione distribuzioni per l'uso di fertilizzanti per ettaro
    fertilizer_usage_per_hectare = np.random.normal(loc=2, scale=0.5, size=5)
    # Calcolo uso totale di fertilizzanti
    fertilizer_usage = fertilizer_usage_per_hectare * 50

    # Generazione di altri dati random facendo uso dei dati di produzione, di distribuzioni uniformi e gaussiane (o normali)
    yield_per_hectare = df_prod['Yield'] # dati di produzione
    prices_per_unit = np.random.uniform(100, 200, size=5) # distribuzione uniforme
    cost_per_water_unit = np.random.normal(loc=10, scale=2, size=5) # distribuzione gaussiana
    cost_per_fertilizer_unit = np.random.normal(loc=15, scale=3, size=5) # distribuzione gaussiana

    # Ricavi dalla vendita del prodotto
    revenue = yield_per_hectare * prices_per_unit * 50
    # Costi totali derivanti dall'uso di acqua e fertilizzante
    costs = (df_prod['Water_Consumption'] * cost_per_water_unit) + (fertilizer_usage * cost_per_fertilizer_unit)
    # Differenza tra ricavi e costi: profitto
    profit = revenue - costs 
    # Margine di profitto espresso in percentuale
    profit_margin = (profit / revenue) * 100
    # Efficienza produttiva, calcolata come la resa per il consumo di acqua
    efficiency = df_prod['Yield'] / df_prod['Water_Consumption']
    # Sostenibilità ambientale, che considera la resa per ettaro rispetto al consumo complessivo di risorse (acqua + fertilizzante)
    env_sustain = (df_prod['Yield'] * 100 / 50) / (df_prod['Water_Consumption'] + df_prod['Fertilizer_Consumption'])

    # I dati generati e calcolati, vengono raccolti dentro un dataframe che la funzione restituirà quando invocata
    df_perf = pd.DataFrame({
        'Year': df_prod['Year'],
        #'Total_Cost': np.random.normal(750, 150, len(df_prod)),
        'Total_Cost': costs,
        #'Total_Price': np.random.normal(1100, 150, len(df_prod)),
        'Total_Price': revenue,
        'Gain': profit,
        'Profit_Margin': profit_margin,
        'Efficiency': efficiency,
        'Env_Sustain': env_sustain,
    })
    # Per una migliore leggibilità, il numero di decimali visualizzati nelle tabelle sono limitati a tre
    return df_perf.round(3)

# Funzione che utilizza un modello di regressione lineare per prevedere la produzione futura in base ai dati ambientali
# Viene creato un modello di regressione lineare che utilizza temperatura, umidità e precipitazioni come variabili
# indipendenti (X) per prevedere la resa (y)
def predict_future_production(df_env, df_prod):
    model = LinearRegression()
    X = df_env[['Temperature', 'Humidity', 'Precipitation']]
    y = df_prod['Yield']
    model.fit(X, y)
    # Si indicano gli anni da considerare
    future_years = np.arange(2025, 2031)
    # Si inseriscono i dati (generati random sempre con l'utilizzo di distribuzioni statistiche) in un dataframe
    df_future = pd.DataFrame({
        'Year': future_years,
        'Temperature': np.random.uniform(20, 35, size=len(future_years)),
        'Humidity': np.random.uniform(40, 80, size=len(future_years)),
        'Precipitation': np.random.uniform(500, 1000, size=len(future_years))
    })
    # La previsione della resa futura viene effettuata utilizzando il modello di regressione lineare addestrato sui dati storici
    future_production = model.predict(df_future[['Temperature', 'Humidity', 'Precipitation']])
    df_future['Predicted_Yield'] = future_production
    
    return df_future

# La funzione principale per creare i dati simulati
# Vengono creati i dati ambientali, produttivi e le previsioni future chiamando le funzioni precedenti
def create_simulation_data():

    years = np.arange(2020, 2025)
    
    df_env = get_env_data(years)
    df_prod = get_prod_data(df_env)
    df_future = predict_future_production(df_env, df_prod)

    # Restituisce i DataFrame con i dati generati
    return df_env, df_prod, df_future #, df_perf

# Infine, viene eseguita la simulazione
df_env, df_prod, df_future = create_simulation_data()