import datetime
from flask import  Blueprint, request, jsonify
from app import app
from models import Post, User
from geopy.distance import geodesic


posts_filter_blueprint = Blueprint('filter_posts', __name__)

@app.route('/api/filter_posts', methods=['POST'])
def filter_posts():
    data = request.form.to_dict()
    data['isVegan'] = data['isVegan'] == "true"
    data['isOrganic'] = data['isOrganic'] == "true"
    data['startDate'] = datetime.datetime.strptime(data["startDate"], "%Y-%m-%d").date()
    data['endDate'] = datetime.datetime.strptime(data["endDate"], "%Y-%m-%d").date()
    data['products'] = data['products'].split(',') if 'products' in data else []

    if data['startDate']> data['endDate']:
        return jsonify({'error': 'נא למלא טווח תאריכים תקין'}), 400
    
    coords_user = (data['latitude'], data['longitude'])


    if data['address'] != '':
        if data['isRealAddress'] == "false":
            return jsonify({'error': 
                            'נא למלא כתובת מדויקת בשדה המיקום או להשאיר ריק אם לא רוצים לסנן לפי כתובת'
                            }), 400
        


    """Validate the location that it is either empty string or 
    actual google api place.
    Also validate the startDate and endDate that its an actual date interval.
    """

    posts = Post.query.all()
    
    post_list = []
    for post in posts:
        user = User.query.filter_by(email=post.email).first()

        if data['isOrganic'] and not post.isOrganic:
            continue

        if data['isVegan'] and not post.isVegan:
            continue


        if post.event_date < data['startDate'] or data['endDate'] < post.event_date:
            continue

        post_products = post.products or []
        if not all(product in post_products for product in data['products']):
            continue

        if data['address'] != '' and data['isRealAddress'] != "false":
            coords_post = (post.latitude, post.longitude)
            dist = geodesic(coords_user, coords_post)
            if dist > int(data['distance']):
                continue

        post_dict = {
            'farmName': user.farm_name,
            'profilePicture': post.profilePicture,
            'photo': post.photo,
            'desc': post.desc,
            'posted': post.posted,
            'date': post.event_date.strftime('%d/%m/%Y') if post.event_date else None,
            'location': post.location,
            'when_posted_date': post.date,
            'when_posted_time': post.time,
            'id': post.id,
            'time': post.time_range,
            #BusinessCard data
            'farm_address': user.address,
            'phone': user.phone_number_official,
            'email': post.email,
            'about': user.about,
            'prices': user.products,
            'delivery_details': user.delivery_details,
            'farm_images_list': user.farm_pictures.split(','),
            'products_images_list': user.products_pictures.split(','),
            'whatsapp': user.phone_number_whatsapp,
            'instagram': user.instagram,
            'facebook': user.facebook,
            'farm_site': user.farm_site,
            'opening_hours': user.opening_hours.split(','),
            'closing_hours': user.closing_hours.split(','),
        }
        post_list.append(post_dict)


    

    # The next line ensures the posts are sorted such that the latest posts are presented first.
    post_list.sort(key=lambda post: (post['when_posted_date'], post['when_posted_time']), reverse=True)

    return jsonify(post_list)
