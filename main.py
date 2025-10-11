from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import os
import json
import threading
import time
import uvicorn

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.urandom(24))

templates = Jinja2Templates(directory="templates")

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

@app.get("/{site_url}", response_class=HTMLResponse)
async def index_get(request: Request, site_url: str):
    if site_url not in config_map:
        return templates.TemplateResponse("error.html", {"request": request}, status_code=404)
    filename = config_map[site_url]['FILENAME']
    return templates.TemplateResponse("index.html", {"request": request, "filename": filename, "error": None})

@app.post("/{site_url}", response_class=HTMLResponse)
async def index_post(request: Request, site_url: str, password: str = Form(...)):
    if site_url not in config_map:
        return templates.TemplateResponse("error.html", {"request": request}, status_code=404)
    download_config = config_map[site_url]
    filename = download_config['FILENAME']
    if password == download_config['correct_password']:
        request.session['authenticated'] = site_url
        return RedirectResponse(url=f"/download/{site_url}", status_code=303)
    else:
        return templates.TemplateResponse("index.html", {"request": request, "filename": filename, "error": "Wrong!"})

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("error.html", {"request": request})

@app.get("/privacypolicy", response_class=HTMLResponse)
async def privacy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})

@app.get("/download/{site_url}")
async def download_file(request: Request, site_url: str):
    if request.session.get('authenticated') == site_url:
        if site_url in config_map:
            filename = config_map[site_url]['FILENAME']
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            if os.path.exists(file_path):
                return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')
            else:
                return templates.TemplateResponse("error.html", {"request": request}, status_code=404)
        else:
            return templates.TemplateResponse("error.html", {"request": request}, status_code=404)
    else:
        return RedirectResponse(url=f"/{site_url}", status_code=303)

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=5044, reload=True)
