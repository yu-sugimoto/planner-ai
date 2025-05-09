// src/main-index.js

// UIkitのCSSをnpmから取り込む場合は、こんな風にimportも可能
// import 'uikit/dist/css/uikit.min.css';

// 独自CSS
import './style.css';

const gpsButton = document.getElementById('gpsButton');
const gpsInfo = document.getElementById('gpsInfo');
const departureInput = document.getElementById('departure');
const areaInput = document.getElementById('area');
const nextButton = document.getElementById('nextButton');

let userLatitude = null;
let userLongitude = null;

// FastAPIサーバ接続テスト → （成功）Consoleに "Hello World" が表示される
const fetchHelloWorld = async () => {
    try {
        const response = await fetch('http://localhost:8000/');  // FastAPIサーバにGETリクエスト
        if (response.ok) {
            const data = await response.json();
            console.log(data.message);
        } else {
            console.error('FastAPI からのデータ取得に失敗しました');
        }
    } catch (error) {
        console.error('APIリクエストエラー:', error);
    }
};
window.addEventListener('DOMContentLoaded', fetchHelloWorld);  // ページ読み込み時に実行

if (gpsButton) {
    gpsButton.addEventListener('click', () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    userLatitude = position.coords.latitude;
                    userLongitude = position.coords.longitude;
                    gpsInfo.style.display = 'block';
                    gpsInfo.textContent = `緯度:${userLatitude}, 経度:${userLongitude}`;
                    // htmlに追加
                    departureInput.value += "大阪市";
                },
                (error) => {
                    userLatitude = 34.702485;
                    userLongitude = 135.495951;
                    gpsInfo.style.display = 'block';
                    gpsInfo.textContent = `緯度:${userLatitude}, 経度:${userLongitude}`;
                    // htmlに追加
                    departureInput.value += "大阪市";
                }
            );
        } else {
            alert('お使いのブラウザはGPSをサポートしていません。');
        }
    });
}

if (nextButton) {
    nextButton.addEventListener('click', () => {
        const area = areaInput.value.trim();
        if (!area || area === 'エリアを選択') {
            alert('エリアを入力してください');
            return;
        }
        localStorage.setItem('area', area);
        localStorage.setItem('departure', '');
        localStorage.setItem('latitude', userLatitude || '');
        localStorage.setItem('longitude', userLongitude || '');
        window.location.href = 'optimize.html';
    });
}
