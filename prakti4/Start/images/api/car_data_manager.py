from typing import Dict, List, Any
import logging
from datetime import datetime, timedelta
import requests
import json
from .base_api import BaseAPI
from .dadata_api import DadataAPI
import os
from dotenv import load_dotenv

load_dotenv()

class CarDataManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.apis: Dict[str, BaseAPI] = {}
        self.last_update = None
        self.update_interval = timedelta(hours=1)
        
        self.api_keys = {
            'dadata': os.getenv('DADATA_API_KEY', '8c70fbaff7d669cfb7dd873ca4cb42893213d598')
        }
        
        self.api_endpoints = {
            'dadata': 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest'
        }

    def register_api(self, name: str, api: BaseAPI) -> None:
        """Регистрация нового API"""
        self.apis[name] = api
        self.logger.info(f"API {name} зарегистрирован")

    def get_cars(self, **kwargs) -> List[Dict[str, Any]]:
        """Получение автомобилей из всех источников"""
        self.logger.info("Получение автомобилей с фильтрами: %s", kwargs)
        
        all_cars = []
        
        for api_name, api in self.apis.items():
            try:
                self.logger.info(f"Получение данных из {api_name}")
                cars = api.get_cars(**kwargs)
                self.logger.info(f"Получено {len(cars)} автомобилей из {api_name}")
                all_cars.extend(cars)
            except Exception as e:
                self.logger.error(f"Ошибка при получении данных из {api_name}: {e}")

        deduplicated_cars = self._deduplicate_cars(all_cars)
        self.logger.info(f"Всего уникальных автомобилей: {len(deduplicated_cars)}")
        
        return deduplicated_cars

    def update_car_data(self) -> None:
        """Обновление данных об автомобилях"""
        if self.last_update and datetime.now() - self.last_update < self.update_interval:
            self.logger.info("Данные не требуют обновления")
            return

        self.logger.info("Начало обновления данных")
        
        for api_name, api in self.apis.items():
            try:
                self.logger.info(f"Обновление данных из {api_name}")
                api.update_car_data()
            except Exception as e:
                self.logger.error(f"Ошибка при обновлении данных из {api_name}: {e}")

        self.last_update = datetime.now()
        self.logger.info("Обновление данных завершено")

    def get_car_details(self, car_id: str, source: str) -> Dict[str, Any]:
        """Получение детальной информации об автомобиле"""
        if source not in self.apis:
            raise ValueError(f"Источник {source} не найден")
        
        try:
            return self.apis[source].get_car_details(car_id)
        except Exception as e:
            self.logger.error(f"Ошибка при получении деталей автомобиля: {e}")
            raise

    def _deduplicate_cars(self, cars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Дедупликация автомобилей"""
        unique_cars = {}
        
        for car in cars:
            key = (car['make'].lower(), car['model'].lower(), car['year'])
            if key not in unique_cars:
                unique_cars[key] = car
            else:
                existing_car = unique_cars[key]
                for field in ['price', 'body_type', 'engine_type', 'transmission', 'fuel_type']:
                    if not existing_car.get(field) and car.get(field):
                        existing_car[field] = car[field]
                
                if 'images' in car and 'images' in existing_car:
                    existing_car['images'].extend(car['images'])
                elif 'images' in car:
                    existing_car['images'] = car['images']
                
                if 'reviews' in car and 'reviews' in existing_car:
                    existing_car['reviews'].extend(car['reviews'])
                elif 'reviews' in car:
                    existing_car['reviews'] = car['reviews']
                
                if 'crash_test' in car and 'crash_test' in existing_car:
                    existing_car['crash_test'].update(car['crash_test'])
                elif 'crash_test' in car:
                    existing_car['crash_test'] = car['crash_test']

        return list(unique_cars.values())

    def _fetch_car_specs(self, make: str, model: str) -> Dict[str, Any]:
        """Получение технических характеристик автомобиля"""
        try:
            response = requests.get(
                f"{self.api_endpoints['carapi']}/trims",
                params={'make': make, 'model': model},
                headers={'Authorization': f"Bearer {self.api_keys['carapi']}"}
            )
            
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            self.logger.error(f"Ошибка при получении технических характеристик: {e}")
            return []

    def _fetch_car_reviews(self, make: str, model: str) -> List[Dict[str, Any]]:
        """Получение отзывов об автомобиле"""
        try:
            return []
        except Exception as e:
            self.logger.error(f"Ошибка при получении отзывов: {e}")
            return []

    def _fetch_crash_tests(self, make: str, model: str) -> Dict[str, Any]:
        """Получение результатов краш-тестов"""
        try:
            return {}
        except Exception as e:
            self.logger.error(f"Ошибка при получении результатов краш-тестов: {e}")
            return {} 