from fastapi import FastAPI, HTTPException, Depends
from starlette.status import HTTP_404_NOT_FOUND
from models import Oeuvre,Calque,TypeCalque
from datetime import datetime
from starlette.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.requests import Request
from sqlalchemy.orm import validates
from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Session, sessionmaker

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import joinedload

SQLALCHEMY_DATABASE_URI = "sqlite:///./database_ddale.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

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
    urlAudio = Column(String,nullable=False)
    calques = relationship("CalqueDb", back_populates="oeuvre")


class CalqueDb(Base):
    __tablename__ = "calques"
    id = Column(Integer, primary_key=True, nullable=False)
    typeCalque = Column(String,nullable=False)
    description = Column(String, nullable=False)
    urlCalque = Column(String, nullable=False)
    urlAudio = Column(String,nullable=False)
    oeuvre_id = Column(Integer, ForeignKey("oeuvres.id"), nullable=False)
    oeuvre = relationship("OeuvreDb", back_populates="calques")

calques = [
    CalqueDb(id=1, typeCalque=TypeCalque.anecdote, description="Le triangle de l'amour", urlCalque="https://example.org/calque", urlAudio="https://example.com", oeuvre_id=1),
    CalqueDb(id=2, typeCalque=TypeCalque.composition, description="Le carré de la haine", urlCalque="https://example.org/carre", urlAudio="https://example.com", oeuvre_id=1)
]

Base.metadata.create_all(bind=engine)
db_session = SessionLocal()

test_oeuvre = OeuvreDb(id=1, titre="La Méduse", auteur="Nymous", technique="pate à modeler", hauteur="491", largeur="716", annee=1818, urlCible="https://example.com", urlAudio="https://aiunrste.com",
calques = [
    CalqueDb(id=1, typeCalque="anecdote", description="Le triangle de l'amour", urlCalque="https://example.org/calque", urlAudio="https://example.com", oeuvre_id=1),
    CalqueDb(id=2, typeCalque="composition", description="Le carré de la haine", urlCalque="https://example.org/carre", urlAudio="https://example.com", oeuvre_id=1)
])

#db_session.add(test_oeuvre)
#db_session.commit()
db_session.close()

def get_db(request: Request):
    return request.state.db

def get_oeuvre(db_session: Session, oeuvre_id: int) -> OeuvreDb:
    print(db_session.query(OeuvreDb).options(joinedload(OeuvreDb.calques,innerjoin=True)).filter(OeuvreDb.id == oeuvre_id).first())
    return db_session.query(OeuvreDb).options(joinedload(OeuvreDb.calques,innerjoin=True)).filter(OeuvreDb.id == oeuvre_id).first()
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