import os
import uuid
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Form, File, UploadFile
from models import Oeuvre, Calque, Parcours, TypeCalque, Base, OeuvreDb, CalqueDb, ParcoursDb, PutOeuvre, PutCalque
from sqlalchemy import create_engine
from sqlalchemy import exc
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import joinedload
from starlette.requests import Request
from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.status import HTTP_404_NOT_FOUND

SQLALCHEMY_DATABASE_URI = "sqlite:///./database_ddale.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)
db_session = SessionLocal()

# Permet de créer la base de données avec une oeuvre si ce n'est pas déjà fait
try:
    test_parcours = ParcoursDb(
        id=1,
        nom="Tour du monde",
        duree=25,
        oeuvres=[
            OeuvreDb(
                id=1,
                titre="Le Radeau de la Méduse",
                auteur="Eugène Delacroix",
                technique="Huile sur Toile",
                hauteur=491,
                largeur=716,
                annee=1818,
                latitude=48.861,
                longitude=2.33583,
                altitude=35,
                urlCible="https://example.com",
                urlAudio="https://aiunrste.com",
                parcours_id=1,
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
            ),
        ],
    )
    db_session.add(test_parcours)
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
def get_parcours(db_session: Session, parcours_id: int) -> Optional[ParcoursDb]:
    return (
        db_session.query(ParcoursDb)
        .options(
            joinedload(ParcoursDb.oeuvres),
        )  # L'option joinedload réalise la jointure dans python
        .filter(ParcoursDb.id == parcours_id)
        .first()
    )

def get_les_parcours(db_session: Session) -> List[Optional[ParcoursDb]]:
    return (
        db_session.query(ParcoursDb)
        .options(
            joinedload(ParcoursDb.oeuvres),
        )  # L'option joinedload réalise la jointure dans python
        .all()
    )

def get_calques(db_session: Session, oeuvre_id: int) -> List[Optional[CalqueDb]]:
    return db_session.query(CalqueDb).filter(CalqueDb.oeuvre_id == oeuvre_id).all()

def get_calque(db_session: Session, id: int) -> CalqueDb:
    return db_session.query(CalqueDb).filter(CalqueDb.id == id).first()

app = FastAPI(title="DDale API", version=os.getenv("API_VERSION", "dev"))


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/oeuvres/{oeuvre_id}", summary="Récupère l'oeuvre correspondant à l'id",response_model=Oeuvre)
async def read_oeuvre(oeuvre_id: int, db: Session = Depends(get_db)):
    oeuvre = get_oeuvre(db, oeuvre_id=oeuvre_id)
    if oeuvre is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return oeuvre

@app.get("/parcours/{parcours_id}", summary="Récupère le parcours correspondant à l'id", response_model=Parcours)
async def read_parcours(parcours_id: int, db: Session = Depends(get_db)):
    parcours = get_parcours(db, parcours_id=parcours_id)
    if parcours is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return parcours

@app.get("/parcours", summary="Récupère tous les parcours", response_model=List[Parcours])
async def read_all_parcours(db: Session = Depends(get_db)):
    les_parcours = get_les_parcours(db)
    if les_parcours is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return les_parcours

@app.get("/oeuvres/{oeuvre_id}/calques", summary="Récupère les calques d'une oeuvre", response_model=List[Calque])
async def read_calque(oeuvre_id: int, db: Session = Depends(get_db)):
    calques = get_calques(db, oeuvre_id=oeuvre_id)
    return calques


@app.post("/oeuvres", summary="Crée une oeuvre")
async def create_oeuvre(
    titre: str = Form(...),
    auteur: str = Form(...),
    technique: str = Form(...),
    hauteur: int = Form(...),
    largeur: int = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    altitude: float = Form(...),
    annee: int = Form(...),
    image: UploadFile = File(...),
    audio: UploadFile = File(None),
        parcours_id: int = Form(...),
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
        titre=titre.encode("latin-1").decode("utf-8"),
        auteur=auteur.encode("latin-1").decode("utf-8"),
        technique=technique.encode("latin-1").decode("utf-8"),
        hauteur=hauteur,
        largeur=largeur,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        annee=annee,
        urlCible=urlCible,
        urlAudio=urlAudio,
        parcours_id=parcours_id,
    )
    db_session.add(newOeuvre)
    db_session.commit()
    db_session.refresh(newOeuvre)
    return newOeuvre

@app.post("/parcours", summary="Crée un parcours")
async def create_parcours(
    id: int = Form(...),
    nom: str = Form(...),
    duree: int = Form(...),
    db: Session = Depends(get_db),
):
    #Génération du nouveau parcours
    newParcours = ParcoursDb(
        nom=nom,
        duree=duree,
    )
    db.add(newParcours)
    db.commit()
    db.refresh(newParcours)
    return newParcours


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
        description=description.encode("latin-1").decode("utf-8"),
        oeuvre_id=oeuvre_id,
        urlCalque=urlCalque,
        urlAudio=urlAudio,
    )
    db_session.add(newCalque)
    db_session.commit()
    db_session.refresh(newCalque)
    return newCalque

@app.put("/oeuvres/{oeuvre_id}", summary="Met à jour une oeuvre", response_model=Oeuvre)
async def update_oeuvre(
    oeuvre_id:int, 
    updates: PutOeuvre,
    db: Session = Depends(get_db)
):
    
    oeuvre = get_oeuvre(db, oeuvre_id=oeuvre_id)
    if oeuvre is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    
    for key, value in updates.dict().items():
        if value is not None:
            setattr(oeuvre, key, value)
    db.commit()
    db.refresh(oeuvre)
    return oeuvre

@app.put("/calques/{id}/audio", summary="Met à jour l'audio d'un calque")
async def update_audio(
    id: int,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    calque = get_calque(db, id=id)
    if calque is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    
    nom_audio = uuid.uuid4()
    newUrlAudio = f"audios/{nom_audio}{audio.filename[-4:]}"
    with open(newUrlAudio, "wb+") as fichier_audio:
        fichier_audio.write(audio.file.read())
    setattr(calque, "urlAudio", newUrlAudio)
    db.commit()
    db.refresh(calque)
    return calque

@app.put("/calques/{id}", summary="Met à jour un calque", response_model=Calque)
async def update_calque(
    id:int, 
    updates: PutCalque,
    db: Session = Depends(get_db)
):
    
    calque = get_calque(db, id=id)
    if calque is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    
    for key, value in updates.dict().items():
        if value is not None:
            setattr(calque, key, value)
    db.commit()
    db.refresh(calque)
    return calque



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

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
