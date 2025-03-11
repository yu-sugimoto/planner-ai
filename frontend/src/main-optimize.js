// src/main-optimize.js

import './style.css';

const optimizeButton = document.getElementById('optimizeButton');

optimizeButton.addEventListener('click', async function() {
    // フォームのバリデーション
    const budget = document.getElementById('budget');
    const days = document.getElementById('days');
    const startDate = document.getElementById('startDate');
    const people = document.getElementById('people');
    const latitude  = localStorage.getItem('latitude');
    const longitude = localStorage.getItem('longitude');
    const departure = localStorage.getItem('departure');
    const area      = localStorage.getItem('area');

    // エラーメッセージをリセット
    clearErrors();

    // 必須項目と整数値のチェック
    let isValid = true;

    if (!budget.value || !Number.isInteger(Number(budget.value))) {
        showError(budget, '予算を整数で入力してください');
        isValid = false;
    }

    if (!days.value || !Number.isInteger(Number(days.value)) || Number(days.value) < 1) {
        showError(days, '日数を正の整数で入力してください');
        isValid = false;
    }

    if (!startDate.value || !Number.isInteger(Number(startDate.value))) {
        showError(startDate, '時刻を整数で入力してください');
        isValid = false;
    } else {
        const time = Number(startDate.value);
        if (time < 0 || time > 2359 || (time % 100) >= 60) {
            showError(startDate, '正しい時刻形式で入力してください (0-2359)');
            isValid = false;
        }
    }

    if (!people.value || !Number.isInteger(Number(people.value)) || Number(people.value) < 1) {
        showError(people, '人数を正の整数で入力してください');
        isValid = false;
    }

    if (isValid) {
        try {
            // 8000番ポートで動くFastAPIサーバにPOST
            const response = await fetch('http://localhost:8000/api/optimize', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    area: area,
                    budget: parseInt(budget.value),
                    days: parseInt(days.value),
                    startDate: parseInt(startDate.value),
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
            console.log(resultData);
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
