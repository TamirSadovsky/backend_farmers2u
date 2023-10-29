from flask import jsonify, Blueprint

from models import User
business_blueprint = Blueprint('bussinesses', __name__)

@business_blueprint.route('/businessCard')
def send_businesses():
    users = User.query.all()
    useres_list = []
    for user in users:
        products_pictures = user.products_pictures.split(',')
        farm_pictures = user.farm_pictures.split(',')
        if user.opening_hours is not None:
            opening_hours = user.opening_hours.split(',')
        else:
            print(str(user.opening_hours))
            opening_hours = []
            print(str(user.farm_name))
        closing_hours = user.closing_hours.split(',')
        dict = {
            "id": user.id,
            "farm_name": user.farm_name,
            "logo_picture": user.logo_picture,
            "location" : user.address,
            "phone": user.phone_number_official,
            "mail": user.email,
            "about" : user.about,
            "whatsapp": user.phone_number_whatsapp,
            "instagram" : user.instagram,
            "facebook" : user.facebook,
            "products" : user.products,
            "is_shipping" : user.is_shipping,
            "shipping_distance" : user.shipping_distance,
            "products_images_list": products_pictures,
            "farm_images_list": farm_pictures,
            "farmer_name" : user.farmer_name,
            "delivery_details" : user.delivery_details,
            "farm_site": user.farm_site,
            "opening_hours": opening_hours,
            "closing_hours": closing_hours
        }
        
        useres_list.append(dict)
  
    return jsonify(useres_list)
