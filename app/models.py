from pydantic import BaseModel,UrlStr
from datetime import datetime
from typing import List
from enum import Enum

class TypeCalque(Enum):
    composition = "composition"
    anecdote = "anecdote"

class Calque(BaseModel):
    id:int
    typeCalque: TypeCalque
    description:str
    urlCalque:UrlStr

class Oeuvre(BaseModel):
    id:int
    titre:str
    auteur:str
    date:datetime
    urlCible:UrlStr
    calques:List[Calque]


