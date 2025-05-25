let carsData = [];

window.carUtils = {
    getAllCars: function() {
        return carsData;
    },

    addCar: function(car) {
        car.id = Date.now().toString();
        carsData.push(car);
        return car;
    },

    getCarById: function(id) {
        return carsData.find(car => car.id === id);
    },

    deleteCar: function(id) {
        const index = carsData.findIndex(car => car.id === id);
        if (index !== -1) {
            carsData.splice(index, 1);
            return true;
        }
        return false;
    },

    filterCars: function(filters) {
        return carsData.filter(car => {
            if (filters.brand && car.brand !== filters.brand) return false;
            if (filters.category && car.category !== filters.category) return false;
            if (filters.priceMin && parseInt(car.price) < filters.priceMin) return false;
            if (filters.priceMax && parseInt(car.price) > filters.priceMax) return false;
            return true;
        });
    },

    updateCar: function(id, updatedCar) {
        const index = carsData.findIndex(car => car.id === id);
        if (index !== -1) {
            carsData[index] = { ...carsData[index], ...updatedCar };
            return carsData[index];
        }
        return null;
    },

    getSimilarCars: function(currentCar, limit = 3) {
        return carsData
        .filter(car => car.id !== currentCar.id && 
                      (car.category === currentCar.category || 
                       car.brand === currentCar.brand))
        .slice(0, limit);
    },

    getCarRecommendations: function(weights) {
    const totalWeight = Object.values(weights).reduce((sum, weight) => sum + weight, 0);
    const normalizedWeights = {};
    Object.entries(weights).forEach(([criterion, weight]) => {
        normalizedWeights[criterion] = weight / totalWeight;
    });

    const carScores = {};
    
        carsData.forEach((car, index) => {
        const criteriaScores = {
                'Цена': this.calculatePriceScore(car.price),
                'Безопасность': this.calculateSafetyScore(car),
                'Комфорт': this.calculateComfortScore(car),
                'Экономичность': this.calculateEfficiencyScore(car),
                'Надежность': this.calculateReliabilityScore(car)
        };
        
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

    calculatePriceScore: function(price) {
        const numericPrice = parseInt(price.replace(/[^\d]/g, ''));
        return Math.max(0, 1 - (numericPrice / 10000000));
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
        const maxPower = 400;
        return Math.max(0, 1 - (car.power / maxPower));
    },

    calculateReliabilityScore: function(car) {
        const maxMileage = 100000;
        return Math.max(0, 1 - (car.mileage / maxMileage));
    },

    isInFavorites: function(carId) {
        const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
        return favorites.includes(carId);
    },

    addToFavorites: function(car) {
        let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
        if (!favorites.includes(car.id)) {
            favorites.push(car.id);
            localStorage.setItem('favorites', JSON.stringify(favorites));
        }
    },

    removeFromFavorites: function(carId) {
        let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
        const index = favorites.indexOf(carId);
        if (index !== -1) {
            favorites.splice(index, 1);
            localStorage.setItem('favorites', JSON.stringify(favorites));
        }
    }
}; 