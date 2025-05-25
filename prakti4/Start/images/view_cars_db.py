from simple_server import app, Car, User, db

with app.app_context():
    print("--- Содержимое таблицы 'cars' ---")
    cars = Car.query.all()
    if cars:
        for car in cars:
            print(f"ID: {car.id}, Марка: {car.make}, Модель: {car.model}, Год: {car.year}, Цена: {car.price}")
    else:
        print("Таблица 'cars' пуста.")

    print("\n--- Содержимое таблицы 'users' (первые 5 записей) ---")
    users = User.query.limit(5).all() # Ограничим вывод, чтобы не показать много пользовательских данных
    if users:
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Имя: {user.first_name}, Фамилия: {user.last_name}")
    else:
        print("Таблица 'users' пуста.") 