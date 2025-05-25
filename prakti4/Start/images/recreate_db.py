from models import db
from simple_server import app

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Таблицы пересозданы!") 