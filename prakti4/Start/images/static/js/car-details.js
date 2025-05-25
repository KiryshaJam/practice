document.addEventListener('DOMContentLoaded', async () => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');
    const source = params.get('source') || 'auto_ru_scraper';
    if (!id) {
        return;
    }

    try {
        const response = await fetch(`/api/cars/${source}/${id}`);
        const car = await response.json();

        const crashTestRatings = {
            'audi q7 2022': { stars: 5, text: '5 из 5 (Euro NCAP)' },
            'kia rio 2021': { stars: 3, text: '3 из 5 (Euro NCAP)' },
            'hyundai solaris 2022': { stars: 3, text: '3 из 5 (Latin NCAP/ARCAP)' },
            'volkswagen passat 2018': { stars: 5, text: '5 из 5 (Euro NCAP)' },
            'lada vesta 2021': { stars: 3, text: '3 из 5 (ARCAP)' },
            'mercedes-benz c-class 2020': { stars: 5, text: '5 из 5 (Euro NCAP)' },
            'audi a4 2019': { stars: 5, text: '5 из 5 (Euro NCAP)' },
            'kia sportage 2022': { stars: 5, text: '5 из 5 (Euro NCAP)' },
            'toyota rav4 2021': { stars: 5, text: '5 из 5 (Euro NCAP)' }
        };

        function getCrashTestInfo(car) {
            if (!car.make || !car.model || !car.year) return null;
            const make = String(car.make).trim().toLowerCase();
            const model = String(car.model).trim().toLowerCase();
            const year = String(car.year).trim();
            const key = `${make} ${model} ${year}`;
            console.log('car:', car);
            console.log('crashTestKey:', key);
            console.log('car-details-js:', document.getElementById('car-details-js'));
            return crashTestRatings[key] || null;
        }

        const crashTestBlock = document.getElementById('car-details-js');
        if (crashTestBlock) {
            const info = getCrashTestInfo(car);
            let starsHtml = '';
            let text = '';
            if (info) {
                for (let i = 1; i <= 5; i++) {
                    starsHtml += `<span style="color:${i <= info.stars ? 'gold' : '#ccc'}; font-size:1.5em;">&#9733;</span>`;
                }
                text = info.text;
            } else {
                for (let i = 1; i <= 5; i++) {
                    starsHtml += `<span style=\"color:#ccc; font-size:1.5em;\">&#9733;</span>`;
                }
                text = '(Нет данных)';
            }
            crashTestBlock.innerHTML = `
                <div class="car-extra-info" style="margin-top: 1.5em; width:100%;">
                    <div class="crash-test-block">
                        <strong>Безопасность (краш-тест):</strong>
                        <span class="stars">${starsHtml}</span>
                        <span>${text}</span>
                    </div>
                    <div class="owner-reviews" style="margin-top:1em;">
                        <strong>Отзывы владельцев:</strong>
                        <ul><li>Пока нет отзывов</li></ul>
                </div>
            </div>
        `;
        }
    } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
    }
}); 