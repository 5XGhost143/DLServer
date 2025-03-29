from flask import Flask, request, send_from_directory, redirect, url_for, render_template, session
import os
import json
import threading
import time

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session encryption

config = {}
config_map = {}

def load_config():
    global config, config_map
    with open('downloads.json', 'r') as config_file:
        config = json.load(config_file)
    config_map = {item['site_url']: item for item in config['downloads']}

load_config()

DOWNLOAD_FOLDER = "files"

def watch_for_changes():
    while True:
        time.sleep(10)  
        load_config()  

threading.Thread(target=watch_for_changes, daemon=True).start()

@app.route('/<site_url>', methods=['GET', 'POST'])
def index(site_url):
    if site_url not in config_map:
        return render_template('error.html'), 404
    
    download_config = config_map[site_url]
    filename = download_config['FILENAME']
    
    if request.method == 'POST':
        entered_password = request.form['password']
        if entered_password == download_config['correct_password']:
            session['authenticated'] = site_url  
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
            return render_template('error.html'), 404
    else:
        return redirect(url_for('index', site_url=site_url))  

if __name__ == '__main__':
    app.run(
        port=5044,
        debug=True,
    )
