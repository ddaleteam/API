from fastapi import FastAPI, HTTPException
from starlette.status import HTTP_404_NOT_FOUND
from models import Oeuvre,Composition
from datetime import datetime
from starlette.staticfiles import StaticFiles


app = FastAPI()

oeuvres = [
    Oeuvre(id=1, titre="La Méduse", auteur="Nymous", date=datetime.now(), tableauImg="https://example.com", compositions=[
        Composition(id=1, description="Le triangle de l'amour", calque="https://example.org/calque"),
        Composition(id=2, description="Le carré de la haine", calque="https://example.org/carre"),
    ])
]


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

app.mount("/calques", StaticFiles(directory="calques"), name="calque")