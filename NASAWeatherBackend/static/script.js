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

    // ⏳ Timeout fallback
    setTimeout(() => {
      if (resultBox.innerHTML.includes("spinner")) {
        resultBox.innerHTML += `<p>⏳ Still waiting... Chromie might be chasing clouds. Try again soon!</p>`;
      }
    }, 10000);

    try {
      console.log("📡 Sending request:", { location, datetime });

      const response = await fetch("https://rain-parade.onrender.com/weather", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ location, datetime })
      });

      console.log("📬 Response status:", response.status);

      const data = await response.json();

      if (!response.ok) {
        resultBox.innerHTML = `
          <p>❌ Error: ${data.error}</p>
          <p>🐼 Chromie says: “Hmm... the weather spirits aren’t responding. Try again later!”</p>
          <button onclick="location.reload()">🔁 Retry</button>
        `;
        return;
      }

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
          <thead><tr><th>Activity</th><th>Condition</th></tr></thead><tbody>
      `;

      for (const activity in data.life_index) {
        const status = data.life_index[activity];
        const emoji = emojiMap[status] || "";
        lifeHTML += `<tr><td>${activity}</td><td>${status} ${emoji}</td></tr>`;
      }

      lifeHTML += `</tbody></table>`;

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

      document.querySelector(".summary-box").innerHTML = `<p><strong>${data.description}</strong></p>`;
      document.querySelector(".life-index-box").innerHTML = lifeHTML;

      // 🐼 Chromie Commentary
      let chromieComment = "";
      if (data.life_index["Beach"] === "More suitable") {
        chromieComment = "Perfect beach vibes today! 🏖️ Don’t forget sunscreen and snacks!";
      } else if (data.life_index["Hiking"] === "Suitable") {
        chromieComment = "Great day to hit the trails! 🥾 Chromie recommends a scenic selfie stop!";
      } else {
        chromieComment = "Not the best weather out there—Chromie recommends hot cocoa and cartoons ☕📺";
      }

      document.querySelector(".chromie-box").innerHTML = `
        <p>🐼 Chromie says: ${chromieComment}</p>
      `;

      // 🎯 Fill Progress Bars
      document.getElementById("rainBar").style.width = `${data.precip_probability || 0}%`;
      document.getElementById("cloudBar").style.width = `${data.cloud_cover || 0}%`;
      document.getElementById("windBar").style.width = `${Math.min(data.wind_gusts || 0, 100)}%`;
      document.getElementById("heatBar").style.width = `${Math.min(data.heat_index || 0, 100)}%`;

    } catch (err) {
      console.error("❌ Fetch failed:", err);
      resultBox.innerHTML = `
        <p>❌ Failed to connect to server.</p>
        <p>🐼 Chromie says: “Oops! My weather wand isn’t working right now.”</p>
        <button onclick="location.reload()">🔁 Try Again</button>
      `;
    }
  });
});
