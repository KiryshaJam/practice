from simple_server import app, db, Car

def check_all_cars():
    with app.app_context():
        print("\nВсе машины в базе данных:")
        cars = Car.query.all()
        if cars:
            for car in cars:
                print(f"ID: {car.id}, Make: {car.make}, Model: {car.model}, Year: {car.year}")
        else:
            print("В базе данных нет машин")

if __name__ == '__main__':
    check_all_cars() 