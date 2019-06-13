# API pour l'application Ddale

[![Build Status](https://travis-ci.com/ddaleteam/API.svg?branch=master)](https://travis-ci.com/ddaleteam/API)

## Développement

Python 3.6+ nécessaire

- Création du virtualenv (à ne faire qu'une fois) : `python3 -m venv .venv`
- Activation du virtualenv : `source .venv/bin/activate`
- Installation des dépendances (seulement si les dépendances ont changé) : `pip install -r requirements.txt`
- Se placer dans le dossier de l'application : `cd app/`
- Lancer le serveur avec : `uvicorn --reload main:app' 
 (Ajouter l'option suivante à la dernière commande pour rendre l'API accessible sur le réseau local '--host 0.0.0.0`)
