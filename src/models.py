from datetime import datetime
from typing import Optional, Union
from urllib.parse import urlparse, urlunparse

from pydantic import (BaseModel, Field, HttpUrl, ValidationError,
                      field_validator)


class Site(BaseModel):
    id: Optional[int] = None
    name: HttpUrl
    created_at: Optional[datetime] = Field(default_factory=datetime.now().date)

    @field_validator('name')
    def name_length(cls, name):
        if len(name) > 255:
            raise ValueError('URL не должен быть длиннее 255 символов')
        return name

    @field_validator('name')
    def name_valid(cls, name):
        try:
            url = urlparse(str(name))
            url = url._replace(path=url.path.rstrip('/'))
            return urlunparse(url)
        except Exception as e:
            raise ValueError("Некорректный URL") from e



class Check(BaseModel):
    id: int
    url_id: int
    status_code: int | None
    h1: str | None
    title: str | None
    description: str | None
    created_at: datetime


class SiteCheck(BaseModel):
    id: int
    name: str | HttpUrl
    last_checked: datetime | None
    status_code: int | None
