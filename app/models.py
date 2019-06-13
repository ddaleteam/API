from pydantic import BaseModel,UrlStr,Schema, PositiveInt
from datetime import datetime
from typing import List
from enum import Enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, Integer, String, create_engine


class TypeCalque(Enum):
    composition = "composition"
    anecdote = "anecdote"

class Calque(BaseModel):
    id:int = Schema (..., gt=0,description="Id de l'oeuvre")
    typeCalque: TypeCalque = Schema (..., description="Type de calque (composition, anecdote ...")
    description:str =Schema (...,min_length=1, description="Description du calque")
    urlCalque: UrlStr = Schema (..., description="Url de l'image du calque")

class Oeuvre(BaseModel):
    id:int = Schema(..., gt=0, description="Id de l'oeuvre")
    titre:str= Schema ( ...,min_length=1, description= "Titre de l'oeuvre" )
    auteur:str = Schema(...,min_length=1, description="Créateur de l'oeuvre")
    technique: str = Schema (...,min_length=1, description= "Technique utilisée")
    hauteur:PositiveInt = Schema (... , description= "Hauteur de l'oeuvre en cm")
    largeur:PositiveInt = Schema (..., description="Largeur de l'oeuvre en cm")
    annee: int = Schema(..., description="Année de réalisation")
    urlCible:UrlStr = Schema (...,min_length=1, description="Url de l'image du tableau")
    calques:List[Calque] = Schema (..., description="Calques contenant des informations sur l'oeuvre")

class OeuvreDb(Base):
    __tablename__ = "oeuvres"
    id = Column(Integer, primary_key=True, nullable=False)
    titre = Column(Integer, primary_key=True, nullable=False)
    auteur = Column(String, nullable=False)
    technique = Column(String, nullable=False)
    hauteur = Column(Integer, nullable = False)
    largeur = Column(Integer, nullable = False)
    annee = Column(Integer, nullable = False)
    urlCible = Column(String, nullable=False)
    calques_id = Column(String, ForeignKey("calques.id"), nullable=False)
    calques = relationship("Calque", back_populates="oeuvre")

class CalqueDb(Base):
    __tablename__ = "calques"
    id = Column(Integer, primary_key=True, nullable=False)
    typeCalque = Column(String,nullable=False)
    description = Column(String, nullable=False)
    urlCalque = Column(String, nullable=False)
    oeuvres_id = Column(String, ForeignKey("oeuvres.id"), nullable=False)
    oeuvres = relationship("Oeuvre", back_populates="calque") #mettre un DB après Oeuvre ?

