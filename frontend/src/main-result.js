// src/main-result.js

import './style.css';

// ページ読込後に実行
window.addEventListener('DOMContentLoaded', () => {
    const resultDataJSON = localStorage.getItem('resultData');
    if (!resultDataJSON) {
        alert('結果情報がありません');
        return;
    } else {
        console.log(resultDataJSON);
    }


    // const routeDataJSON = localStorage.getItem('routeData');
    // let routeData = null;

    // if (routeDataJSON) {
    //     // { route: [ {lat, lng, name}, ... ] } の構造を想定
    //     routeData = JSON.parse(routeDataJSON).route;
    // } else {
    //     alert('ルート情報がありません');
    //     return;
    // }

    // Leaflet の地図初期化
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

    // マーカーをまとめる
    const markers = [];

    // ルートデータをもとにマーカー & リスト生成
    resultDataJSON.forEach((point, index) => {
        const marker = L.marker([point.lat, point.lng]).addTo(map);
        marker.bindPopup(point.name);
        markers.push(marker);

        // リストに追加
        const div = document.createElement('div');
        div.classList.add('uk-card', 'uk-card-default', 'uk-card-body', 'uk-margin-small');
        div.innerHTML = `<strong>${index + 1}. ${point.name}</strong><br>
                     緯度: ${point.lat}, 経度: ${point.lng}`;
        routeList.appendChild(div);
    });

    // 全マーカーを含むように自動ズーム調整
    const group = L.featureGroup(markers);
    map.fitBounds(group.getBounds(), { padding: [50, 50] });
});
