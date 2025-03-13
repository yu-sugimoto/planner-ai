import './style.css';

// ページ読込後に実行
window.addEventListener('DOMContentLoaded', () => {
    const resultDataJSON = localStorage.getItem('resultData');
    if (!resultDataJSON) {
        alert('結果情報がありません');
        return;
    }

    const resultData = JSON.parse(resultDataJSON);

    const map = L.map('map', {
        center: [35.681236, 139.767125], // 東京駅付近
        zoom: 12
    });

    // OpenStreetMap タイルレイヤー
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // リスト表示エリア
    const routeList = document.getElementById('routeList');

    const markers = [];
    const routeCoordinates = [];

    resultData.route.forEach((point, index) => {
        // マーカー追加
        const marker = L.marker([point.lat, point.lng]).addTo(map);
        marker.bindPopup(point.name);
        markers.push(marker);

        routeCoordinates.push([point.lat, point.lng]);
        const div = document.createElement('div');
        div.classList.add('uk-card', 'uk-card-default', 'uk-card-body', 'uk-margin-small');
        div.innerHTML = `
            <strong>${index + 1}. ${point.name}</strong>
            <a href="destination.html?name=${point.name}" style="margin-left: 10px;">詳細</a><br>
            交通手段: ${point.transportation_method}<br>
            出発時刻: ${point.departure_time}<br>
            到着時刻: ${point.arrival_time}<br>
            滞在時間(分): ${point.stay_duration_minutes}<br>
            合計コスト: ${point.total_cost}
        `;
        routeList.appendChild(div);
    });

    const polyline = L.polyline(routeCoordinates, { color: 'blue' }).addTo(map);
    map.fitBounds(polyline.getBounds(), { padding: [50, 50] });
});
