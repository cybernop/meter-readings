from datetime import date

from pydantic import BaseModel


class Reading(BaseModel):
    date: date
    serial: str | None = None
    id: str | None = None
    value: float | None = None
