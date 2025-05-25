function updateHeaderState() {
    const token = localStorage.getItem('auth_token');
    const headerButtons = document.querySelector('.header-buttons');
    
    if (!headerButtons) return;
    
    if (token) {
        headerButtons.innerHTML = `
            <button class="btn btn-outline-light me-2" onclick="logout()">Выйти</button>
            <a href="/profile" class="btn btn-light">Профиль</a>
        `;
    } else {
        headerButtons.innerHTML = `
            <button class="btn btn-outline-light me-2" onclick="window.location.href='/auth/login'">Войти</button>
            <button class="btn btn-light" onclick="window.location.href='/auth/register'">Регистрация</button>
        `;
    }
}

function logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('favorites');
    updateHeaderState();
    window.location.href = '/';
}

document.addEventListener('DOMContentLoaded', updateHeaderState); 