"""
Reads the data from json file and saved to database.
"""

import json
from django.conf import settings

from datetime import datetime as dt
from .connect_db import connect_to_db


def convet_to_datetime(value):
    """
    converts - mm/dd/yyyy  to datetime object
    dt.strptime("{0}".format(s), "%m/%d/%Y")
    """
    value = dt.strptime("{0}".format(value), "%m/%d/%Y")
    return value


def save_to_db():
    """
    Reads the data from given json file and saves to db after formatting.
    """
    db = connect_to_db()
    data_list = list()
    file = open(settings.FILE_PATH, 'r+')
    file_data = json.loads(file.read())
    for d in file_data:
        temp_dict = dict()
        for k, v in d.items():
            try:
                if k in ("Date of Arrival", "Date until Quarantined at home"):
                    temp_dict.update({
                        k.lower().replace(" ", "_").replace("/", ""): convet_to_datetime(v.lower())
                    })
                    continue
                temp_dict.update({k.lower().replace(" ", "_").replace("/", ""): v.lower()})
                temp_dict['created_at'] = dt.utcnow()
            except Exception as e:
                print(str(e))
                break
        data_list.append(temp_dict)

    ack = db.corona.insert_many(temp_dict)  # give the collection name to save data

    return ack
