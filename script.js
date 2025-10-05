document.getElementById("weatherForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const location = document.getElementById("location").value;
  const datetime = document.getElementById("datetime").value;

  const resultBox = document.getElementById("result");
  resultBox.innerHTML = "🔍 Fetching weather data...";

  try {
    const response = await fetch("https://rain-parade.onrender.com/weather", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ location, datetime })
    });

    const data = await response.json();
    const tempC = data.temp;
const tempF = (tempC * 9/5 + 32).toFixed(1); // Rounded to 1 decimal
    
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
      resultBox.innerHTML = `
  <h2>📍 ${data.location}</h2>
  <p>🕒 ${data.timestamp}</p>
  <p>🌡️ Temperature: ${tempC}°C / ${tempF}°F</p>
  <p>💨 Wind: ${data.wind} km/h</p>
  <p>🌧️ Precipitation: ${data.precip} mm</p>
  <p>💦 Humidity: ${data.humidity}%</p>
  <p>🔍 Summary: <strong>${data.description}</strong></p>
  ${lifeHTML}
`;

    } else {
      resultBox.innerHTML = `❌ Error: ${data.error}`;
    }
  } catch (err) {
    resultBox.innerHTML = `❌ Failed to connect to server.`;
  }
});




