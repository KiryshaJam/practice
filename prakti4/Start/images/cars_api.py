from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from models import Car, APISource, db
from car_api_sources import CarAPIManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_api_manager = None

def get_api_manager():
    global _api_manager
    if _api_manager is None:
        _api_manager = CarAPIManager()
    return _api_manager

@app.get("/cars")
async def get_cars():
    """Получение списка всех автомобилей"""
    try:
        cars = Car.query.all()
        return [car.to_dict() for car in cars]
    except Exception as e:
        logger.error(f"Error getting cars: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cars/{car_id}")
async def get_car(car_id: int):
    """Получение информации об автомобиле по ID"""
    try:
        car = Car.query.get(car_id)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        return car.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting car {car_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/cars/search")
async def search_cars(
    make: Optional[str] = None,
    model: Optional[str] = None,
    year: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """Поиск автомобилей по параметрам"""
    try:
        query = Car.query
        if make:
            query = query.filter(Car.make == make)
        if model:
            query = query.filter(Car.model == model)
        if year:
            query = query.filter(Car.year == year)
        if min_price is not None:
            query = query.filter(Car.price >= min_price)
        if max_price is not None:
            query = query.filter(Car.price <= max_price)
            
        cars = query.all()
        return [car.to_dict() for car in cars]
    except Exception as e:
        logger.error(f"Error searching cars: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/sync")
async def sync_data():
    """Запуск синхронизации данных со всех источников"""
    try:
        get_api_manager().sync_all()
        return {"message": "Data synchronization completed successfully"}
    except Exception as e:
        logger.error(f"Error during synchronization: {e}")
        raise HTTPException(status_code=500, detail="Synchronization failed")

@app.get("/sources")
async def get_sources():
    """Получение списка всех источников данных"""
    try:
        sources = APISource.query.all()
        return [{
            'id': source.id,
            'name': source.name,
            'api_url': source.api_url,
            'last_sync': source.last_sync,
            'is_active': source.is_active
        } for source in sources]
    except Exception as e:
        logger.error(f"Error getting sources: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/sources")
async def add_source(source_data: Dict):
    """Добавление нового источника данных"""
    try:
        source = APISource(
            name=source_data['name'],
            api_url=source_data['api_url'],
            api_key=source_data.get('api_key'),
            sync_interval=source_data.get('sync_interval', 60),
            is_active=source_data.get('is_active', True)
        )
        db.session.add(source)
        db.session.commit()
        get_api_manager()._init_sources()
        return {"message": "Source added successfully", "source_id": source.id}
    except Exception as e:
        logger.error(f"Error adding source: {e}")
        raise HTTPException(status_code=500, detail="Failed to add source")

@app.put("/sources/{source_id}")
async def update_source(source_id: int, source_data: Dict):
    """Обновление источника данных"""
    try:
        source = APISource.query.get(source_id)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
            
        for key, value in source_data.items():
            if hasattr(source, key):
                setattr(source, key, value)
                
        db.session.commit()

        get_api_manager()._init_sources()
        
        return {"message": "Source updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating source: {e}")
        raise HTTPException(status_code=500, detail="Failed to update source")

@app.delete("/sources/{source_id}")
async def delete_source(source_id: int):
    """Удаление источника данных"""
    try:
        source = APISource.query.get(source_id)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
            
        db.session.delete(source)
        db.session.commit()
        
        get_api_manager()._init_sources()
        
        return {"message": "Source deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting source: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete source") 