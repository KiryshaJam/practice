from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Профильные поля
    usage_goals = db.Column(db.String(256))  # JSON-строка: список целей
    budget = db.Column(db.Integer)
    body_type = db.Column(db.String(32))
    fuel_type = db.Column(db.String(32))
    transmission = db.Column(db.String(32))
    drivetrain = db.Column(db.String(32))
    engine_power = db.Column(db.Integer)
    fuel_consumption = db.Column(db.Float)
    safety_features = db.Column(db.String(256))  # JSON-строка: список
    comfort_features = db.Column(db.String(256))  # JSON-строка: список
    # Критерии выбора (JSON: веса критериев)
    criteria = db.Column(db.String(512))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_criteria(self):
        return json.loads(self.criteria) if self.criteria else {}

    def set_criteria(self, criteria_dict):
        self.criteria = json.dumps(criteria_dict)

    def get_usage_goals(self):
        return json.loads(self.usage_goals) if self.usage_goals else []

    def set_usage_goals(self, goals_list):
        self.usage_goals = json.dumps(goals_list)

    def get_safety_features(self):
        return json.loads(self.safety_features) if self.safety_features else []

    def set_safety_features(self, features_list):
        self.safety_features = json.dumps(features_list)

    def get_comfort_features(self):
        return json.loads(self.comfort_features) if self.comfort_features else []

    def set_comfort_features(self, features_list):
        self.comfort_features = json.dumps(features_list)

    # Связь с критериями
    criteria_set = db.relationship('Criteria', backref='user', lazy=True)

class Criteria(db.Model):
    __tablename__ = 'criteria'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(64))
    value = db.Column(db.Float)  # Вес критерия (0-1)
    # user = db.relationship('User', backref=db.backref('criteria_set', lazy=True))

class Criterion(db.Model):
    __tablename__ = 'criterion'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    weight = db.Column(db.Float, default=1.0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связь с парными сравнениями
    comparisons = db.relationship('PairwiseComparison', backref='criterion', lazy=True)

class PairwiseComparison(db.Model):
    __tablename__ = 'pairwise_comparisons'
    
    id = db.Column(db.Integer, primary_key=True)
    criterion_id = db.Column(db.Integer, db.ForeignKey('criterion.id'), nullable=False)
    first_image = db.Column(db.String(255), nullable=False)
    second_image = db.Column(db.String(255), nullable=False)
    comparison_value = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Car(db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(64), nullable=False)
    model = db.Column(db.String(64), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float)
    body_type = db.Column(db.String(64))
    engine_type = db.Column(db.String(64))
    transmission = db.Column(db.String(64))
    fuel_type = db.Column(db.String(64))
    image_url = db.Column(db.String(256))
    # Новые поля для подбора
    safety_features = db.Column(db.String)
    comfort_features = db.Column(db.String)
    fuel_consumption = db.Column(db.Float)
    mileage = db.Column(db.Integer)
    # Новые поля для подробного описания
    color = db.Column(db.String(64))
    generation = db.Column(db.String(128))
    generation_url = db.Column(db.String(256))
    trim = db.Column(db.String(128))
    trim_url = db.Column(db.String(256))
    tax = db.Column(db.String(64))
    drivetrain = db.Column(db.String(64))
    steering = db.Column(db.String(32))
    condition = db.Column(db.String(64))
    owners = db.Column(db.String(64))
    pts = db.Column(db.String(64))
    ownership_period = db.Column(db.String(64))
    customs = db.Column(db.String(64))
    vin = db.Column(db.String(32))
    city = db.Column(db.String(64))
    dealer = db.Column(db.String(128))
    images = db.Column(db.PickleType)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи с другими таблицами
    specifications = db.relationship('CarSpecification', backref='car', lazy=True)
    reviews = db.relationship('CarReview', backref='car', lazy=True)
    crash_tests = db.relationship('CrashTest', backref='car', lazy=True)

    def to_dict(self):
        """Преобразование объекта автомобиля в словарь"""
        return {
            'id': self.id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'body_type': self.body_type,
            'engine_type': self.engine_type,
            'transmission': self.transmission,
            'fuel_type': self.fuel_type,
            'price': self.price,
            'image_url': self.image_url,
            'specifications': {spec.name: spec.value for spec in self.specifications},
            'reviews': [{
                'rating': review.rating,
                'comment': review.comment,
                'source': review.source,
                'author': review.author
            } for review in self.reviews],
            'crash_tests': [{
                'organization': test.organization,
                'rating': test.rating,
                'year': test.year,
                'details': test.details
            } for test in self.crash_tests],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CarSpecification(db.Model):
    __tablename__ = 'car_specifications'
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(200), nullable=False)
    source = db.Column(db.String(100))  # Источник данных (API)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CarReview(db.Model):
    __tablename__ = 'car_reviews'
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    rating = db.Column(db.Float)
    comment = db.Column(db.Text)
    source = db.Column(db.String(100))
    author = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CrashTest(db.Model):
    __tablename__ = 'crash_tests'
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    organization = db.Column(db.String(100))  # NCAP, IIHS и т.д.
    rating = db.Column(db.String(10))
    year = db.Column(db.Integer)
    details = db.Column(db.JSON)  # Детальные результаты тестов
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class APISource(db.Model):
    __tablename__ = 'api_sources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    api_url = db.Column(db.String(500))
    api_key = db.Column(db.String(200))
    last_sync = db.Column(db.DateTime)
    sync_interval = db.Column(db.Integer)  # в минутах
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 