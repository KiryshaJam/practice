// Функция для обновления состояния шапки сайта
function updateHeaderState() {
    const token = localStorage.getItem('auth_token');
    const headerButtons = document.querySelector('.header-buttons');
    
    if (!headerButtons) return;
    
    if (token) {
        // Если пользователь авторизован
        headerButtons.innerHTML = `
            <button class="btn btn-outline-light me-2" onclick="logout()">Выйти</button>
            <a href="/profile" class="btn btn-light">Профиль</a>
        `;
    } else {
        // Если пользователь не авторизован
        headerButtons.innerHTML = `
            <button class="btn btn-outline-light me-2" onclick="window.location.href='/auth/login'">Войти</button>
            <button class="btn btn-light" onclick="window.location.href='/auth/register'">Регистрация</button>
        `;
    }
}

// Функция выхода из системы
function logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('favorites');
    updateHeaderState();
    // Перенаправляем на главную страницу
    window.location.href = '/';
}

// Обновляем состояние шапки при загрузке страницы
document.addEventListener('DOMContentLoaded', updateHeaderState); 