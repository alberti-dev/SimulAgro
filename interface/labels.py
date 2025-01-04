# labels.py

# Modulo che gestisce la traduzione in italiano delle etichette di colonna della dashboard e dei report e
# le legende dei grafici.
# Contiene i dizionari che mappano i nomi delle colonne dei DataFrame dall'inglese all'italiano

# Dizionario importato sia nel modulo layout.py (per tradurre le intestazioni di colonna delle
# tabelle visualizzate sotto ai grafici) che nel modulo charts.py (per tradurre le legende dei grafici)
col_mapping = {
    "Year": "Anno", 
    "Temperature": "Temperatura (°C)", 
    "Humidity": "Umidità (%)",
    "Precipitation": "Precipitazioni (cm)", 
    "Growth_Days": "Giorni di Crescita",
    "Yield": "Raccolto (q)", 
    "Water_Consumption": "Cons. Acqua (dm3)",
    "Fertilizer_Consumption": "Cons. Fertilizz. (q)", 
    "Efficiency": "Efficienza",
    "Env_Sustain": "Sostenibilità", 
    "Total_Cost": "Totale Costi (€)",
    "Total_Price": "Totale Ricavi (€)", 
    "Gain": "Profitto (€)", 
    "Profit_Margin": "Margine di Profitto (%)"
}

# Dizionario è importato nel modulo data_export.py del package data_tools (per tradurre le intestazioni
# di colonna delle tabelle visualizzate sotto ai grafici nel report PDF)
col_mapping_pdf = {
    "Year": "Anno", 
    "Temperature": "Temp. (°C)", 
    "Humidity": "Umid. (%)",
    "Precipitation": "Precip. (cm)", 
    "Growth_Days": "Crescita (gg)",
    "Yield": "Raccolto (q)", 
    "Water_Consumption": "Acqua (dm3)",
    "Fertilizer_Consumption": "Fertil. (q)", 
    "Efficiency": "Efficienza",
    "Env_Sustain": "Sostenibilità", 
    "Total_Cost": "Costi (€)",
    "Total_Price": "Ricavi (€)", 
    "Gain": "Profitto (€)", 
    "Profit_Margin": "Margine (%)"
}