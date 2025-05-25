from abc import ABC, abstractmethod
import requests
from typing import Dict, List, Any
import logging

class BaseAPI(ABC):
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def get_cars(self, **kwargs) -> List[Dict[str, Any]]:
        """Получение списка автомобилей"""
        pass

    @abstractmethod
    def get_car_details(self, car_id: str) -> Dict[str, Any]:
        """Получение детальной информации об автомобиле"""
        pass

    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> Dict:
        """Базовый метод для выполнения HTTP-запросов"""
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при выполнении запроса: {e}")
            raise

    def _normalize_car_data(self, car_data: Dict) -> Dict:
        """Нормализация данных об автомобиле к единому формату"""
        normalized = {
            'source': self.__class__.__name__,
            'make': car_data.get('make', ''),
            'model': car_data.get('model', ''),
            'year': car_data.get('year', None),
            'price': car_data.get('price', None),
            'body_type': car_data.get('body_type', ''),
            'engine_type': car_data.get('engine_type', ''),
            'transmission': car_data.get('transmission', ''),
            'fuel_type': car_data.get('fuel_type', ''),
            'image_url': car_data.get('image_url', ''),
            'source_id': car_data.get('id', ''),
            'raw_data': car_data
        }
        return normalized 