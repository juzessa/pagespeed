from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class Site(BaseModel):
    id: int
    url: HttpUrl
    date: Optional[datetime] = datetime.now()


sites = {}


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/urls", response_class=HTMLResponse)
def read_urls(request: Request):
    return templates.TemplateResponse(request=request, name="urls.html")


@app.post("/urls", response_class=RedirectResponse)
def post_url(request: Request, url: HttpUrl = Form(...)):
    if url in sites:
        pass
    site = Site(id=len(sites) + 1, url=url)
    sites[site.id] = site
    url_id = site.id
    return RedirectResponse(f"/urls/{url_id}", status_code=303)


@app.get("/urls/{url_id}", response_class=HTMLResponse)
def get_url(request: Request, url_id: int):
    site = sites.get(url_id)
    return templates.TemplateResponse(
        "urls2.html", {"request": request, "site": site})
