from pydantic import BaseModel


class Satellite(BaseModel):
    id: str
    name: str
    norad_id: int
    description: str | None = None
