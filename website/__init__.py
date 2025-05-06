from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from datetime import date

# Data base creation
db = SQLAlchemy()
DB_NAME = 'luxurydata.db'


from website import models


# Function that creates the Flask app and connects with the database
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '12312345656'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # The app's run always loads the routes and authentications
    from .views import views
    from .auth import auth

    # Registering blueprints with organized routes
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Create the database if it doesn't exist
    create_database(app)

    from .models import User
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


def create_database(app):
    with app.app_context():
        if not path.exists('website/' + DB_NAME):
            db.create_all()
            print('Created Database!')
            from .models import Vehicles

            # Check if the database already contains vehicles; if not, add them.
            if db.session.query(Vehicles).first() is None:
                vehicles_data = [{
                    # 3 cars
                    "registration": "TT-01-CL",
                    "type_vehicle": "Car",
                    "brand": "Toyota",
                    "model": "Corolla",
                    "category": "Economy",
                    "transmission": "Manual",
                    "passengers_number": 5,
                    "image": "vehicles/TT-01-CL.jpeg",
                    "price_day": 50,
                    "fuel": "Gasoline",
                    "horsepower": 132,
                    "engine_displacement": 1.8,
                    "last_maintenance": date(2023, 5, 1),
                    "next_maintenance": date(2025, 5, 1),
                    "last_inspection": date(2024, 4, 1)
                },
                    {"registration": "HD-02-CV",
                     "type_vehicle": "Car",
                     "brand": "Honda",
                     "model": "Civic",
                     "category": "Compact",
                     "transmission": "Automatic",
                     "passengers_number": 5,
                     "image": "vehicles/HD-02-CV.jpeg",
                     "price_day": 60,
                     "fuel": "Gasoline",
                     "horsepower": 158,
                     "engine_displacement": 2.0,
                     "last_maintenance": date(2024, 7, 1),
                     "next_maintenance": date(2025, 7, 1),
                     "last_inspection": date(2024, 6, 1)
                     },
                    {
                        "registration": "AD-03-AA",
                        "type_vehicle": "Car",
                        "brand": "Audi",
                        "model": "A4",
                        "category": "Luxury",
                        "transmission": "Automatic",
                        "passengers_number": 5,
                        "image": "vehicles/AD-03-AA.jpeg",
                        "price_day": 120,
                        "fuel": "Gasoline",
                        "horsepower": 220,
                        "engine_displacement": 2.0,
                        "last_maintenance": date(2024, 8, 1),
                        "next_maintenance": date(2025, 8, 1),
                        "last_inspection": date(2024, 7, 1)
                    },
                    # 2 SUVs
                    {
                        "registration": "BM-04-XV",
                        "type_vehicle": "SUV",
                        "brand": "BMW",
                        "model": "X5",
                        "category": "Luxury",
                        "transmission": "Automatic",
                        "passengers_number": 5,
                        "image": "vehicles/BM-04-XV.jpeg",
                        "price_day": 150,
                        "fuel": "Diesel",
                        "horsepower": 335,
                        "engine_displacement": 3.0,
                        "last_maintenance": date(2024, 6, 1),
                        "next_maintenance": date(2024, 6, 1),
                        "last_inspection": date(2023, 5, 1)
                    }, {
                        "registration": "RR-05-VL",
                        "type_vehicle": "SUV",
                        "brand": "Land Rover",
                        "model": "Velar",
                        "category": "Luxury",
                        "transmission": "Automatic",
                        "passengers_number": 5,
                        "image": "vehicles/LR-05-VL.jpeg",
                        "price_day": 180,
                        "fuel": "Diesel",
                        "horsepower": 380,
                        "engine_displacement": 3.0,
                        "last_maintenance": date(2024, 9, 1),
                        "next_maintenance": date(2025, 9, 1),
                        "last_inspection": date(2024, 8, 1)
                    },  # 2 Motorcycles
                    {
                        "registration": "YH-06-MT",
                        "type_vehicle": "Motorcycle",
                        "brand": "Yamaha",
                        "model": "MT-07",
                        "category": "Sport",
                        "transmission": "Manual",
                        "passengers_number": 2,
                        "image": "vehicles/YH-06-MT.jpeg",
                        "price_day": 40,
                        "fuel": "Gasoline",
                        "horsepower": 74,
                        "engine_displacement": 0.7,
                        "last_maintenance": date(2024, 4, 1),
                        "next_maintenance": date(2025, 4, 1),
                        "last_inspection": date(2024, 3, 1)
                    }, {
                        "registration": "KW-07-NJ",
                        "type_vehicle": "Motorcycle",
                        "brand": "Kawasaki",
                        "model": "Ninja ZX-6R",
                        "category": "Sport",
                        "transmission": "Manual",
                        "passengers_number": 2,
                        "image": "vehicles/KW-07-NJ.jpeg",
                        "price_day": 45,
                        "fuel": "Gasoline",
                        "horsepower": 128,
                        "engine_displacement": 0.6,
                        "last_maintenance": date(2024, 5, 1),
                        "next_maintenance": date(2025, 5, 1),
                        "last_inspection": date(2024, 4, 1)
                    },
                    # 2 Motorcycles 4 wheels
                    {
                        "registration": "CA-08-SP",
                        "type_vehicle": "Motorcycle",
                        "brand": "Can-Am",
                        "model": "Spyder F3",
                        "category": "Sport",
                        "transmission": "Automatic",
                        "passengers_number": 2,
                        "image": "vehicles/CA-08-SP.jpeg",
                        "price_day": 70,
                        "fuel": "Gasoline",
                        "horsepower": 115,
                        "engine_displacement": 0.9,
                        "last_maintenance": date(2024, 6, 1),
                        "next_maintenance": date(2025, 6, 1),
                        "last_inspection": date(2024, 5, 1)
                    },
                    {
                        "registration": "YH-09-VI",
                        "type_vehicle": "Motorcycle",
                        "brand": "Yamaha",
                        "model": "Viking VI",
                        "category": "Utility",
                        "transmission": "Automatic",
                        "passengers_number": 6,
                        "image": "vehicles/YH-09-VI.jpeg",
                        "price_day": 90,
                        "fuel": "Gasoline",
                        "horsepower": 100,
                        "engine_displacement": 1.0,
                        "last_maintenance": date(2024, 7, 1),
                        "next_maintenance": date(2025, 7, 1),
                        "last_inspection": date(2023, 6, 1)
                    },  # 3 Supercars
                    {
                        "registration": "ML-10-OS",
                        "type_vehicle": "Supercar",
                        "brand": "McLaren",
                        "model": "720S",
                        "category": "Supercar",
                        "transmission": "Automatic",
                        "passengers_number": 2,
                        "image": "vehicles/ML-10-OS.jpeg",
                        "price_day": 500,
                        "fuel": "Gasoline",
                        "horsepower": 710,
                        "engine_displacement": 4.0,
                        "last_maintenance": date(2024, 8, 1),
                        "next_maintenance": date(2025, 8, 1),
                        "last_inspection": date(2024, 7, 1)
                    },
                    {
                        "registration": "FR-11-GT",
                        "type_vehicle": "Supercar",
                        "brand": "Ferrari",
                        "model": "488 GTB",
                        "category": "Supercar",
                        "transmission": "Automatic",
                        "passengers_number": 2,
                        "image": "vehicles/FR-11-GT.jpeg",
                        "price_day": 600,
                        "fuel": "Gasoline",
                        "horsepower": 670,
                        "engine_displacement": 3.9,
                        "last_maintenance": date(2024, 9, 1),
                        "next_maintenance": date(2025, 9, 1),
                        "last_inspection": date(2024, 8, 1),
                    },
                    {
                        "registration": "LB-12-AV",
                        "type_vehicle": "Supercar",
                        "brand": "Lamborghini",
                        "model": "Aventador",
                        "category": "Supercar",
                        "transmission": "Automatic",
                        "passengers_number": 2,
                        "image": "vehicles/LB-12-AV.jpeg",
                        "price_day": 700,
                        "fuel": "Gasoline",
                        "horsepower": 730,
                        "engine_displacement": 6.5,
                        "last_maintenance": date(2023, 10, 1),
                        "next_maintenance": date(2024, 10, 1),
                        "last_inspection": date(2024, 9, 1)
                    }  # add more vehicles here if needed
                ]

                # Create Vehicle objects from dictionary data and add to the database
                for vehicle_data in vehicles_data:
                    vehicle = Vehicles(
                        registration=vehicle_data["registration"],
                        type_vehicle=vehicle_data["type_vehicle"],
                        brand=vehicle_data["brand"],
                        model=vehicle_data["model"],
                        category=vehicle_data["category"],
                        transmission=vehicle_data["transmission"],
                        passengers_number=vehicle_data["passengers_number"],
                        image=vehicle_data["image"],
                        price_day=vehicle_data["price_day"],
                        fuel=vehicle_data["fuel"],
                        horsepower=vehicle_data["horsepower"],
                        engine_displacement=vehicle_data["engine_displacement"],
                        last_maintenance=vehicle_data["last_maintenance"],
                        next_maintenance=vehicle_data["next_maintenance"],
                        last_inspection=vehicle_data["last_inspection"],
                        reserve_dates=[]
                    )
                    db.session.add(vehicle)

                db.session.commit()
                print(f'{len(vehicles_data)} vehicles added to the database!')
