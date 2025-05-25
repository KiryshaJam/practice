from simple_server import app, Car, User, Criterion, CarReview, db

with app.app_context():
    print("Очистка таблицы 'cars'...")
    num_deleted_cars = db.session.query(Car).delete()
    print(f"Удалено записей из 'cars': {num_deleted_cars}")

    print("Очистка таблицы 'users'...")
    num_deleted_users = db.session.query(User).delete()
    print(f"Удалено записей из 'users': {num_deleted_users}")

    print("Очистка таблицы 'criterion'...")
    num_deleted_criterion = db.session.query(Criterion).delete()
    print(f"Удалено записей из 'criterion': {num_deleted_criterion}")

    print("Очистка таблицы 'car_review'...")
    num_deleted_reviews = db.session.query(CarReview).delete()
    print(f"Удалено записей из 'car_review': {num_deleted_reviews}")

    db.session.commit()
    print("Очистка базы данных завершена.") 