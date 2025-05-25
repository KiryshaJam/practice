from .base_api import BaseAPI
from typing import Dict, List, Any
import requests

class AutoRuAPI(BaseAPI):
    BASE_URL = "https://auto.ru/api/v1"

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        })

    def get_cars(self, **kwargs) -> List[Dict[str, Any]]:
        """Получение списка автомобилей с Auto.ru"""
        params = {
            'category': 'cars',
            'page': kwargs.get('page', 1),
            'page_size': kwargs.get('page_size', 20)
        }
        
        if 'make' in kwargs:
            params['mark'] = kwargs['make']
        if 'model' in kwargs:
            params['model'] = kwargs['model']
        if 'year_from' in kwargs:
            params['year_from'] = kwargs['year_from']
        if 'year_to' in kwargs:
            params['year_to'] = kwargs['year_to']
        if 'price_from' in kwargs:
            params['price_from'] = kwargs['price_from']
        if 'price_to' in kwargs:
            params['price_to'] = kwargs['price_to']

        response = self._make_request(f"{self.BASE_URL}/offers", params=params)
        return [self._normalize_car_data(offer) for offer in response.get('offers', [])]

    def get_car_details(self, car_id: str) -> Dict[str, Any]:
        """Получение детальной информации об автомобиле"""
        response = self._make_request(f"{self.BASE_URL}/offers/{car_id}")
        return self._normalize_car_data(response) 