from app import db
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth
from flask import jsonify, request, url_for, g
from app.models import Garden, User, Plant




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


