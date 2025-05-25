from flask import Blueprint, jsonify, request
from .car_data_manager import CarDataManager
from .dadata_api import DadataAPI
import logging

api = Blueprint('api', __name__)
car_data_manager = CarDataManager()

# Инициализация DaData API
dadata_api = DadataAPI('8c70fbaff7d669cfb7dd873ca4cb42893213d598')

# Регистрация DaData API
car_data_manager.register_api('dadata', dadata_api)

@api.route('/cars', methods=['GET'])
def get_cars():
    """Получение списка автомобилей"""
    try:
        # Получение параметров фильтрации
        filters = {
            'make': request.args.get('make'),
            'model': request.args.get('model'),
            'year_from': request.args.get('year_from', type=int),
            'year_to': request.args.get('year_to', type=int),
            'price_from': request.args.get('price_from', type=int),
            'price_to': request.args.get('price_to', type=int),
            'body_type': request.args.get('body_type'),
            'engine_type': request.args.get('engine_type'),
            'transmission': request.args.get('transmission'),
            'fuel_type': request.args.get('fuel_type')
        }
        
        # Удаление None значений
        filters = {k: v for k, v in filters.items() if v is not None}
        
        cars = car_data_manager.get_cars(**filters)
        return jsonify(cars)
    except Exception as e:
        logging.error(f"Ошибка при получении автомобилей: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/cars/<car_id>', methods=['GET'])
def get_car(car_id):
    """Получение детальной информации об автомобиле"""
    try:
        source = request.args.get('source', 'dadata')
        car = car_data_manager.get_car_details(car_id, source)
        if car:
            return jsonify(car)
        return jsonify({'error': 'Автомобиль не найден'}), 404
    except Exception as e:
        logging.error(f"Ошибка при получении деталей автомобиля: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/cars/update', methods=['POST'])
def update_cars():
    """Обновление данных об автомобилях"""
    try:
        car_data_manager.update_car_data()
        return jsonify({'message': 'Данные успешно обновлены'})
    except Exception as e:
        logging.error(f"Ошибка при обновлении данных: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/cars/stats', methods=['GET'])
def get_car_stats():
    """Получение статистики по автомобилям"""
    try:
        cars = car_data_manager.get_cars()
        
        # Статистика по маркам
        makes = {}
        for car in cars:
            make = car['make']
            if make not in makes:
                makes[make] = 0
            makes[make] += 1
        
        # Статистика по годам
        years = {}
        for car in cars:
            year = car['year']
            if year not in years:
                years[year] = 0
            years[year] += 1
        
        # Статистика по ценам
        prices = [car['price'] for car in cars]
        avg_price = sum(prices) / len(prices) if prices else 0
        
        return jsonify({
            'makes': makes,
            'years': years,
            'avg_price': avg_price,
            'total_cars': len(cars)
        })
    except Exception as e:
        logging.error(f"Ошибка при получении статистики: {e}")
        return jsonify({'error': str(e)}), 500 