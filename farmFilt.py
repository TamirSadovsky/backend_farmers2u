from flask import Blueprint, request, jsonify
from models import User, db
# from geopy.geocoders import Nominatim
# from geopy.distance import geodesic
import googlemaps

farmfilter_blueprint = Blueprint('faFilt', __name__)

# @farmfilter_blueprint.route('/ourfarmers')
# def showAllFarmers(): = 
#     farmers = User.query.all()
#     return jsonify(farmers)

@farmfilter_blueprint.route('/farmerFilter', methods=["POST"])
def filterTheFarmers():
    # shipping = request.args.get('shipping')
    shipping = request.json['shipping']
    address = request.json['address']
    # address = request.args.get('address')
    # dist = request.args.get('distance')
    dist = request.json['distance']
    # categoriesToFilter = request.args.get('categories')
    categoriesToFilter = request.json['categories']
    products_list = ['ירקות', 'פירות','גבינות ומוצרי חלב', 'ביצים', 'דבש', 'צמחים', 'יינוץ ושמן זית', 'תבלינים', 'דגנים']
    isRealAddress = request.json['isRealAddress'] and address != ""
    print("isRealaddress: " + str(isRealAddress))
    print("address == '': " + str(address == ""))
    print("shipping: " + str(shipping))
    print("dist: " + str(dist))
    if (isRealAddress == False):
        print(dist)
        if (address == "" and shipping == False and int(dist) != 0):
            return jsonify({'error': 
                            'נא למלא את שדה הכתובת עם כתובת תקינה על מנת לסנן לפי מרחק'
                            }), 400
        if (address != ''):
            return jsonify({'error': 
                            'נא לבחור כתובת תקינה בשדה המיקום או להשאיר ריק אם לא רוצים לסנן לפי כתובת'
                            }), 400
    

    users_query = User.query
    if shipping:
        farmers = users_query.filter_by(is_shipping = True)
    else:
        farmers = users_query.all()   
    
    result = 0
    cond_dist = lambda res, distance : res <= distance
    cond_categories = lambda farmers_categories : len([c for c in farmers_categories if c in categoriesToFilter]) == len(categoriesToFilter)
    
    # if(len(categoriesToFilter) == 0):
    #     categoriesToFilter = products_list
    
    good_farmers = []
        
    for farmer in farmers:
        if address != '':
            gmaps = googlemaps.Client(key='AIzaSyAW-HDgK8fdEceybLwvRN_7wYgI_TtHmQ0')
            result = gmaps.distance_matrix(address, farmer.address)["rows"][0]["elements"][0]["distance"]["value"]
            result = result / 1000
        if cond_categories(farmer.types_of_products.split(',')):
            if (shipping and cond_dist(result, int(farmer.shipping_distance))) or (not(shipping) and cond_dist(result, int(dist))):
                products_pictures = farmer.products_pictures.split(',')
                farm_pictures = farmer.farm_pictures.split(',')
                opening_hours = farmer.opening_hours.split(',')
                closing_hours = farmer.closing_hours.split(',')
                dict = {
                        "id": farmer.id,
                        "farm_name": farmer.farm_name,
                        "logo_picture": farmer.logo_picture,
                        "location" : farmer.address,
                        "phone": farmer.phone_number_official,
                        "mail": farmer.email,
                        "about" : farmer.about,
                        "whatsapp": farmer.phone_number_whatsapp,
                        "instagram" : farmer.instagram,
                        "facebook" : farmer.facebook,
                        "products" : farmer.products,
                        "is_shipping" : farmer.is_shipping,
                        "shipping_distance" : farmer.shipping_distance,
                        "products_images_list": products_pictures,
                        "farm_images_list": farm_pictures,
                        "farmer_name" : farmer.farmer_name,
                        "delivery_details" : farmer.delivery_details,
                        "opening_hours": opening_hours,
                        "closing_hours": closing_hours
                    }
                good_farmers.append(dict)
        
    return(good_farmers)
    

   

    
        




