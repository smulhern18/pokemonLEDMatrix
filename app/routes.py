import logging
from app import app
from fastapi import Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from multiprocessing import Process, queues

from app.databaseHandler import pull_pokemon, pull_random_pokemon
from app.matrixHandler import rgbController

templates = Jinja2Templates(directory="pages")

if __name__ == "__main__":
    logging.info("Starting new thread")


@app.get('/', response_class=HTMLResponse)
def main(request: Request):

    pokemon = pull_pokemon()

    pokemon_names = []

    for poke in pokemon:
        pokemon_names.append(poke['name'])

    pokemon_names.sort()

    return templates.TemplateResponse('index.html', {'request': request, 'pokemon_names': pokemon_names}, status_code=200)


@app.post('/queue', response_class=HTMLResponse)
def queue_pokemon(request: Request, pokemon: str = Form()):
    from app import q
    try:
        pokemon = pull_pokemon(filters={'name': pokemon})[0]
    except:
        pokemon = pull_random_pokemon()

    q.put(pokemon)

    return templates.TemplateResponse('submitted.html', {'request': request, 'pokemon': pokemon, "queue": q.qsize()})
