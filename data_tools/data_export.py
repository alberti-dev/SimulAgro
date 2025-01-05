# data_export.py

# Modulo incaricato di gestire l'esportazione dei dati visualizzati nella dashboard.
# Contiene le funzioni:
# - save_to_excel: salva i dati visualizzati sulla dashboard in un file Excel che invia all'utente. E' richiamata dalla
#   callback che gestisce il pulsante btn-download
# - format_data_table: formatta per la visualizzazione su PDF i dati della tabella che gli viene passata come parametro.
#   E' richiamata dalla funzione create_pdf_report 
# - add_section: inserisce una sezione nel report PDF
#   E' richiamata dalla funzione create_pdf_report
# - create_pdf_report: crea un report PDF contenente i dati visualizzati nella dashboard. E' richiamata dalla callback
#   che gestisce il pulsante btn--generate-report

# Importazione delle librerie necessarie
import os, io # per la gestione dei flussi di I/O (ad esempio gestione dei file in memoria)
import plotly.io as pio # per la gestione di I/O grafici (ad esempio salvare i grafici come immagini)
import pandas as pd # per la gestione dei DataFrame
from datetime import datetime # per gestire date ed orari
from dash import dcc # per generare file Excel
# Importazione degli strumenti di ReportLab per la generazione dei file PDF
from reportlab.lib.pagesizes import A4 # specifica le dimensioni standard del foglio A4 (per generare report PDF)
from reportlab.pdfgen import canvas # per gestire gli oggetti canvas utili nella generazione dei PDF
from reportlab.lib import colors # per gestire i colori nei PDF
from reportlab.platypus import Table, TableStyle # per creare e stilizzare le tabelle nei PDF
from reportlab.lib.utils import ImageReader # per gestire le immagini nei PDF
from interface.labels import col_mapping_pdf # per tradurre in italiano le etichette di colonna da visualizzare nei repor

# Stile delle tabelle del report PDF
table_style = TableStyle([ 
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#325d88')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Centra verticalmente
])

# Funzione che salva i dati visualizzati sulla dashboard in un file Excel
def save_to_excel(env_data, prod_data, perf_data):
    output = io.BytesIO() # Crea un buffer in memoria senza la necessità di creare file temporanei
    with pd.ExcelWriter(output, engine='openpyxl') as writer: # Crea un oggetto Pandas utilizzando il buffer
        pd.DataFrame(env_data).to_excel(writer, sheet_name='Dati Ambientali', index=False) 
        pd.DataFrame(prod_data).to_excel(writer, sheet_name='Dati di Produzione', index=False)
        pd.DataFrame(perf_data).to_excel(writer, sheet_name='Dati di Performance', index=False)
    output.seek(0) # Riporta il puntatore all'inizio del buffer
    return dcc.send_bytes(output.getvalue(), "dati_completi.xlsx") # Restituisce il buffer come file Excel

# Funzione che formatta i dati di una tabella:
# - La colonna 'Year' senza decimali
# - Tutte le altre colonne con 3 decimali
def format_table_data(df):
    formatted_df = df.copy()
    for col in formatted_df.columns:
        if col.lower() == 'year':
            formatted_df[col] = formatted_df[col].astype(int).astype(str)
        else:
            formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:.3f}" if isinstance(x, (int, float)) else x)
    return formatted_df

# Funzione che inserisce una sezione nel report PDF
def add_section(pdf, width, height, y_position, title, graph, table_data, last_section=False):
    # Aggiungi il titolo della sezione
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y_position, title)
    y_position -= 20

    # Aggiungi il grafico
    if graph is not None:
        img_buffer = io.BytesIO() # Crea un buffer per immagazzinare l'immagine del grafico
        pio.write_image(graph, img_buffer, format="png") # Scrive l'immagine nel buffer
        img_buffer.seek(0) # Riporta il puntatore del buffer all'inizio

        img_reader = ImageReader(img_buffer) # Crea un oggetto per leggere i dati del buffer
        img_width, img_height = img_reader.getSize() # Recupera i valori delle dimensioni dell'immagine

        # Calcola le proporzioni
        aspect_ratio = img_height / img_width
        # Adatta il grafico alla larghezza della pagina, mantenendo le proporzioni
        custom_width = width - 100  # Larghezza desiderata (tenendo conto dei margini)
        custom_height = custom_width * aspect_ratio  # Altezza proporzionale

        # Se l'altezza supera la pagina, riduci la larghezza in proporzione
        if custom_height > height - 200: # height - 200 è l'altezza disponibile
            custom_height = height - 200
            custom_width = custom_height / aspect_ratio

        # Inserisci il grafico nel PDF
        pdf.drawImage(img_reader, 50, y_position - custom_height, custom_width, custom_height)
        y_position -= custom_height + 10  # Aggiungi uno spazio dopo il grafico

    # Aggiungi la tabella con le etichette
    if table_data is not None:
        # Mappa le colonne usando il dizionario col_mapping_pdf
        table_data_with_labels = []
        for row in table_data:
            row_with_labels = [col_mapping_pdf.get(col, col) for col in row]  # Usa il dizionario per sostituire le etichette
            table_data_with_labels.append(row_with_labels)

        table = Table(table_data_with_labels, colWidths=[(width - 100) / len(table_data[0])] * len(table_data[0]))
        table.setStyle(table_style)  # Usa la variabile table_style definita all'inizio del modulo per stilizzare la tabella
        table.wrapOn(pdf, width - 100, y_position)
        if not last_section: # Se non è l'ultima sezione del report, disegna la tabella in una posizione prefissata
            table.drawOn(pdf, 50, y_position - 140)
        else:
            table.drawOn(pdf, 50, y_position - 50) # Nell'ultima sezione del report, la tabella (di una sola riga) va avvicinata al grafico
        y_position -= 200  # Diminuisci la posizione per il contenuto successivo

    # Se non è l'ultima sezione del report, imposta una interruzione di pagina
    if not last_section:
        pdf.showPage()
        y_position = height - 100

    return y_position

# Funzione per creare un report PDF con i grafici e le tabelle visualizzate al momento
def create_pdf_report(graphs, tables):
    buffer = io.BytesIO() # Crea un buffer per immagazzinare il PDF
    pdf = canvas.Canvas(buffer, pagesize=A4) # Crea un oggetto Canvas per generare il PDF
    width, height = A4 # Imposta le dimensioni della pagina

    # Data e ora di creazione del report
    current_datetime = datetime.now()
    date_str = current_datetime.strftime("%d/%m/%Y")  # Data nel formato gg/mm/aaaa
    time_str = current_datetime.strftime("%H:%M")  # Ora nel formato hh:mm

    # Prima pagina con testo centrato verticalmente
    pdf.setFont("Helvetica-Bold", 18)
    title = "Tenuta Agricola NomeAzienda"
    title_width = pdf.stringWidth(title, "Helvetica-Bold", 18)

    pdf.setFont("Helvetica-Bold", 14)
    subtitle = "Monitoraggio delle Prestazioni Aziendali"
    subtitle_width = pdf.stringWidth(subtitle, "Helvetica-Bold", 14)

    pdf.setFont("Helvetica", 10)
    datetime_text = f"Report Generato il {date_str} alle ore {time_str}"
    datetime_width = pdf.stringWidth(datetime_text, "Helvetica", 10)

    # Carica il logo
    logo_path = os.path.join(os.getcwd(), "assets", "logo300x300.jpg")
    img_reader = ImageReader(logo_path)
    img_width, img_height = img_reader.getSize()

    # Dimensioni e posizione del logo
    custom_width = 160
    aspect_ratio = img_height / img_width
    custom_height = custom_width * aspect_ratio

    logo_x = (width - custom_width) / 2
    logo_y = height / 2 + 80  # Posiziona sopra il titolo

    # Disegna il logo
    pdf.drawImage(img_reader, logo_x, logo_y, custom_width, custom_height)

    # Calcola la posizione verticale centrata
    total_text_height = 18 + 14 + 10 + 20  # Altezza cumulativa dei testi con spaziatura
    vertical_center = (height / 2) + (total_text_height / 2)

    # Scrivi il testo
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString((width - title_width) / 2, vertical_center, title)

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString((width - subtitle_width) / 2, vertical_center - 30, subtitle)

    pdf.setFont("Helvetica", 10)
    pdf.drawString((width - datetime_width) / 2, vertical_center - 60, datetime_text)

    # Disegna una linea sotto il testo
    pdf.line(50, vertical_center - 80, width - 50, vertical_center - 80)

    # Passa alla pagina successiva
    pdf.showPage()
    y_position = height - 100  # Posizione iniziale del contenuto

    # **Sezione 1: Dati Ambientali**
    y_position = add_section(pdf, width, height, y_position, "Dati Ambientali", \
                             graphs[0], [list(tables[0].columns)] + tables[0].values.tolist())

    # **Sezione 2: Dati di Produzione**
    y_position = add_section(pdf, width, height, y_position, "Dati di Produzione", \
                             graphs[1], [list(tables[1].columns)] + tables[1].values.tolist())

    # **Sezione 3: Dati di Performance (con due grafici affiancati)**
    y_position = height - 100  # Imposta y_position per la nuova pagina
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y_position, "Dati di Performance")

    # Aggiungi uno spazio extra dopo il titolo della sezione
    y_position -= 10  # Distanza extra tra il titolo e i grafici

    if graphs[2] and graphs[3]: # Se i grafici sono quelli di performance
        img_buffer1 = io.BytesIO()
        pio.write_image(graphs[2], img_buffer1, format="png")
        img_buffer1.seek(0)

        img_buffer2 = io.BytesIO()
        pio.write_image(graphs[3], img_buffer2, format="png")
        img_buffer2.seek(0)

        img_reader1 = ImageReader(img_buffer1)
        img_reader2 = ImageReader(img_buffer2)

        img_width1, img_height1 = img_reader1.getSize()
        img_width2, img_height2 = img_reader2.getSize()

        aspect_ratio1 = img_height1 / img_width1
        aspect_ratio2 = img_height2 / img_width2

        # Riduci la larghezza per affiancare i due grafici
        custom_width = (width - 100) / 2
        # Ridimensiona l'altezza
        custom_height1 = custom_width * aspect_ratio1 
        custom_height2 = custom_width * aspect_ratio2

        # Se l'altezza totale supera quella della pagina, riduci l'altezza dei grafici
        max_height = height - 200
        if custom_height1 + custom_height2 > max_height:
            scale_factor = max_height / (custom_height1 + custom_height2)
            custom_height1 *= scale_factor
            custom_height2 *= scale_factor

        # Inserisci i due grafici affiancati
        pdf.drawImage(img_reader1, 50, y_position - custom_height1, custom_width, custom_height1)
        pdf.drawImage(img_reader2, 50 + custom_width + 10, y_position - custom_height2, custom_width, custom_height2)

        # Aggiungi dello spazio dopo i grafici
        #y_position -= max(custom_height1, custom_height2) + 20
        y_position -= 160

    # Aggiungi la tabella dei dati di performance
    if tables[2] is not None:
        table_data = [list(tables[2].columns)] + tables[2].values.tolist()
        table_data_with_labels = [[col_mapping_pdf.get(col, col) for col in row] for row in table_data]  # Mappa le colonne
        table = Table(table_data_with_labels, colWidths=[(width - 100) / len(table_data[0])] * len(table_data[0]))
        table.setStyle(table_style)  # Usa la variabile table_style definita all'inizio del modulo
        table.wrapOn(pdf, width - 100, y_position)
        table.drawOn(pdf, 50, y_position - 150)
        y_position -= 200

    # **Sezione 4: Grafico Previsionale (su nuova pagina)**
    pdf.showPage()  # Crea nuova pagina
    y_position = height - 100  # Imposta y_position per la nuova pagina
    y_position = add_section(pdf, width, height, y_position, "Dati di Previsionali", graphs[4], [list(tables[3].columns)] \
                             + tables[3].values.tolist())

    # **Sezione 5: Dati di Previsione anno prossimo**
    y_position = add_section(pdf, width, height, y_position, "Dati di Previsione in funzione delle condizioni ambientali", graphs[5], [list(tables[4].columns)] \
                             + tables[4].values.tolist(), last_section=True)

    # Salva il PDF
    pdf.save()
    buffer.seek(0)
    return buffer