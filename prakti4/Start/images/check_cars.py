from create_db import app, db, Car

def check_specific_cars():
    with app.app_context():
        print("Проверка Toyota Camry 2020:")
        toyotas = Car.query.filter_by(make='Toyota', model='Camry', year=2020).all()
        if toyotas:
            for car in toyotas:
                print(f"ID: {car.id}, Make: {car.make}, Model: {car.model}, Year: {car.year}")
        else:
            print("Toyota Camry 2020 не найдена в базе данных.")

        print("\nПроверка BMW 3 Series 2019:")
        bmws = Car.query.filter_by(make='BMW', model='3 Series', year=2019).all()
        if bmws:
            for car in bmws:
                print(f"ID: {car.id}, Make: {car.make}, Model: {car.model}, Year: {car.year}")
        else:
            print("BMW 3 Series 2019 не найдена в базе данных.")

if __name__ == '__main__':
    check_specific_cars() 