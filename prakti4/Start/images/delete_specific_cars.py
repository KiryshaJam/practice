from simple_server import app, Car, db

with app.app_context():
    cars_to_delete = Car.query.filter(Car.id.in_([10, 11])).all()
    
    for car in cars_to_delete:
        print(f"Удаляем машину: {car.make} {car.model} {car.year}")
        db.session.delete(car)
    
    db.session.commit()
    print("Машины успешно удалены из базы данных.") 