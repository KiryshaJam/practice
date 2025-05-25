from .base_api import BaseAPI
from typing import Dict, List, Any
import requests
from bs4 import BeautifulSoup
import re
import random
import time

class WebScraper(BaseAPI):
    def __init__(self):
        super().__init__()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        print("WebScraper initialized")

    def _parse_price(self, text: str) -> float:
        """Парсинг цены из текста"""
        if not text:
            return 0.0
        price_str = re.sub(r'[^\d.]', '', text)
        try:
            return float(price_str)
        except ValueError:
            return 0.0

    def _parse_year(self, text: str) -> int:
        """Парсинг года из текста"""
        if not text:
            return 2023
        match = re.search(r'\d{4}', text)
        if match:
            return int(match.group())
        return 2023

    def _get_random_image(self, make: str, model: str) -> str:
        """Получение случайного изображения автомобиля"""
        return f"/static/images/cars/{make.lower()}_{model.lower()}.jpg"

    def _normalize_car_data(self, car_data: Dict[str, Any]) -> Dict[str, Any]:
        """Нормализация данных об автомобиле"""
        print("Normalizing car data:", car_data)
        normalized = {
            'make': car_data.get('make', ''),
            'model': car_data.get('model', ''),
            'year': car_data.get('year', 2023),
            'price': car_data.get('price', 0.0),
            'body_type': car_data.get('body_type', ''),
            'engine_type': car_data.get('engine_type', ''),
            'transmission': car_data.get('transmission', ''),
            'fuel_type': car_data.get('fuel_type', ''),
            'image_url': car_data.get('image_url', ''),
            'source_id': car_data.get('source_id', ''),
            'raw_data': car_data
        }
        print("Normalized data:", normalized)
        return normalized

class AutoRuScraper(WebScraper):
    BASE_URL = "https://auto.ru/cars/all"

    def get_cars(self, **kwargs) -> List[Dict[str, Any]]:
        """Получение списка автомобилей с Auto.ru"""
        self.logger.info("Получение автомобилей с Auto.ru с фильтрами: %s", kwargs)
        
        try:
            test_cars = [
                {
                    'make': 'Toyota', 'model': 'Camry', 'year': 2020, 'price': 2500000, 'body_type': 'Седан', 'engine_type': '2.5L', 'transmission': 'Автомат', 'fuel_type': 'Бензин', 'image_url': '/static/images/cars/toyota_camry.jpg', 'source_id': '1'
                },
                {
                    'make': 'Toyota', 'model': 'RAV4', 'year': 2021, 'price': 3000000, 'body_type': 'Внедорожник', 'engine_type': '2.0L', 'transmission': 'Автомат', 'fuel_type': 'Бензин', 'image_url': '/static/images/cars/toyota_rav4.jpg', 'source_id': '2'
                },
                {
                    'make': 'BMW', 'model': 'X5', 'year': 2022, 'price': 5000000, 'body_type': 'Внедорожник', 'engine_type': '3.0L', 'transmission': 'Автомат', 'fuel_type': 'Бензин', 'image_url': '/static/images/cars/bmw_x5.jpg', 'source_id': '3'
                },
                {
                    'make': 'Hyundai', 'model': 'Solaris', 'year': 2019, 'price': 1200000, 'body_type': 'Седан', 'engine_type': '1.6L', 'transmission': 'Механика', 'fuel_type': 'Бензин', 'image_url': '/static/images/cars/hyundai_solaris.jpg', 'source_id': '4'
                },
                {
                    'make': 'Kia', 'model': 'Rio', 'year': 2018, 'price': 1100000, 'body_type': 'Седан', 'engine_type': '1.6L', 'transmission': 'Автомат', 'fuel_type': 'Бензин', 'image_url': '/static/images/cars/kia_rio.jpg', 'source_id': '5'
                },
                {
                    'make': 'Volkswagen', 'model': 'Polo', 'year': 2020, 'price': 1300000, 'body_type': 'Седан', 'engine_type': '1.4L', 'transmission': 'Автомат', 'fuel_type': 'Бензин', 'image_url': '/static/images/cars/vw_polo.jpg', 'source_id': '6'
                },
                {
                    'make': 'Lada', 'model': 'Vesta', 'year': 2021, 'price': 1000000, 'body_type': 'Седан', 'engine_type': '1.6L', 'transmission': 'Механика', 'fuel_type': 'Бензин', 'image_url': '/static/images/cars/lada_vesta.jpg', 'source_id': '7'
                },
                {
                    'make': 'Audi', 'model': 'A4', 'year': 2022, 'price': 3500000, 'body_type': 'Седан', 'engine_type': '2.0L', 'transmission': 'Автомат', 'fuel_type': 'Бензин', 'image_url': '/static/images/cars/audi_a4.jpg', 'source_id': '8'
                },
                {
                    'make': 'Mercedes-Benz', 'model': 'C-Class', 'year': 2021, 'price': 4000000, 'body_type': 'Седан', 'engine_type': '2.0L', 'transmission': 'Автомат', 'fuel_type': 'Бензин', 'image_url': '/static/images/cars/mercedes_c.jpg', 'source_id': '9'
                },
                {
                    'make': 'Skoda', 'model': 'Octavia', 'year': 2020, 'price': 1700000, 'body_type': 'Лифтбек', 'engine_type': '1.4L', 'transmission': 'Автомат', 'fuel_type': 'Бензин', 'image_url': '/static/images/cars/skoda_octavia.jpg', 'source_id': '10'
                }
            ]

            filtered_cars = test_cars
            if 'make' in kwargs:
                filtered_cars = [car for car in filtered_cars if car['make'].lower() == kwargs['make'].lower()]
            if 'model' in kwargs:
                filtered_cars = [car for car in filtered_cars if car['model'].lower() == kwargs['model'].lower()]
            if 'year_from' in kwargs:
                filtered_cars = [car for car in filtered_cars if car['year'] >= kwargs['year_from']]
            if 'year_to' in kwargs:
                filtered_cars = [car for car in filtered_cars if car['year'] <= kwargs['year_to']]
            if 'price_from' in kwargs:
                filtered_cars = [car for car in filtered_cars if car['price'] >= kwargs['price_from']]
            if 'price_to' in kwargs:
                filtered_cars = [car for car in filtered_cars if car['price'] <= kwargs['price_to']]

            return [self._normalize_car_data(car) for car in filtered_cars]
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении автомобилей с Auto.ru: {e}")
            return []

    def get_car_details(self, car_id: str) -> Dict[str, Any]:
        """Получение детальной информации об автомобиле"""
        try:
            test_cars = {
                '1': {
                    'make': 'Toyota',
                    'model': 'Camry',
                    'year': 2020,
                    'price': 2500000,
                    'body_type': 'Седан',
                    'engine_type': '2.5L',
                    'transmission': 'Автомат',
                    'fuel_type': 'Бензин',
                    'image_url': '/static/images/cars/toyota_camry.jpg',
                    'source_id': '1',
                    'description': 'Отличный семейный седан с комфортным салоном и экономичным двигателем',
                    'features': ['Кожаный салон', 'Камера заднего вида', 'Круиз-контроль'],
                    'reviews': [
                        'Отличный автомобиль!',
                        'Очень доволен покупкой.'
                    ],
                    'crash_test': {
                        'nhtsa_rating': 5,
                        'euro_ncap': 5
                    },
                    'specs': {
                        'engine': '2.5L',
                        'body': 'Седан',
                        'transmission': 'Автомат',
                        'drivetrain': 'Передний',
                        'mileage': 15000
                    },
                    'images': ['/static/images/cars/toyota_camry.jpg']
                },
                '2': {
                    'make': 'Toyota',
                    'model': 'RAV4',
                    'year': 2021,
                    'price': 3000000,
                    'body_type': 'Внедорожник',
                    'engine_type': '2.0L',
                    'transmission': 'Автомат',
                    'fuel_type': 'Бензин',
                    'image_url': '/static/images/cars/toyota_rav4.jpg',
                    'source_id': '2',
                    'description': 'Надежный кроссовер для города и бездорожья',
                    'features': ['Полный привод', 'Климат-контроль'],
                    'reviews': [
                        'Хороший внедорожник',
                        'Удобен для семьи.'
                    ],
                    'crash_test': {
                        'nhtsa_rating': 5,
                        'euro_ncap': 5
                    },
                    'specs': {
                        'engine': '2.0L',
                        'body': 'Внедорожник',
                        'transmission': 'Автомат',
                        'drivetrain': 'Полный',
                        'mileage': 20000
                    },
                    'images': ['/static/images/cars/toyota_rav4.jpg']
                },
                '3': {
                    'make': 'BMW',
                    'model': 'X5',
                    'year': 2022,
                    'price': 5000000,
                    'body_type': 'Внедорожник',
                    'engine_type': '3.0L',
                    'transmission': 'Автомат',
                    'fuel_type': 'Бензин',
                    'image_url': '/static/images/cars/bmw_x5.jpg',
                    'source_id': '3',
                    'description': 'Премиальный внедорожник с отличной динамикой',
                    'features': ['Панорамная крыша', 'Премиум аудиосистема'],
                    'reviews': [
                        'Мощный и комфортный!',
                        'Лучший выбор для города и трассы.'
                    ],
                    'crash_test': {
                        'nhtsa_rating': 5,
                        'euro_ncap': 5
                    },
                    'specs': {
                        'engine': '3.0L',
                        'body': 'Внедорожник',
                        'transmission': 'Автомат',
                        'drivetrain': 'Полный',
                        'mileage': 10000
                    },
                    'images': ['/static/images/cars/bmw_x5.jpg']
                },
                '4': {
                    'make': 'Hyundai',
                    'model': 'Solaris',
                    'year': 2019,
                    'price': 1200000,
                    'body_type': 'Седан',
                    'engine_type': '1.6L',
                    'transmission': 'Механика',
                    'fuel_type': 'Бензин',
                    'image_url': '/static/images/cars/hyundai_solaris.jpg',
                    'source_id': '4',
                    'description': 'Экономичный городской седан',
                    'features': ['Кондиционер', 'Подогрев сидений'],
                    'reviews': [
                        'Очень экономичный!',
                        'Дешевое обслуживание.'
                    ],
                    'crash_test': {
                        'nhtsa_rating': 4,
                        'euro_ncap': 4
                    },
                    'specs': {
                        'engine': '1.6L',
                        'body': 'Седан',
                        'transmission': 'Механика',
                        'drivetrain': 'Передний',
                        'mileage': 35000
                    },
                    'images': ['/static/images/cars/hyundai_solaris.jpg']
                },
                '5': {
                    'make': 'Kia',
                    'model': 'Rio',
                    'year': 2018,
                    'price': 1100000,
                    'body_type': 'Седан',
                    'engine_type': '1.6L',
                    'transmission': 'Автомат',
                    'fuel_type': 'Бензин',
                    'image_url': '/static/images/cars/kia_rio.jpg',
                    'source_id': '5',
                    'description': 'Надежный и доступный седан',
                    'features': ['Обогрев зеркал', 'Bluetooth'],
                    'reviews': [
                        'Приятный в управлении.',
                        'Низкий расход топлива.'
                    ],
                    'crash_test': {
                        'nhtsa_rating': 4,
                        'euro_ncap': 4
                    },
                    'specs': {
                        'engine': '1.6L',
                        'body': 'Седан',
                        'transmission': 'Автомат',
                        'drivetrain': 'Передний',
                        'mileage': 40000
                    },
                    'images': ['/static/images/cars/kia_rio.jpg']
                },
                '6': {
                    'make': 'Volkswagen',
                    'model': 'Polo',
                    'year': 2020,
                    'price': 1300000,
                    'body_type': 'Седан',
                    'engine_type': '1.4L',
                    'transmission': 'Автомат',
                    'fuel_type': 'Бензин',
                    'image_url': '/static/images/cars/vw_polo.jpg',
                    'source_id': '6',
                    'description': 'Немецкое качество по доступной цене',
                    'features': ['ABS', 'ESP'],
                    'reviews': [
                        'Качественная сборка.',
                        'Удобный салон.'
                    ],
                    'crash_test': {
                        'nhtsa_rating': 4,
                        'euro_ncap': 5
                    },
                    'specs': {
                        'engine': '1.4L',
                        'body': 'Седан',
                        'transmission': 'Автомат',
                        'drivetrain': 'Передний',
                        'mileage': 25000
                    },
                    'images': ['/static/images/cars/vw_polo.jpg']
                },
                '7': {
                    'make': 'Lada',
                    'model': 'Vesta',
                    'year': 2021,
                    'price': 1000000,
                    'body_type': 'Седан',
                    'engine_type': '1.6L',
                    'transmission': 'Механика',
                    'fuel_type': 'Бензин',
                    'image_url': '/static/images/cars/lada_vesta.jpg',
                    'source_id': '7',
                    'description': 'Современный российский седан',
                    'features': ['ЭРА-ГЛОНАСС', 'Мультимедиа'],
                    'reviews': [
                        'Доступная цена.',
                        'Просторный салон.'
                    ],
                    'crash_test': {
                        'nhtsa_rating': 3,
                        'euro_ncap': 3
                    },
                    'specs': {
                        'engine': '1.6L',
                        'body': 'Седан',
                        'transmission': 'Механика',
                        'drivetrain': 'Передний',
                        'mileage': 5000
                    },
                    'images': ['/static/images/cars/lada_vesta.jpg']
                },
                '8': {
                    'make': 'Audi',
                    'model': 'A4',
                    'year': 2022,
                    'price': 3500000,
                    'body_type': 'Седан',
                    'engine_type': '2.0L',
                    'transmission': 'Автомат',
                    'fuel_type': 'Бензин',
                    'image_url': '/static/images/cars/audi_a4.jpg',
                    'source_id': '8',
                    'description': 'Бизнес-седан с немецким характером',
                    'features': ['LED-фары', 'Кожаный салон'],
                    'reviews': [
                        'Очень комфортный.',
                        'Динамичный разгон.'
                    ],
                    'crash_test': {
                        'nhtsa_rating': 5,
                        'euro_ncap': 5
                    },
                    'specs': {
                        'engine': '2.0L',
                        'body': 'Седан',
                        'transmission': 'Автомат',
                        'drivetrain': 'Передний',
                        'mileage': 8000
                    },
                    'images': ['/static/images/cars/audi_a4.jpg']
                },
                '9': {
                    'make': 'Mercedes-Benz',
                    'model': 'C-Class',
                    'year': 2021,
                    'price': 4000000,
                    'body_type': 'Седан',
                    'engine_type': '2.0L',
                    'transmission': 'Автомат',
                    'fuel_type': 'Бензин',
                    'image_url': '/static/images/cars/mercedes_c.jpg',
                    'source_id': '9',
                    'description': 'Элегантный и технологичный седан',
                    'features': ['Ассистент парковки', 'Премиум аудиосистема'],
                    'reviews': [
                        'Высокий уровень комфорта.',
                        'Отличная управляемость.'
                    ],
                    'crash_test': {
                        'nhtsa_rating': 5,
                        'euro_ncap': 5
                    },
                    'specs': {
                        'engine': '2.0L',
                        'body': 'Седан',
                        'transmission': 'Автомат',
                        'drivetrain': 'Задний',
                        'mileage': 12000
                    },
                    'images': ['/static/images/cars/mercedes_c.jpg']
                },
                '10': {
                    'make': 'Skoda',
                    'model': 'Octavia',
                    'year': 2020,
                    'price': 1700000,
                    'body_type': 'Лифтбек',
                    'engine_type': '1.4L',
                    'transmission': 'Автомат',
                    'fuel_type': 'Бензин',
                    'image_url': '/static/images/cars/skoda_octavia.jpg',
                    'source_id': '10',
                    'description': 'Практичный и вместительный лифтбек',
                    'features': ['Большой багажник', 'Парктроник'],
                    'reviews': [
                        'Очень вместительная.',
                        'Экономичный расход.'
                    ],
                    'crash_test': {
                        'nhtsa_rating': 5,
                        'euro_ncap': 5
                    },
                    'specs': {
                        'engine': '1.4L',
                        'body': 'Лифтбек',
                        'transmission': 'Автомат',
                        'drivetrain': 'Передний',
                        'mileage': 18000
                    },
                    'images': ['/static/images/cars/skoda_octavia.jpg']
                }
            }
            if car_id in test_cars:
                return test_cars[car_id]
            return {}
        except Exception as e:
            self.logger.error(f"Ошибка при получении деталей автомобиля с Auto.ru: {e}")
            return {}

    def update_car_data(self) -> None:
        """Обновление данных об автомобилях"""
        try:
            self.logger.info("Обновление данных с Auto.ru")
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении данных с Auto.ru: {e}") 