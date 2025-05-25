from simple_server import app, db, Car

def add_sample_cars():
    with app.app_context():

        sample_cars_data = [
            {'make': 'Kia', 'model': 'Rio', 'year': 2021, 'price': 1100000, 'specs': {}, 'images': ['/static/images/kia_rio.jpg'], 'features': [], 'body_type': 'Седан', 'engine_type': '1.6 л / 123 л.с.', 'transmission': 'Автоматическая', 'fuel_type': 'Бензин'},
            {'make': 'Volkswagen', 'model': 'Passat', 'year': 2018, 'price': 1700000, 'specs': {}, 'images': ['/static/images/volkswagen_passat.jpg'], 'features': [], 'body_type': 'Седан', 'engine_type': '1.8 л / 180 л.с.', 'transmission': 'Автоматическая', 'fuel_type': 'Бензин'},
            {'make': 'Lada', 'model': 'Vesta', 'year': 2021, 'price': 950000, 'specs': {}, 'images': ['/static/images/lada_vesta.jpg'], 'features': [], 'body_type': 'Седан', 'engine_type': '1.6 л / 113 л.с.', 'transmission': 'Механическая', 'fuel_type': 'Бензин'},
            {'make': 'Mercedes-Benz', 'model': 'C-Class', 'year': 2020, 'price': 3200000, 'specs': {}, 'images': ['/static/images/mercedes_c_class.jpg'], 'features': [], 'body_type': 'Седан', 'engine_type': '2.0 л / 197 л.с.', 'transmission': 'Автоматическая', 'fuel_type': 'Бензин'},
            {'make': 'Audi', 'model': 'A4', 'year': 2019, 'price': 2100000, 'specs': {}, 'images': ['/static/images/audi_a4.jpg'], 'features': [], 'body_type': 'Седан', 'engine_type': '2.0 л / 190 л.с.', 'transmission': 'Автоматическая', 'fuel_type': 'Бензин'},
            {'make': 'Toyota', 'model': 'RAV4', 'year': 2021, 'price': 3000000, 'specs': {}, 'images': ['/static/images/toyota_rav4.jpg'], 'features': [], 'body_type': 'Внедорожник 5 дв.', 'engine_type': '2.5 л / 149 л.с.', 'transmission': 'Вариатор', 'fuel_type': 'Бензин'},
        ]

        for car_data in sample_cars_data:
            existing_car = Car.query.filter_by(make=car_data['make'], model=car_data['model'], year=car_data['year'], price=car_data['price']).first()
            if not existing_car:
                car = Car(
                    make=car_data['make'],
                    model=car_data['model'],
                    year=car_data['year'],
                    price=car_data['price'],
                    body_type=car_data['body_type'],
                    engine_type=car_data['engine_type'],
                    transmission=car_data['transmission'],
                    fuel_type=car_data['fuel_type']
                )
                car.specs = car_data['specs']
                car.images = car_data['images']
                car.features = car_data['features']
                db.session.add(car)

        db.session.commit()
        print("Sample cars added to the database.")

if __name__ == '__main__':
    add_sample_cars() 