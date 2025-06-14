document.addEventListener('DOMContentLoaded', () => {
    let selectedBrands = [];
    const carContainer = document.getElementById('carContainer');
    
    const bodyTypeSelect = document.getElementById('bodyTypeSelect');
    if (bodyTypeSelect) {
        bodyTypeSelect.addEventListener('change', filterCars);
    }

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

    function filterCars() {
        const selectedBody = document.getElementById('bodyTypeSelect').value;
        const cars = document.querySelectorAll('.car-card');
        
        cars.forEach(card => {
            const matchesBody = !selectedBody || card.classList.contains(selectedBody);
            const matchesBrand = !selectedBrands.length || selectedBrands.some(b => card.classList.contains(b));
            card.style.display = (matchesBody && matchesBrand) ? 'block' : 'none';
        });
    }

    document.querySelectorAll('.car-card').forEach(card => {
        card.addEventListener('click', (e) => {
            const href = card.getAttribute('href');
            if (href) {
                e.preventDefault();
                window.location.href = href;
            }
        });
    });

    const quickSearchForm = document.getElementById('quickSearchForm');
    if (quickSearchForm) {
        quickSearchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(quickSearchForm);
            const params = new URLSearchParams();

            if (formData.get('brand')) params.append('brand', formData.get('brand'));
            if (formData.get('category')) params.append('category', formData.get('category'));
            if (formData.get('priceRange')) params.append('price', formData.get('priceRange'));

            window.location.href = `/catalog?${params.toString()}`;
        });
    }

    filterCars();
}); 