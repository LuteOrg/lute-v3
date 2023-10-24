import os
from flask import Blueprint, send_from_directory, current_app

bp = Blueprint('userimages', __name__, url_prefix='/userimages')

@bp.route('/<int:lgid>/<term>', methods=['GET'])
def get_image(lgid, term):
    datapath = current_app.config['DATAPATH']
    directory = os.path.join(datapath, 'userimages', str(lgid))
    filename = term + '.jpeg'
    return send_from_directory(directory, filename)
