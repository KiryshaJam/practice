from create_db import app, db, Car

def find_all_cars():
    with app.app_context():
        print("\nВсе Toyota в базе данных:")
        toyotas = Car.query.filter(Car.make.like('%Toyota%')).all()
        if toyotas:
            for car in toyotas:
                print(f"ID: {car.id}, Make: {car.make}, Model: {car.model}, Year: {car.year}")
        else:
            print("Toyota не найдены в базе данных.")

        print("\nВсе BMW в базе данных:")
        bmws = Car.query.filter(Car.make.like('%BMW%')).all()
        if bmws:
            for car in bmws:
                print(f"ID: {car.id}, Make: {car.make}, Model: {car.model}, Year: {car.year}")
        else:
            print("BMW не найдены в базе данных.")

if __name__ == '__main__':
    find_all_cars() 