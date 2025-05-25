window.checkAuth = function() {
    const token = localStorage.getItem('auth_token');
    return {
        isAuthenticated: !!token,
        token: token
    };
};

window.logout = function() {
    localStorage.removeItem('auth_token');
    window.location.href = '/';
};

function updateAuthUI() {
    const auth = window.checkAuth();
    const authButtons = document.querySelector('.auth-buttons');
    if (!authButtons) return;

    const loginBtn = authButtons.querySelector('.auth-login');
    const registerBtn = authButtons.querySelector('.auth-register');
    const userMenu = authButtons.querySelector('.user-menu');

    if (auth.isAuthenticated) {
        loginBtn.classList.add('d-none');
        registerBtn.classList.add('d-none');
        userMenu.classList.remove('d-none');
    } else {
        loginBtn.classList.remove('d-none');
        registerBtn.classList.remove('d-none');
        userMenu.classList.add('d-none');
    }
}

document.addEventListener('DOMContentLoaded', updateAuthUI);

function updateActiveNavLink() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        const href = link.getAttribute('href');
        link.classList.remove('active');
        
        if (href === '/' && currentPath === '/') {
            link.classList.add('active');
        }
        else if (href !== '/' && currentPath.startsWith(href)) {
            link.classList.add('active');
        }
    });
}

function updateHeader() {
    const { isAuthenticated } = window.checkAuth();
    const authLogin = document.querySelector('.auth-login');
    const authRegister = document.querySelector('.auth-register');
    const userMenu = document.querySelector('.user-menu');
    
    if (isAuthenticated) {
        if (authLogin) authLogin.classList.add('d-none');
        if (authRegister) authRegister.classList.add('d-none');
        if (userMenu) userMenu.classList.remove('d-none');
    } else {
        if (authLogin) authLogin.classList.remove('d-none');
        if (authRegister) authRegister.classList.remove('d-none');
        if (userMenu) userMenu.classList.add('d-none');
    }

    updateActiveNavLink();
}

function register(userData) {
    localStorage.setItem('userData', JSON.stringify(userData));
    localStorage.setItem('isAuthenticated', 'true');
    updateHeader();
    return true;
}

function login(email, password, remember) {
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');
    
    if (userData.email === email && userData.password === password) {
        localStorage.setItem('isAuthenticated', 'true');
        
        if (remember) {
            localStorage.setItem('rememberMe', 'true');
        }
        
        updateHeader();
        return true;
    }
    return false;
}

function updateUserData(newData) {
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');
    const updatedData = { ...userData, ...newData };
    localStorage.setItem('userData', JSON.stringify(updatedData));
    updateHeader();
}

document.addEventListener('DOMContentLoaded', function() {
    updateHeader();
    
    const protectedPaths = ['/profile', '/favorites'];
    if (protectedPaths.includes(window.location.pathname) && !window.checkAuth().isAuthenticated) {
        window.location.href = '/auth/login';
    }

    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function() {
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

window.addEventListener('popstate', updateHeader);

if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const rememberMe = document.getElementById('rememberMe').checked;

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    remember: rememberMe
                })
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('auth_token', data.token);
                
                Swal.fire({
                    title: 'Успешно!',
                    text: 'Вы успешно вошли в систему',
                    icon: 'success',
                    confirmButtonText: 'OK'
                }).then(() => {
                    window.location.href = '/';
                });
            } else {
                Swal.fire({
                    title: 'Ошибка!',
                    text: data.message || 'Неверный email или пароль',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            }
        } catch (error) {
            console.error('Ошибка:', error);
            Swal.fire({
                title: 'Ошибка!',
                text: 'Произошла ошибка при входе в систему',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
    });
}

if (document.getElementById('registerForm')) {
    document.getElementById('registerForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const password = document.getElementById('password').value.trim();
        const confirmPassword = document.getElementById('confirmPassword').value.trim();

        if (password !== confirmPassword) {
            Swal.fire({
                title: 'Ошибка!',
                text: 'Пароли не совпадают',
                icon: 'error',
                confirmButtonText: 'OK'
            });
            return;
        }
        
        if (password.length < 8) {
            Swal.fire({
                title: 'Ошибка!',
                text: 'Пароль должен содержать минимум 8 символов',
                icon: 'error',
                confirmButtonText: 'OK'
            });
            return;
        }

        if (!document.getElementById('terms').checked) {
            Swal.fire({
                title: 'Ошибка!',
                text: 'Необходимо согласиться с условиями использования',
                icon: 'error',
                confirmButtonText: 'OK'
            });
            return;
        }
        
        const userData = {
            firstName: document.getElementById('firstName').value.trim(),
            lastName: document.getElementById('lastName').value.trim(),
            email: document.getElementById('email').value.trim(),
            password: password
        };

        if (!userData.firstName || !userData.lastName || !userData.email) {
            Swal.fire({
                title: 'Ошибка!',
                text: 'Все поля обязательны для заполнения',
                icon: 'error',
                confirmButtonText: 'OK'
            });
            return;
        }

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('userData', JSON.stringify({
                    email: userData.email,
                    firstName: userData.firstName,
                    lastName: userData.lastName
                }));

                Swal.fire({
                    title: 'Успешно!',
                    text: 'Вы успешно зарегистрировались',
                    icon: 'success',
                    confirmButtonText: 'OK'
                }).then(() => {
                    fetch('/api/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            email: userData.email,
                            password: userData.password
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.token) {
                            localStorage.setItem('auth_token', data.token);
                            window.location.href = '/';
                        } else {
                            throw new Error('Ошибка при автоматическом входе');
                        }
                    })
                    .catch(error => {
                        console.error('Ошибка при автоматическом входе:', error);
                        window.location.href = '/auth/login';
                    });
                });
            } else {
                Swal.fire({
                    title: 'Ошибка!',
                    text: data.message || 'Ошибка при регистрации',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            }
        } catch (error) {
            console.error('Ошибка:', error);
            Swal.fire({
                title: 'Ошибка!',
                text: 'Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
    });
} 