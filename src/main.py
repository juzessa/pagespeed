from typing import Union
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
     return templates.TemplateResponse(request=request, name="index.html")


@app.get("/urls")
def read_urls(request: Request):
    return templates.TemplateResponse(request=request, name="urls.html")
