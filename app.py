# app.py

# Dashboard in Python e Dash
# Fornisce una vista interattiva dei dati ambientali, di produzione e di performance aziendale di un'azienda del 
# settore agroalimentare nonchè dati previsionali per il quinquennio successivo.

# Questo script inizializza l'applicazione, indicando il titolo da visualizzare nel tab del browser, il tema grafico e 
# il set di icone da utilizzare. Registra tutte le callback che gestiranno eventi ed interazioni tra utente e widget e,
# nel caso, avvia il server di sviluppo in modalità debug per controllo a runtime di eventuali errori

# Importazione delle librerie necessarie
import os # modulo per interagire col sistema operativo
from dash import Dash # framework Dash per creare app interattive
import dash_bootstrap_components as dbc # modulo per impostare tema grafico e icone
from interface.layout import create_layout # modulo che definisce layout della dashboard
from interface import callbacks # modulo delle callbacks

# Creazione dell'applicazione Dash
# Viene specificato un titolo che verrà visualizzato nella scheda del browser
# Sono inclusi uno stile esterno, un set di icone e la localizzazione in italiano
app = Dash(__name__, 
           title='Simul-Agro', 
           external_stylesheets=[dbc.themes.SANDSTONE, dbc.icons.FONT_AWESOME],
           external_scripts=[os.path.join(os.getcwd(), "assets", "plotly-locale-it.js")])

# Imposta il layout dell'app richiamando la funzione specifica dal modulo "layouts.layout"
app.layout = create_layout(app)

# Registra le callback che gestiscono l'interazione tra i componenti dell'interfaccia e dati
callbacks.register_callbacks(app)

# Avvio del server di sviluppo
# Se lo script viene eseguito direttamente (e non importato come modulo), il server viene avviato in modalità debug
# per il controllo di eventuali errori
if __name__ == "__main__":
    app.run_server(debug=True)
