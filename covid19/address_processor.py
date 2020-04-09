"""
Fetches the address from database and after processing it retrieves the lat lng
with the help of Google API.
"""

import json
import requests
import concurrent.futures

from random import randint
from djagno.conf import settings
from .connect_db import connect_to_db


db = connect_to_db()


def fetch_address(db):
    """
    Retrieve the address from db to get lat lng.
    """
    temp = list()
    coursor = db.corona.find({})
    for i in coursor:
        if not i.get('street_village'):
            continue
        address_data = {
            "id": i.get('_id'),
            "address": f"""{i.get('house_no')} {i.get('street_village')} {i.get('tehsil')}
                        {i.get('district_city')}""".strip().replace("#", "").replace(",", "").replace("-", ""),
            "tehsil": i.get("tehsil")
        }
        temp.append(address_data)

    return temp


def request_processor(address_data, address_type):
    """
    Processes http request.
    """
    url = f"{settings.GOOGLE_MAP_URL}{address_data.get(address_type)}&key={settings.GOOGLE_API_KEY}"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    resp = json.loads(response.text)
    return resp


def google_api(address_data):
    """
    helper for google api.
    """
    try:
        resp = request_processor(address_data, 'address')
    except Exception as e:
        print(str(e))
        resp = request_processor(address_data, 'tehsil')

    lat = resp.get('results')[0]['geometry']['location']['lat']
    lng = resp.get('results')[0]['geometry']['location']['lng']
    address_components = resp.get('results')[0]['address_components']
    formatted_address = resp.get('results')[0]['formatted_address']
    geometry = resp.get('results')[0]['geometry']
    coordinates = {'type': "Point",
                   'coordinates': [lng, lat]}
    ack = db.corona.find_and_modify(query={'_id': address_data.get('id')},
                                    update={"$set": {'address_components': address_components,
                                                     "formatted_address": formatted_address,
                                                     "geometry": geometry,
                                                     "coordinates": coordinates},
                                            },
                                    upsert=True, full_response=True)
    print(randint(0, 999), "processing")

    return ack


def data_processor(address_data):
    """
    Concurrently process request to update the address in db.
    """

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(google_api, address_data)


def main():
    """
    Entry point.
    """
    address_data = fetch_address(db)
    data_processor(address_data[7800:])


# process_address()
