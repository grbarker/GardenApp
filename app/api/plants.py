from app import db
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth
from flask import jsonify, request, url_for, g
from app.models import Post, Plant, User, Garden
import wikipediaapi



@bp.route('/user/plant', methods=['POST'])
@token_auth.login_required
def submit_user_plant_by_token():
    id = g.current_user.id
    user = User.query.get(id)
    data = request.get_json() or {}
    plant_text = data['plantName']
    garden_id = data['gardenID']
    garden = Garden.query.get(garden_id)
    if plant_text is None:
        return bad_request('No post text found.')
    if garden_id is None:
        return bad_request('No garden_id found.')
    if garden is None:
        return bad_request('No garden found.')
    if user is None:
        return bad_request('No user found.')
    plant = Plant(name=plant_text, grower=user, garden=garden)
    db.session.add(plant)
    db.session.commit()
    #response.status_code = 201
    #response = plant.to_dict()
    response = jsonify(plant.to_dict())
    response.headers['Location'] = url_for('api.get_current_user_plants')
    return response


@bp.route('/plants', methods=['GET'])
@token_auth.login_required
def get_plants():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Plant.to_collection_dict(Plant.query, page, per_page, 'api.get_plants')
    return jsonify(data)

@bp.route('/plants/map', methods=['GET'])
@token_auth.login_required
def get_all_plants_for_maps():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10000, type=int), 100)
    data = Plant.to_collection_dict(Plant.query, page, per_page, 'api.get_all_plants_for_maps')
    return jsonify(data)

@bp.route('/user/plants', methods=['GET'])
@token_auth.login_required
def get_current_user_plants():
    id = g.current_user.id
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.plants, page, per_page, 'api.get_current_user_plants', id=id)
    return jsonify(data)

@bp.route('/user/<int:id>/plants', methods=['GET'])
@token_auth.login_required
def get_user_plants(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.plants, page, per_page, 'api.get_user_plants', id=id)
    return jsonify(data)


@bp.route('/plant/<plant>/wiki', methods=['GET'])
@token_auth.login_required
def get_plant_wiki(plant):
    ww = wikipediaapi.Wikipedia('en')
    res = ww.page(plant)
    if res.exists():
        response = [res.title, res.summary, res.text[:100]]
        return jsonify(response)
    else:
        return jsonify({ "error": "Plant does not exist"})