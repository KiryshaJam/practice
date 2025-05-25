// Глобальные переменные
let allCars = [];
let currentFilters = {};
let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');

// Загрузка автомобилей при загрузке страницы
document.addEventListener('DOMContentLoaded', async () => {
    await loadCars();
    updateFilters();
    renderCars();
});

// Загрузка автомобилей с сервера
async function loadCars() {
    try {
        const response = await fetch('/api/cars');
        allCars = await response.json();
        console.log('Loaded cars:', allCars);
    } catch (error) {
        console.error('Error loading cars:', error);
    }
}

// Обновление фильтров на основе загруженных автомобилей
function updateFilters() {
    const makes = new Set(allCars.map(car => car.make));
    const models = new Set(allCars.map(car => car.model));
    const years = new Set(allCars.map(car => car.year));

    // Обновление селекта марок
    const makeSelect = document.getElementById('make');
    makeSelect.innerHTML = '<option value="">Все марки</option>';
    makes.forEach(make => {
        const option = document.createElement('option');
        option.value = make;
        option.textContent = make;
        makeSelect.appendChild(option);
    });

    // Обновление селекта моделей
    const modelSelect = document.getElementById('model');
    modelSelect.innerHTML = '<option value="">Все модели</option>';
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        modelSelect.appendChild(option);
    });

    // Обновление селекта годов
    const yearSelect = document.getElementById('year');
    yearSelect.innerHTML = '<option value="">Все годы</option>';
    years.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearSelect.appendChild(option);
    });

    // Обновление слайдера цены
    const priceSlider = document.getElementById('price');
    const maxPrice = Math.max(...allCars.map(car => car.price));
    priceSlider.max = maxPrice;
    priceSlider.value = maxPrice;
    updatePriceValue(maxPrice);
}

// Обновление отображения цены
function updatePriceValue(value) {
    const priceValue = document.getElementById('price-value');
    priceValue.textContent = `0 - ${value.toLocaleString()} ₽`;
}

// Обработчик изменения слайдера цены
document.getElementById('price').addEventListener('input', (e) => {
    updatePriceValue(parseInt(e.target.value));
});

// Обработчик применения фильтров
document.getElementById('apply-filters').addEventListener('click', () => {
    currentFilters = {
        make: document.getElementById('make').value,
        model: document.getElementById('model').value,
        year: document.getElementById('year').value,
        price_to: parseInt(document.getElementById('price').value)
    };
    renderCars();
});

// Отображение автомобилей
function renderCars() {
    const carsGrid = document.querySelector('.cars-grid');
    carsGrid.innerHTML = '';

    const filteredCars = allCars.filter(car => {
        if (currentFilters.make && car.make !== currentFilters.make) return false;
        if (currentFilters.model && car.model !== currentFilters.model) return false;
        if (currentFilters.year && car.year !== parseInt(currentFilters.year)) return false;
        if (currentFilters.price_to && car.price > currentFilters.price_to) return false;
        return true;
    });

    filteredCars.forEach(car => {
        const carCard = createCarCard(car);
        carsGrid.appendChild(carCard);
    });
}

function createCarCard(car) {
    const card = document.createElement('div');
    card.className = 'car-card';
    card.innerHTML = `
        <button class="favorite-btn${isInFavorites(car.id) ? ' active' : ''}" data-car-id="${car.id}" title="В избранное">❤</button>
        <img src="${car.image_url}" alt="${car.make} ${car.model}">
        <div class="car-card-content">
            <h3>${car.make} ${car.model}</h3>
            <div class="price">${car.price.toLocaleString()} ₽</div>
            <div class="specs">
                <div>Год: ${car.year}</div>
                <div>Тип кузова: ${car.body_type}</div>
                <div>Двигатель: ${car.engine_type}</div>
                <div>Коробка: ${car.transmission}</div>
                <div>Топливо: ${car.fuel_type}</div>
            </div>
        </div>
    `;
    
    // Добавляем обработчик для кнопки избранного
    const favoriteBtn = card.querySelector('.favorite-btn');
    favoriteBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Предотвращаем переход на страницу деталей
        toggleFavorite(car.id, favoriteBtn);
    });
    
    // Добавляем обработчик клика для перехода на страницу деталей
    card.addEventListener('click', (e) => {
        if (!e.target.closest('.favorite-btn')) {
        window.location.href = `/cars/${car.id}`;
        }
    });
    
    return card;
}

// Обработка формы добавления автомобиля
document.getElementById('addCarForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const newCar = {
        make: document.getElementById('new-make').value,
        model: document.getElementById('new-model').value,
        year: parseInt(document.getElementById('new-year').value),
        price: parseInt(document.getElementById('new-price').value),
        body_type: document.getElementById('new-body-type').value,
        engine_type: document.getElementById('new-engine').value,
        transmission: document.getElementById('new-transmission').value,
        fuel_type: document.getElementById('new-fuel').value,
        image_url: document.getElementById('new-image').value || '/static/images/cars/default.jpg'
    };
    
    try {
        const response = await fetch('/api/cars', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newCar)
        });
        
        if (response.ok) {
            // Очищаем форму
            document.getElementById('addCarForm').reset();
            
            // Перезагружаем список автомобилей
            await loadCars();
            updateFilters();
            renderCars();
            
            alert('Автомобиль успешно добавлен!');
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.error}`);
        }
    } catch (error) {
        console.error('Error adding car:', error);
        alert('Произошла ошибка при добавлении автомобиля');
    }
});

// Обработка клика по автомобилю
function showCarDetails(car) {
    const modal = document.getElementById('carDetails');
    const title = document.getElementById('carDetailsTitle');
    const image = document.getElementById('carDetailsImage');
    const power = document.getElementById('carPower');
    const acceleration = document.getElementById('carAcceleration');
    const fuelConsumption = document.getElementById('carFuelConsumption');
    const reviews = document.getElementById('carReviews');
    const crashTestFront = document.getElementById('crashTestFront');
    const crashTestSide = document.getElementById('crashTestSide');
    const crashTestRollover = document.getElementById('crashTestRollover');

    // Заполнение основной информации
    title.textContent = `${car.make} ${car.model} ${car.year}`;
    image.src = car.image_url;
    image.alt = `${car.make} ${car.model}`;

    // Заполнение технических характеристик
    if (car.specs) {
        power.textContent = `${car.specs.power} л.с.`;
        acceleration.textContent = `${car.specs.acceleration} сек`;
        fuelConsumption.textContent = `${car.specs.fuel_consumption} л/100км`;
    }

    // Заполнение отзывов
    reviews.innerHTML = '';
    if (car.reviews && car.reviews.length > 0) {
        car.reviews.forEach(review => {
            const reviewElement = document.createElement('div');
            reviewElement.className = 'review-item';
            reviewElement.innerHTML = `
                <div class="review-rating">${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}</div>
                <div class="review-text">${review.text}</div>
                <div class="review-author">${review.author}</div>
            `;
            reviews.appendChild(reviewElement);
        });
    } else {
        reviews.innerHTML = '<p>Отзывов пока нет</p>';
    }

    // Заполнение результатов краш-тестов
    if (car.crash_test) {
        crashTestFront.innerHTML = createStars(car.crash_test.front);
        crashTestSide.innerHTML = createStars(car.crash_test.side);
        crashTestRollover.innerHTML = createStars(car.crash_test.rollover);
    }

    // Показываем модальное окно
    modal.style.display = 'flex';

    // Обработчик закрытия модального окна
    const closeButton = modal.querySelector('.close');
    closeButton.onclick = () => {
        modal.style.display = 'none';
    };

    // Закрытие по клику вне модального окна
    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };
}

function createStars(rating) {
    return '★'.repeat(rating) + '☆'.repeat(5 - rating);
}

// Обновление данных
async function updateCarData() {
    try {
        const response = await fetch('/api/cars/update', {
            method: 'POST'
        });
        
        if (response.ok) {
            await loadCars();
            updateFilters();
            renderCars();
            alert('Данные успешно обновлены');
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.error}`);
        }
    } catch (error) {
        console.error('Error updating car data:', error);
        alert('Произошла ошибка при обновлении данных');
    }
}

// Получение статистики
async function getCarStats() {
    try {
        const response = await fetch('/api/cars/stats');
        if (response.ok) {
            const stats = await response.json();
            console.log('Car statistics:', stats);
            // Здесь можно добавить отображение статистики
        }
    } catch (error) {
        console.error('Error getting car stats:', error);
    }
}

// Автоматическое обновление данных каждый час
setInterval(updateCarData, 3600000); 

// Функции для работы с избранным
function toggleFavorite(carId, button) {
    const index = favorites.indexOf(carId);
    if (index === -1) {
        favorites.push(carId);
        button.classList.add('active');
    } else {
        favorites.splice(index, 1);
        button.classList.remove('active');
    }
    localStorage.setItem('favorites', JSON.stringify(favorites));
}

function isInFavorites(carId) {
    return favorites.includes(carId);
}

function updateFavoriteButtons() {
    document.querySelectorAll('.favorite-btn').forEach(btn => {
        const carId = btn.dataset.carId;
        if (isInFavorites(carId)) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
} 