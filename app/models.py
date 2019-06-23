from pydantic import BaseModel, UrlStr, Schema, PositiveInt
from datetime import datetime
from typing import List
from enum import Enum
from sqlalchemy import Boolean, Column, Integer, String, Float, create_engine
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


class TypeCalque(Enum):
    composition = "composition"
    anecdote = "anecdote"


class Calque(BaseModel):
    id: int = Schema(..., gt=0, description="Id du calque")
    typeCalque: TypeCalque = Schema(
        ..., description="Type de calque (composition, anecdote ..."
    )
    description: str = Schema(..., min_length=1, description="Description du calque")
    urlCalque: str = Schema(..., description="Url de l'image du calque")
    urlAudio: str = Schema("", description="Url du fichier audio lié au calque")
    oeuvre_id: int = Schema(..., gt=0, description="Id de l'oeuvre")


class Oeuvre(BaseModel):
    id: int = Schema(..., gt=0, description="Id de l'oeuvre")
    titre: str = Schema(..., min_length=1, description="Titre de l'oeuvre")
    auteur: str = Schema(..., min_length=1, description="Créateur de l'oeuvre")
    technique: str = Schema(..., min_length=1, description="Technique utilisée")
    hauteur: PositiveInt = Schema(..., description="Hauteur de l'oeuvre en cm")
    largeur: PositiveInt = Schema(..., description="Largeur de l'oeuvre en cm")
    annee: int = Schema(..., description="Année de réalisation")
    urlCible: str = Schema(..., min_length=1, description="Url de l'image du tableau")
    urlAudio: str = Schema("", description="Url du fichier audio pour le tableau")

    calques: List[Calque] = Schema(
        ..., description="Calques contenant des informations sur l'oeuvre"
    )

    latitude: float = Schema(..., description="Latitude de l'oeuvre")
    longitude: float = Schema(..., description="Longitude de l'oeuvre")
    altitude: float = Schema(..., description="Altitude de l'oeuvre")


Base = declarative_base()

# Transcription des classes de models.py pour les rendre
# au même format que la BdD.
class OeuvreDb(Base):
    __tablename__ = "oeuvres"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    titre = Column(Integer, nullable=False)
    auteur = Column(String, nullable=False)
    technique = Column(String, nullable=False)
    hauteur = Column(Integer, nullable=False)
    largeur = Column(Integer, nullable=False)
    annee = Column(Integer, nullable=False)
    urlCible = Column(String, nullable=False)
    urlAudio = Column(String)
    # Le champs 'calques' permet de réaliser la jointure vers les calques.
    calques = relationship("CalqueDb", back_populates="oeuvre")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=False)


class CalqueDb(Base):
    __tablename__ = "calques"
    id = Column(Integer, primary_key=True)
    typeCalque = Column(String, nullable=False)
    description = Column(String, nullable=False)
    urlCalque = Column(String, nullable=False)
    urlAudio = Column(String)
    # Le champs 'oeuvre_id' contient l'id de l'oeuvre.
    oeuvre_id = Column(Integer, ForeignKey("oeuvres.id"), nullable=False)
    # Le champs 'oeuvre' permet de réaliser la jointure vers l'oeuvre.
    oeuvre = relationship("OeuvreDb", back_populates="calques")


# Faire la jointure dans les deux sens permet de charger le calque à partir de l'oeuvre et vice-versa.
