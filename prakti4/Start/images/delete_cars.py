from create_db import app, db, Car

def delete_specific_cars():
with app.app_context():
        deleted_toyota_count = Car.query.filter(Car.make == 'Toyota', Car.model == 'Camry', Car.year == 2020).delete()
        print(f"Удалено Toyota Camry 2020: {deleted_toyota_count}")
        
        deleted_bmw_count = Car.query.filter(Car.make == 'BMW', Car.model == '3 Series', Car.year == 2019).delete()
        print(f"Удалено BMW 3 Series 2019: {deleted_bmw_count}")
        
    db.session.commit()
        print("Операция удаления завершена")

if __name__ == '__main__':
    delete_specific_cars() 