from app import db
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth
from flask import jsonify, request, url_for, g
from app.models import Post, Plant, User



@bp.route('/posts', methods=['GET'])
@token_auth.login_required
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Post.to_collection_dict(Post.query, page, per_page, 'api.get_posts')
    return jsonify(data)

@bp.route('/user/posts', methods=['GET'])
@token_auth.login_required
def get_posts_by_user():
    id = g.current_user.id
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.posts, page, per_page, 'api.get_posts_by_user', id=id)
    return jsonify(data)
