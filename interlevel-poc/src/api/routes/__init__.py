from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/status', methods=['GET'])
def status():
    return {'status': 'ok'}, 200
