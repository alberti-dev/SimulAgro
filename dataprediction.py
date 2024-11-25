# dataprediction.py

# Modulo che, basandosi su modelli statistici e distribuzioni casuali, provvede a calcolare la produzione futura e i consumi di acqua e fertilizzante,
# utilizzando una regressione lineare basata sui dati ambientali (aggiungendo un "rumore" casuale per simulare l'instabilità metereologica).
# Viene invocato sia dal modulo dataprediction che dalla dashboard per generare i dati previsionali ambientali e di produzione

# Importazione delle librerie necessarie
import pandas as pd # Per la gestione e la manipolazione dei dataframe
import numpy as np # Per la generazione di numeri casuali e le operazioni sugli array
from sklearn.linear_model import LinearRegression # Per eseguire la regressione lineare

# Funzione che genera i dati previsionali ambientali e di produzione
# instability_factor (float): controlla l'intensità del "rumore" (default 0.1, corrisponde al 10% di deviazione rispetto al valore previsto)
def predict_future_production(df_env, df_prod, instability_factor=0.1):
    ### Preprocessing dei dati
    # Selezione dei dati ambientali come variabili indipendenti
    X = df_env[['Year']].values
    y_temp = df_env['Temperature'].values
    y_humidity = df_env['Humidity'].values
    y_precip = df_env['Precipitation'].values
    
    # Creazione dei modelli di regressione lineare per ogni variabile ambientale
    model_temp = LinearRegression()
    model_humidity = LinearRegression()
    model_precip = LinearRegression()

    # Addestramento dei modelli sui dati storici
    model_temp.fit(X, y_temp)
    model_humidity.fit(X, y_humidity)
    model_precip.fit(X, y_precip)

    ### Previsione dei dati ambientali per i prossimi 5 anni
    future_years = np.arange(df_env['Year'].max() + 1, df_env['Year'].max() + 6)  # Anni futuri
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
    # Designazione dei dati storici come variabili dipendenti
    X_prod = df_env[['Temperature', 'Humidity', 'Precipitation']].values  # Dati ambientali storici
    y_growth_days = df_prod['Growth_Days'].values
    y_yield = df_prod['Yield'].values
    y_water_consumption = df_prod['Water_Consumption'].values
    y_fertilizer_consumption = df_prod['Fertilizer_Consumption'].values

    # Creazione di modelli di regressione lineare per ogni variabile di output (produzione)
    model_growth_days = LinearRegression()
    model_yield = LinearRegression()
    model_water_consumption = LinearRegression()
    model_fertilizer_consumption = LinearRegression()

    # Addestramento dei modelli sui dati storici
    model_growth_days.fit(X_prod, y_growth_days)
    model_yield.fit(X_prod, y_yield)
    model_water_consumption.fit(X_prod, y_water_consumption)
    model_fertilizer_consumption.fit(X_prod, y_fertilizer_consumption)

    # Calcolo della previsione dei dati di produzione e dei consumi per i prossimi 5 anni
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
    
    # Restituzione dei due dataframe
    future_data = pd.merge(df_future_env, df_future_prod, on="Year")
    return future_data