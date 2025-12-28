// -----------------------
// INITIALIZATION
// -----------------------
document.addEventListener('DOMContentLoaded', function () {
  initializeCharts();
  initializeEventListeners();
  startDataSimulation();
  generateSampleAlerts();
  updateDashboardCounts(); // Calculate counts before initializing chart
  initializeDeviceStatusChart();
  initializeMap();
});

// -----------------------
// GLOBAL DATA
// -----------------------
const sensors = [
  { lat: 19.0760, lng: 72.8777, name: "Central Hub", status: "online" },
  { lat: 19.2183, lng: 72.9781, name: "Thane Node", status: "online" },
  { lat: 19.0330, lng: 73.0297, name: "Navi Mumbai Node", status: "warning" },
  { lat: 18.9220, lng: 72.8347, name: "South Mumbai Node", status: "offline" }
];

function updateDashboardCounts() {
  const online = sensors.filter(s => s.status === 'online').length;
  const warning = sensors.filter(s => s.status === 'warning').length;
  const offline = sensors.filter(s => s.status === 'offline').length;

  document.getElementById('onlineCount').textContent = online;
  document.getElementById('warningCount').textContent = warning;
  document.getElementById('offlineCount').textContent = offline;
}

// -----------------------
// THEME TOGGLE
// -----------------------
document.getElementById("themeToggle").addEventListener("click", function () {
  document.documentElement.classList.toggle("dark");
  const icon = document.querySelector('#themeToggle i');
  if (document.documentElement.classList.contains('dark')) {
    icon.className = 'fas fa-sun';
    document.querySelector('#themeToggle span').textContent = 'Light Mode';

    // Update chart colors for dark mode
    updateChartColorsForDarkMode();
  } else {
    icon.className = 'fas fa-moon';
    document.querySelector('#themeToggle span').textContent = 'Dark Mode';

    // Update chart colors for light mode
    updateChartColorsForLightMode();
  }
});

// -----------------------
// SIDEBAR TOGGLE
// -----------------------
document.querySelector('.toggle-sidebar').addEventListener('click', function () {
  document.getElementById('sidebar').classList.toggle('collapsed');
  document.getElementById('content').classList.toggle('expanded');

  const icon = this.querySelector('i');
  if (document.getElementById('sidebar').classList.contains('collapsed')) {
    icon.className = 'fas fa-chevron-right';
  } else {
    icon.className = 'fas fa-chevron-left';
  }
});

// Mobile menu toggle
document.querySelector('.mobile-menu-btn').addEventListener('click', function () {
  document.getElementById('sidebar').classList.toggle('mobile-open');
});

// -----------------------
// PAGE SWITCHING
// -----------------------
function switchPage(page) {
  document.querySelectorAll("section").forEach(sec => sec.style.display = "none");
  document.getElementById(page + "Page").style.display = "block";

  document.querySelectorAll("#sidebar nav a").forEach(a => a.classList.remove("active"));
  event.currentTarget.classList.add("active");

  // Update page title
  const titles = {
    dashboard: 'Disaster Monitoring Dashboard',
    alerts: 'Alert History',
    devices: 'Connected Devices',
    settings: 'Settings'
  };

  document.getElementById('pageTitle').textContent = titles[page];

  // Close mobile menu after selection
  if (window.innerWidth < 992) {
    document.getElementById('sidebar').classList.remove('mobile-open');
  }
}

// -----------------------
// CHART OPTIONS
// -----------------------
function getChartOptions() {
  const isDarkMode = document.documentElement.classList.contains('dark');
  const gridColor = isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
  const textColor = isDarkMode ? '#e8f4ff' : '#0b2340';

  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          color: textColor
        }
      },
      zoom: {
        zoom: {
          wheel: { enabled: true },
          pinch: { enabled: true },
          mode: 'x',
          maxScale: 5
        },
        pan: {
          enabled: true,
          mode: 'x'
        },
        limits: {
          x: { min: 0, max: "original" }
        }
      }
    },
    scales: {
      x: {
        ticks: {
          maxTicksLimit: 6,
          color: textColor
        },
        grid: {
          color: gridColor
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: gridColor
        },
        ticks: {
          color: textColor
        }
      }
    },
    elements: {
      point: {
        radius: 2,
        hoverRadius: 5
      }
    },
    interaction: {
      intersect: false,
      mode: 'index'
    },
    animations: {
      tension: {
        duration: 1000,
        easing: 'linear'
      }
    }
  };
}

// -----------------------
// CREATE CHARTS (WITH SOLID COLORS - NO GRADIENT ISSUES)
// -----------------------
let soilChart, humidityChart, windChart, tempChart, deviceStatusChart;

function getChartDatasetConfig(type) {
  const configs = {
    soil: {
      label: "Soil Moisture (%)",
      borderColor: "#22c55e",
      backgroundColor: "rgba(34, 197, 94, 0.2)",
      fill: true,
      tension: 0.3,
      borderWidth: 2,
      pointBackgroundColor: "#22c55e",
      pointBorderColor: "#ffffff",
      pointBorderWidth: 1
    },
    humidity: {
      label: "Humidity (%)",
      borderColor: "#0ea5e9",
      backgroundColor: "rgba(14, 165, 233, 0.2)",
      fill: true,
      tension: 0.3,
      borderWidth: 2,
      pointBackgroundColor: "#0ea5e9",
      pointBorderColor: "#ffffff",
      pointBorderWidth: 1
    },
    wind: {
      label: "Wind Speed (km/h)",
      borderColor: "#f97316",
      backgroundColor: "rgba(249, 115, 22, 0.2)",
      fill: true,
      tension: 0.3,
      borderWidth: 2,
      pointBackgroundColor: "#f97316",
      pointBorderColor: "#ffffff",
      pointBorderWidth: 1
    },
    temp: {
      label: "Temperature (°C)",
      borderColor: "#ef4444",
      backgroundColor: "rgba(239, 68, 68, 0.2)",
      fill: true,
      tension: 0.3,
      borderWidth: 2,
      pointBackgroundColor: "#ef4444",
      pointBorderColor: "#ffffff",
      pointBorderWidth: 1
    }
  };

  return configs[type];
}

function initializeCharts() {
  const soilCtx = document.getElementById("soilChart").getContext("2d");
  const humidityCtx = document.getElementById("humidityChart").getContext("2d");
  const windCtx = document.getElementById("windChart").getContext("2d");
  const tempCtx = document.getElementById("tempChart").getContext("2d");

  soilChart = new Chart(soilCtx, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        ...getChartDatasetConfig('soil')
      }]
    },
    options: getChartOptions()
  });

  humidityChart = new Chart(humidityCtx, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        ...getChartDatasetConfig('humidity')
      }]
    },
    options: getChartOptions()
  });

  windChart = new Chart(windCtx, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        ...getChartDatasetConfig('wind')
      }]
    },
    options: getChartOptions()
  });

  tempChart = new Chart(tempCtx, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        ...getChartDatasetConfig('temp')
      }]
    },
    options: getChartOptions()
  });
}

function initializeDeviceStatusChart() {
  const ctx = document.getElementById("deviceStatusChart").getContext("2d");
  const isDarkMode = document.documentElement.classList.contains('dark');
  const textColor = isDarkMode ? '#e8f4ff' : '#0b2340';

  deviceStatusChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Online", "Warning", "Offline"],
      datasets: [{
        data: [
          sensors.filter(s => s.status === 'online').length,
          sensors.filter(s => s.status === 'warning').length,
          sensors.filter(s => s.status === 'offline').length
        ],
        backgroundColor: ["#22c55e", "#eab308", "#ef4444"],
        borderWidth: 0,
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: textColor,
            font: {
              size: 12
            }
          }
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              return `${context.label}: ${context.parsed} devices`;
            }
          }
        }
      },
      cutout: '60%'
    }
  });
}


// -----------------------
// MAP INITIALIZATION
// -----------------------
let map;

function initializeMap() {
  // Initialize map centered on Mumbai (or any default location)
  map = L.map('map').setView([19.0760, 72.8777], 10);

  // Fix for map not rendering correctly if container is hidden/resized
  setTimeout(() => {
    map.invalidateSize();
  }, 100);

  // Add OpenStreetMap base layer
  const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  // API Key for OpenWeatherMap (Placeholder)
  const OWM_API_KEY = 'd553762b871e048e31ec298aa3099e8b'; // Replace with valid key

  // Weather Layers
  const precipitationLayer = L.tileLayer(`https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=${OWM_API_KEY}`, {
    attribution: '&copy; <a href="https://openweathermap.org/">OpenWeatherMap</a>'
  });

  const cloudsLayer = L.tileLayer(`https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid=${OWM_API_KEY}`, {
    attribution: '&copy; <a href="https://openweathermap.org/">OpenWeatherMap</a>'
  });

  const tempLayer = L.tileLayer(`https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=${OWM_API_KEY}`, {
    attribution: '&copy; <a href="https://openweathermap.org/">OpenWeatherMap</a>'
  });

  const windLayer = L.tileLayer(`https://tile.openweathermap.org/map/wind_new/{z}/{x}/{y}.png?appid=${OWM_API_KEY}`, {
    attribution: '&copy; <a href="https://openweathermap.org/">OpenWeatherMap</a>'
  });

  // Layer Control
  const baseMaps = {
    "OpenStreetMap": osmLayer
  };

  const overlayMaps = {
    "Precipitation": precipitationLayer,
    "Clouds": cloudsLayer,
    "Temperature": tempLayer,
    "Wind Speed": windLayer
  };

  L.control.layers(baseMaps, overlayMaps).addTo(map);

  // Add sensor markers from global data
  sensors.forEach(sensor => {
    let color = sensor.status === 'online' ? 'green' : (sensor.status === 'warning' ? 'orange' : 'red');

    const circle = L.circleMarker([sensor.lat, sensor.lng], {
      color: color,
      fillColor: color,
      fillOpacity: 0.5,
      radius: 8
    }).addTo(map);

    circle.bindPopup(`<b>${sensor.name}</b><br>Status: ${sensor.status.toUpperCase()}`);
  });
}

// -----------------------
// UPDATE CHART COLORS FOR THEME CHANGES
// -----------------------
function updateChartColorsForDarkMode() {
  const gridColor = 'rgba(255,255,255,0.1)';
  const textColor = '#e8f4ff';

  // Update line charts
  [soilChart, humidityChart, windChart, tempChart].forEach(chart => {
    if (chart) {
      chart.options.scales.x.grid.color = gridColor;
      chart.options.scales.y.grid.color = gridColor;
      chart.options.scales.x.ticks.color = textColor;
      chart.options.scales.y.ticks.color = textColor;
      chart.options.plugins.legend.labels.color = textColor;
      chart.update();
    }
  });

  // Update device status chart
  if (deviceStatusChart) {
    deviceStatusChart.options.plugins.legend.labels.color = textColor;
    deviceStatusChart.update();
  }
}

function updateChartColorsForLightMode() {
  const gridColor = 'rgba(0,0,0,0.1)';
  const textColor = '#0b2340';

  // Update line charts
  [soilChart, humidityChart, windChart, tempChart].forEach(chart => {
    if (chart) {
      chart.options.scales.x.grid.color = gridColor;
      chart.options.scales.y.grid.color = gridColor;
      chart.options.scales.x.ticks.color = textColor;
      chart.options.scales.y.ticks.color = textColor;
      chart.options.plugins.legend.labels.color = textColor;
      chart.update();
    }
  });

  // Update device status chart
  if (deviceStatusChart) {
    deviceStatusChart.options.plugins.legend.labels.color = textColor;
    deviceStatusChart.update();
  }
}

// -----------------------
// RESET ZOOM
// -----------------------
function resetZoom(type) {
  switch (type) {
    case "soil":
      if (soilChart) soilChart.resetZoom();
      break;
    case "humidity":
      if (humidityChart) humidityChart.resetZoom();
      break;
    case "wind":
      if (windChart) windChart.resetZoom();
      break;
    case "temp":
      if (tempChart) tempChart.resetZoom();
      break;
  }
}

// -----------------------
// FULLSCREEN CHARTS
// -----------------------
function openFullscreen(type) {
  const modal = new bootstrap.Modal(document.getElementById('chartModal'));
  const modalChartCanvas = document.getElementById('modalChart');
  const modalTitle = document.getElementById('modalChartTitle');

  let chartToClone;
  let title;

  switch (type) {
    case "soil":
      chartToClone = soilChart;
      title = "Soil Moisture Trend";
      break;
    case "humidity":
      chartToClone = humidityChart;
      title = "Humidity Trend";
      break;
    case "wind":
      chartToClone = windChart;
      title = "Wind Speed Trend";
      break;
    case "temp":
      chartToClone = tempChart;
      title = "Temperature Trend";
      break;
    default:
      return;
  }

  modalTitle.textContent = title;

  // Create a copy of the chart for the modal
  const ctx = modalChartCanvas.getContext('2d');

  // Destroy existing chart if it exists
  if (window.modalChartInstance) {
    window.modalChartInstance.destroy();
  }

  // Create new chart with the same data but optimized for fullscreen
  const options = JSON.parse(JSON.stringify(chartToClone.options));
  options.maintainAspectRatio = true;
  options.aspectRatio = 1.8;
  options.plugins.legend.position = 'top';

  window.modalChartInstance = new Chart(ctx, {
    type: chartToClone.config.type,
    data: JSON.parse(JSON.stringify(chartToClone.data)),
    options: options
  });

  modal.show();
}

// -----------------------
// DATA SIMULATION
// -----------------------
let dataInterval;
let refreshRate = 5000; // 5 seconds

function startDataSimulation() {
  // Clear any existing interval
  if (dataInterval) clearInterval(dataInterval);

  // Set new interval with current refresh rate
  dataInterval = setInterval(() => {
    const now = new Date();
    const t = now.toLocaleTimeString();

    // Generate realistic data with some trends
    const soil = Math.max(15, Math.min(85,
      (Math.sin(now.getMinutes() / 5) * 10) + 50 + (Math.random() * 10 - 5)
    ));
    const hum = Math.max(20, Math.min(90,
      (Math.cos(now.getMinutes() / 7) * 15) + 60 + (Math.random() * 8 - 4)
    ));
    const wind = Math.max(5, Math.min(45,
      (Math.sin(now.getMinutes() / 3) * 8) + 25 + (Math.random() * 6 - 3)
    ));
    const temp = Math.max(10, Math.min(35,
      (Math.sin(now.getMinutes() / 10) * 5) + 22 + (Math.random() * 4 - 2)
    ));

    // Update cards with formatted values
    document.getElementById("soilValue").innerText = Math.round(soil) + "%";
    document.getElementById("humidityValue").innerText = Math.round(hum) + "%";
    document.getElementById("windValue").innerText = Math.round(wind) + " km/h";
    document.getElementById("tempValue").innerText = Math.round(temp) + "°C";

    // AI Risk Assessment
    calculateFloodRisk(soil, hum);

    // Update charts
    const charts = [soilChart, humidityChart, windChart, tempChart];
    const values = [soil, hum, wind, temp];

    charts.forEach((chart, index) => {
      if (chart && chart.data) {
        chart.data.labels.push(t);
        chart.data.datasets[0].data.push(values[index]);

        // Keep only last 15 data points for better performance
        if (chart.data.labels.length > 15) {
          chart.data.labels.shift();
          chart.data.datasets[0].data.shift();
        }
      }
    });

    // Update all charts
    Chart.helpers.each(Chart.instances, (chart) => {
      chart.update('none');
    });

  }, refreshRate);
}

// -----------------------
// AI PREDICTIVE ANALYTICS
// -----------------------
function calculateFloodRisk(soil, humidity) {
  const riskCard = document.getElementById('aiRiskCard');
  const riskLevel = document.getElementById('riskLevel');
  const aiAnalysis = document.getElementById('aiAnalysis');

  let risk = "LOW";
  let color = "#22c55e"; // Green
  let message = "Conditions are stable. No immediate flood risk.";

  // Predictive Logic
  if (soil > 80) {
    risk = "CRITICAL";
    color = "#ef4444"; // Red
    message = "CRITICAL: Soil saturation > 80%. High flood probability.";
  } else if (soil > 60 || (soil > 50 && humidity > 85)) {
    risk = "HIGH";
    color = "#f97316"; // Orange
    message = "Warning: High soil moisture detected. Monitor closely.";
  } else if (soil > 40) {
    risk = "MEDIUM";
    color = "#eab308"; // Yellow
    message = "Caution: Soil moisture rising. Moderate risk.";
  }

  // Update UI
  riskLevel.textContent = risk + " RISK";
  riskLevel.style.color = color;
  aiAnalysis.textContent = message;
  riskCard.style.borderLeftColor = color;

  // Visual effect for critical risk
  if (risk === "CRITICAL") {
    riskCard.style.boxShadow = "0 0 15px rgba(239, 68, 68, 0.4)";
  } else {
    riskCard.style.boxShadow = "0 2px 14px var(--shadow)";
  }
}

// -----------------------
// ALERT SYSTEM
// -----------------------
let alertList = document.getElementById("alertList");
let alertCounts = { critical: 0, warning: 0, info: 0 };

function addAlert(text, type = "warning") {
  // Update alert counts
  alertCounts[type]++;
  updateAlertCounts();

  // Show banner for critical alerts
  if (type === "critical") {
    document.getElementById("alertBanner").style.display = "block";
    document.getElementById("alertBanner").innerText = text;

    // Auto-hide banner after 10 seconds
    setTimeout(() => {
      document.getElementById("alertBanner").style.display = "none";
    }, 10000);
  }

  // Add to alert list
  let item = document.createElement("li");

  let iconClass, alertClass, alertTypeText;

  switch (type) {
    case "critical":
      iconClass = "fas fa-exclamation-circle";
      alertClass = "alert-critical";
      alertTypeText = "CRITICAL";
      break;
    case "warning":
      iconClass = "fas fa-exclamation-triangle";
      alertClass = "alert-warning";
      alertTypeText = "WARNING";
      break;
    case "info":
      iconClass = "fas fa-info-circle";
      alertClass = "alert-info";
      alertTypeText = "INFO";
      break;
  }

  item.innerHTML = `
    <div class="alert-icon ${alertClass}">
      <i class="${iconClass}"></i>
    </div>
    <div class="alert-content">
      <div><strong>${alertTypeText}:</strong> ${text}</div>
      <div class="alert-time">${new Date().toLocaleString()}</div>
    </div>
  `;

  alertList.prepend(item);

  // Limit alert list to 50 items
  if (alertList.children.length > 50) {
    alertList.removeChild(alertList.lastChild);
  }

  // Show popup notification
  showPopupNotification(text, type);
}

function showPopupNotification(text, type) {
  let popup = document.getElementById("popup");
  popup.style.display = "block";
  popup.innerText = text;

  // Set color based on alert type
  switch (type) {
    case "critical":
      popup.style.background = "#ef4444";
      break;
    case "warning":
      popup.style.background = "#eab308";
      break;
    case "info":
      popup.style.background = "#0ea5e9";
      break;
  }

  // Auto-hide after 5 seconds
  setTimeout(() => {
    popup.style.display = "none";
  }, 5000);
}

function updateAlertCounts() {
  // Update header counts if needed
  document.getElementById("warningCount").textContent =
    alertCounts.critical + alertCounts.warning;
}

function generateSampleAlerts() {
  // Add some sample alerts
  setTimeout(() => addAlert("Soil moisture level critically low in Sector B", "critical"), 1000);
  setTimeout(() => addAlert("Wind speed exceeding safe threshold", "warning"), 2000);
  setTimeout(() => addAlert("New device connected to network", "info"), 3000);
  setTimeout(() => addAlert("Temperature sensor calibration required", "warning"), 4000);
}

// Trigger random alerts
setInterval(() => {
  if (Math.random() < 0.15) { // 15% chance every interval
    const alertTypes = ["critical", "warning", "info"];
    const weights = [0.2, 0.5, 0.3]; // Probability weights
    const random = Math.random();

    let type;
    if (random < weights[0]) type = "critical";
    else if (random < weights[0] + weights[1]) type = "warning";
    else type = "info";

    const messages = {
      critical: [
        "Critical: Soil erosion detected in Sector C",
        "Critical: Water level rising rapidly",
        "Critical: Structural integrity compromised",
        "Critical: Power failure in Node 7"
      ],
      warning: [
        "Warning: High humidity levels detected",
        "Warning: Wind gusts exceeding 50 km/h",
        "Warning: Temperature fluctuation detected",
        "Warning: Network latency increasing"
      ],
      info: [
        "Info: Data sync completed successfully",
        "Info: Backup system activated",
        "Info: New firmware update available",
        "Info: Scheduled maintenance in 2 hours"
      ]
    };

    const message = messages[type][Math.floor(Math.random() * messages[type].length)];
    addAlert(message, type);
  }
}, 15000);

// -----------------------
// SETTINGS
// -----------------------
function initializeEventListeners() {
  // Refresh rate slider
  const refreshSlider = document.getElementById('refreshRate');
  const refreshValue = document.getElementById('refreshValue');

  refreshSlider.addEventListener('input', function () {
    refreshValue.textContent = this.value;
    refreshRate = this.value * 1000;
    startDataSimulation();
  });

  // Smooth lines toggle
  const smoothLinesToggle = document.getElementById('smoothLines');
  smoothLinesToggle.addEventListener('change', function () {
    const tension = this.checked ? 0.3 : 0;
    const charts = [soilChart, humidityChart, windChart, tempChart];

    charts.forEach(chart => {
      if (chart && chart.data && chart.data.datasets[0]) {
        chart.data.datasets[0].tension = tension;
        chart.update();
      }
    });
  });

  // Data points toggle
  const dataPointsToggle = document.getElementById('dataPoints');
  dataPointsToggle.addEventListener('change', function () {
    const radius = this.checked ? 2 : 0;
    const charts = [soilChart, humidityChart, windChart, tempChart];

    charts.forEach(chart => {
      if (chart && chart.data && chart.data.datasets[0]) {
        chart.data.datasets[0].pointRadius = radius;
        chart.update();
      }
    });
  });

  // Alert filter buttons
  document.querySelectorAll('.btn-outline-primary').forEach(btn => {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.btn-outline-primary').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      // Implement alert filtering here if needed
    });
  });
}

// -----------------------
// PERFORMANCE OPTIMIZATIONS
// -----------------------
// Throttle chart updates during zoom/pan
function throttleChartUpdates() {
  let isUpdating = false;

  return function (chart) {
    if (!isUpdating) {
      isUpdating = true;
      chart.update();

      setTimeout(() => {
        isUpdating = false;
      }, 100);
    }
  };
}

const throttledUpdate = throttleChartUpdates();

// Initialize throttled updates for charts
[soilChart, humidityChart, windChart, tempChart].forEach(chart => {
  if (chart) {
    chart.options.animation = false;
  }
});