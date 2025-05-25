let carsData = [];

// Создаем объект с утилитами для работы с автомобилями
window.carUtils = {
    // Функция для получения всех автомобилей
    getAllCars: function() {
        return carsData;
    },

    // Функция для добавления нового автомобиля
    addCar: function(car) {
        car.id = Date.now().toString(); // Генерируем уникальный ID
        carsData.push(car);
        return car;
    },

    // Функция для получения автомобиля по ID
    getCarById: function(id) {
        return carsData.find(car => car.id === id);
    },

    // Функция для удаления автомобиля
    deleteCar: function(id) {
        const index = carsData.findIndex(car => car.id === id);
        if (index !== -1) {
            carsData.splice(index, 1);
            return true;
        }
        return false;
    },

    // Функция для фильтрации автомобилей
    filterCars: function(filters) {
        return carsData.filter(car => {
            if (filters.brand && car.brand !== filters.brand) return false;
            if (filters.category && car.category !== filters.category) return false;
            if (filters.priceMin && parseInt(car.price) < filters.priceMin) return false;
            if (filters.priceMax && parseInt(car.price) > filters.priceMax) return false;
            return true;
        });
    },

    // Функция для обновления данных автомобиля
    updateCar: function(id, updatedCar) {
        const index = carsData.findIndex(car => car.id === id);
        if (index !== -1) {
            carsData[index] = { ...carsData[index], ...updatedCar };
            return carsData[index];
        }
        return null;
    },

// Функция для получения похожих автомобилей
    getSimilarCars: function(currentCar, limit = 3) {
        return carsData
        .filter(car => car.id !== currentCar.id && 
                      (car.category === currentCar.category || 
                       car.brand === currentCar.brand))
        .slice(0, limit);
    },

// Функция для получения рекомендаций на основе весов критериев
    getCarRecommendations: function(weights) {
    // Нормализуем веса (сумма должна быть равна 1)
    const totalWeight = Object.values(weights).reduce((sum, weight) => sum + weight, 0);
    const normalizedWeights = {};
    Object.entries(weights).forEach(([criterion, weight]) => {
        normalizedWeights[criterion] = weight / totalWeight;
    });

    // Оценки автомобилей по критериям (от 0 до 1)
    const carScores = {};
    
        carsData.forEach((car, index) => {
        const criteriaScores = {
                'Цена': this.calculatePriceScore(car.price),
                'Безопасность': this.calculateSafetyScore(car),
                'Комфорт': this.calculateComfortScore(car),
                'Экономичность': this.calculateEfficiencyScore(car),
                'Надежность': this.calculateReliabilityScore(car)
        };
        
        // Вычисляем общий балл автомобиля
        const matchScore = Object.entries(normalizedWeights).reduce((score, [criterion, weight]) => {
            return score + (criteriaScores[criterion] * weight);
        }, 0);
        
            carScores[car.id] = {
            ...car,
            matchScore,
            criteriaScores
        };
    });
    
        return Object.values(carScores).sort((a, b) => b.matchScore - a.matchScore);
    },

    // Вспомогательные функции для расчета оценок
    calculatePriceScore: function(price) {
        const numericPrice = parseInt(price.replace(/[^\d]/g, ''));
        return Math.max(0, 1 - (numericPrice / 10000000)); // Максимальная цена 10 млн
    },

    calculateSafetyScore: function(car) {
    const safetyFeatures = [
        'Камера заднего вида',
            'Парктроники',
            'Круиз-контроль'
    ];
    
        const score = car.features.reduce((total, feature) => {
            return total + (safetyFeatures.includes(feature) ? 1 : 0);
        }, 0);
    
    return score / safetyFeatures.length;
    },

    calculateComfortScore: function(car) {
    const comfortFeatures = [
        'Климат-контроль',
            'Кондиционер',
        'Кожаный салон',
            'Подогрев сидений'
    ];
    
        const score = car.features.reduce((total, feature) => {
            return total + (comfortFeatures.includes(feature) ? 1 : 0);
        }, 0);
    
    return score / comfortFeatures.length;
    },

    calculateEfficiencyScore: function(car) {
        // Простая оценка на основе мощности двигателя
        // Предполагаем, что менее мощные двигатели более экономичны
        const maxPower = 400; // Максимальная мощность для нормализации
        return Math.max(0, 1 - (car.power / maxPower));
    },

    calculateReliabilityScore: function(car) {
        // Простая оценка на основе пробега
        const maxMileage = 100000; // Максимальный пробег для нормализации
        return Math.max(0, 1 - (car.mileage / maxMileage));
    },

    // Проверка, находится ли автомобиль в избранном
    isInFavorites: function(carId) {
        const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
        return favorites.includes(carId);
    },

    // Добавление в избранное
    addToFavorites: function(car) {
        let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
        if (!favorites.includes(car.id)) {
            favorites.push(car.id);
            localStorage.setItem('favorites', JSON.stringify(favorites));
        }
    },

    // Удаление из избранного
    removeFromFavorites: function(carId) {
        let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
        const index = favorites.indexOf(carId);
        if (index !== -1) {
            favorites.splice(index, 1);
            localStorage.setItem('favorites', JSON.stringify(favorites));
        }
    }
}; 