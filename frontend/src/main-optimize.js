// src/main-optimize.js

import './style.css';

const optimizeButton = document.getElementById('optimizeButton');

if (optimizeButton) {
    optimizeButton.addEventListener('click', async () => {
        // localStorage から GPS/出発地 情報取得
        const latitude  = localStorage.getItem('latitude');
        const longitude = localStorage.getItem('longitude');
        const departure = localStorage.getItem('departure');

        // 画面入力取得
        const people    = document.getElementById('people').value.trim();
        const budget    = document.getElementById('budget').value.trim();
        const days      = document.getElementById('days').value.trim();
        const startDate = document.getElementById('startDate').value;

        const requestData = {
            latitude,
            longitude,
            departure,
            people,
            budget,
            days,
            startDate
        };

        try {
            // 3000番ポートで動くExpressサーバにPOST
            const response = await fetch('http://localhost:3000/api/optimize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error('サーバーエラーが発生しました');
            }

            const resultData = await response.json();
            // 取得したルートを localStorage に格納
            localStorage.setItem('routeData', JSON.stringify(resultData));

            // 結果ページへ遷移
            window.location.href = 'result.html';

        } catch (err) {
            alert('ルートの最適化に失敗しました: ' + err.message);
        }
    });
}
