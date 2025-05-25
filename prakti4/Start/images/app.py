from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
import json
import logging
import os
from werkzeug.utils import secure_filename
import uuid
import jwt
from datetime import datetime, timedelta
from functools import wraps
from api.routes import api

app = Flask(__name__, template_folder='templates')
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SECRET_KEY'] = 'your-secret-key'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

users = {}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = users.get(data['email'])
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalog')
def catalog():
    return render_template('catalog.html')

@app.route('/pairwise')
def pairwise():
    return render_template('pairwise.html')

@app.route('/auth/login')
def login_page():
    return render_template('login.html')

@app.route('/auth/register')
def register_page():
    return render_template('register.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/favorites')
def favorites():
    return render_template('favorites.html')

@app.route('/car-details')
def car_details():
    return render_template('car-details.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    
    if not all([email, password, first_name, last_name]):
        return jsonify({'message': 'All fields are required'}), 400
    
    if '@' not in email:
        return jsonify({'message': 'Invalid email format'}), 400
        
    if len(password) < 8:
        return jsonify({'message': 'Password must be at least 8 characters long'}), 400
    
    if email in users:
        return jsonify({'message': 'User already exists'}), 409
    
    users[email] = {
        'email': email,
        'password': password,
        'firstName': first_name,
        'lastName': last_name,
        'created_at': datetime.utcnow()
    }
    
    return jsonify({
        'message': 'User created successfully',
        'user': {
            'email': email,
            'firstName': first_name,
            'lastName': last_name
        }
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = users.get(email)
    if user and user['password'] == password:
        token = jwt.encode({
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'])
        
        return jsonify({
            'token': token,
            'email': email
        })
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        'email': current_user['email'],
        'created_at': current_user['created_at'].isoformat()
    })

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

def load_cars_data():
    try:
        with open('cars_data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            for car in data.values():
                car['images'] = [f"/static/{img}" for img in car['images']]
                car['brand_logo'] = f"/static/{car['brand'].lower()}-logo.png"
            return data
    except FileNotFoundError:
        app.logger.error("cars_data.json не найден")
        return {}
    except json.JSONDecodeError:
        app.logger.error("Ошибка при чтении cars_data.json")
        return {}

def save_cars_data(cars_data):
    try:
        data_to_save = {}
        for car_id, car in cars_data.items():
            car_copy = car.copy()
            car_copy['images'] = [img.lstrip('/') for img in car['images']]
            if 'brand_logo' in car_copy:
                del car_copy['brand_logo']
            data_to_save[car_id] = car_copy

        with open('cars_data.json', 'w', encoding='utf-8') as file:
            json.dump(data_to_save, file, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        app.logger.error(f"Ошибка при сохранении cars_data.json: {str(e)}")
        return False

@app.route('/api/cars', methods=['GET'])
def get_cars():
    cars = load_cars_data()
    return jsonify(list(cars.values()))

@app.route('/api/cars/<car_id>', methods=['GET'])
def get_car(car_id):
    cars = load_cars_data()
    car = cars.get(car_id)
    if car:
        return jsonify(car)
    return jsonify({'error': 'Автомобиль не найден'}), 404

@app.route('/api/cars', methods=['POST'])
def add_car():
    cars = load_cars_data()
    data = request.form
    files = request.files
    
    images = []
    for file in files.getlist('images'):
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            images.append(f'/static/uploads/{filename}')
    
    new_car = {
        'id': str(len(cars) + 1),
        'title': data.get('title'),
        'year': data.get('year'),
        'price': data.get('price'),
        'mileage': data.get('mileage'),
        'engine': data.get('engine'),
        'power': data.get('power'),
        'transmission': data.get('transmission'),
        'drivetrain': data.get('drivetrain'),
        'features': data.get('features', '').split(','),
        'description': data.get('description'),
        'images': images
    }
    
    cars[new_car['id']] = new_car
    if save_cars_data(cars):
        return jsonify(new_car), 201
    return jsonify({'error': 'Ошибка при сохранении данных'}), 500

@app.route('/api/cars/<car_id>', methods=['PUT'])
def update_car(car_id):
    cars = load_cars_data()
    if car_id not in cars:
        return jsonify({'error': 'Автомобиль не найден'}), 404
    
    data = request.form
    files = request.files
    
    images = []
    for file in files.getlist('images'):
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            images.append(f'/static/uploads/{filename}')
    
    car = cars[car_id]
    car.update({
        'title': data.get('title', car['title']),
        'year': data.get('year', car['year']),
        'price': data.get('price', car['price']),
        'mileage': data.get('mileage', car['mileage']),
        'engine': data.get('engine', car['engine']),
        'power': data.get('power', car['power']),
        'transmission': data.get('transmission', car['transmission']),
        'drivetrain': data.get('drivetrain', car['drivetrain']),
        'features': data.get('features', car['features']).split(','),
        'description': data.get('description', car['description']),
        'images': images if images else car['images']
    })
    
    if save_cars_data(cars):
        return jsonify(car)
    return jsonify({'error': 'Ошибка при сохранении данных'}), 500

@app.route('/api/cars/<car_id>', methods=['DELETE'])
def delete_car(car_id):
    cars = load_cars_data()
    if car_id not in cars:
        return jsonify({'error': 'Автомобиль не найден'}), 404
    
    car = cars[car_id]
    for image_path in car['images']:
        try:
            full_path = os.path.join(app.root_path, image_path.lstrip('/'))
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception as e:
            app.logger.error(f"Ошибка при удалении изображения {image_path}: {str(e)}")
    
    del cars[car_id]
    
    if save_cars_data(cars):
        return '', 204
    return jsonify({'error': 'Ошибка при сохранении данных'}), 500

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Нет файла изображения'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Не выбран файл'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        try:
            file.save(file_path)
            return jsonify({
                'path': f"/{file_path}",
                'message': 'Файл успешно загружен'
            })
        except Exception as e:
            app.logger.error(f"Ошибка при сохранении файла: {str(e)}")
            return jsonify({'error': 'Ошибка при сохранении файла'}), 500
    
    return jsonify({'error': 'Недопустимый тип файла'}), 400

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    weights = request.json
    cars = load_cars_data()
    
    total_weight = sum(weights.values())
    normalized_weights = {k: v/total_weight for k, v in weights.items()}
    
    car_scores = []
    for car_id, car in cars.items():
        criteria_scores = {
            'Цена': calculate_price_score(car['price']),
            'Безопасность': calculate_safety_score(car),
            'Комфорт': calculate_comfort_score(car),
            'Экономичность': calculate_efficiency_score(car),
            'Надежность': calculate_reliability_score(car)
        }
        
        match_score = sum(score * normalized_weights[criterion] 
                         for criterion, score in criteria_scores.items())
        
        car_scores.append({
            **car,
            'matchScore': match_score,
            'criteriaScores': criteria_scores
        })
    
    car_scores.sort(key=lambda x: x['matchScore'], reverse=True)
    return jsonify(car_scores[:5])

def calculate_price_score(price):
    price_value = int(price.replace('₽', '').replace(' ', ''))
    max_price = 6000000
    return 1 - (price_value / max_price)

def calculate_safety_score(car):
    safety_features = [
        'Система контроля слепых зон',
        'Система предотвращения столкновений',
        'Адаптивный круиз-контроль',
        'Система кругового обзора',
        'Камера заднего вида',
        'Парктроники'
    ]
    score = sum(1 for feature in safety_features if feature in car['features'])
    return score / len(safety_features)

def calculate_comfort_score(car):
    comfort_features = [
        'Климат-контроль',
        'Кожаный салон',
        'Подогрев сидений',
        'Вентиляция сидений',
        'Панорамная крыша',
        'Премиум аудиосистема'
    ]
    score = sum(1 for feature in comfort_features if feature in car['features'])
    return score / len(comfort_features)

def calculate_efficiency_score(car):
    engine_volume = float(car['engine'].split(' ')[0])
    max_volume = 3.5
    volume_score = 1 - (engine_volume / max_volume)
    
    engine_type = car['engine'].lower()
    engine_type_score = 0.9 if 'дизель' in engine_type else 0.7
    
    return (volume_score + engine_type_score) / 2

def calculate_reliability_score(car):
    score = car['rating'] / 5
    
    mileage = int(car['mileage'].replace('км', '').replace(' ', ''))
    mileage_score = 1 - (mileage / 100000)
    
    age = 2024 - int(car['year'])
    age_score = 1 - (age / 5)
    
    return (score + mileage_score + age_score) / 3

app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    app.logger.info("Запуск сервера на порту 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True) 