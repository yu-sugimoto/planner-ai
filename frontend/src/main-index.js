// src/main-index.js

// UIkitのCSSをnpmから取り込む場合は、こんな風にimportも可能
// import 'uikit/dist/css/uikit.min.css';

// 独自CSS
import './style.css';

const gpsButton = document.getElementById('gpsButton');
const gpsInfo = document.getElementById('gpsInfo');
const departureInput = document.getElementById('departure');
const nextButton = document.getElementById('nextButton');

let userLatitude = null;
let userLongitude = null;

if (gpsButton) {
    gpsButton.addEventListener('click', () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    userLatitude = position.coords.latitude;
                    userLongitude = position.coords.longitude;
                    gpsInfo.style.display = 'block';
                    gpsInfo.textContent = `緯度:${userLatitude}, 経度:${userLongitude}`;
                },
                (error) => {
                    alert('GPS取得に失敗しました: ' + error.message);
                }
            );
        } else {
            alert('お使いのブラウザはGPSをサポートしていません。');
        }
    });
}

if (nextButton) {
    nextButton.addEventListener('click', () => {
        const departure = departureInput.value.trim();
        localStorage.setItem('departure', departure);
        localStorage.setItem('latitude', userLatitude || '');
        localStorage.setItem('longitude', userLongitude || '');
        window.location.href = 'optimize.html';
    });
}
