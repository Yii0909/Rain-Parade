// 🌍 Initialize Map and Radar
const map = L.map('radar-map').setView([3.139, 101.6869], 6);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap'
}).addTo(map);

const radarLayer = L.tileLayer('https://tilecache.rainviewer.com/v2/radar/1696500000/256/{z}/{x}/{y}/2/1_1.png', {
  attribution: 'Weather data © RainViewer'
}).addTo(map);

// 🎛️ Radar Controls
function toggleRadar() {
  if (map.hasLayer(radarLayer)) {
    map.removeLayer(radarLayer);
  } else {
    map.addLayer(radarLayer);
  }
}

function changeOpacity(value) {
  radarLayer.setOpacity(value);
}

// 📍 Map Click Handler
map.on('click', function(e) {
  const { lat, lng } = e.latlng;
  L.popup()
    .setLatLng([lat, lng])
    .setContent(`📍 You clicked at:<br>Latitude: ${lat.toFixed(4)}<br>Longitude: ${lng.toFixed(4)}`)
    .openOn(map);
});

// 🧪 Sample Marker
const sampleWeather = {
  location: "Kuala Lumpur",
  lat: 3.139,
  lon: 101.6869,
  temp: 29.5,
  wind: 5.2,
  humidity: 78
};

const marker = L.marker([sampleWeather.lat, sampleWeather.lon]).addTo(map);
marker.bindPopup(`
  <strong>${sampleWeather.location}</strong><br>
  🌡️ Temp: ${sampleWeather.temp}°C<br>
  💨 Wind: ${sampleWeather.wind} km/h<br>
  💦 Humidity: ${sampleWeather.humidity}%
`);

// 📬 Form Submission
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("weatherForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const location = document.getElementById("location").value;
    const datetime = document.getElementById("datetime").value;

    const resultBox = document.getElementById("result");
    resultBox.innerHTML = `
      <div class="loading">
        <p>🔍 Fetching weather data...</p>
        <div class="spinner"></div>
      </div>
    `;

    try {
      const response = await fetch("https://rain-parade.onrender.com/weather", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ location, datetime })
      });

      const data = await response.json();
      const tempC = data.temp;
      const tempF = (tempC * 9 / 5 + 32).toFixed(1);

      const emojiMap = {
        "Suitable": "✅",
        "More suitable": "🌟",
        "Not suitable": "❌",
        "Inappropriate": "🚫",
        "Very inappropriate": "😬"
      };

      let lifeHTML = `
        <h3>🎯 Life Index</h3>
        <table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%; text-align: left;">
          <thead>
            <tr>
              <th>Activity</th>
              <th>Condition</th>
            </tr>
          </thead>
          <tbody>
      `;

      for (const activity in data.life_index) {
        const status = data.life_index[activity];
        const emoji = emojiMap[status] || "";
        lifeHTML += `
          <tr>
            <td>${activity}</td>
            <td>${status} ${emoji}</td>
          </tr>
        `;
      }

      lifeHTML += `
          </tbody>
        </table>
      `;

      if (response.ok) {
        resultBox.innerHTML = "";

        document.querySelector(".location-box").innerHTML = `
          <h2>📍 ${data.location}</h2>
          <p>🕒 ${data.timestamp}</p>
        `;

        document.querySelector(".stats-box").innerHTML = `
          <p>🌡️ Temp: ${tempC}°C / ${tempF}°F</p>
          <p>💨 Wind: ${data.wind} km/h</p>
          <p>💦 Humidity: ${data.humidity}%</p>
          <p>🌧️ Precipitation: ${data.precip} mm</p>
        `;

        document.querySelector(".summary-box").innerHTML = `
          <p><strong>${data.description}</strong></p>
        `;

        document.querySelector(".life-index-box").innerHTML = lifeHTML;

        let chromieComment = "";
        if (data.life_index["Beach"] === "More suitable") {
          chromieComment = "Perfect beach vibes today! 🏖️";
        } else if (data.life_index["Hiking"] === "Suitable") {
          chromieComment = "Great day to hit the trails! 🥾";
        } else {
          chromieComment = "Maybe stay cozy indoors and play with Chromie instead! 🎮";
        }

        document.querySelector(".chromie-box").innerHTML = `
          <p>🐼 Chromie says: ${chromieComment}</p>
        `;

        // 🎯 Fill Progress Bars
        document.getElementById("rainBar").style.width = `${data.precip_probability || 0}%`;
        document.getElementById("cloudBar").style.width = `${data.cloud_cover || 0}%`;
        document.getElementById("windBar").style.width = `${Math.min(data.wind_gusts || 0, 100)}%`;
        document.getElementById("heatBar").style.width = `${Math.min(data.heat_index || 0, 100)}%`;
      } else {
        resultBox.innerHTML = `❌ Error: ${data.error}`;
      }
    } catch (err) {
      resultBox.innerHTML = `❌ Failed to connect to server.`;
    }
  });
});

