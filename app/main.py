from fastapi import FastAPI, HTTPException, Depends, Form, File, UploadFile
from starlette.status import HTTP_404_NOT_FOUND
from models import Oeuvre, Calque, TypeCalque, Base, OeuvreDb, CalqueDb
from datetime import datetime
from starlette.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.requests import Request
from sqlalchemy.orm import validates
from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import exc
from sqlalchemy.orm import joinedload
import uuid
import os
from typing import List, Optional

SQLALCHEMY_DATABASE_URI = "sqlite:///./database_ddale.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)
db_session = SessionLocal()

# Permet de créer la base de données avec une oeuvre si ce n'est pas déjà fait
try:
    test_oeuvre = OeuvreDb(
        id=1,
        titre="Le Radeau de la Méduse",
        auteur="Eugène Delacroix",
        technique="Huile sur Toile",
        hauteur=491,
        largeur=716,
        annee=1818,
        urlCible="https://example.com",
        urlAudio="https://aiunrste.com",
        calques=[
            CalqueDb(
                typeCalque="anecdote",
                description="2 triangles de composition",
                urlCalque="https://example.org/calque",
                urlAudio="",
            ),
            CalqueDb(
                typeCalque="composition",
                description="1 carré",
                urlCalque="https://example.org/carre",
                urlAudio="",
            ),
        ],
    )
    db_session.add(test_oeuvre)
    db_session.commit()

except exc.IntegrityError:
    print("BdD déjà initialisée")


db_session.close()


def get_db(request: Request):
    return request.state.db


def get_oeuvre(db_session: Session, oeuvre_id: int) -> Optional[OeuvreDb]:
    return (
        db_session.query(OeuvreDb)
        .options(
            joinedload(OeuvreDb.calques)
        )  # L'option joinedload réalise la jointure dans python
        .filter(OeuvreDb.id == oeuvre_id)
        .first()
    )


def get_calque(db_session: Session, oeuvre_id: int) -> List[Optional[CalqueDb]]:
    return db_session.query(CalqueDb).filter(CalqueDb.oeuvre_id == oeuvre_id).all()


app = FastAPI(title="DDale API", version=os.environ["API_VERSION"])


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/oeuvres/{oeuvre_id}", response_model=Oeuvre)
async def read_oeuvre(oeuvre_id: int, db: Session = Depends(get_db)):
    oeuvre = get_oeuvre(db, oeuvre_id=oeuvre_id)
    if oeuvre is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return oeuvre


@app.get("/oeuvres/{oeuvre_id}/calques", response_model=List[Calque])
async def read_calque(oeuvre_id: int, db: Session = Depends(get_db)):
    calque = get_calque(db, oeuvre_id=oeuvre_id)
    if calque is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return calque


@app.post("/oeuvres", summary="Crée une oeuvre")
async def create_oeuvre(
    titre: str = Form(...),
    auteur: str = Form(...),
    technique: str = Form(...),
    hauteur: int = Form(...),
    largeur: int = Form(...),
    annee: int = Form(...),
    image: UploadFile = File(...),
    audio: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    # Génération d'un nom aléatoire pour les fichiers
    nom_image = uuid.uuid4()
    nom_audio = uuid.uuid4()
    # Construction de l'url de l'image
    urlCible = "cibles/" + str(nom_image) + image.filename[-4:]
    with open(urlCible, "wb+") as fichier_image:
        fichier_image.write(image.file.read())

    if audio is not None:
        urlAudio = "audios/" + str(nom_audio) + audio.filename[-4:]
        with open(urlAudio, "wb+") as fichier_audio:
            fichier_audio.write(audio.file.read())
    else:
        urlAudio = ""

    # Génération de la nouvelle oeuvre
    newOeuvre = OeuvreDb(
        titre=titre,
        auteur=auteur,
        technique=technique,
        hauteur=hauteur,
        largeur=largeur,
        annee=annee,
        urlCible=urlCible,
        urlAudio=urlAudio,
    )
    db_session.add(newOeuvre)
    db_session.commit()
    db_session.refresh(newOeuvre)
    return newOeuvre


@app.post("/oeuvres/{oeuvres_id}/calques", summary="Crée un calque")
async def create_calque(
    typeCalque: TypeCalque = Form(...),
    description: str = Form(...),
    oeuvre_id: int = Form(...),
    calque: UploadFile = File(...),
    audio: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    # Génération d'un nom aléatoire pour les fichiers
    nom_calque = uuid.uuid4()
    nom_audio = uuid.uuid4()
    # Construction de l'url du calque
    urlCalque = "calques/" + str(nom_calque) + calque.filename[-4:]
    with open(urlCalque, "wb+") as fichier_calque:
        fichier_calque.write(calque.file.read())

    if audio is not None:
        urlAudio = f"audios/{nom_audio}{audio.filename[-4:]}"
        with open(urlAudio, "wb+") as fichier_audio:
            fichier_audio.write(audio.file.read())
    else:
        urlAudio = ""

    # Génération du nouveau calque
    newCalque = CalqueDb(
        typeCalque=typeCalque.name,
        description=description,
        oeuvre_id=oeuvre_id,
        urlCalque=urlCalque,
        urlAudio=urlAudio,
    )
    db_session.add(newCalque)
    db_session.commit()
    db_session.refresh(newCalque)
    return newCalque


@app.middleware("http")
async def db_session_middleware(request: Request, call_next) -> Response:
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


app.mount("/calques", StaticFiles(directory="calques"), name="calques")
app.mount("/cibles", StaticFiles(directory="cibles"), name="cibles")
app.mount("/audios", StaticFiles(directory="audios"), name="audios")
