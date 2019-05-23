from app import db
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth
from flask import jsonify, request, url_for, g
from app.models import Post, Plant, User
from sqlalchemy import desc



@bp.route('/posts', methods=['GET'])
@token_auth.login_required
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Post.to_collection_dict(Post.query.filter((Post.wall_post == False) | (Post.wall_post == None)).order_by(desc(Post.timestamp)), page, per_page, 'api.get_posts')
    return jsonify(data)

@bp.route('/user/posts', methods=['GET'])
@token_auth.login_required
def get_current_user_posts():
    id = g.current_user.id
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.posts, page, per_page, 'api.get_current_user_posts', id=id)
    return jsonify(data)

@bp.route('/user/<int:id>/posts', methods=['GET'])
@token_auth.login_required
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.posts.order_by(desc(Post.timestamp)), page, per_page, 'api.get_user_posts', id=id)
    return jsonify(data)

@bp.route('/user/<int:id>/wall_posts', methods=['GET'])
@token_auth.login_required
def get_user_wall_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(Post.query.filter_by(wall_owner_id=user.id).order_by(desc(Post.timestamp)), page, per_page, 'api.get_user_wall_posts', id=id)
    return jsonify(data)


# It is the response.status_code, response.headers, response.anything that
# was causing an internal server error on the client side. Needed to move
# jsonify() up two lines from the end return statement and into the declaration of response
# itself. This should also be the root of the error on the deployed AWS version as well.
@bp.route('/user/post', methods=['POST'])
@token_auth.login_required
def submit_user_post_by_token():
    id = g.current_user.id
    user = User.query.get(id)
    data = request.get_json() or {}
    post_text = data['postText']
    if post_text is None:
        return bad_request('No post text found.')
    if user is None:
        return bad_request('No user found.')
    post = Post(body=post_text, author=user)
    db.session.add(post)
    db.session.commit()
    #response.status_code = 201
    response = jsonify(post.to_dict())
    response.headers['Location'] = url_for('api.get_posts')
    return response


@bp.route('/user/<int:id>/posts', methods=['GET', 'POST'])
@token_auth.login_required
def new_user_post(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(user.posts, page, per_page, 'api.get_user_posts', id=id)
    return jsonify(data)
