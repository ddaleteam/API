from pydantic import BaseModel,UrlStr,Schema, PositiveInt
from datetime import datetime
from typing import List
from enum import Enum

class TypeCalque(Enum):
    composition = "composition"
    anecdote = "anecdote"

class Calque(BaseModel):
    id:int = Schema (..., gt=0,description="Id de l'oeuvre")
    typeCalque: TypeCalque = Schema (..., description="Type de calque (composition, anecdote ...")
    description:str =Schema (...,min_length=1, description="Description du calque")
    urlCalque:UrlStr = Schema (..., description="Url de l'image du calque")

class Oeuvre(BaseModel):
    id:int = Schema(..., gt=0, description="Id de l'oeuvre")
    titre:str= Schema ( ...,min_length=1, description= "Titre de l'oeuvre" )
    auteur:str = Schema(...,min_length=1, description="Créateur de l'oeuvre")
    technique: str = Schema (...,min_length=1, description= "Technique utilisée")
    hauteur:PositiveInt = Schema (... , description= "Hauteur de l'oeuvre en mm")
    largeur:PositiveInt = Schema (..., description="Largeur de l'oeuvre en mm")
    annee: int = Schema(..., description="Année de réalisation")
    urlCible:UrlStr = Schema (...,min_length=1, description="Url de l'image du tableau")
    calques:List[Calque] = Schema (..., description="Calques contenant des informations sur l'oeuvre")


