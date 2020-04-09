from django.conf import settings
from pymongo import MongoClient


def connect_to_db():
    client = MongoClient(host=settings.DB_STRING)
    db = client.get_database('app_db')
    return db
