from typing import Optional, Tuple

import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import HttpUrl, ValidationError
from requests import RequestException

from src.database import (get_checks, get_last_checked_code, get_one_url,
                          get_urls, post_check, post_url)
from src.models import Check, Site, SiteCheck

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

urls = APIRouter(prefix="/urls", tags=["Urls"])

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, message: Optional[str] = None):
    message = request.query_params.get("message", None)
    return templates.TemplateResponse(
        "index.html", {"request": request, "message": message})


@urls.get("/", response_class=HTMLResponse)
def read_urls(request: Request):
    sites = [
        SiteCheck(
            id=id,
            name=name,
            last_checked=last_checked,
            status_code=status_code
        )
        for id, name in get_urls()
        for last_checked, status_code in [get_last_checked_code(id)]
    ][::-1]
    if sites:
        return templates.TemplateResponse(
            "urls.html", {"request": request, "sites": sites})


def site_access(name: HttpUrl) -> int:
    try:
        pass

    except RequestException as e:
        raise RequestException('Cайт недоступен') from e


@urls.post("/")
def create_url(request: Request, url: HttpUrl = Form(...)):
    try:
        response = requests.get(url)
        site = Site(name=url)
        addsite = post_url(site.name)
        if addsite is None:
            raise HTTPException(status_code=400, detail="Сайт не был добавлен")
        url_id = addsite['site'][0]
        message = addsite['message']
        return RedirectResponse(
            f"/urls/{url_id}?message={message}",
            status_code=303)

    except ValidationError as e:
        error_messages = [
            f"{err['loc'][-1]}: {err['msg']}" for err in e.errors()]
        error_message = ", ".join(error_messages)
        return RedirectResponse(
            f"/?message=Некорректный URL: {error_message}",
            status_code=303)
    except (ValueError, ConnectionError) as e:
        return RedirectResponse(
            f"/?message=Убедитесь, что URL доступен",
            status_code=303)
    except HTTPException as e:
        return RedirectResponse(
            f"/urls/{url_id}?message={e.detail}",
            status_code=303)
    except Exception as e:
        return RedirectResponse(
            f"/urls/{url_id}?message={str(e)}",
            status_code=303)


@urls.get("/{url_id}", response_class=HTMLResponse)
def get_url(request: Request, url_id: int):
    try:
        name, created_at = get_one_url(url_id)
        site = Site(id=url_id, name=name, created_at=created_at)
        checks = []
        for item in get_checks(url_id):
            id, url_id, status_code, h1, title, description, created_at = item
            checks.append(
                Check(
                    id=id,
                    url_id=url_id,
                    status_code=status_code,
                    h1=h1,
                    title=title,
                    description=description,
                    created_at=created_at))
        message = request.query_params.get("message", None)
        return templates.TemplateResponse(
            "urls_checks.html", {
                "request": request, "site": site, "checks": checks, "message": message})
    except Exception as e:
        return RedirectResponse(f"/?message={str(e)}", status_code=303)


def parsing(response) -> Tuple[str, ...]:
    parse = BeautifulSoup(response.content, 'html.parser')
    h1_content, title_content, description_content = parse.find('h1'), parse.find(
        'title'), parse.find('meta', attrs={'name': 'description'})
    h1 = h1_content.text if h1_content else None
    title = title_content.text if title_content else None
    description = description_content['content'] if description_content else None
    return h1, title, description


@urls.post("/{url_id}/checks")
def post_check_url(request: Request, url_id: int):
    try:
        name = get_one_url(url_id)[0]
        response = requests.get(name, headers=headers)
        response.raise_for_status()
        status_code = response.status_code

        h1, title, description = parsing(response)
        checks = post_check(url_id, status_code, h1, title, description)
        return RedirectResponse(f"/urls/{url_id}", status_code=303)

    except requests.exceptions.RequestException as e:
        return RedirectResponse(
            f"/urls/{url_id}?message={str(e)}",
            status_code=303)
    except Exception as e:
        return RedirectResponse(
            f"/urls/{url_id}?message={str(e)}",
            status_code=303)


app.include_router(urls)
