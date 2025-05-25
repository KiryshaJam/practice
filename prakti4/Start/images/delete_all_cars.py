from simple_server import app
from models import db, Car
 
with app.app_context():
    deleted = Car.query.delete()
    db.session.commit()
    print(f"Удалено автомобилей: {deleted}") 