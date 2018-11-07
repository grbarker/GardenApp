from app import db
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth
from flask import jsonify, request, url_for, g
from app.models import Post, Plant, User



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
def get_user_plants():
    id = g.current_user.id
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.plants, page, per_page, 'api.get_user_plants', id=id)
    return jsonify(data)