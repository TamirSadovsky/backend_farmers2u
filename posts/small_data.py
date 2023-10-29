from flask import jsonify, request, Blueprint
from app import app
from models import Post  
from models import User

smalldata_blueprint = Blueprint('small_data', __name__)

@app.route('/api/small_data', methods=['POST'])
def small_data():
    data = request.form.to_dict()
    user = User.query.filter_by(email=data['email']).first()

    if user:
        small_data = { 'profilePicture': user.logo_picture, 'profileName': user.farm_name }
        return jsonify(small_data), 200
    else:
        return jsonify({}), 204
