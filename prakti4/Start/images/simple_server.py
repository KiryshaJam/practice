from flask import Flask, send_from_directory, render_template, request, jsonify, flash, redirect, url_for
from flask_cors import CORS
import os
import jwt
from datetime import datetime, timedelta
from models import db, User, Criterion, Car, CarReview
from db_config import SQLALCHEMY_DATABASE_URI
import requests
import json
from sqlalchemy import and_
import time
from bs4 import BeautifulSoup
import random
from collections import defaultdict
from cars_api import get_api_manager
from api.car_data_manager import CarDataManager
from api.auto_ru_api import AutoRuAPI
from api.drom_api import DromAPI
from dotenv import load_dotenv
from api.web_scraper import AutoRuScraper
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from sqlalchemy.orm import selectinload
from api.dadata_api import DadataAPI

load_dotenv()

app = Flask(__name__, template_folder='templates')
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Секретный ключ для JWT
app.config['SECRET_KEY'] = 'your-secret-key'  # В продакшене используйте безопасный ключ

# Временное хранилище пользователей (в реальном приложении используйте базу данных)
users = {}

# Примеры API-эндпоинтов (замените на реальные)
API_ENDPOINTS = {
    'manufacturer': 'https://api.example.com/manufacturer',
    'aggregator': 'https://api.example.com/aggregator',
    'reviews': 'https://api.example.com/reviews',
    'crash_tests': 'https://api.example.com/crash_tests'
}

# Добавляем константы для API
DADATA_API_KEY = "8c70fbaff7d669cfb7dd873ca4cb42893213d598"
DADATA_API_URL = "http://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/car_brand"
NHTSA_API_URL = "https://vpic.nhtsa.dot.gov/api/vehicles"

CARAPI_KEY = "206efdd2-b95b-4c59-9e20-33e2d190272d"
CARAPI_URL = "https://carapi.app/api"

# Словарь с характеристиками по умолчанию для моделей из CarAPI.app (примерные значения, все ключи в нижнем регистре)
DEFAULT_SPECS = {
    ("toyota", "camry"): {"engine": "2.5L I4", "body": "Sedan", "transmission": "Automatic", "drivetrain": "FWD", "mileage": 0},
    ("toyota", "corolla"): {"engine": "1.8L I4", "body": "Sedan", "transmission": "CVT", "drivetrain": "FWD", "mileage": 0},
    ("toyota", "rav4"): {"engine": "2.5L I4", "body": "SUV", "transmission": "Automatic", "drivetrain": "AWD", "mileage": 0},
    ("bmw", "3 series"): {"engine": "2.0L Turbo I4", "body": "Sedan", "transmission": "Automatic", "drivetrain": "RWD", "mileage": 0},
    ("bmw", "5 series"): {"engine": "2.0L Turbo I4", "body": "Sedan", "transmission": "Automatic", "drivetrain": "RWD", "mileage": 0},
    ("mercedes-benz", "c-class"): {"engine": "2.0L Turbo I4", "body": "Sedan", "transmission": "Automatic", "drivetrain": "RWD", "mileage": 0},
    ("mercedes-benz", "e-class"): {"engine": "2.0L Turbo I4", "body": "Sedan", "transmission": "Automatic", "drivetrain": "RWD", "mileage": 0},
    ("audi", "a4"): {"engine": "2.0L Turbo I4", "body": "Sedan", "transmission": "Automatic", "drivetrain": "AWD", "mileage": 0},
    ("audi", "q5"): {"engine": "2.0L Turbo I4", "body": "SUV", "transmission": "Automatic", "drivetrain": "AWD", "mileage": 0},
    ("volkswagen", "passat"): {"engine": "2.0L Turbo I4", "body": "Sedan", "transmission": "Automatic", "drivetrain": "FWD", "mileage": 0},
    ("volkswagen", "tiguan"): {"engine": "2.0L Turbo I4", "body": "SUV", "transmission": "Automatic", "drivetrain": "AWD", "mileage": 0},
    ("kia", "rio"): {"engine": "1.6L I4", "body": "Sedan", "transmission": "Automatic", "drivetrain": "FWD", "mileage": 0},
    ("kia", "sportage"): {"engine": "2.0L I4", "body": "SUV", "transmission": "Automatic", "drivetrain": "AWD", "mileage": 0},
    ("hyundai", "solaris"): {"engine": "1.6L I4", "body": "Sedan", "transmission": "Automatic", "drivetrain": "FWD", "mileage": 0},
    ("hyundai", "tucson"): {"engine": "2.0L I4", "body": "SUV", "transmission": "Automatic", "drivetrain": "AWD", "mileage": 0},
    ("lada", "vesta"): {"engine": "1.6L I4", "body": "Sedan", "transmission": "Manual", "drivetrain": "FWD", "mileage": 0},
    ("lada", "granta"): {"engine": "1.6L I4", "body": "Sedan", "transmission": "Manual", "drivetrain": "FWD", "mileage": 0},
    ("toyota", "scion xa"): {"engine": "1.5L I4", "body": "Hatchback", "transmission": "Automatic", "drivetrain": "FWD", "mileage": 0},
    ("toyota", "scion tc"): {"engine": "2.4L I4", "body": "Coupe", "transmission": "Manual", "drivetrain": "FWD", "mileage": 0},
    # ... можно добавить другие модели по мере необходимости ...
}

FIXED_MODELS = [
    ("toyota", "corolla"),
    ("toyota", "rav4"),
    ("bmw", "5 series"),
    ("mercedes-benz", "c-class"),
    ("mercedes-benz", "e-class"),
    ("audi", "a4"),
    ("audi", "q5"),
    ("volkswagen", "passat"),
    ("volkswagen", "tiguan"),
    ("kia", "rio"),
    ("kia", "sportage"),
    ("hyundai", "solaris"),
    ("hyundai", "tucson"),
    ("lada", "vesta"),
    ("lada", "granta"),
    ("toyota", "scion xa"),
    ("bmw", "128i"),
    ("bmw", "135i"),
]

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация менеджера данных
with app.app_context():
    car_manager = CarDataManager()
    print("Initializing car_manager...")  # Отладочная информация

    # Регистрация скрапера
    auto_ru_scraper = AutoRuScraper()
    print("Created AutoRuScraper instance")  # Отладочная информация
    car_manager.register_api('auto_ru_scraper', auto_ru_scraper)
    print("Registered auto_ru_scraper API")  # Отладочная информация

    # Регистрация API
    auto_ru_api = AutoRuAPI(api_key=os.getenv('AUTO_RU_API_KEY'))
    drom_api = DromAPI(api_key=os.getenv('DROM_API_KEY'))

    car_manager.register_api('auto_ru_api', auto_ru_api)
    car_manager.register_api('drom', drom_api)

    # Проверка регистрации API
    print("Registered APIs after initialization:", car_manager.apis.keys())  # Отладочная информация

# Декоратор для обеспечения контекста приложения
def with_app_context(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        with app.app_context():
            return f(*args, **kwargs)
    return decorated_function

# --- Адаптеры для разных API ---
def fetch_from_carapi(make, model):
    try:
        headers = {"Authorization": f"Bearer {CARAPI_KEY}"}
        # Пример запроса к CarAPI.app
        response = requests.get(f"{CARAPI_URL}/trims?make={make}&model={model}", headers=headers)
        if response.status_code == 200:
            data = response.json().get("data", [])
            result = []
            for trim in data:
                result.append({
                    "make": make,
                    "model": model,
                    "year": trim.get("year", 2023),
                    "specs": {
                        "engine": trim.get("engine_type", "Unknown"),
                        "body": trim.get("body_type", "Unknown"),
                        "transmission": trim.get("transmission", "Unknown"),
                        "drivetrain": trim.get("drivetrain", "Unknown"),
                        "mileage": 0
                    },
                    "price": trim.get("msrp", 0),
                    "reviews": [],
                    "crash_test": {},
                    "images": [trim.get("image_url", "/static/images/no-image.jpg")],
                    "source": "carapi"
                })
            return result
        return []
    except Exception as e:
        print(f"CarAPI error: {e}")
        return []

def fetch_from_nhtsa(make, model):
    try:
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake/{make}?format=json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("Results", [])
            result = []
            for item in data:
                if item.get("Model_Name", "").lower() == model.lower():
                    result.append({
                        "make": make,
                        "model": model,
                        "year": 2023,
                        "specs": {},
                        "price": None,
                        "reviews": [],
                        "crash_test": {},
                        "images": [],
                        "source": "nhtsa"
                    })
            return result
        return []
    except Exception as e:
        print(f"NHTSA error: {e}")
        return []

def fetch_from_reviews_api(make, model):
    # Пример: возвращаем тестовые отзывы
    return [{
        "make": make,
        "model": model,
        "year": 2023,
        "reviews": ["Отличная машина!", "Экономичная"],
        "source": "reviews"
    }]

# --- Унификация и сопоставление ---
def normalize_car_data(car, source):
    # Привести к единому формату в зависимости от источника
    if source == "carapi":
        return car
    elif source == "nhtsa":
        return {
            "make": car["make"],
            "model": car["model"],
            "year": car.get("year", 2023),
            "specs": car.get("specs", {}),
            "price": car.get("price"),
            "reviews": car.get("reviews", []),
            "crash_test": car.get("crash_test", {}),
            "images": car.get("images", []),
        }
    elif source == "reviews":
        return {
            "make": car["make"],
            "model": car["model"],
            "year": car.get("year", 2023),
            "specs": {},
            "price": None,
            "reviews": car.get("reviews", []),
            "crash_test": {},
            "images": [],
        }
    return car

def merge_cars(car_list):
    # Сопоставление и объединение дубликатов (по make, model, year)
    merged = defaultdict(lambda: {
        "make": None, "model": None, "year": None, "specs": {}, "price": None,
        "reviews": [], "crash_test": {}, "images": []
    })
    for car in car_list:
        key = (car["make"].lower(), car["model"].lower(), car["year"])
        m = merged[key]
        m["make"] = car["make"]
        m["model"] = car["model"]
        m["year"] = car["year"]
        # Объединяем характеристики
        if car.get("specs"):
            m["specs"].update(car["specs"])
        # Объединяем отзывы
        if car.get("reviews"):
            m["reviews"].extend(car["reviews"])
        # Объединяем crash_test
        if car.get("crash_test"):
            m["crash_test"].update(car["crash_test"])
        # Объединяем изображения
        if car.get("images"):
            m["images"].extend(car["images"])
        # Цена — берём первую не None
        if m["price"] is None and car.get("price") is not None:
            m["price"] = car["price"]
    return list(merged.values())

# --- Основная функция обновления ---
def update_cars_data():
    all_raw = []
    # Пример: фиксированный список моделей
    for make, model in [
        ("Toyota", "Camry"), ("BMW", "3 Series"), ("Kia", "Rio")
    ]:
        all_raw += fetch_from_carapi(make, model)
        all_raw += fetch_from_nhtsa(make, model)
        all_raw += fetch_from_reviews_api(make, model)
    # Нормализация
    normalized = [normalize_car_data(car, car.get('source')) for car in all_raw]
    # Сопоставление и объединение
    merged = merge_cars(normalized)
    return merged

# Маршруты для статических файлов
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Маршрут для изображений автомобилей
@app.route('/static/images/<path:path>')
def send_car_images(path):
    return send_from_directory('static/images', path)

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница каталога
@app.route('/catalog')
def catalog():
    """Страница каталога автомобилей"""
    return render_template('catalog.html')

# Страница избранного
@app.route('/favorites')
def favorites():
    return render_template('favorites.html')

# Страница подбора авто
@app.route('/pairwise')
def pairwise():
    return render_template('pairwise.html')

# Страница подбора авто (альтернативный маршрут)
@app.route('/selection')
def selection():
    return render_template('pairwise.html')

# Страница авторизации
@app.route('/auth/login')
def login_page():
    return render_template('login.html')

# Страница регистрации
@app.route('/auth/register')
def register_page():
    return render_template('register.html')

# API для регистрации
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    if not email or not password:
        return jsonify({'error': 'Email и пароль обязательны'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Пользователь уже существует'}), 400
    user = User(
        username=email,
        email=email,
        first_name=first_name,
        last_name=last_name
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Пользователь успешно зарегистрирован'})

# API для входа
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        import jwt
        token = jwt.encode({
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({
            'message': 'Вход выполнен',
            'token': token,
            'user_id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
    return jsonify({'error': 'Неверный email или пароль'}), 401

# Декоратор для проверки токена и получения пользователя
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1] if ' ' in token else token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user = User.query.filter_by(email=data['email']).first()
            if not user:
                return jsonify({'error': 'User not found'}), 401
        except Exception as e:
            return jsonify({'error': 'Token is invalid'}), 401
        return f(user, *args, **kwargs)
    return decorated

# Получить профиль пользователя
@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(user):
    return jsonify({
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'usage_goals': user.get_usage_goals(),
        'budget': user.budget,
        'body_type': user.body_type,
        'fuel_type': user.fuel_type,
        'transmission': user.transmission,
        'drivetrain': user.drivetrain,
        'engine_power': user.engine_power,
        'fuel_consumption': user.fuel_consumption,
        'safety_features': user.get_safety_features(),
        'comfort_features': user.get_comfort_features(),
        'criteria': user.get_criteria(),
        'created_at': user.created_at.isoformat() if user.created_at else None
    })

# Обновить профиль пользователя
@app.route('/api/profile', methods=['POST'])
@token_required
def update_profile(user):
    data = request.json
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'usage_goals' in data:
        user.set_usage_goals(data['usage_goals'])
    if 'budget' in data:
        user.budget = int(data['budget']) if str(data['budget']).strip() else None
    if 'body_type' in data:
        user.body_type = data['body_type']
    if 'fuel_type' in data:
        user.fuel_type = data['fuel_type']
    if 'transmission' in data:
        user.transmission = data['transmission']
    if 'drivetrain' in data:
        user.drivetrain = data['drivetrain']
    if 'engine_power' in data:
        user.engine_power = int(data['engine_power']) if str(data['engine_power']).strip() else None
    if 'fuel_consumption' in data:
        user.fuel_consumption = float(data['fuel_consumption']) if str(data['fuel_consumption']).strip() else None
    if 'safety_features' in data:
        user.set_safety_features(data['safety_features'])
    if 'comfort_features' in data:
        user.set_comfort_features(data['comfort_features'])
    if 'criteria' in data:
        user.set_criteria(data['criteria'])
    from models import db
    db.session.commit()
    return jsonify({'message': 'Профиль обновлён'})

# Страница профиля
@app.route('/profile')
def profile():
    return render_template('profile.html')

# Страница отдельного автомобиля
@app.route('/cars/<int:car_id>')
def car_details(car_id):
    from models import Car
    car = Car.query.get(car_id)
    if not car:
        return render_template('car-details.html', car=None)
    return render_template('car-details.html', car=car)

@app.route('/cars', methods=['GET'])
def get_cars_list():
    all_cars = Car.query.all()
    result = []
    for car in all_cars:
        specs = car.specs or {}
        # Формируем описание в стиле: '2.5 AT | 15 000 км | Москва'
        engine = specs.get('engine', '')
        transmission = specs.get('transmission', '')
        mileage = specs.get('mileage', None)
        city = specs.get('city', '') or 'Москва'
        # Преобразуем коробку в более привычный вид
        transmission_ru = {
            'Automatic': 'AT',
            'CVT': 'CVT',
            'Manual': 'MT',
            '': ''
        }.get(transmission, transmission)
        # Формируем строку описания
        desc_parts = []
        if engine:
            desc_parts.append(engine)
        if transmission_ru:
            desc_parts.append(transmission_ru)
        if mileage is not None:
            desc_parts.append(f"{mileage:,}".replace(",", " ") + " км")
        if city:
            desc_parts.append(city)
        desc = " | ".join(desc_parts)
        result.append({
            'id': car.id,
            'make': car.make,
            'model': car.model,
            'year': car.year,
            'price': car.price,
            'specs': car.specs,
            'features': car.features,
            'reviews': car.reviews,
            'crash_test': car.crash_test,
            'description': desc,
            'images': car.images
        })
    return jsonify(result)

@app.route('/add_criterion', methods=['POST'])
def add_criterion():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404
    crit = Criterion(
        name=data['name'],
        description=data.get('description', ''),
        weight=data.get('weight', 1.0),
        user_id=user.id
    )
    db.session.add(crit)
    db.session.commit()
    return jsonify({'message': 'Критерий добавлен!'})

# API для массового добавления машин в базу (пример)
@app.route('/api/add_cars', methods=['POST'])
def add_cars():
    data = request.json
    added = []
    for car in data.get('cars', []):
        car_obj = Car(
            make=car['make'],
            model=car['model'],
            year=car['year'],
            price=car.get('price'),
            specs=car.get('specs'),
            reviews=car.get('reviews'),
            crash_test=car.get('crash_test')
        )
        db.session.add(car_obj)
        added.append(f"{car['make']} {car['model']} {car['year']}")
    db.session.commit()
    return jsonify({'added': added, 'count': len(added)})

@app.route('/api/cars', methods=['GET'])
@with_app_context
def get_cars():
    try:
        cars = Car.query.all()
        filtered = [
            car.to_dict() for car in cars
            if not (
                (car.make.lower() == 'toyota' and car.model.lower() == 'camry' and str(car.year) == '2020') or
                (car.make.lower() == 'bmw' and car.model.lower() == '3 series' and str(car.year) == '2019')
            )
        ]
        return jsonify(filtered)
    except Exception as e:
        logger.error(f"Error getting cars: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/sync', methods=['POST'])
@with_app_context
def sync_cars():
    try:
        app.api_manager.sync_all()
        return jsonify({"message": "Data synchronization completed successfully"})
    except Exception as e:
        logger.error(f"Error during synchronization: {e}")
        return jsonify({"error": "Synchronization failed"}), 500

@app.route('/api/cars/<int:car_id>', methods=['GET'])
@with_app_context
def get_car_details(car_id):
    try:
        car = app.api_manager.get_car_by_id(car_id)
        if not car:
            return jsonify({"error": "Car not found"}), 404

        # --- АВТОЗАПОЛНЕНИЕ НЕДОСТАЮЩИХ ПОЛЕЙ ---
        # Список полей, которые нужно проверять и дополнять
        FIELDS_TO_CHECK = [
            'body_type', 'engine_type', 'transmission', 'fuel_type', 'color', 'generation',
            'trim', 'tax', 'drivetrain', 'steering', 'condition', 'owners', 'pts',
            'ownership_period', 'customs', 'mileage', 'description'
        ]
        need_update = False
        missing_fields = {}
        for field in FIELDS_TO_CHECK:
            value = getattr(car, field, None)
            if not value or value == '-' or value == '—':
                missing_fields[field] = True
                need_update = True

        if need_update:
            # Пример: используем внешний API для автозаполнения (можно расширить список источников)
            dadata = DadataAPI('8c70fbaff7d669cfb7dd873ca4cb42893213d598')
            # Формируем идентификатор для поиска (например, dadata_Make_Model)
            car_id_str = f"dadata_{car.make}_{car.model}"
            api_data = dadata.get_car_details(car_id_str)
            # Обновляем только отсутствующие поля
            for field in FIELDS_TO_CHECK:
                if missing_fields.get(field) and api_data.get(field):
                    setattr(car, field, api_data[field])
            db.session.commit()

        return jsonify(car.to_dict())
    except Exception as e:
        logger.error(f"Error getting car details: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/cars', methods=['POST'])
def add_car():
    """Добавление нового автомобиля"""
    try:
        data = request.json
        print("Received car data:", data)  # Отладочная информация

        # Проверка обязательных полей
        required_fields = ['make', 'model', 'year', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Создание нового автомобиля в базе данных (без description)
        car = Car(
            make=data['make'],
            model=data['model'],
            year=data['year'],
            price=data['price'],
            body_type=data.get('body_type', ''),
            engine_type=data.get('engine_type', ''),
            transmission=data.get('transmission', ''),
            fuel_type=data.get('fuel_type', ''),
            image_url=data.get('image_url', '/static/images/cars/default.jpg'),
            description=data.get('description', '')
        )
        db.session.add(car)
        db.session.commit()

        return jsonify({
            'message': 'Car added successfully',
            'car': {
                'id': car.id,
                'make': car.make,
                'model': car.model,
                'year': car.year,
                'price': car.price,
                'body_type': car.body_type,
                'engine_type': car.engine_type,
                'transmission': car.transmission,
                'fuel_type': car.fuel_type,
                'image_url': car.image_url,
                'description': car.description
            }
        }), 201

    except Exception as e:
        logger.error(f"Ошибка при добавлении автомобиля: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/car-details')
def car_details_page():
    return render_template('car-details.html', car=None)

# Получить рекомендации на основе весов критериев
@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    weights = request.json
    try:
        # Получаем все автомобили из базы данных
        cars = Car.query.all()

        # Фильтруем нежелательные машины
        filtered_cars = [
            car for car in cars
            if not (
                (car.make.lower() == 'toyota' and car.model.lower() == 'camry' and str(car.year) == '2020') or
                (car.make.lower() == 'bmw' and car.model.lower() == '3 series' and str(car.year) == '2019')
            )
        ]

        print("cars in DB (filtered):", [(car.make, car.model, car.year, car.price) for car in filtered_cars])
        # Нормализуем веса
        total_weight = sum(weights.values())
        normalized_weights = {k: v/total_weight for k, v in weights.items()}
        print("weights:", weights)
        print("normalized_weights:", normalized_weights)
        # Рассчитываем оценки для каждого автомобиля
        car_scores = []
        for car in filtered_cars:
            criteria_scores = {
                'Цена': calculate_price_score(car.price),
                'Безопасность': calculate_safety_score(car),
                'Комфорт': calculate_comfort_score(car),
                'Экономичность': calculate_efficiency_score(car),
                'Надежность': calculate_reliability_score(car)
            }
            # Вычисляем общий балл по ключам из normalized_weights
            match_score = sum(criteria_scores.get(crit, 0) * normalized_weights.get(crit, 0) for crit in normalized_weights)
            car_scores.append({
                'id': car.id,
                'make': car.make,
                'model': car.model,
                'year': car.year,
                'price': car.price,
                'specs': {
                    'engine': car.engine_type,
                    'body': car.body_type,
                    'transmission': car.transmission,
                    'drivetrain': getattr(car, 'drivetrain', ''),
                    'mileage': getattr(car, 'mileage', None)
                },
                'images': [car.image_url] if car.image_url else [],
                'description': getattr(car, 'description', ''),
                'matchScore': match_score,
                'criteriaScores': criteria_scores
            })
        print("car_scores:", car_scores)
        # Сортируем по общему баллу
        car_scores.sort(key=lambda x: x['matchScore'], reverse=True)
        return jsonify(car_scores[:5])  # Return top 5 recommendations
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return jsonify([])

# Функции для расчета оценок по критериям
def calculate_price_score(price):
    # Чем ниже цена, тем выше оценка (от 0 до 1)
    max_price = 10000000  # Максимальная цена для нормализации
    return 1 - (price / max_price)

def calculate_safety_score(car):
    # Оценка безопасности на основе наличия систем безопасности
    score = 0.5  # Базовый балл
    if car.safety_features:
        features = car.safety_features.split(',')
        score += len(features) * 0.1  # +0.1 за каждую систему
    return min(score, 1.0)

def calculate_comfort_score(car):
    # Оценка комфорта на основе наличия опций комфорта
    score = 0.5  # Базовый балл
    if car.comfort_features:
        features = car.comfort_features.split(',')
        score += len(features) * 0.1  # +0.1 за каждую опцию
    return min(score, 1.0)

def calculate_efficiency_score(car):
    # Оценка экономичности на основе типа топлива и расхода
    score = 0.5  # Базовый балл
    if car.fuel_type == 'Электрический':
        score += 0.3
    elif car.fuel_type == 'Гибрид':
        score += 0.2
    if car.fuel_consumption:
        try:
            consumption = float(car.fuel_consumption)
            score += (10 - min(consumption, 10)) * 0.05  # +0.05 за каждый литр меньше 10
        except:
            pass
    return min(score, 1.0)

def calculate_reliability_score(car):
    # Оценка надежности на основе года выпуска и пробега
    score = 0.5  # Базовый балл
    current_year = datetime.now().year
    age = current_year - car.year
    if age <= 3:
        score += 0.3
    elif age <= 5:
        score += 0.2
    elif age <= 7:
        score += 0.1
    if car.mileage:
        try:
            mileage = float(car.mileage)
            if mileage <= 50000:
                score += 0.2
            elif mileage <= 100000:
                score += 0.1
        except:
            pass
    return min(score, 1.0)

# --- ДОБАВЛЕНИЕ 10 ФИКСИРОВАННЫХ МАШИН ПРИ СТАРТЕ ---
def add_fixed_cars():
    cars = [
        {
            "make": "Kia",
            "model": "Rio",
            "year": 2021,
            "price": 1100000,
            "specs": {
                "engine": "1.6L I4",
                "body": "Sedan",
                "transmission": "Automatic",
                "drivetrain": "FWD",
                "mileage": 15000
            },
            "images": ["/static/images/Kia_Rio_2021.jpg", "/static/images/Kia_Rio_2021_2.jpg"],
            "safety_features": "ABS,Airbags",
            "comfort_features": "Кондиционер,Электростеклоподъемники,Подогрев сидений",
            "fuel_type": "Бензин",
            "fuel_consumption": 6.2,
            "generation": "IV",
            "color": "Белый",
            "trim": "Комфорт",
            "tax": None,
            "drivetrain": "FWD",
            "steering": "Левый",
            "condition": "Отличное",
            "owners": 1,
            "pts": "Оригинал",
            "ownership_period": "Более 3 лет",
            "customs": "Растаможен",
            "description": "Надежный городской автомобиль."
        },
        {
            "make": "Hyundai",
            "model": "Solaris",
            "year": 2022,
            "price": 1200000,
            "specs": {
                "engine": "1.6L I4",
                "body": "Sedan",
                "transmission": "Automatic",
                "drivetrain": "FWD",
                "mileage": 10000
            },
            "images": ["/static/images/hyundai_solaris_2022.jpg", "/static/images/hyundai_solaris_2022_2.jpg"],
            "safety_features": "ABS,Airbags,ESP",
            "comfort_features": "Кондиционер,Электростеклоподъемники,Подогрев сидений",
            "fuel_type": "Бензин",
            "fuel_consumption": 6.0,
            "generation": "II",
            "color": "Серый",
            "trim": "Элеганс",
            "tax": None,
            "drivetrain": "FWD",
            "steering": "Левый",
            "condition": "Отличное",
            "owners": 1,
            "pts": "Оригинал",
            "ownership_period": "Менее 1 года",
            "customs": "Растаможен",
            "description": "Популярный и экономичный седан."
        },
        {
            "make": "Volkswagen",
            "model": "Passat",
            "year": 2018,
            "price": 1600000,
            "specs": {
                "engine": "2.0L Turbo I4",
                "body": "Sedan",
                "transmission": "Automatic",
                "drivetrain": "FWD",
                "mileage": 60000
            },
            "images": ["/static/images/volkswagen_passat_2018.jpg", "/static/images/volkswagen_passat_2018_2.jpg"],
            "safety_features": "ABS,ESP,Airbags,Brake Assist,Adaptive Cruise",
            "comfort_features": "Климат-контроль,Круиз-контроль,Подогрев сидений,Электропривод сидений",
            "fuel_type": "Бензин",
            "fuel_consumption": 7.2,
            "generation": "B8",
            "color": "Черный",
            "trim": "Highline",
            "tax": None,
            "drivetrain": "FWD",
            "steering": "Левый",
            "condition": "Хорошее",
            "owners": 2,
            "pts": "Оригинал",
            "ownership_period": "Более 3 лет",
            "customs": "Растаможен",
            "description": "Просторный бизнес-седан."
        },
        {
            "make": "Lada",
            "model": "Vesta",
            "year": 2021,
            "price": 900000,
            "specs": {
                "engine": "1.6L I4",
                "body": "Sedan",
                "transmission": "Manual",
                "drivetrain": "FWD",
                "mileage": 20000
            },
            "images": ["/static/images/lada_vesta_2021.jpg", "/static/images/lada_vesta_2021_2.jpg"],
            "safety_features": "ABS,Airbags",
            "comfort_features": "Кондиционер,Электростеклоподъемники",
            "fuel_type": "Бензин",
            "fuel_consumption": 7.0,
            "generation": "I",
            "color": "Синий",
            "trim": "Комфорт",
            "tax": None,
            "drivetrain": "FWD",
            "steering": "Левый",
            "condition": "Отличное",
            "owners": 1,
            "pts": "Оригинал",
            "ownership_period": "От 1 до 3 лет",
            "customs": "Растаможен",
            "description": "Современный отечественный автомобиль."
        },
        {
            "make": "Mercedes-Benz",
            "model": "C-Class",
            "year": 2022,
            "price": 2500000,
            "specs": {
                "engine": "2.0L Turbo I4",
                "body": "Sedan",
                "transmission": "Automatic",
                "drivetrain": "RWD",
                "mileage": 30000
            },
            "images": ["/static/images/Mercedes-Benz_c_class_2022.jpg", "/static/images/Mercedes-Benz_c_class_2022_2.jpg"],
            "safety_features": "ABS,ESP,Airbags,Brake Assist,Blind Spot Monitor,Adaptive Cruise",
            "comfort_features": "Климат-контроль,Круиз-контроль,Подогрев сидений,Электропривод сидений,Навигация,Панорамная крыша",
            "fuel_type": "Бензин",
            "fuel_consumption": 7.1,
            "generation": "W206",
            "color": "Белый",
            "trim": "AMG Line",
            "tax": None,
            "drivetrain": "RWD",
            "steering": "Левый",
            "condition": "Отличное",
            "owners": 1,
            "pts": "Оригинал",
            "ownership_period": "Менее 1 года",
            "customs": "Растаможен",
            "description": "Премиальный седан."
        },
        {
            "make": "Audi",
            "model": "A4",
            "year": 2019,
            "price": 2100000,
            "specs": {
                "engine": "2.0L Turbo I4",
                "body": "Sedan",
                "transmission": "Automatic",
                "drivetrain": "AWD",
                "mileage": 35000
            },
            "images": ["/static/images/audi_a4_2019.jpg", "/static/images/audi_a4 _2019_2.jpg"],
            "safety_features": "ABS,ESP,Airbags,Brake Assist,Adaptive Cruise",
            "comfort_features": "Климат-контроль,Круиз-контроль,Подогрев сидений,Электропривод сидений,Навигация",
            "fuel_type": "Бензин",
            "fuel_consumption": 6.8,
            "generation": "B9",
            "color": "Серый",
            "trim": "Business",
            "tax": None,
            "drivetrain": "AWD",
            "steering": "Левый",
            "condition": "Хорошее",
            "owners": 2,
            "pts": "Оригинал",
            "ownership_period": "От 1 до 3 лет",
            "customs": "Растаможен",
            "description": "Спортивный и элегантный седан."
        },
        {
            "make": "Kia",
            "model": "Sportage",
            "year": 2022,
            "price": 1700000,
            "specs": {
                "engine": "2.0L I4",
                "body": "SUV",
                "transmission": "Automatic",
                "drivetrain": "AWD",
                "mileage": 12000
            },
            "images": ["/static/images/kia_sportage_2022.jpg", "/static/images/kia_sportage_2022_2.jpg"],
            "safety_features": "ABS,ESP,Airbags,Brake Assist",
            "comfort_features": "Климат-контроль,Круиз-контроль,Подогрев сидений,Электростеклоподъемники",
            "fuel_type": "Бензин",
            "fuel_consumption": 7.9,
            "generation": "V",
            "color": "Красный",
            "trim": "Prestige",
            "tax": None,
            "drivetrain": "AWD",
            "steering": "Левый",
            "condition": "Отличное",
            "owners": 1,
            "pts": "Оригинал",
            "ownership_period": "Менее 1 года",
            "customs": "Растаможен",
            "description": "Популярный кроссовер для семьи и путешествий."
        },
        {
            "make": "Toyota",
            "model": "RAV4",
            "year": 2021,
            "price": 2100000,
            "specs": {
                "engine": "2.5L I4",
                "body": "SUV",
                "transmission": "Automatic",
                "drivetrain": "AWD",
                "mileage": 18000
            },
            "images": ["/static/images/toyota_rav4_2021.jpg", "/static/images/toyota_rav4_2021_2.jpg"],
            "safety_features": "ABS,ESP,Airbags,Brake Assist,Adaptive Cruise",
            "comfort_features": "Климат-контроль,Круиз-контроль,Подогрев сидений,Электропривод сидений,Навигация",
            "fuel_type": "Бензин",
            "fuel_consumption": 7.4,
            "generation": "XA50",
            "color": "Синий",
            "trim": "Престиж Safety",
            "tax": None,
            "drivetrain": "AWD",
            "steering": "Левый",
            "condition": "Отличное",
            "owners": 1,
            "pts": "Оригинал",
            "ownership_period": "От 1 до 3 лет",
            "customs": "Растаможен",
            "description": "Надежный и вместительный кроссовер."
        }
    ]

    from models import Car
    for car in cars:
        exists = Car.query.filter_by(make=car["make"], model=car["model"], year=car["year"]).first()
        if not exists:
            car_obj = Car(
                make=car["make"],
                model=car["model"],
                year=car["year"],
                price=car["price"],
                body_type=car.get("specs", {}).get("body", ""),
                engine_type=car.get("specs", {}).get("engine", ""),
                transmission=car.get("specs", {}).get("transmission", ""),
                drivetrain=car.get("specs", {}).get("drivetrain", ""),
                mileage=car.get("specs", {}).get("mileage", None),
                fuel_type=car.get("fuel_type", ""),
                image_url=car["images"][0] if car.get("images") else "/static/images/no-image.jpg",
                safety_features=car.get("safety_features", ""),
                comfort_features=car.get("comfort_features", ""),
                fuel_consumption=car.get("fuel_consumption", None),
                generation=car.get("generation", ""),
                color=car.get("color", ""),
                trim=car.get("trim", ""),
                tax=car.get("tax", None),
                steering=car.get("steering", ""),
                condition=car.get("condition", ""),
                owners=car.get("owners", None),
                pts=car.get("pts", ""),
                ownership_period=car.get("ownership_period", ""),
                customs=car.get("customs", ""),
                description=car.get("description", "")
            )
            db.session.add(car_obj)
    db.session.commit()
    all_cars = Car.query.all()
    print("Cars in DB after add_fixed_cars:", [f"{c.make} {c.model} {c.year} (ID: {c.id})" for c in all_cars])
    print("Total cars:", len(all_cars))
    print("Все id машин в базе:", [car.id for car in all_cars])

@app.route('/cars/<int:car_id>/review', methods=['POST'])
def add_review(car_id):
    # Получаем токен из заголовка
    token = request.headers.get('Authorization')
    author = None
    if token:
        try:
            token = token.split(' ')[1] if ' ' in token else token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user = User.query.filter_by(email=data['email']).first()
            if user:
                author = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email
        except Exception as e:
            pass
    if not author:
        author = request.form.get('author')
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    if not comment:
        flash('Отзыв не может быть пустым', 'error')
        return redirect(url_for('car_details', car_id=car_id))
    review = CarReview(car_id=car_id, author=author, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    flash('Отзыв успешно добавлен', 'success')
    return redirect(url_for('car_details', car_id=car_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        add_fixed_cars()
        # Добавляем обогащение данных для всех машин в базе после добавления фиксированных
        from models import Car
        from api.dadata_api import DadataAPI # Убедимся, что импорт DadataAPI доступен здесь
        print("Starting data enrichment for fixed cars...") # Отладочное сообщение
        dadata = DadataAPI('8c70fbaff7d669cfb7dd873ca4cb4293213d598') # Убедимся, что API ключ правильный

        # Проходим по всем машинам в базе данных
        all_cars_in_db = Car.query.all()
        print(f"Found {len(all_cars_in_db)} cars in the database.") # Отладочное сообщение

        FIELDS_TO_CHECK = [
            'body_type', 'engine_type', 'transmission', 'fuel_type', 'color', 'generation',
            'trim', 'tax', 'drivetrain', 'steering', 'condition', 'owners', 'pts',
            'ownership_period', 'customs', 'mileage', 'description'
        ]

        for car in all_cars_in_db:
            need_update = False
            missing_fields = {}
            for field in FIELDS_TO_CHECK:
                value = getattr(car, field, None)
                # Проверяем, отсутствует ли поле или содержит пустую строку, '-' или '—'
                if not value or str(value).strip() in ['', '-', '—', 'None']:
                    missing_fields[field] = True
                    need_update = True

            if need_update:
                try:
                    # Формируем идентификатор для поиска (например, dadata_Make_Model)
                    # Приводим make и model к нижнему регистру и заменяем пробелы на подчеркивания для URL
                    car_make_model_str = f"{car.make.lower().replace(' ', '_')}_{car.model.lower().replace(' ', '_')}"
                    car_id_str = f"dadata_{car_make_model_str}"
                    print(f"Attempting to enrich car {car.make} {car.model} (ID: {car.id}) with DadataAPI using key: {car_id_str}") # Отладочное сообщение
                    api_data = dadata.get_car_details(car_id_str)

                    if api_data:
                        print(f"Received data from DadataAPI for {car.make} {car.model}: {api_data}") # Отладочное сообщение
                        updated_fields = []
                        for field in FIELDS_TO_CHECK:
                            if missing_fields.get(field) and api_data.get(field) and str(api_data.get(field)).strip() not in ['', '-', '—', 'None']:
                                setattr(car, field, api_data[field])
                                updated_fields.append(field)
                        if updated_fields:
                             db.session.commit() # Коммитим изменения для этой машины
                             print(f"Обогащены данные для машины {car.make} {car.model} {car.year}. Обновлены поля: {', '.join(updated_fields)}")
                        else:
                            print(f"Для машины {car.make} {car.model} {car.year} нет новых данных для обогащения.")
                    else:
                         print(f"DadataAPI не вернул данные для машины {car.make} {car.model} {car.year} с ключом {car_id_str}.")

                except Exception as e:
                    print(f"Ошибка при обогащении данных для машины {car.make} {car.model} {car.year} (ID: {car.id}): {e}")

        print("Data enrichment for fixed cars completed.") # Отладочное сообщение
        app.api_manager = get_api_manager()
    app.run(debug=True, port=5001) 