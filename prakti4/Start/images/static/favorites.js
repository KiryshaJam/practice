function addToFavorites(car) {
    if (!car || !car.id || !car.name || !car.image || !car.price) {
        console.error('Некорректные данные автомобиля:', car);
        return;
    }

    let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    
    if (!favorites.some(item => item.id === car.id)) {
        favorites.push({
            id: car.id,
            name: car.name,
            image: car.image,
            description: car.description || '',
            specs: car.specs || '',
            price: car.price
        });
        
        localStorage.setItem('favorites', JSON.stringify(favorites));
        
        Swal.fire({
            title: 'Успешно!',
            text: 'Автомобиль добавлен в избранное',
            icon: 'success',
            timer: 1500,
            showConfirmButton: false
        });
    }
}

function removeFromFavorites(carId) {
    Swal.fire({
        title: 'Удалить из избранного?',
        text: 'Вы действительно хотите удалить этот автомобиль из избранного?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Да, удалить',
        cancelButtonText: 'Отмена',
        confirmButtonColor: '#dc3545'
    }).then((result) => {
        if (result.isConfirmed) {
            let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
            favorites = favorites.filter(id => id !== carId);
            localStorage.setItem('favorites', JSON.stringify(favorites));
            
            const card = document.getElementById(`favorite-${carId}`);
            card.style.transition = 'all 0.3s ease';
            card.style.opacity = '0';
            card.style.transform = 'scale(0.8)';
            
            setTimeout(() => {
                loadFavorites();
            }, 300);

            Swal.fire({
                title: 'Готово!',
                text: 'Автомобиль удален из избранного',
                icon: 'success',
                timer: 2000,
                showConfirmButton: false
            });
        }
    });
}

function isInFavorites(carId) {
    if (!carId) return false;
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    return favorites.some(car => car.id === carId);
}

function clearAllFavorites() {
    localStorage.removeItem('favorites');
    if (window.location.pathname === '/favorites') {
        loadFavorites();
    }
    updateFavoriteButtons();
}

function loadFavorites() {
    const favoritesList = document.getElementById('favoritesList');
    const emptyFavorites = document.getElementById('emptyFavorites');
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');

    if (!favorites.length) {
        favoritesList.innerHTML = '';
        emptyFavorites.classList.remove('d-none');
        return;
    }

    emptyFavorites.classList.add('d-none');
    const favoriteCars = favorites.map(id => window.carUtils.getCarById(id)).filter(Boolean);
    
    favoritesList.innerHTML = favoriteCars.map(car => createFavoriteCard(car)).join('');
}

function createFavoriteCard(car) {
    return `
        <div class="col" id="favorite-${car.id}">
            <div class="card h-100">
                <div class="image-container">
                    <img src="${car.image}" class="card-img-top" alt="${car.name}">
                </div>
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">${car.name}</h5>
                    <p class="card-text">${car.description}</p>
                    <p class="card-text"><small class="text-muted">${car.specs}</small></p>
                    <div class="mt-auto">
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="h5 mb-0">${car.price}</span>
                            <div class="btn-group">
                                <button class="btn btn-primary" onclick="showCarDetails('${car.id}')">
                                    Подробнее
                                </button>
                                <button class="btn btn-danger" onclick="removeFromFavorites('${car.id}')">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function showCarDetails(carId) {
    window.location.href = `/car-details?id=${carId}`;
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
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    document.querySelectorAll('.favorite-button').forEach(button => {
        const carId = button.dataset.carId;
        if (favorites.some(car => car.id === carId)) {
            button.classList.add('active');
            const icon = button.querySelector('i');
            if (icon) {
                icon.classList.replace('bi-heart', 'bi-heart-fill');
            }
        } else {
            button.classList.remove('active');
            const icon = button.querySelector('i');
            if (icon) {
                icon.classList.replace('bi-heart-fill', 'bi-heart');
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    loadFavorites();
    checkAuth();
});

function checkAuth() {
    const token = localStorage.getItem('auth_token');
    if (!token && window.location.pathname === '/favorites') {
        Swal.fire({
            title: 'Требуется авторизация',
            text: 'Для доступа к избранному необходимо войти в систему',
            icon: 'info',
            showCancelButton: true,
            confirmButtonText: 'Войти',
            cancelButtonText: 'Отмена'
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = '/auth/login';
            } else {
                window.location.href = '/catalog';
            }
        });
    }
    return token;
} 