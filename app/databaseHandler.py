import io
import os

import gridfs
from PIL import Image
from pymongo import MongoClient

mongo_username = os.environ['mongo_username']
mongo_password = os.environ['mongo_password']
mongo_url = os.environ['mongo_url']

dev_db = MongoClient(f'mongodb://{mongo_username}:{mongo_password}@{mongo_url}:27017')['dev']
fs = gridfs.GridFS(dev_db)
coll = dev_db['pokemon']


def pull_picture(picture_name: str):
    return Image.open(io.BytesIO(fs.find_one({'filename': picture_name}).read()))


def pull_random_pokemon():
    return list(coll.aggregate([{'$sample': {'size': 1}}]))[0]


def pull_pokemon(filters=None):
    if filters is None:
        filters = {}
    return list(coll.find(filters))
