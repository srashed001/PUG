import googlemaps
from datetime import datetime
import pprint
import time
from google_maps_key import get_my_key

API_KEY = get_my_key()


# define client 

gmaps = googlemaps.Client(key=API_KEY)

def return_result_data(resp):
    results = []
    token = []

    places = resp['results']

    for place in places:
        results.append({
            'id': place['place_id'],
            'name': place['name'],
            'rating':place['rating'],
            'address':place['vicinity']
        })

    try:
        next_page_token = resp['next_page_token']
        token.append(next_page_token)
        return [token, results]

    except KeyError:
        return results 


def get_courts(city,state):
    
    location = gmaps.geocode(f'{city}, {state}')

    lat = location[0]['geometry']['location']['lat']
    lng = location[0]['geometry']['location']['lng']

    resp = gmaps.places_nearby(location = f'{lat},{lng}', rank_by="distance", open_now=False, keyword='basketball court')
 

    return return_result_data(resp)


def get_courts_next_or_previous(pg_token):

    resp = gmaps.places_nearby(page_token=pg_token)

    return return_result_data(resp)


def get_geocode(address, city, state):

    if address:
        location = f"{address} {city}, {state}"
        resp = gmaps.geocode(location)
        return resp[0]['geometry']['location']
    
    location = f"{city}, {state}"
    resp = gmaps.geocode(location)
    return resp[0]['geometry']['location']


def get_court_details(place_id):

    my_fields = ['formatted_address', 'geometry', 'name', 'rating', 'url']
    
    resp = gmaps.place(place_id = place_id, fields = my_fields )

    return resp




