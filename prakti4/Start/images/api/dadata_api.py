from .base_api import BaseAPI
from typing import Dict, List, Any
import requests
import logging

class DadataAPI(BaseAPI):
    BASE_URL = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest"
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.logger = logging.getLogger(__name__)

    def get_cars(self, **kwargs) -> List[Dict[str, Any]]:
        """Получение списка автомобилей из DaData"""
        try:
            # Получение списка марок автомобилей
            response = requests.post(
                f"{self.BASE_URL}/car_brand",
                headers=self.headers,
                json={"query": kwargs.get('make', '')}
            )
            
            if response.status_code != 200:
                self.logger.error(f"Ошибка при получении марок автомобилей: {response.status_code}")
                return []
            
            brands = response.json().get('suggestions', [])
            
            # Получение списка моделей для каждой марки
            cars = []
            for brand in brands:
                brand_name = brand.get('value', '')
                if not brand_name:
                    continue
                
                # Получение моделей для марки
                models_response = requests.post(
                    f"{self.BASE_URL}/car_model",
                    headers=self.headers,
                    json={
                        "query": kwargs.get('model', ''),
                        "filters": [{"brand": brand_name}]
                    }
                )
                
                if models_response.status_code != 200:
                    self.logger.error(f"Ошибка при получении моделей для {brand_name}: {models_response.status_code}")
                    continue
                
                models = models_response.json().get('suggestions', [])
                
                # Создание объектов автомобилей
                for model in models:
                    car = {
                        'make': brand_name,
                        'model': model.get('value', ''),
                        'year': kwargs.get('year', 2023),
                        'price': kwargs.get('price', 0),
                        'body_type': kwargs.get('body_type', ''),
                        'engine_type': kwargs.get('engine_type', ''),
                        'transmission': kwargs.get('transmission', ''),
                        'fuel_type': kwargs.get('fuel_type', ''),
                        'image_url': f"/static/images/cars/{brand_name.lower()}_{model.get('value', '').lower()}.jpg",
                        'source_id': f"dadata_{brand_name}_{model.get('value', '')}",
                        'reviews': [],
                        'crash_test': {},
                        'specs': {}
                    }
                    cars.append(car)
            
            return cars
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении автомобилей из DaData: {e}")
            return []

    def get_car_details(self, car_id: str) -> Dict[str, Any]:
        """Получение детальной информации об автомобиле"""
        try:
            # Разбор идентификатора автомобиля
            _, make, model = car_id.split('_')
            
            # Получение информации о марке
            brand_response = requests.post(
                f"{self.BASE_URL}/car_brand",
                headers=self.headers,
                json={"query": make}
            )
            
            if brand_response.status_code != 200:
                self.logger.error(f"Ошибка при получении информации о марке: {brand_response.status_code}")
                return {}
            
            brand_info = brand_response.json().get('suggestions', [{}])[0]
            
            # Получение информации о модели
            model_response = requests.post(
                f"{self.BASE_URL}/car_model",
                headers=self.headers,
                json={
                    "query": model,
                    "filters": [{"brand": make}]
                }
            )
            
            if model_response.status_code != 200:
                self.logger.error(f"Ошибка при получении информации о модели: {model_response.status_code}")
                return {}
            
            model_info = model_response.json().get('suggestions', [{}])[0]
            
            # Формирование детальной информации
            car_details = {
                'make': make,
                'model': model,
                'year': 2023,  # По умолчанию
                'price': 0,    # По умолчанию
                'body_type': brand_info.get('data', {}).get('body_type', ''),
                'engine_type': model_info.get('data', {}).get('engine_type', ''),
                'transmission': model_info.get('data', {}).get('transmission', ''),
                'fuel_type': model_info.get('data', {}).get('fuel_type', ''),
                'image_url': f"/static/images/cars/{make.lower()}_{model.lower()}.jpg",
                'source_id': car_id,
                'description': f"{make} {model} - {brand_info.get('value', '')}",
                'features': [],
                'reviews': [],
                'crash_test': {},
                'specs': {}
            }
            
            return car_details
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении деталей автомобиля из DaData: {e}")
            return {}

    def update_car_data(self) -> None:
        """Обновление данных об автомобилях"""
        try:
            self.logger.info("Обновление данных из DaData")
            # Здесь можно добавить логику обновления данных
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении данных из DaData: {e}") 