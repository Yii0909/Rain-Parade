document.getElementById("weatherForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const location = document.getElementById("location").value;
  const datetime = document.getElementById("datetime").value;

  const resultBox = document.getElementById("result");
  resultBox.innerHTML = "🔍 Fetching weather data...";

  try {
    const response = await fetch("http://localhost:5000/weather", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ location, datetime })
    });

    const data = await response.json();

    if (response.ok) {
      resultBox.innerHTML = `
        <h2>📍 ${data.location}</h2>
        <p>🕒 ${data.timestamp}</p>
        <p>🌡️ Temperature: ${data.temp}°C</p>
        <p>💨 Wind: ${data.wind} km/h</p>
        <p>🌧️ Precipitation: ${data.precip} mm</p>
        <p>💦 Humidity: ${data.humidity}%</p>
        <p>🔍 Summary: <strong>${data.description}</strong></p>
      `;
    } else {
      resultBox.innerHTML = `❌ Error: ${data.error}`;
    }
  } catch (err) {
    resultBox.innerHTML = `❌ Failed to connect to server.`;
  }
});
