let currentCar = null;

document.addEventListener('DOMContentLoaded', () => {
    const carPath = window.location.pathname;
    const carId = carPath.split('/').pop();

    const car = window.carUtils.getCarById(carId);
    if (!car) {
        Swal.fire({
            title: 'Ошибка',
            text: 'Автомобиль не найден',
            icon: 'error'
        }).then(() => {
            window.location.href = '/';
        });
        return;
    }

    document.getElementById('carTitle').textContent = car.name;
    document.getElementById('carPrice').textContent = car.price;
    document.getElementById('carDescription').textContent = car.description;

    const specsTable = document.getElementById('specsTable');
    const specs = [
        { label: 'Марка', value: car.brand },
        { label: 'Модель', value: car.model },
        { label: 'Год выпуска', value: car.year },
        { label: 'Пробег', value: car.mileage },
        { label: 'Двигатель', value: car.engine },
        { label: 'Мощность', value: car.power },
        { label: 'Коробка передач', value: car.transmission },
        { label: 'Привод', value: car.drivetrain },
        { label: 'Тип кузова', value: car.category }
    ];

    specs.forEach(spec => {
        if (spec.value) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="fw-bold">${spec.label}</td>
                <td>${spec.value}</td>
            `;
            specsTable.appendChild(row);
        }
    });

    const mainImage = document.getElementById('mainImage');
    const thumbnailsContainer = document.getElementById('thumbnailsContainer');
    
    if (car.images && car.images.length > 0) {
        mainImage.src = car.images[0];
        mainImage.alt = car.name;

        car.images.forEach((img, index) => {
            const thumb = document.createElement('img');
            thumb.src = img;
            thumb.alt = `${car.name} - изображение ${index + 1}`;
            thumb.className = 'thumbnail';
            thumb.style.width = '80px';
            thumb.style.height = '60px';
            thumb.style.objectFit = 'cover';
            thumb.style.cursor = 'pointer';
            thumb.addEventListener('click', () => {
                mainImage.src = img;
                mainImage.alt = `${car.name} - изображение ${index + 1}`;
            });
            thumbnailsContainer.appendChild(thumb);
        });
    }

    const featuresList = document.getElementById('featuresList');
    if (car.features && car.features.length > 0) {
        car.features.forEach(feature => {
            const col = document.createElement('div');
            col.className = 'col-md-6 mb-2';
            col.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="bi bi-check2-circle text-success me-2"></i>
                    <span>${feature}</span>
                </div>
            `;
            featuresList.appendChild(col);
        });
    }

    const favoriteBtn = document.getElementById('addToFavoriteBtn');
    const updateFavoriteButton = () => {
        const isInFavorites = window.isInFavorites(carId);
        favoriteBtn.innerHTML = isInFavorites ? 
            '<i class="bi bi-heart-fill"></i> В избранном' : 
            '<i class="bi bi-heart"></i> В избранное';
        favoriteBtn.classList.toggle('btn-outline-primary', !isInFavorites);
        favoriteBtn.classList.toggle('btn-primary', isInFavorites);
    };

    favoriteBtn.addEventListener('click', () => {
        const auth = window.checkAuth();
        if (!auth.isAuthenticated) {
            Swal.fire({
                title: 'Требуется авторизация',
                text: 'Для добавления в избранное необходимо войти в систему',
                icon: 'info',
                showCancelButton: true,
                confirmButtonText: 'Войти',
                cancelButtonText: 'Отмена'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = '/auth/login';
                }
            });
            return;
        }

        if (window.isInFavorites(carId)) {
            window.removeFromFavorites(carId);
        } else {
            window.addToFavorites(carId);
        }
        updateFavoriteButton();
    });

    document.getElementById('contactSellerBtn').addEventListener('click', () => {
        Swal.fire({
            title: 'Контакты продавца',
            html: `
                <p><strong>Телефон:</strong> ${car.sellerPhone || '+7 (XXX) XXX-XX-XX'}</p>
                <p><strong>Email:</strong> ${car.sellerEmail || 'seller@example.com'}</p>
                <p><strong>Адрес:</strong> ${car.location || 'Москва'}</p>
            `,
            icon: 'info',
            confirmButtonText: 'Закрыть'
        });
    });

    updateFavoriteButton();
});

function setupEventListeners() {
    const favoriteBtn = document.getElementById('favoriteBtn');
    if (favoriteBtn) {
        favoriteBtn.addEventListener('click', toggleFavorite);
    }
}

function loadCarDetails() {
    const urlParams = new URLSearchParams(window.location.search);
    const carId = urlParams.get('id');

    if (!carId) {
        showError('Идентификатор автомобиля не указан');
        return;
    }

    try {
        currentCar = window.carUtils.getCarById(carId);
        
        if (!currentCar) {
            showError('Автомобиль не найден');
            return;
        }

        document.title = `${currentCar.name} - АвтоЭксперт`;

        document.getElementById('carName').textContent = currentCar.name;
        document.getElementById('carPrice').textContent = currentCar.price;
        document.getElementById('carDescription').textContent = currentCar.description;

        const specsList = document.getElementById('carSpecs');
        specsList.innerHTML = `
            <li><strong>Год выпуска:</strong> ${currentCar.year}</li>
            <li><strong>Пробег:</strong> ${currentCar.mileage}</li>
            <li><strong>Двигатель:</strong> ${currentCar.engine}</li>
            <li><strong>Мощность:</strong> ${currentCar.power}</li>
            <li><strong>Коробка:</strong> ${currentCar.transmission}</li>
            <li><strong>Привод:</strong> ${currentCar.drivetrain}</li>
        `;

        const featuresContainer = document.getElementById('carFeatures');
        featuresContainer.innerHTML = currentCar.features.map(feature => `
            <div class="col-md-4 mb-2">
                <div class="d-flex align-items-center">
                    <i class="bi bi-check-circle-fill text-success me-2"></i>
                    <span>${feature}</span>
                </div>
            </div>
        `).join('');

        loadCarImages();

        loadSimilarCars();

        updateFavoriteButton();

    } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
        showError('Не удалось загрузить информацию об автомобиле');
    }
}

function loadCarImages() {
    const carouselInner = document.getElementById('carImageSlides');
    if (!currentCar || !carouselInner) return;

    carouselInner.innerHTML = currentCar.images.map((image, index) => `
        <div class="carousel-item ${index === 0 ? 'active' : ''}">
            <img src="${image}" class="d-block w-100" alt="${currentCar.name}">
        </div>
    `).join('');
}

function loadSimilarCars() {
    const similarCarsContainer = document.getElementById('similarCars');
    if (!currentCar || !similarCarsContainer) return;

    const similarCars = window.carUtils.getSimilarCars(currentCar);
    
    similarCarsContainer.innerHTML = similarCars.map(car => `
        <div class="col">
            <div class="card h-100">
                <img src="${car.image}" class="card-img-top" alt="${car.name}">
                <div class="card-body">
                    <h5 class="card-title">${car.name}</h5>
                    <p class="card-text"><small class="text-muted">${car.specs}</small></p>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="h5 mb-0">${car.price}</span>
                        <a href="/car-details?id=${car.id}" class="btn btn-outline-primary">
                            <i class="bi bi-info-circle"></i> Подробнее
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function toggleFavorite() {
    if (!currentCar) return;

    const auth = checkAuth();
    if (!auth.isAuthenticated) {
        Swal.fire({
            title: 'Требуется авторизация',
            text: 'Для добавления в избранное необходимо войти в систему',
            icon: 'info',
            showCancelButton: true,
            confirmButtonText: 'Войти',
            cancelButtonText: 'Отмена'
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = '/auth/login';
            }
        });
        return;
    }

    const favoriteBtn = document.getElementById('favoriteBtn');
    const icon = favoriteBtn.querySelector('i');
    
    if (isInFavorites(currentCar.id)) {
        removeFromFavorites(currentCar.id);
        favoriteBtn.classList.remove('active');
        icon.classList.replace('bi-heart-fill', 'bi-heart');
    } else {
        addToFavorites(currentCar.id);
        favoriteBtn.classList.add('active');
        icon.classList.replace('bi-heart', 'bi-heart-fill');
    }
}

function isInFavorites(carId) {
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    return favorites.includes(carId);
}

function addToFavorites(carId) {
    let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    if (!favorites.includes(carId)) {
        favorites.push(carId);
        localStorage.setItem('favorites', JSON.stringify(favorites));
        showToast('Добавлено в избранное');
    }
}

function removeFromFavorites(carId) {
    let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    const index = favorites.indexOf(carId);
    if (index !== -1) {
        favorites.splice(index, 1);
        localStorage.setItem('favorites', JSON.stringify(favorites));
        showToast('Удалено из избранного');
    }
}

function updateFavoriteButton() {
    const favoriteBtn = document.getElementById('favoriteBtn');
    if (!favoriteBtn || !currentCar) return;

    const icon = favoriteBtn.querySelector('i');
    if (isInFavorites(currentCar.id)) {
        favoriteBtn.classList.add('active');
        icon.classList.replace('bi-heart', 'bi-heart-fill');
    } else {
        favoriteBtn.classList.remove('active');
        icon.classList.replace('bi-heart-fill', 'bi-heart');
    }
}

function showToast(message) {
    Swal.fire({
        text: message,
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        icon: 'success'
    });
}

function showError(message) {
    Swal.fire({
        title: 'Ошибка!',
        text: message,
        icon: 'error',
        confirmButtonText: 'OK'
    });
} 