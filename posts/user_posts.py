from flask import jsonify, request, Blueprint
from app import app
from models import Post  
from models import User

userposts_blueprint = Blueprint('getuserposts', __name__)

@app.route('/api/getuserposts', methods=['POST'])
def get_user_posts():
    data = request.form.to_dict()
    user = User.query.filter_by(email=data['email']).first()
    posts = Post.query.filter_by(email=data['email']).all()
    opening_hours= user.opening_hours.split(',')
    closing_hours= user.closing_hours.split(',')

    post_list = []
    for post in posts:
        post_dict = {
            'farmName': post.farmName,
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
            'opening_hours': opening_hours,
            'closing_hours': closing_hours,
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
        }
        post_list.append(post_dict)


    post_list.sort(key=lambda post: (post['when_posted_date'], post['when_posted_time']), reverse=True)

    return jsonify(post_list), 200