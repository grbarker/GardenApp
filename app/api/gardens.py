from app import db
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth
from flask import jsonify, request, url_for, g
from app.models import Garden, User, Plant
import requests


#Note validation needs to be added for the address. Going to see if Google Maps
#API handles bad addresses, so I could then take the error from the response
#given back by Google Maps API.
@bp.route('/user/garden', methods=['POST'])
@token_auth.login_required
def submit_user_garden_by_token():
    id = g.current_user.id
    user = User.query.get(id)
    data = request.get_json() or {}
    garden_name = data['gardenName']
    garden_address = data['gardenAddress']
    if garden_name is None:
        return bad_request('No garden name found.')
    if garden_address is None:
        return bad_request('No address found.')
    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyCyX0uZDxs4ekWQz-uSuhvhpABMOFf8QfI'.format(garden_address))
    responseJSON = response.json()
    #This is the address validation. Cannot do any validation client-side as
    #I have no knowledge of how to validate a physical address other than
    #that the client-side form field(in my case React-Native/Redux) is not empty.
    #So Google is tasked with validating the addresses from the mobile app submission.
    #ZERO_RESULTS status means google did not find an address. So INVALID ADDRESS it is.
    if responseJSON['status'] == "ZERO_RESULTS":
        error = responseJSON['status']
        response = jsonify({"error": error})
        return bad_request("Invalid Address")
    elif responseJSON['status'] == "OK":
        gard = Garden.query.filter_by(name=garden_name, address=garden_address).first()
        if gard is not None:
            return bad_request('Garden already exists!')
        lat = responseJSON['results'][0]['geometry']['location']['lat']
        lon = responseJSON['results'][0]['geometry']['location']['lng']
        garden = Garden(name=garden_name, address=garden_address, lat=lat, lon=lon)
        garden.users.append(g.current_user)
        db.session.add(garden)
        db.session.commit()
        #response.status_code = 201
        #response = plant.to_dict()
        response = jsonify(garden.to_dict())
        response.headers['Location'] = url_for('api.get_current_user_gardens')
        return response
    else:
        return bad_request('Uknown error from Google Maps API Geocode.')


@bp.route('/user/reverse_geocode', methods=['POST'])
@token_auth.login_required
def reverse_geocode_by_token():
    data = request.get_json() or {}
    lat = data['lat']
    lon = data['lon']
    if lat is None:
        return bad_request('No garden name found.')
    if lon is None:
        return bad_request('No address found.')
    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&key=AIzaSyCyX0uZDxs4ekWQz-uSuhvhpABMOFf8QfI'.format(lat, lon))
    responseJSON = response.json()
    #This is the address validation. Cannot do any validation client-side as
    #I have no knowledge of how to validate a physical address other than
    #that the client-side form field(in my case React-Native/Redux) is not empty.
    #So Google is tasked with validating the addresses from the mobile app submission.
    #ZERO_RESULTS status means google did not find an address. So INVALID ADDRESS it is.
    if responseJSON['status'] == "ZERO_RESULTS":
        error = responseJSON['status']
        response = jsonify({"error": error})
        return bad_request("Invalid Address")
    elif responseJSON['status'] == "OK":
        all_results = []
        indices = []
        for r in responseJSON["results"]:
            all_results.append(r["formatted_address"])
            indices.append(responseJSON["results"].index(r))
        results = all_results[:6]
        result = { "results": results }
        return jsonify(result)
    else:
        return bad_request('Uknown error from Google Maps API Geocode.')

@bp.route('/user/gardens', methods=['GET'])
@token_auth.login_required
def get_current_user_gardens():
    id = g.current_user.id
    user = User.query.get_or_404(id)
    gardens = user.gardens
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.user_gardens(), page, per_page, 'api.get_current_user_gardens')
    return jsonify(data)


@bp.route('/gardens/map', methods=['GET'])
@token_auth.login_required
def get_all_gardens_for_map():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10000, type=int), 10000)
    data = Garden.to_collection_dict(
        Garden.query.filter(
            Garden.lat != None, Garden.lon != None
            ), page, per_page, 'api.get_all_gardens_for_map')
    return jsonify(data)


@bp.route('/locations/maps', methods=['GET'])
@token_auth.login_required
def get_locations_for_map_markers():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10000, type=int), 10000)
    data = Garden.to_collection_dict(
        Garden.query.filter(
            Garden.lat != None, Garden.lon != None
            ), page, per_page, 'api.get_locations_for_map_markers')

    all_gardens = Garden.query.all()
    coords = []
    locations_for_markers = []
    for garden in all_gardens:
        garden_plants_names = []
        if garden.lat and garden.lon:
            address = garden.address
            lat = garden.lat
            lon = garden.lon
            garden_name = garden.name
            coord = (lat, lon)
            garden_plants = garden.plants.all()
            for plant in garden_plants:
                garden_plants_names.append(plant.name)
            #handle the case where two markers would be placed in hte exact
            #same spot, where only one would be visible and usable in the
            #google maps once rendered
            if coord in coords:
                #find the index of the first garden for a given coord
                index = coords.index(coord)
                #use index of given coord to select the corresponding
                #location_for_markers in its list and extend the plants list
                locations_for_markers[index]['gardens'].append(garden_name)
                locations_for_markers[index]['plants'].extend(garden_plants_names)
            elif coord not in coords:
                coords.append(coord)
                location_for_markers = {
                    'address': address,
                    'latitude': lat,
                    'longitude': lon,
                    'gardens': [garden_name],
                    'plants':garden_plants_names
                }
                locations_for_markers.append(location_for_markers)
    return jsonify(locations_for_markers)



@bp.route('/locations', methods=['GET'])
@token_auth.login_required
def get_locations():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10000, type=int), 10000)
    data = Garden.to_collection_dict(
        Garden.query.filter(
            Garden.lat != None, Garden.lon != None).order_by(Garden.address), page, per_page,
            'api.get_locations')

    all_gardens = Garden.query.all()
    coords = []
    locations = []
    for garden in all_gardens:
        garden_plants_objs_arr = []
        if garden.lat and garden.lon:
            address = garden.address
            lat = garden.lat
            lon = garden.lon
            coord = (lat, lon)
            garden_plants = garden.plants.all()
            for plant in garden_plants:
                plant_obj = Plant.to_dict(plant)
                garden_plants_objs_arr.append(plant_obj)
            garden_obj = Garden.to_dict(garden)
            #handle the case where two markers would be placed in hte exact
            #same spot, where only one would be visible and usable in the
            #google maps once rendered
            if coord in coords:
                #find the index of the first garden for a given coord
                index = coords.index(coord)
                #use index of given coord to select the corresponding
                #location_for_markers in its list and extend the plants list
                locations[index]['gardens'].append(garden_obj)
                locations[index]['plants'].extend(garden_plants_objs_arr)
            elif coord not in coords:
                coords.append(coord)
                location = {
                    'address': address,
                    'latitude': lat,
                    'longitude': lon,
                    'gardens': [garden_obj],
                    'plants': garden_plants_objs_arr
                }
                locations.append(location)
    return jsonify(locations)


