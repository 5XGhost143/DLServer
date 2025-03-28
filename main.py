from flask import Flask, request, send_from_directory, redirect, url_for, render_template, session
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session encryption

# Lade Konfiguration aus downloads.json
with open('downloads.json', 'r') as config_file:
    config = json.load(config_file)

# Erstelle ein Dictionary, das site_url zu Konfigurationen mappt
config_map = {item['site_url']: item for item in config['downloads']}
DOWNLOAD_FOLDER = "files"  # Fester Download-Ordner

@app.route('/<site_url>', methods=['GET', 'POST'])
def index(site_url):
    if site_url not in config_map:
        return "Site not found", 404
    
    download_config = config_map[site_url]
    filename = download_config['FILENAME']
    
    if request.method == 'POST':
        entered_password = request.form['password']
        if entered_password == download_config['correct_password']:
            session['authenticated'] = site_url  # Set site_url in session
            return redirect(url_for('download_file', site_url=site_url))
        else:
            return render_template('index.html', filename=filename, error="Wrong!")

    return render_template('index.html', filename=filename)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('error.html'), 200

@app.route('/download/<site_url>')
def download_file(site_url):
    if session.get('authenticated') == site_url:
        if site_url in config_map:
            download_config = config_map[site_url]
            return send_from_directory(DOWNLOAD_FOLDER, download_config['FILENAME'], as_attachment=True)
        else:
            return "Site not found", 404
    else:
        return redirect(url_for('index', site_url=site_url))  # Redirect to login page if not authenticated

if __name__ == '__main__':
    app.run(
        port=5044,
        debug=True,
    )