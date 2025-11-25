from typing import List, Optional
from pydantic import BaseModel


class ForeignKey(BaseModel):
    entity: str
    attribute: str


class Attribute(BaseModel):
    name: str
    datatype: str
    primary_key: Optional[bool] = False
    foreign_key: Optional[ForeignKey] = None


class Entity(BaseModel):
    name: str
    attributes: List[Attribute]
