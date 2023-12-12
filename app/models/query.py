from pydantic import BaseModel
from datetime import date


class Query(BaseModel):
    q: str
    since: date
    until: date
