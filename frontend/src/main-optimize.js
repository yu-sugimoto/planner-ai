// src/main-optimize.js

import './style.css';

const optimizeButton = document.getElementById('optimizeButton');

optimizeButton.addEventListener('click', async function() {
    // フォームのバリデーション
    const budget = document.getElementById('budget');
    const startTimes = document.getElementById('startTimes');
    const days = document.getElementById('days');
    const people = document.getElementById('people');
    const latitude  = localStorage.getItem('latitude');
    const longitude = localStorage.getItem('longitude');
    const departure = localStorage.getItem('departure');
    const area      = localStorage.getItem('area');
    const startDate = document.getElementById('startDate');

    let isValid = true;
    let numericTime = 0;

    clearErrors();

    if (!budget.value || !Number.isInteger(Number(budget.value))) {
        showError(budget, '予算を整数で入力してください');
        isValid = false;
    }

    if (!days.value || !Number.isInteger(Number(days.value)) || Number(days.value) < 1) {
        showError(days, '日数を正の整数で入力してください');
        isValid = false;
    }

    if (!people.value || !Number.isInteger(Number(people.value)) || Number(people.value) < 1) {
        showError(people, '人数を正の整数で入力してください');
        isValid = false;
    }

    if (isValid) {
        try {
            // 8000番ポートで動くFastAPIサーバにPOST
            console.log("area: " + area);
            console.log("budget: " + parseInt(budget.value));
            console.log("days: " + parseInt(days.value));
            console.log("startDate: " + startDate.value);
            console.log("startTimes: " + startTimes.value);
            console.log("people: " + parseInt(people.value));
            console.log("latitude: " + latitude);
            console.log("longitude: " + longitude);
            console.log("departure: " + departure);

            
            const response = await fetch('http://127.0.0.1:8000/api/optimize', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    area: area,
                    budget: parseInt(budget.value),
                    days: parseInt(days.value),
                    startDate: startDate.value,
                    startTimes: startTimes.value,
                    people: parseInt(people.value),
                    latitude: latitude ? parseFloat(latitude) : 0,
                    longitude: longitude ? parseFloat(longitude) : 0,
                    departure: departure
                })
            });

            if (!response.ok) {
                throw new Error('サーバーエラーが発生しました');
            }

            const resultData = await response.json();
            if (resultData === {"route": []}){
                throw new Error('該当する組み合わせが存在しません');
            }

            // 取得したルートを localStorage に格納
            localStorage.setItem('resultData', resultData);
            // 結果ページへ遷移
            window.location.href = 'result.html';

        } catch (err) {
            alert('ルートの最適化に失敗しました: ' + err.message);
        }
    }
});

function showError(element, message) {
    const parent = element.parentNode;
    element.classList.add('uk-form-danger');

    const errorDiv = document.createElement('div');
    errorDiv.className = 'uk-text-danger uk-text-small uk-margin-small-top';
    errorDiv.textContent = message;
    parent.appendChild(errorDiv);
}

function clearErrors() {
    document.querySelectorAll('.uk-form-danger').forEach(el => {
        el.classList.remove('uk-form-danger');
    });

    document.querySelectorAll('.uk-text-danger').forEach(el => {
        el.remove();
    });
}
