from flask import jsonify, request, Blueprint
from app import app
from models import Post, User, db
import datetime
import os
from werkzeug.utils import secure_filename
from google.cloud import storage
from dotenv import load_dotenv, find_dotenv
import base64
import json




updatePost_blueprint = Blueprint('update_post', __name__)
# Load environment variables from .env
load_dotenv()

# Retrieve the JSON string from the environment variable
google_credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

# Parse the JSON string into a dictionary
google_credentials_dict = json.loads(google_credentials_json)

# Create a storage client using the parsed service account info
storage_client = storage.Client.from_service_account_info(google_credentials_dict)

bucket_name = 'image_storage_farmers2u'
bucket = storage_client.bucket(bucket_name)

def generate_unique_filename(filename):
    from uuid import uuid4
    # Generate a unique filename by combining a random UUID and the original filename
    unique_filename = str(uuid4()) + '_' + filename
    return unique_filename


@app.route('/api/update_post', methods=['POST'])
def update_post():
    data = request.form.to_dict()


    # Validate data
    if 'text' not in data or not data['text'] or data['text'] == 'undefined':
        return jsonify({'error': 'נא למלא את שדה הטקסט'}), 400

    if 'location' not in data or not data['location'] or data['location'] == 'undefined':
        return jsonify({'error': 'נא למלא את שדה המיקום'}), 400

    if 'date' not in data or not data['date'] :
        return jsonify({'error': 'נא למלא את שדה התאריך'}), 400

    if 'startTime' not in data or not data['startTime']:
        return jsonify({'error': 'נא למלא את שדה שעת התחלה'}), 400

    if 'endTime' not in data or not data['endTime']:
        return jsonify({'error': 'נא למלא את שדה שעת סיום'}), 400
    
    if 'email' not in data or not data['email']:
        return jsonify({'error': 'חלה תקלה. נא להתחבר לאתר מחדש.'}), 400
    

    # Validate that the location is an actual address
    if data['isRealAddress'] == "false":
        return jsonify({'error': 
                        'נא למלא כתובת מדויקת בשדה המיקום'
                        }), 400
    
    # Validate endTime > startTime
    start_time = datetime.datetime.strptime(data['startTime'], '%H:%M').time()
    end_time = datetime.datetime.strptime(data['endTime'], '%H:%M').time()
    if end_time <= start_time:
        return jsonify({'error': 'נא למלא טווח שעות תקין'}), 400
    
    # Validates the email is actually a correct email of a registered account. If it is not, then something wrong happened.
    user = User.query.filter_by(email=data['email']).first()
    if user is None:
        return jsonify({'error': 'חלה תקלה, נא להתחבר מחדש למערכת.'}), 400
    

    post_image_filename = None

    post_image = request.files.get('image')
    if post_image:
        # Check if the uploaded file is an image of JPEG or PNG format
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        if post_image.filename.split('.')[-1].lower() not in allowed_extensions:
            return jsonify({'error': 'מותר לצרף תמונות בפורמט PNG, JPEG או JPG בלבד.'}), 400
        
        post_image_filename = generate_unique_filename(secure_filename(post_image.filename))
        blob = bucket.blob(post_image_filename)
        blob.upload_from_file(post_image)
        image_url = f"https://storage.googleapis.com/{bucket_name}/{post_image_filename}"


    time_range = f"{data['endTime']}-{data['startTime']}"

    product_types = data.get('products')
    if product_types:
        product_types = product_types.split(',')

    post = Post.query.get(data['post_id'])
    if post_image:
        post.photo = image_url

    

    post.desc = data.get('text')
    post.location = data.get('location')
    if data['latitude'] != "null":
        post.latitude = data['latitude']
    if data['longitude'] != "null":
        post.longitude = data['longitude']
    post.event_date = datetime.datetime.strptime(data["date"], "%Y-%m-%d").date()
    post.time_range = time_range
    post.products = product_types
    post.isOrganic = data.get('isOrganic') == "true"
    post.isVegan = data.get('isVegan') == "true" 

    db.session.commit()

    response = {'message': 'Post updated successfully'}
    return jsonify(response), 201