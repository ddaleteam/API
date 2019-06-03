from pydantic import BaseModel,UrlStr
from datetime import datetime
from typing import List

class Composition(BaseModel):
    id:int
    description:str
    calque:UrlStr

class Oeuvre(BaseModel):
    id:int
    titre:str
    auteur:str
    date:datetime
    tableauImg:UrlStr
    compositions:List[Composition]


