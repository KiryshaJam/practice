// car-details.js

function getCarIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

async function loadCarDetails() {
    const carId = getCarIdFromUrl();
    if (!carId) {
        document.getElementById('car-title').textContent = 'Автомобиль не найден';
        return;
    }

    try {
        const response = await fetch(`/api/cars/${carId}`);
        if (!response.ok) throw new Error('Ошибка загрузки данных');
        const car = await response.json();

        document.getElementById('car-title').textContent = `${car.make} ${car.model} (${car.year})`;
        document.getElementById('car-image').src = car.image_url || '/static/images/default-car.png';
        document.getElementById('car-image').alt = `${car.make} ${car.model}`;

        document.getElementById('body-type').textContent = car.body_type || '-';
        document.getElementById('engine-type').textContent = car.engine_type || '-';
        document.getElementById('transmission').textContent = car.transmission || '-';
        document.getElementById('fuel-type').textContent = car.fuel_type || '-';
        document.getElementById('year').textContent = car.year || '-';
        document.getElementById('price').textContent = car.price ? car.price + ' ₽' : '-';
        document.getElementById('description').textContent = car.description || '-';

        // Краш-тесты
        let nhtsa = '-';
        let euro = '-';
        if (car.crash_tests && car.crash_tests.length) {
            for (const test of car.crash_tests) {
                if (test.organization === 'NHTSA') nhtsa = test.rating;
                if (test.organization === 'Euro NCAP') euro = test.rating;
            }
        }
        document.getElementById('nhtsa-rating').textContent = nhtsa;
        document.getElementById('euro-ncap-rating').textContent = euro;

        // Отзывы
        const reviewsList = document.getElementById('reviews-list');
        reviewsList.innerHTML = '';
        if (car.reviews && car.reviews.length) {
            car.reviews.forEach(r => {
                const li = document.createElement('li');
                li.textContent = `★${r.rating} — ${r.comment} (${r.author})`;
                reviewsList.appendChild(li);
            });
        } else {
            reviewsList.innerHTML = '<li>Нет отзывов</li>';
        }
    } catch (e) {
        document.getElementById('car-title').textContent = 'Ошибка загрузки автомобиля';
    }
}

window.onload = loadCarDetails; 