const weatherForm = document.getElementById('weatherForm');
const cityInput = document.getElementById('cityInput');
const unitToggle = document.getElementById('unitToggle');
const weatherResult = document.getElementById('weatherResult');
const weatherData = document.getElementById('weatherData');
const travelData = document.getElementById('travelData');
const exportBtn = document.getElementById('exportBtn');
const forecast = document.getElementById('forecast');
const forecastCards = document.getElementById('forecastCards');

const OPENWEATHER_API = "45e97eb6e5e89357830f2a793be16338";

let currentUnit = "metric"; // default: Celsius

weatherForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const city = cityInput.value.trim();
  if (!city) return;

  weatherData.innerHTML = "Loading...";
  travelData.innerHTML = "";
  forecastCards.innerHTML = "";

  try {
    const unitParam = currentUnit === "metric" ? "metric" : "imperial";

    const res = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=${city}&units=${unitParam}&appid=${OPENWEATHER_API}`);
    const data = await res.json();

    if (data.cod !== 200) {
      weatherData.innerHTML = `<p class="text-red-500">City not found</p>`;
      return;
    }

    renderWeather(data);
    await suggestTravel(city, data.weather[0].main.toLowerCase(), data.main.temp);
    await renderForecast(city);
    weatherResult.classList.remove('hidden');
    forecast.classList.remove('hidden');

    await fetch("/save", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        city,
        unit: currentUnit
      })
    });

  } catch (err) {
    weatherData.innerHTML = `<p class="text-red-500">Error fetching data</p>`;
    console.error(err);
  }
});

unitToggle.addEventListener("change", () => {
  currentUnit = unitToggle.checked ? "imperial" : "metric";
});

function renderWeather(data) {
  const temp = data.main.temp;
  const weather = data.weather[0].main;
  const humidity = data.main.humidity;
  const wind = data.wind.speed;
  const pressure = data.main.pressure;
  const visibility = data.visibility / 1000;
  const sunrise = new Date(data.sys.sunrise * 1000).toLocaleTimeString();
  const sunset = new Date(data.sys.sunset * 1000).toLocaleTimeString();

  weatherData.innerHTML = `
    <p><strong>Temperature:</strong> ${temp}° ${currentUnit === 'metric' ? 'C' : 'F'}</p>
    <p><strong>Condition:</strong> ${weather}</p>
    <p><strong>Humidity:</strong> ${humidity}%</p>
    <p><strong>Wind Speed:</strong> ${wind} ${currentUnit === 'metric' ? 'm/s' : 'mph'}</p>
    <p><strong>Pressure:</strong> ${pressure} hPa</p>
    <p><strong>Visibility:</strong> ${visibility} km</p>
    <p><strong>Sunrise:</strong> ${sunrise}</p>
    <p><strong>Sunset:</strong> ${sunset}</p>
  `;
}

// 🌍 Dynamic Travel Suggestions with Serper image integration
async function suggestTravel(city, weatherCondition, temp) {
  try {
    const placeRes = await fetch('/places', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ city, weather: weatherCondition })
    });

    const data = await placeRes.json();
    const places = data.places;

    let imageBlocks = ``;

    for (const place of places) {
      const query = `${place} ${city}`;
      const imgRes = await fetch('/image-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });

      const imgData = await imgRes.json();

      if (imgData.length > 0) {
        const { thumbnail, title, link } = imgData[0];
        imageBlocks += `
          <div>
            <a href="${link}" target="_blank">
              <img src="${thumbnail}" alt="${title}" class="rounded-xl shadow w-full h-40 object-cover" />
            </a>
            <p class="text-xs mt-1 text-gray-600">${title}</p>
          </div>
        `;
      }
    }

    travelData.innerHTML = `
      <p><strong>Top Spots in ${city}:</strong></p>
      <p class="text-sm text-gray-500">Best for ${weatherCondition.toLowerCase()} weather (${Math.round(temp)}° ${currentUnit === 'metric' ? 'C' : 'F'})</p>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
        ${imageBlocks}
      </div>
    `;

  } catch (err) {
    travelData.innerHTML = `<p class="text-red-500">Could not fetch travel suggestions.</p>`;
    console.error(err);
  }
}

async function renderForecast(city) {
  const res = await fetch(`https://api.openweathermap.org/data/2.5/forecast?q=${city}&units=${currentUnit}&appid=${OPENWEATHER_API}`);
  const data = await res.json();

  const daily = {};
  for (const item of data.list) {
    const date = item.dt_txt.split(" ")[0];
    if (!daily[date]) daily[date] = [];
    daily[date].push(item);
  }

  const sliced = Object.entries(daily).slice(0, 5);

  forecastCards.innerHTML = sliced.map(([date, list]) => {
    const temps = list.map(i => i.main.temp);
    const avgTemp = (temps.reduce((a, b) => a + b, 0) / temps.length).toFixed(1);
    const icon = list[0].weather[0].icon;
    return `
      <div class="forecast-card p-4 text-center">
        <p class="font-bold">${new Date(date).toLocaleDateString()}</p>
        <img src="http://openweathermap.org/img/wn/${icon}@2x.png" class="mx-auto w-16" />
        <p>${avgTemp}° ${currentUnit === 'metric' ? 'C' : 'F'}</p>
      </div>
    `;
  }).join('');
}

// 📄 Export to PDF
exportBtn.addEventListener("click", () => {
  const pdfContent = document.getElementById("weatherResult");

  html2canvas(pdfContent).then((canvas) => {
    const imgData = canvas.toDataURL("image/png");
    const pdf = new jspdf.jsPDF({
      orientation: "portrait",
      unit: "px",
      format: "a4",
    });

    const width = pdf.internal.pageSize.getWidth();
    const height = (canvas.height * width) / canvas.width;

    pdf.addImage(imgData, "PNG", 0, 0, width, height);
    pdf.save("weather_report.pdf");
  });
});
