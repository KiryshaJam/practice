from simple_server import app, db, Car

with app.app_context():
    print("Attempting to delete Toyota Camry and BMW 3 Series from DB...")
    num_camry_deleted = db.session.query(Car).filter(Car.make == 'Toyota', Car.model == 'Camry').delete()
    num_bmw_deleted = db.session.query(Car).filter(Car.make == 'BMW', Car.model == '3 Series').delete()
    db.session.commit()
    print(f"Deleted {num_camry_deleted} Toyota Camry cars.")
    print(f"Deleted {num_bmw_deleted} BMW 3 Series cars.")
    print("Deletion script finished.") 