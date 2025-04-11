document.addEventListener('DOMContentLoaded', () => {
    // Elements for weather lookup
    const cityInput = document.getElementById('cityInput');
    const dateInput = document.getElementById('dateInput');
    const searchBtn = document.getElementById('searchBtn');
    const weatherResult = document.getElementById('weatherResult');
  
    // Elements for export
    const exportCity = document.getElementById('exportCity');
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    const exportBtn = document.getElementById('exportBtn');
  
    // The animated container
    const weatherAnimation = document.getElementById('weatherAnimation');
  
    // Simple function to guess a weather condition
    function getWeatherCondition(temperature, windSpeed) {
      // Example logic:
      // - Very cold => snow
      // - High wind => storm
      // - Hot => sunny
      // - Otherwise => cloudy
      if (temperature <= 0) {
        return 'snow';
      } else if (windSpeed >= 10) {
        return 'storm';
      } else if (temperature >= 25) {
        return 'sunny';
      } else {
        return 'cloudy';
      }
    }
  
    // Handle weather lookup
    searchBtn.addEventListener('click', async () => {
      const city = cityInput.value.trim();
      const dateVal = dateInput.value.trim();
  
      if (!city || !dateVal) {
        alert("Please enter both city and date.");
        return;
      }
  
      try {
        // Fetch weather from /api/weather?city=...&date=...
        const response = await fetch(`/api/weather?city=${encodeURIComponent(city)}&date=${encodeURIComponent(dateVal)}`);
        const data = await response.json();
  
        if (data.error) {
          weatherResult.innerHTML = `<p class="error">${data.error}</p>`;
          // Reset animation
          weatherAnimation.className = 'weather-animation';
        } else {
          // Display the weather info
          weatherResult.innerHTML = `
            <h3>Weather for ${data.city} on ${data.date}</h3>
            <p><strong>Temperature:</strong> ${data.temperature ?? 'N/A'} °C</p>
            <p><strong>Humidity:</strong> ${data.humidity ?? 'N/A'} %</p>
            <p><strong>Wind Speed:</strong> ${data.wind_speed ?? 'N/A'} m/s</p>
            <p><strong>Air Quality:</strong> ${data.air_quality !== null ? data.air_quality : 'N/A'}</p>
            <p><strong>UV Index:</strong> ${data.uv_index !== null ? data.uv_index : 'N/A'}</p>
            <p><strong>Latitude:</strong> ${data.latitude ?? 'N/A'}</p>
            <p><strong>Longitude:</strong> ${data.longitude ?? 'N/A'}</p>
            <p><strong>Last Updated:</strong> ${data.created_at}</p>
          `;
  
          // Determine animation based on temperature + wind speed
          const temp = parseFloat(data.temperature) || 0;
          const wind = parseFloat(data.wind_speed) || 0;
          const conditionClass = getWeatherCondition(temp, wind);
  
          // Apply the animation class
          weatherAnimation.className = `weather-animation ${conditionClass}`;
        }
      } catch (err) {
        weatherResult.innerHTML = `<p class="error">Error fetching data: ${err}</p>`;
        // Reset animation
        weatherAnimation.className = 'weather-animation';
      }
    });
  
    // Handle export
    exportBtn.addEventListener('click', () => {
      // Build query params
      const cityParam = exportCity.value.trim();
      const startParam = startDate.value.trim();
      const endParam = endDate.value.trim();
  
      let url = '/api/export?';
      if (cityParam) url += `city=${encodeURIComponent(cityParam)}&`;
      if (startParam) url += `start_date=${encodeURIComponent(startParam)}&`;
      if (endParam) url += `end_date=${encodeURIComponent(endParam)}&`;
  
      // Remove trailing '&' or '?' if any
      url = url.replace(/[&?]$/, '');
  
      // Navigate to the export endpoint to trigger CSV download
      window.location.href = url;
    });
  });
  