from pydantic import BaseModel
# from datetime import date, datetime


class Query(BaseModel):
    query: str
    since_time: int
    until_time: int
