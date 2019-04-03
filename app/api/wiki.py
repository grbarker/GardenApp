from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth
from flask import jsonify, request, url_for, g
from app.models import User
import wikipediaapi


@bp.route('/wiki/<query>', methods=['GET'])
@token_auth.login_required
def get_wiki(query):
    ww = wikipediaapi.Wikipedia('en')
    res = ww.page(query)
    if res.exists():
        response = [res.title, res.summary, res.text[:100]]
        return jsonify(response)
    else:
        return jsonify({ "error": "Plant does not exist"})