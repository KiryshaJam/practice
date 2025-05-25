document.addEventListener('DOMContentLoaded', () => {
    // Инициализация фильтров
    let selectedBrands = [];
    const carContainer = document.getElementById('carContainer');
    
    // Обработка фильтра по типу кузова
    const bodyTypeSelect = document.getElementById('bodyTypeSelect');
    if (bodyTypeSelect) {
        bodyTypeSelect.addEventListener('change', filterCars);
    }

    // Обработка клика по брендам
    document.querySelectorAll('.brand').forEach(el => {
        el.addEventListener('click', () => {
            const brand = el.dataset.brand;
            el.classList.toggle('selected');
            
            if (el.classList.contains('selected')) {
                selectedBrands.push(brand);
            } else {
                selectedBrands = selectedBrands.filter(b => b !== brand);
            }
            
            filterCars();
        });
    });

    // Функция фильтрации автомобилей
    function filterCars() {
        const selectedBody = document.getElementById('bodyTypeSelect').value;
        const cars = document.querySelectorAll('.car-card');
        
        cars.forEach(card => {
            const matchesBody = !selectedBody || card.classList.contains(selectedBody);
            const matchesBrand = !selectedBrands.length || selectedBrands.some(b => card.classList.contains(b));
            card.style.display = (matchesBody && matchesBrand) ? 'block' : 'none';
        });
    }

    // Обработка клика по карточкам автомобилей
    document.querySelectorAll('.car-card').forEach(card => {
        card.addEventListener('click', (e) => {
            // Получаем оригинальный URL из атрибута href
            const href = card.getAttribute('href');
            if (href) {
                e.preventDefault();
                window.location.href = href;
            }
        });
    });

    // Обработка формы быстрого поиска
    const quickSearchForm = document.getElementById('quickSearchForm');
    if (quickSearchForm) {
        quickSearchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(quickSearchForm);
            const params = new URLSearchParams();

            // Добавляем параметры поиска в URL
            if (formData.get('brand')) params.append('brand', formData.get('brand'));
            if (formData.get('category')) params.append('category', formData.get('category'));
            if (formData.get('priceRange')) params.append('price', formData.get('priceRange'));

            // Переходим на страницу каталога с параметрами
            window.location.href = `/catalog?${params.toString()}`;
        });
    }

    // Инициализация фильтрации при загрузке страницы
    filterCars();
}); 