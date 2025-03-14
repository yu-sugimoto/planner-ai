// src/main-destination.js

import './style.css';

const params = new URLSearchParams(window.location.search);
const destinationName = params.get('name');
const encodedName = encodeURIComponent(destinationName);
const url = `http://localhost:8000/destinations/${encodedName}`;

fetch(url)
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();
    })
    .then(data => {
        console.log("Data:", data); 
        const destinationDetail = document.getElementById("destination-detail");
        destinationDetail.innerHTML = `
            <h1>${data.destination_name}（${data.destination_rating}）</h1>
            <p>場所: ${data.destination_address}</p>
            <p>料金: ${data.destination_fare}</p>
            <p>平均滞在時間: ${data.destination_staytime}分</p>
            <p>説明: ${data.destination_description}</p>
        `;
    })
    .catch(error => {
        console.error("Error:", error);
        const destinationDetail = document.getElementById("destination-detail");
        destinationDetail.innerHTML = `<p>データの取得に失敗しました。</p>`;
    });