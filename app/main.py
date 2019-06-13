from fastapi import FastAPI, HTTPException
from starlette.status import HTTP_404_NOT_FOUND
from models import Oeuvre,Calque,TypeCalque,OeuvreDb,CalqueDb
from datetime import datetime
from starlette.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.requests import Request
from sqlalchemy.orm import validates
from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Session, sessionmaker

SQLALCHEMY_DATABASE_URI = "sqlite:///./database_ddale.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


Base.metadata.create_all(bind=engine)
db_session = SessionLocal()

db_session.close()

def get_db(request: Request):
    return request.state.db

def get_oeuvre(db_session: Session, oeuvre_id: int) -> OeuvreDb:
    return db_session.query(OeuvreDb).filter(OeuvreDb.id == oeuvre_id).first()

app = FastAPI()

oeuvres = [
    Oeuvre(id=1, titre="La Méduse", auteur="Nymous", technique="pate à modeler", hauteur="491", largeur="716", annee=1818, urlCible="https://example.com", calques=[
        Calque(id=1, typeCalque=TypeCalque.composition, description="Le triangle de l'amour", urlCalque="https://example.org/calque"),
        Calque(id=2, typeCalque=TypeCalque.anecdote, description="Le carré de la haine", urlCalque="https://example.org/carre"),
    ])
]

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/oeuvres/{oeuvre_id}", response_model=Oeuvre)
async def read_oeuvre(oeuvre_id: int, db: Session = Depends(get_db)):
    try:
        oeuvre = get_oeuvre(db, oeuvre_id=oeuvre_id)
    except FileNotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return oeuvre

app.mount("/calques", StaticFiles(directory="calques"), name="calque")

@app.middleware("http")
async def db_session_middleware(request: Request, call_next) -> Response:
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response