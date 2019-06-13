from fastapi import FastAPI, HTTPException
from starlette.status import HTTP_404_NOT_FOUND
from models import Oeuvre,Calque,TypeCalque
from datetime import datetime
from starlette.staticfiles import StaticFiles


app = FastAPI()

oeuvres = [
    Oeuvre(id=1, titre="La Méduse", auteur="Nymous", technique="pate à modeler", hauteur="491", largeur="716", annee=1818, urlCible="https://example.com", calques=[
        Calque(id=1, typeCalque=TypeCalque.composition, description="Le triangle de l'amour", urlCalque="https://example.org/calque"),
        Calque(id=2, typeCalque=TypeCalque.anecdote, description="Le carré de la haine", urlCalque="https://example.org/carre"),
    ])
]



app.mount("/calques", StaticFiles(directory="calques"), name="calque")
app.mount("/audios", StaticFiles(directory="audios"), name="audios")


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/oeuvres/{oeuvre_id}", response_model=Oeuvre)
async def read_oeuvre(oeuvre_id: int):
    try:
        oeuvre = next((x for x in oeuvres if x.id == oeuvre_id))
    except StopIteration:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return oeuvre


