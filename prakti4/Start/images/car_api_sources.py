from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Union
import requests
from datetime import datetime
from models import Car, CarSpecification, CarReview, CrashTest, APISource, db
import logging
from flask import current_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CarAPISource(ABC):
    """Базовый класс для источников данных об автомобилях"""
    
    def __init__(self, name: str, api_key: str = None):
        self.name = name
        self.api_key = api_key
        self.is_active = True
        
    @abstractmethod
    def fetch_car_data(self) -> List[Dict]:
        """Получение данных об автомобилях из API"""
        pass
        
    @abstractmethod
    def fetch_car_details(self, car_id: str) -> Optional[Dict]:
        """Получение детальной информации об автомобиле"""
        pass
        
    def normalize_car_data(self, car_data: Dict) -> Dict:
        """Нормализация данных автомобиля к единому формату"""
        return {
            'make': car_data.get('make', ''),
            'model': car_data.get('model', ''),
            'year': car_data.get('year'),
            'body_type': car_data.get('body_type'),
            'engine_type': car_data.get('engine_type'),
            'transmission': car_data.get('transmission'),
            'fuel_type': car_data.get('fuel_type'),
            'price': car_data.get('price'),
            'image_url': car_data.get('image_url'),
            'specifications': car_data.get('specifications', {}),
            'reviews': car_data.get('reviews', []),
            'crash_tests': car_data.get('crash_tests', [])
        }
        
    def save_car(self, car_data: Dict) -> Car:
        """Сохранение автомобиля в базу данных"""
        normalized_data = self.normalize_car_data(car_data)
        
        car = Car.query.filter_by(
            make=normalized_data['make'],
            model=normalized_data['model'],
            year=normalized_data['year']
        ).first()
        
        if not car:
            car = Car(**{k: v for k, v in normalized_data.items() 
                        if k not in ['specifications', 'reviews', 'crash_tests']})
            db.session.add(car)
            db.session.commit()
            
        for name, value in normalized_data['specifications'].items():
            spec = CarSpecification(
                car_id=car.id,
                name=name,
                value=str(value),
                source=self.name
            )
            db.session.add(spec)
            
        for review in normalized_data['reviews']:
            car_review = CarReview(
                car_id=car.id,
                rating=review.get('rating'),
                comment=review.get('comment'),
                source=self.name,
                author=review.get('author')
            )
            db.session.add(car_review)
            
        for crash_test in normalized_data['crash_tests']:
            test = CrashTest(
                car_id=car.id,
                organization=crash_test.get('organization'),
                rating=crash_test.get('rating'),
                year=crash_test.get('year'),
                details=crash_test.get('details')
            )
            db.session.add(test)
            
        db.session.commit()
        return car

class NHTSASource(CarAPISource):
    """Источник данных NHTSA (Национальная администрация безопасности дорожного движения)"""
    
    def __init__(self, api_key: str = None):
        super().__init__("NHTSA", api_key)
        
    def fetch_car_data(self) -> List[Dict]:
        try:
            response = requests.get(
                f"{self.api_url}/vehicles",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('results', [])
        except Exception as e:
            logger.error(f"Error fetching cars from NHTSA: {e}")
            return []
            
    def fetch_car_details(self, car_id: str) -> Optional[Dict]:
        try:
            response = requests.get(
                f"{self.api_url}/vehicles/{car_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching car details from NHTSA: {e}")
            return None

class EuroNCAPSource(CarAPISource):
    """Источник данных Euro NCAP"""
    
    def __init__(self, api_key: str = None):
        super().__init__("EuroNCAP", api_key)
        
    def fetch_car_data(self) -> List[Dict]:
        try:
            response = requests.get(
                f"{self.api_url}/vehicles",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('results', [])
        except Exception as e:
            logger.error(f"Error fetching cars from Euro NCAP: {e}")
            return []
            
    def fetch_car_details(self, car_id: str) -> Optional[Dict]:
        try:
            response = requests.get(
                f"{self.api_url}/vehicles/{car_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching car details from Euro NCAP: {e}")
            return None

class CarAPIManager:
    """Менеджер для работы с несколькими источниками данных"""
    
    def __init__(self):
        self.sources = {}
        self._init_sources()
        
    def _init_sources(self):
        """Инициализация источников данных из базы"""
        try:
            with current_app.app_context():
                api_sources = APISource.query.filter_by(is_active=True).all()
                for source in api_sources:
                    if source.name == 'NHTSA':
                        self.sources[source.id] = NHTSASource(source.api_key)
                    elif source.name == 'EuroNCAP':
                        self.sources[source.id] = EuroNCAPSource(source.api_key)
        except Exception as e:
            logger.error(f"Error initializing sources: {e}")
            raise
        
    def sync_all(self):
        """Синхронизация данных со всех источников"""
        try:
            with current_app.app_context():
                for source_id, source in self.sources.items():
                    try:
                        car_data_list = source.fetch_car_data()
                        for car_data in car_data_list:
                            source.save_car(car_data)
                            
                        api_source = APISource.query.get(source_id)
                        api_source.last_sync = datetime.utcnow()
                        db.session.commit()
                        
                        logger.info(f"Successfully synced {len(car_data_list)} cars from {source.name}")
                    except Exception as e:
                        logger.error(f"Error syncing from {source.name}: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error during sync: {e}")
            raise
        
    def get_car_by_id(self, car_id: Optional[int] = None) -> Union[Car, List[Car]]:
        """Получение автомобиля по ID или всех автомобилей"""
        try:
            with current_app.app_context():
                if car_id is not None:
                    return Car.query.get(car_id)
                return Car.query.all()
        except Exception as e:
            logger.error(f"Error getting car(s): {e}")
            raise
        
    def search_cars(self, filters: Dict) -> List[Car]:
        """Поиск автомобилей по фильтрам"""
        try:
            with current_app.app_context():
                query = Car.query
                
                if filters.get('make'):
                    query = query.filter(Car.make == filters['make'])
                if filters.get('model'):
                    query = query.filter(Car.model == filters['model'])
                if filters.get('year'):
                    query = query.filter(Car.year == filters['year'])
                if filters.get('min_price'):
                    query = query.filter(Car.price >= filters['min_price'])
                if filters.get('max_price'):
                    query = query.filter(Car.price <= filters['max_price'])
                
                return query.all()
        except Exception as e:
            logger.error(f"Error searching cars: {e}")
            raise 