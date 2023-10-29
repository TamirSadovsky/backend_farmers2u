from flask import Blueprint, request, jsonify
import datetime
from models import User, Post, db
import os
import pytz
from werkzeug.utils import secure_filename
from geopy.geocoders import Nominatim
import urllib.parse
from google.cloud import storage
from dotenv import load_dotenv, find_dotenv
import base64
import json



'''
Assumption:
AddPost.jsx is supposed to use this route. It sends a POST request with
the new post made and the data is:
{
    text: ?,
    location: ?,
    date: ?,
    startTime: ?,
    endTime: ?,
    lowPrice: ?,
    highPrice: ?,
    image: ?,
}
'''
def generate_unique_filename(filename):
    from uuid import uuid4
    # Generate a unique filename by combining a random UUID and the original filename
    unique_filename = str(uuid4()) + '_' + filename
    return unique_filename


posts_blueprint = Blueprint('posts', __name__)
load_dotenv()

# Retrieve the JSON string from the environment variable
google_credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

# Parse the JSON string into a dictionary
google_credentials_dict = json.loads(google_credentials_json)

# Create a storage client using the parsed service account info
storage_client = storage.Client.from_service_account_info(google_credentials_dict)

#storage_client = storage.Client.from_service_account_json('C:\\Users\\tamir\\OneDrive\\Desktop\\GoogleWorkshop\\frontend\\keyfile.json')
bucket_name = 'image_storage_farmers2u'
bucket = storage_client.bucket(bucket_name)

@posts_blueprint.route('/api/posts', methods=['POST'])
def create_post():
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
    

    image_url = None


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




    israel_timezone = pytz.timezone('Asia/Jerusalem')  # Set the time zone to IST (Israel Standard Time)
    current_time = datetime.datetime.now(israel_timezone)
    time_range = f"{data['endTime']}-{data['startTime']}"

    product_types = data.get('products')
    if product_types:
        product_types = product_types.split(',')
    else:
        product_types = []
    
    
    new_post = Post(
        farmName = user.farm_name,
        profilePicture = user.logo_picture, #profilePicture = user.profilePicture,
        photo = image_url,
        desc = urllib.parse.unquote(data.get('text')),
        date = current_time.date(),
        time = current_time.strftime('%H:%M:%S'),
        location = data.get('location'),
        latitude = data['latitude'],
        longitude = data['longitude'],
        event_date = datetime.datetime.strptime(data["date"], "%Y-%m-%d").date(),  # Convert to date object
        time_range = time_range,
        products = product_types,
        email = data.get('email'),
        isOrganic = data.get('isOrganic') == "true",
        isVegan = data.get('isVegan') == "true",
    ) 

    db.session.add(new_post)
    db.session.commit()
    
    response = {'message': 'Post created successfully'}
    return jsonify(response), 201
