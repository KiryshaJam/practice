let cars = [];
let editingCarId = null;

document.addEventListener('DOMContentLoaded', () => {
    loadCars();
    setupEventListeners();
    updateFavoriteButtons();
});

function setupEventListeners() {
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(filterForm);
            const filters = {
                brand: formData.get('brand'),
                category: formData.get('category'),
                yearMin: formData.get('yearMin'),
                yearMax: formData.get('yearMax'),
                priceMin: formData.get('priceMin'),
                priceMax: formData.get('priceMax'),
                mileageMin: formData.get('mileageMin'),
                mileageMax: formData.get('mileageMax'),
                transmission: formData.get('transmission'),
                drivetrain: formData.get('drivetrain'),
                features: formData.getAll('features')
            };
            filterCars(filters);
        });

        filterForm.addEventListener('reset', (e) => {
            setTimeout(() => {
                displayCars(cars);
            }, 0);
        });
    }

    document.getElementById('saveCarBtn').addEventListener('click', saveCar);

    document.getElementById('carForm').addEventListener('submit', (e) => e.preventDefault());
}

function loadCars() {
    fetch('/cars')
        .then(response => response.json())
        .then(data => {
            cars = data;
        displayCars(cars);
        })
        .catch(error => {
        console.error('Ошибка при загрузке автомобилей:', error);
        showError('Не удалось загрузить список автомобилей');
    });
}

function displayCars(carsToDisplay) {
    const carsList = document.getElementById('carsList');
    if (!carsList) return;

    carsList.innerHTML = carsToDisplay.map(car => createCarCard(car)).join('');
    updateFavoriteButtons();
}

function createCarCard(car) {
    const name = `${car.make || ''} ${car.model || ''} ${car.year || ''}`.trim();
    const description = car.description || '';
    const image = car.image || '/static/images/no-image.jpg';
    const isInFavorite = isInFavorites(car.id);
    let priceStr = '';
    if (car.price) {
        priceStr = Number(car.price).toLocaleString('ru-RU') + ' ₽';
    }
    return `
        <div class="col">
        <div class="card h-100">
                <div class="image-container">
                    <img src="${image}" class="card-img-top" alt="${name}">
                </div>
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">${name}</h5>
                    <p class="card-text">${description}</p>
                    <div class="mt-auto">
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="h5 mb-0 text-success fw-bold">${priceStr}</span>
                            <div class="btn-group">
                                <button class="btn btn-primary" onclick="showCarDetails('${car.id}')">
                                    Подробнее
                                </button>
                                <button class="btn btn-outline-danger favorite-button ${isInFavorite ? 'active' : ''}" 
                                        data-car-id="${car.id}"
                                        onclick="toggleFavorite(this, '${car.id}')">
                                    <i class="bi bi-heart${isInFavorite ? '-fill' : ''}"></i>
                </button>
            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function filterCars(filters) {
    let filtered = cars;

    if (filters.brand && filters.brand !== 'Все') {
        filtered = filtered.filter(car => (car.make || '').toLowerCase() === filters.brand.toLowerCase());
    }

    if (filters.category && filters.category !== 'Все') {
        filtered = filtered.filter(car =>
            car.specs && car.specs.body && car.specs.body.toLowerCase() === filters.category.toLowerCase()
        );
    }

    if (filters.yearMin) {
        filtered = filtered.filter(car => car.year >= parseInt(filters.yearMin));
    }
    if (filters.yearMax) {
        filtered = filtered.filter(car => car.year <= parseInt(filters.yearMax));
    }

    if (filters.priceMin) {
        filtered = filtered.filter(car => car.price >= parseInt(filters.priceMin));
    }
    if (filters.priceMax) {
        filtered = filtered.filter(car => car.price <= parseInt(filters.priceMax));
    }

    if (filters.features && filters.features.length > 0) {
        filtered = filtered.filter(car => {
            if (!car.specs) return false;
            return filters.features.every(feature =>
                Object.values(car.specs).some(val =>
                    typeof val === 'string' && val.toLowerCase().includes(feature.toLowerCase())
                )
            );
        });
    }

    displayCars(filtered);
}

async function saveCar() {
    const form = document.getElementById('carForm');
    const formData = new FormData(form);
    
    const carData = {
        id: editingCarId || `${formData.get('brand').toLowerCase()}-${formData.get('title').toLowerCase()}-${formData.get('year')}`,
        brand: formData.get('brand'),
        title: formData.get('title'),
        price: `${formData.get('price')} ₽`,
        year: formData.get('year'),
        mileage: `${formData.get('mileage')} км`,
        engine: `${formData.get('engine')}`,
        power: `${formData.get('power')} л.с.`,
        transmission: formData.get('transmission'),
        drivetrain: formData.get('drivetrain'),
        category: formData.get('category'),
        description: formData.get('description'),
        features: Array.from(formData.getAll('features')),
        images: [],
        rating: 0
    };

    try {
        const imageFiles = formData.getAll('images');
        if (imageFiles.length === 0 && !editingCarId) {
            throw new Error('Пожалуйста, загрузите хотя бы одно изображение');
        }

        const imageUploadPromises = Array.from(imageFiles).map(async file => {
            const imageFormData = new FormData();
            imageFormData.append('image', file);
            const response = await fetch('/api/upload-image', {
                method: 'POST',
                body: imageFormData
            });
            const result = await response.json();
            return result.path;
        });

        carData.images = await Promise.all(imageUploadPromises);

        const response = await fetch('/api/cars', {
            method: editingCarId ? 'PUT' : 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(carData)
        });

        if (!response.ok) {
            throw new Error('Ошибка при сохранении автомобиля');
        }

        await loadCars();
        const modal = bootstrap.Modal.getInstance(document.getElementById('addCarModal'));
        modal.hide();
        form.reset();
        editingCarId = null;

        await Swal.fire({
            title: 'Успешно!',
            text: `Автомобиль ${editingCarId ? 'обновлен' : 'добавлен'}`,
            icon: 'success'
        });

    } catch (error) {
        console.error('Ошибка при сохранении:', error);
        showError(error.message || 'Не удалось сохранить автомобиль');
    }
}

function editCar(carId) {
    const car = cars.find(c => c.id === carId);
    if (!car) return;

    editingCarId = carId;
    const form = document.getElementById('carForm');
    
    form.elements['brand'].value = car.brand;
    form.elements['title'].value = car.title;
    form.elements['price'].value = parseInt(car.price.replace(/[^\d]/g, ''));
    form.elements['year'].value = car.year;
    form.elements['mileage'].value = parseInt(car.mileage.replace(/[^\d]/g, ''));
    form.elements['engine'].value = car.engine;
    form.elements['power'].value = parseInt(car.power);
    form.elements['transmission'].value = car.transmission;
    form.elements['drivetrain'].value = car.drivetrain;
    form.elements['category'].value = car.category;
    form.elements['description'].value = car.description;

    const checkboxes = form.querySelectorAll('input[name="features"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = car.features.includes(checkbox.value);
    });

    const modal = new bootstrap.Modal(document.getElementById('addCarModal'));
    modal.show();
}

async function deleteCar(carId) {
    const result = await Swal.fire({
        title: 'Удаление автомобиля',
        text: 'Вы уверены, что хотите удалить этот автомобиль?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Да, удалить',
        cancelButtonText: 'Отмена'
    });

    if (result.isConfirmed) {
        try {
            const response = await fetch(`/api/cars/${carId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error('Ошибка при удалении автомобиля');
            }

            await loadCars();
            await Swal.fire({
                title: 'Успешно!',
                text: 'Автомобиль был удален',
                icon: 'success'
            });
        } catch (error) {
            console.error('Ошибка при удалении:', error);
            showError('Не удалось удалить автомобиль');
        }
    }
}

function checkAuth() {
    const token = localStorage.getItem('auth_token');
    return {
        isAuthenticated: !!token,
        token: token
    };
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

function isInFavorites(carId) {
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    return favorites.includes(carId);
}

function toggleFavorite(button, carId) {
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

    const icon = button.querySelector('i');
    if (isInFavorites(carId)) {
        removeFromFavorites(carId);
        button.classList.remove('active');
        icon.classList.replace('bi-heart-fill', 'bi-heart');
    } else {
        addToFavorites(carId);
        button.classList.add('active');
        icon.classList.replace('bi-heart', 'bi-heart-fill');
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

function updateFavoriteButtons() {
    document.querySelectorAll('.favorite-button').forEach(button => {
        const carId = button.dataset.carId;
        const icon = button.querySelector('i');
        if (isInFavorites(carId)) {
            button.classList.add('active');
            icon.classList.replace('bi-heart', 'bi-heart-fill');
        } else {
            button.classList.remove('active');
            icon.classList.replace('bi-heart-fill', 'bi-heart');
        }
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

function showCarDetails(carId) {
    window.location.href = `/cars/${carId}`;
} 