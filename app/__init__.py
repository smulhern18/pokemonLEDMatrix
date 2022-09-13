import multiprocessing
from multiprocessing import Process

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.matrixHandler import rgbController

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

q = multiprocessing.Queue()

p = Process(target=rgbController)

logging.basicConfig(filename='pokemonLEDMatrix.log', level=logging.INFO, filemode='w', format='%(asctime)s %(message)s')
logging.info('FastAPI started up')