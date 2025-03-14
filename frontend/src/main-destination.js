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
      <h2 class="uk-card-title">${data.destination_name}</h2>
      <hr>
      <ul class="uk-list uk-list-divider">
        <li><strong>評価:</strong> ${data.destination_rating} / 5.0</li>
        <li><strong>場所:</strong> ${data.destination_address}</li>
        <li><strong>料金:</strong> ${data.destination_fare}円</li>
        <li><strong>平均滞在時間:</strong> ${data.destination_staytime}分</li>
        <li><strong>エリア:</strong> ${data.destination_area}</li>
      </ul>
      <p class="uk-margin-small-top">
        <strong>説明:</strong><br>
        ${data.destination_description}
      </p>
      <div class="uk-text-center uk-margin-small-top">
        <img src="${data.image_url}" alt="destination image" style="max-width: 200px;">
      </div>
    `;

        const { destination_latitude, destination_longitude } = data;
        const map = L.map("map").setView([destination_latitude, destination_longitude], 15);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution:
                '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        }).addTo(map);

        L.marker([destination_latitude, destination_longitude])
            .addTo(map)
            .bindPopup(`${data.destination_name}`)
            .openPopup();
    })
    .catch(error => {
        console.error("Error:", error);
        const destinationDetail = document.getElementById("destination-detail");
        destinationDetail.innerHTML = `<p>データの取得に失敗しました。</p>`;
    });
