// AHP парные сравнения с расчетом весов и согласованности

document.addEventListener('DOMContentLoaded', function() {
    // Критерии и пояснения с иконками
    const criteria = [
        { key: 'Цена', desc: 'Стоимость автомобиля', icon: 'bi-cash-stack' },
        { key: 'Безопасность', desc: 'Системы безопасности и защиты', icon: 'bi-shield-lock' },
        { key: 'Комфорт', desc: 'Уровень комфорта и оснащения', icon: 'bi-cup-hot' },
        { key: 'Экономичность', desc: 'Экономия топлива и обслуживания', icon: 'bi-fuel-pump' },
        { key: 'Надежность', desc: 'Долговечность и ремонтопригодность', icon: 'bi-tools' }
    ];
    // Шкала Саати
    const saatyScale = [
        { value: 5, label: 'В 5 раз важнее (левый)' },
        { value: 3, label: 'В 3 раза важнее (левый)' },
        { value: 1,   label: 'Одинаково важны' },
        { value: 1/3,   label: 'В 3 раза важнее (правый)' },
        { value: 1/5,   label: 'В 5 раз важнее (правый)' }
    ];
    // Таблица случайных индексов (RI)
    const RI = { 1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32 };

    // Генерируем все уникальные пары критериев для сравнения
    const pairs = [];
    for (let i = 0; i < criteria.length; i++) {
        for (let j = i + 1; j < criteria.length; j++) {
            pairs.push([i, j]);
        }
    }
    let currentStep = 0;
    const totalSteps = pairs.length;
    const answers = new Array(totalSteps).fill(0); // по умолчанию "Одинаково важны"

    // DOM элементы
    const prevButton = document.getElementById('prevButton');
    const nextButton = document.getElementById('nextButton');
    const finishButton = document.getElementById('finishButton');
    const helpText = document.getElementById('helpText');
    const slider = document.querySelector('.comparison-slider');
    const criterion1 = document.getElementById('criterion1');
    const criterion2 = document.getElementById('criterion2');
    const description1 = document.getElementById('description1');
    const description2 = document.getElementById('description2');
    const progressText = document.querySelector('.progress-text');
    const progressBar = document.querySelector('.progress');
    const resultsBlock = document.getElementById('results');
    const weightsList = document.getElementById('weightsList');

    // Функция отображения текущей пары
    function renderStep() {
        const [i, j] = pairs[currentStep];
        criterion1.innerHTML = `<i class="bi ${criteria[i].icon}" style="font-size:2rem;color:#3498db;"></i><br><span>${criteria[i].key}</span>`;
        criterion2.innerHTML = `<i class="bi ${criteria[j].icon}" style="font-size:2rem;color:#3498db;"></i><br><span>${criteria[j].key}</span>`;
        description1.textContent = criteria[i].desc;
        description2.textContent = criteria[j].desc;
        // ВОССТАНАВЛИВАЕМ сохранённое значение для текущей пары
        slider.value = answers[currentStep];
        progressText.textContent = Math.round(((currentStep + 1) / totalSteps) * 100) + '%';
        progressBar.style.width = Math.round(((currentStep + 1) / totalSteps) * 100) + '%';
        prevButton.disabled = currentStep === 0;
        nextButton.style.display = (currentStep < totalSteps - 1) ? 'inline-block' : 'none';
        finishButton.style.display = (currentStep === totalSteps - 1) ? 'inline-block' : 'none';
        resultsBlock.style.display = 'none';
    }

    // Слушатели событий
    prevButton.onclick = function() {
        if (currentStep > 0) {
            currentStep--;
            renderStep();
        }
    };
    nextButton.onclick = function() {
        if (currentStep < totalSteps - 1) {
            currentStep++;
            renderStep();
        }
    };
    finishButton.onclick = function() {
        calculateAHP();
    };
    slider.oninput = function() {
        answers[currentStep] = parseInt(slider.value, 10);
    };
    window.toggleHelp = function() {
        helpText.style.display = (helpText.style.display === 'none') ? 'block' : 'none';
    };

    // Построение матрицы парных сравнений
    function buildMatrix() {
        const n = criteria.length;
        const matrix = Array.from({ length: n }, () => Array(n).fill(1));
        for (let k = 0; k < pairs.length; k++) {
            const [i, j] = pairs[k];
            const scaleIdx = answers[k] + 2; // Исправлено: преобразуем значение ползунка к индексу шкалы Саати
            const value = saatyScale[scaleIdx].value;
            matrix[i][j] = value;
            matrix[j][i] = 1 / value;
        }
        return matrix;
    }

    // Нормализация по столбцам и расчет весов
    function calculateWeights(matrix) {
        const n = matrix.length;
        const colSums = Array(n).fill(0);
        for (let j = 0; j < n; j++) {
            for (let i = 0; i < n; i++) {
                colSums[j] += matrix[i][j];
            }
        }
        // Нормализуем и считаем веса
        const weights = Array(n).fill(0);
        for (let i = 0; i < n; i++) {
            for (let j = 0; j < n; j++) {
                weights[i] += matrix[i][j] / colSums[j];
            }
            weights[i] /= n;
        }
        return weights;
    }

    // Расчет λmax
    function calculateLambdaMax(matrix, weights) {
        const n = matrix.length;
        let lambdaMax = 0;
        for (let j = 0; j < n; j++) {
            let colSum = 0;
            for (let i = 0; i < n; i++) {
                colSum += matrix[i][j];
            }
            lambdaMax += colSum * weights[j];
        }
        return lambdaMax;
    }

    // Основная функция расчета AHP
    function calculateAHP() {
        const matrix = buildMatrix();
        const weights = calculateWeights(matrix);
        const lambdaMax = calculateLambdaMax(matrix, weights);
        const n = matrix.length;
        const CI = (lambdaMax - n) / (n - 1);
        const crRI = RI[n] || 1.12;
        const CR = CI / crRI;
        showResults(weights, CR);
    }

    // Показ результатов
    function showResults(weights, CR) {
        resultsBlock.style.display = 'block';
        let html = '<h4>Веса критериев:</h4><ul>';
        for (let i = 0; i < criteria.length; i++) {
            html += `<li><b>${criteria[i].key}</b>: ${(weights[i]*100).toFixed(1)}% <span style="color:#888;font-size:0.9em">(${criteria[i].desc})</span></li>`;
        }
        html += '</ul>';
        html += `<div class="consistency-info mb-3">
            <b>Индекс согласованности (CR):</b> <span style="font-size:1.1em;">${CR.toFixed(3)}</span> `;
        if (CR > 0.1) {
            html += `<span style="color:red;font-weight:600;">(Плохо)</span><br><span style="color:#888;font-size:0.95em;">Ваши ответы противоречивы. Рекомендуется пройти сравнение ещё раз, чтобы повысить точность результата.</span>`;
        } else if (CR > 0.05) {
            html += `<span style="color:orange;font-weight:600;">(Хорошо)</span><br><span style="color:#888;font-size:0.95em;">Согласованность ваших ответов хорошая, но можно попробовать сделать её ещё лучше.</span>`;
        } else {
            html += `<span style="color:green;font-weight:600;">(Отлично)</span><br><span style="color:#888;font-size:0.95em;">Ваши ответы очень согласованы. Результаты можно считать надёжными.</span>`;
        }
        html += `</div>`;
        html += `<button id="repeatBtn" class="btn btn-warning mt-2">Повторить сравнение</button>`;

        // Преобразуем веса в формат для API
        const weightsObj = {
            'Цена': weights[0],
            'Безопасность': weights[1],
            'Комфорт': weights[2],
            'Экономичность': weights[3],
            'Надежность': weights[4]
        };

        // Получаем рекомендации с сервера
        fetch('/api/recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(weightsObj)
        })
        .then(response => response.json())
        .then(recommended => {
            if (recommended && recommended.length > 0) {
                html += '<h4 class="mt-4">Рекомендуемые автомобили:</h4>';
                html += '<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">';
                for (const car of recommended) {
                    const imageUrl = car.images && car.images[0] ? car.images[0] : '/static/images/no-image.jpg';
                    html += `
                        <div class="col">
                            <a href="/cars/${car.id}" class="car-card-link" style="text-decoration:none;color:inherit;">
                            <div class="card h-100">
                                <img src="${imageUrl}" class="card-img-top" alt="${car.make} ${car.model}" onerror="this.src='/static/images/no-image.jpg'">
                                <div class="card-body">
                                    <h5 class="card-title">${car.make} ${car.model}</h5>
                                    <p class="card-text">
                                        <b>Год:</b> ${car.year}<br>
                                        <b>Цена:</b> ${car.price.toLocaleString()} ₽<br>
                                        <b>Двигатель:</b> ${car.specs.engine}<br>
                                        <b>Кузов:</b> ${car.specs.body}<br>
                                        <b>Коробка:</b> ${car.specs.transmission}
                                    </p>
                                    <p class="card-text"><small>${car.description || ''}</small></p>
                                    <div class="match-score-container mb-3">
                                        <div class="match-score-label mb-1">Совпадение с вашими критериями:</div>
                                        <div class="progress" style="height: 100%; background-color: #e9ecef; border-radius: 12px; box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);">
                                            <div class="progress-bar d-flex align-items-center justify-content-center" role="progressbar" 
                                                style="width: ${(car.matchScore * 100).toFixed(0)}%; 
                                                background: linear-gradient(90deg, #2ecc71, #27ae60);
                                                font-size: 16px;
                                                font-weight: 600;
                                                height: 100%;
                                                border-radius: 12px;
                                                transition: width 0.6s ease;"
                                                aria-valuenow="${(car.matchScore * 100).toFixed(0)}" 
                                                aria-valuemin="0" 
                                                aria-valuemax="100">
                                                ${(car.matchScore * 100).toFixed(0)}%
                                            </div>
                                        </div>
                                    </div>
                                    <span class="btn btn-primary">Подробнее</span>
                                </div>
                            </div>
                            </a>
                        </div>`;
                }
                html += '</div>';
            } else {
                html += '<p class="mt-4 text-warning">К сожалению, не удалось подобрать автомобили по вашим критериям.</p>';
            }
            weightsList.innerHTML = html;
            
            // Кнопка повторить
            const repeatBtn = document.getElementById('repeatBtn');
            if (repeatBtn) {
                repeatBtn.onclick = function() {
                    for (let i = 0; i < answers.length; i++) answers[i] = 0;
                    currentStep = 0;
                    renderStep();
                    resultsBlock.style.display = 'none';
                    prevButton.style.display = 'inline-block';
                    nextButton.style.display = 'inline-block';
                    finishButton.style.display = 'none';
                };
            }
            // Скрыть кнопки навигации
            prevButton.style.display = 'none';
            nextButton.style.display = 'none';
            finishButton.style.display = 'none';
        })
        .catch(error => {
            console.error('Error getting recommendations:', error);
            html += '<p class="mt-4 text-danger">Ошибка при получении рекомендаций. Пожалуйста, попробуйте позже.</p>';
            weightsList.innerHTML = html;
        });
    }

    // Инициализация
    renderStep();
}); 