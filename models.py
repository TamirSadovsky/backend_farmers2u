from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from datetime import datetime
import pytz

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)
    # email = db.Column(db.String(150), nullable=True, unique=True)
    email = db.Column(db.String(150), nullable=True)
    google_profile_picture = db.Column(db.String(150))
    google_name = db.Column(db.String(150))
    google_family_name = db.Column(db.String(150))
    shipping_distance = db.Column(db.String(10))
    is_shipping = db.Column(db.String(10))
    opening_hours = db.Column(db.String(300), nullable=True)
    closing_hours = db.Column(db.String(300), nullable=True)
    logo_picture = db.Column(db.String(300), nullable=True)
    products_pictures = db.Column(db.String(1000), nullable=True)    
    farm_pictures = db.Column(db.String(1000), nullable=True)     
    farm_name = db.Column(db.String(150), nullable=True, unique=False)  # Set nullable=True for the name column
    about = db.Column(db.String(300), default='')
    phone_number_official = db.Column(db.String(20), default='')
    phone_number_whatsapp = db.Column(db.String(20), default='')
    phone_number_telegram = db.Column(db.String(20), default='')
    address = db.Column(db.String(150))
    farmer_name = db.Column(db.String(150))
    #is_organic = db.Column(db.String(10))
    #is_vegan = db.Column(db.String(10))
    delivery_details = db.Column(db.String(150))
    products = db.Column(db.String(300))
    types_of_products = db.Column(db.String(200))
    farm_site = db.Column(db.String(150), default='')
    facebook = db.Column(db.String(150), default='')
    instagram = db.Column(db.String(150), default='')


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.String(11), primary_key=True, unique=True, default=get_uuid)  # unique identifier of the post
    farmName = db.Column(db.String(150), nullable=False)   
    email = db.Column(db.String(150), nullable=False)                        
    profilePicture = db.Column(db.String(255))                                      # The logo of the farm
    photo = db.Column(db.String(255))                                               # The picture on the post
    desc = db.Column(db.String(1000))                                               # The text of the post
    date = db.Column(db.Date)                                                       # The date it was posted month/day/year              
    latitude = db.Column(db.Float)                                                  # Latitude for the distance function
    longitude = db.Column(db.Float)                                                 # Longitude for the distance function    
    location = db.Column(db.String(150))                                            # The location mentioned in the post
    time = db.Column(db.String(100))                                                # The time it was posted in hour/minute/second
    event_date = db.Column(db.Date)                                                 # The date when the event takes place
    time_range = db.Column(db.String(50))                                           # The hour range the event will take place
    products = db.Column(db.JSON, nullable=True)                                    # The list of the product types
    isOrganic = db.Column(db.Boolean, default=False)                                # Only organic stuff on the post?
    isVegan = db.Column(db.Boolean, default=False)                                  # Only vegan stuff on the post?

    ''' 
    posted explanation: How long was it since the post was posted:
    1) Less then 1 minute, then its written in seconds
    2) Less then 1 hour, then its written in minutes
    3) Less then 1 day, then its written in hours
    4) Less then a week, then its written in days
    5) More then a week, then its the date it was posted
    '''

    @property
    def posted(self):          #The initializer of the posted property
        ist = pytz.timezone('Asia/Jerusalem')   # ist = Israel timezone

        posted_datetime = datetime.strptime(self.date.strftime('%Y-%m-%d') + ' ' + self.time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=ist).replace(tzinfo=None)
        current_datetime = datetime.now(ist).replace(tzinfo=None)

        time_difference = current_datetime - posted_datetime
        time_difference_seconds = int(time_difference.total_seconds())

        if time_difference_seconds < 60:
            return f"{time_difference_seconds} שניות"
        elif time_difference_seconds < 3600:
            return f"{time_difference_seconds // 60} דק'"
        elif time_difference_seconds < 86400:
            return f"{time_difference_seconds // 3600} שעות"
        elif time_difference_seconds < 604800:
            return f"{time_difference_seconds // 86400} ימים"
        else:
            return posted_datetime.strftime('%d/%m/%Y')
