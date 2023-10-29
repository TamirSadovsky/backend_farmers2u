from flask import jsonify, request, Blueprint
from app import app
from models import User

getprofile_blueprint = Blueprint('get_profile', __name__)

@app.route('/api/get_profile', methods=['POST'])
def get_profile():
    data = request.form.to_dict()
    user = User.query.filter_by(email=data['email']).first()
    
    if user:
        logo = user.logo_picture
        farmName = user.farm_name
        return jsonify({'logo': logo, 'farmName': farmName}), 200
    else:
        return jsonify({'error': 'חלה תקלה, נא להתחבר מחדש למערכת.'}), 404
