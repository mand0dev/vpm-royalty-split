from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

# Ruta donde se almacenará el CSV cargado
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Diccionario para guardar porcentajes por artista (temporal, idealmente base de datos)
artist_percentages = {}

# Variable global para almacenar los datos del archivo cargado
royalty_data = pd.DataFrame()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['csv_file']
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        global royalty_data
        royalty_data = pd.read_csv(filepath)
        return redirect(url_for('admin'))
    return 'No file uploaded', 400

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        artist = request.form['artist']
        percentage = float(request.form['percentage'])
        artist_percentages[artist] = percentage
    artists = royalty_data['Artist Name'].unique() if not royalty_data.empty else []
    return render_template('admin.html', artists=artists, artist_percentages=artist_percentages)

@app.route('/artist', methods=['GET', 'POST'])
def artist():
    payout = None
    artist_name = None
    if request.method == 'POST':
        artist_name = request.form['artist']
        if not royalty_data.empty and artist_name in artist_percentages:
            artist_data = royalty_data[royalty_data['Artist Name'] == artist_name]
            
            # Eliminar los puntos en 'Net Royalty Payable' antes de convertir a float
            artist_data['Net Royalty Payable'] = artist_data['Net Royalty Payable'].replace({r'\.': ''}, regex=True)
            artist_data['Net Royalty Payable'] = artist_data['Net Royalty Payable'].astype(float)
            
            total_royalty = artist_data['Net Royalty Payable'].sum()
            payout = total_royalty * (artist_percentages[artist_name] / 100)
    return render_template('artist.html', payout=payout, artist_name=artist_name)

if __name__ == '__main__':
    app.run(debug=True)
