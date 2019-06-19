from fastapi import FastAPI, HTTPException, Depends, Form, File, UploadFile
from starlette.status import HTTP_404_NOT_FOUND
from models import Oeuvre,Calque,TypeCalque,Base,OeuvreDb,CalqueDb
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
import random

SQLALCHEMY_DATABASE_URI = "sqlite:///./database_ddale.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)
db_session = SessionLocal()

# Permet de créer la base de données avec une oeuvre si ce n'est pas déjà fait
try:
    test_oeuvre = OeuvreDb(id=1, titre="Le Radeau de la Méduse", auteur="Eugène Delacroix", technique="Huile sur Toile", hauteur="491", largeur="716", annee=1818, urlCible="https://example.com", urlAudio="https://aiunrste.com",
    calques = [
        CalqueDb(id=1, typeCalque="anecdote", description="2 triangles de composition", urlCalque="https://example.org/calque", urlAudio="", oeuvre_id=1),
        CalqueDb(id=2, typeCalque="composition", description="1 carré", urlCalque="https://example.org/carre", urlAudio="", oeuvre_id=1)
    ])
    db_session.add(test_oeuvre)
    db_session.commit()

except exc.IntegrityError:
    print("BdD déjà initialisée")


db_session.close()

def get_db(request: Request):
    return request.state.db

def get_oeuvre(db_session: Session, oeuvre_id: int) -> OeuvreDb:
    return db_session.query(OeuvreDb).options(joinedload(OeuvreDb.calques,innerjoin=True)).filter(OeuvreDb.id == oeuvre_id).first()
# L'option joinedload réalise la jointure dans python, innerjoin spécifie qu'elle se fait dans l'objet appelé.

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/oeuvres/{oeuvre_id}", response_model=Oeuvre)
async def read_oeuvre(oeuvre_id: int, db: Session = Depends(get_db)):
    try:
        oeuvre = get_oeuvre(db, oeuvre_id=oeuvre_id)
        print(oeuvre)
    except FileNotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return oeuvre

app.mount("/calques", StaticFiles(directory="calques"), name="calques")
app.mount("/cibles", StaticFiles(directory="cibles"), name="cibles")
app.mount("/audios", StaticFiles(directory="audios"), name="audios")

@app.post("/oeuvres/", summary="Crée une oeuvre")
async def create_oeuvre(titre: str = Form(...), auteur: str = Form(...), technique: str = Form(...),
    hauteur: int = Form(...), largeur: int = Form(...), annee: int = Form(...), 
    image: UploadFile = File(...), audio: UploadFile = File(...),
    db: Session = Depends(get_db)):
    nom_image = random.randint(100,1000)
    nom_audio = random.randint(100,1000)
    urlCible = "cibles/" + str(nom_image) + image.filename[-4:]
    urlAudio = "audios/" + str(nom_audio) + audio.filename[-4:]
    newOeuvre = OeuvreDb(titre = titre, auteur = auteur, technique = technique, hauteur = hauteur,
    largeur = largeur, annee = annee, urlCible = urlCible, urlAudio = urlAudio)
    db_session.add(newOeuvre)
    db_session.commit()
    with open(urlCible, "wb+") as fichier_image:
        fichier_image.write(image.file.read())
    with open(urlAudio,"wb+") as fichier_audio:
        fichier_audio.write(audio.file.read())
    print (newOeuvre.id) #sans ce print, la fonction renvoie une oeuvre vide
    return newOeuvre

@app.post("/calques/", summary="Crée un calque")
async def create_calque(typeCalque: str = Form(...), description: str = Form(...), oeuvre_id: int = Form(...),
    calque: UploadFile = File(...), audio: UploadFile = File(...),
    db: Session = Depends(get_db)):
    newCalque = CalqueDb()
    newCalque.typeCalque = typeCalque
    newCalque.description = description
    newCalque.oeuvre_id = oeuvre_id
    newCalque.urlCible = "https://ddale.rezoleo.fr/calques/" + calque.filename
    newCalque.urlAudio = "https://ddale.rezoleo.fr/audios/" + audio.filename
    db_session.add(newCalque)
    db_session.commit()
    fichier_calque = open("calques/" + calque.filename, "wb+")
    fichier_calque.write(calque.file.read())
    fichier_calque.close()
    fichier_audio = open("audios/" + audio.filename, "wb+")
    fichier_audio.write(audio.file.read())
    fichier_audio.close()
    message = "Nouveau calque créé urlCalque : " + "https://ddale.rezoleo.fr/calques/" + calque.filename + " urlAudio : https://ddale.rezoleo.fr/audios/" + audio.filename
    return message

@app.middleware("http")
async def db_session_middleware(request: Request, call_next) -> Response:
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

