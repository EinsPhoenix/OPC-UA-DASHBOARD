let weatherDataSaved = null;
async function getGeoLocation() {
    try {
        const position = await new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject);
        });

        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;


        const csrfToken = getCookie('csrftoken');


        const response = await fetch('api/set_location/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                latitude: latitude,
                longitude: longitude
            })
        });

        if (!response.ok) {
            throw new Error('Failed to send location data');
        }
        else {
            const responseData = await response.json();

            createWeatherChart(responseData.weather_data);
            weatherDataSaved = responseData.weather_data;

            initializeTemperatureGaugeCurrent();

            updateCurrentTemperature(weatherDataSaved);

            initializeHumidityGaugeCurrent();
            updateCurrentHumidity(weatherDataSaved);

        }

        console.log('Location sent successfully!');
    } catch (error) {
        console.error('Error occurred:', error);
    }
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}






function createWeatherChart(weatherData) {

    const hourlyData = weatherData.days[0].hours;
    const labels = hourlyData.map(hour => hour.datetime);
    const temperatures = hourlyData.map(hour => ((hour.temp - 32) * 5) / 9);


    const ctx = document.getElementById('weatherChart').getContext('2d');
    const weatherChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Temperature (°C)',
                data: temperatures,
                borderColor: '#7e3fff',
                backgroundColor: 'rgba(126, 63, 255, 0.2)',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointBackgroundColor: '#6a19d6',
                pointBorderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 0 },
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.1)' },
                    ticks: { color: '#e0e0e0' }
                },
                y: {
                    grid: { color: 'rgba(255,255,255,0.1)' },
                    ticks: { color: '#e0e0e0' },
                    suggestedMin: 0,
                    suggestedMax: this.maxValue
                }
            }
        }
    });
}
function checkMaxValue(input) {
    const value = parseInt(input.value, 10);
    const max = parseInt(input.max, 10);
    const min = parseInt(input.min, 10);

    if (isNaN(value)) {
        input.value = "";
    } else if (value > max) {
        input.value = max;
    } else if (value < min) {
        input.value = min;
    }
}






function initializeTemperatureGaugeCurrent() {
    const ctx = document.getElementById("currentTemp");
    this.chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Temperature'],
            datasets: [{
                data: [50, 50],
                backgroundColor: [
                    'rgba(126, 63, 255, 0.8)',
                    'rgba(24, 0, 71, 0.63)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '80%',
            rotation: -90,
            circumference: 180,
            plugins: {
                tooltip: { enabled: false },
                legend: { display: false }
            }
        },
        plugins: [{
            id: 'temperatureText',
            beforeDraw: function (chart) {
                const { ctx, chartArea, data } = chart;
                const centerX = (chartArea.left + chartArea.right) / 2;
                const centerY = (chartArea.bottom + chartArea.top) / 2 + 20;
                // Berechne die tatsächliche Temperatur aus dem normalisierten Wert zurück
                const minTemp = -50;
                const maxTemp = 50;
                const normalizedValue = data.datasets[0].data[0];
                const actualTemp = ((normalizedValue / 50) * (maxTemp - minTemp) + minTemp).toFixed(1);

                ctx.clearRect(centerX - 50, centerY - 30, 100, 50);
                ctx.font = 'bold 36px Inter, Arial';
                ctx.fillStyle = '#7e3fff';
                ctx.textAlign = 'center';
                ctx.fillText(`${actualTemp}°C`, centerX, centerY);
            }
        }]
    });
}

function updateTemperatureGaugeCurrent(temp) {
    const chart = document.getElementById("currentTemp");
    if (!chart) {
        console.error('Chart ist nicht initialisiert');
        return;
    }

    const minTemp = -50;
    const maxTemp = 50;


    const normalizedTemp = Math.min(Math.max(temp, minTemp), maxTemp);


    const gaugeValue = ((normalizedTemp - minTemp) / (maxTemp - minTemp)) * 50;

    this.chart.data.datasets[0].data = [gaugeValue, 50 - gaugeValue];
    this.chart.update();
}



function getCurrentTemperature(weatherData) {
    try {
        const now = new Date();
        const currentHour = now.getHours();
        const currentMinute = now.getMinutes();


        if (!weatherData?.days?.[0]?.hours) {
            console.error('Ungültige weatherData Struktur');
            return 0;
        }

        const hourlyData = weatherData.days[0].hours;


        let currentHourData = hourlyData.find(hour => {
            const hourTime = hour.datetime.split(':')[0];
            return parseInt(hourTime) === currentHour;
        });

        let nextHourData = hourlyData.find(hour => {
            const hourTime = hour.datetime.split(':')[0];
            return parseInt(hourTime) === (currentHour + 1) % 24;
        });


        if (!nextHourData) {
            nextHourData = currentHourData;
        }



        if (!currentHourData && weatherData.currentConditions) {
            currentHourData = weatherData.currentConditions;
            nextHourData = currentHourData;
        }


        if (!currentHourData || !nextHourData) {
            console.error('Keine Temperaturdaten verfügbar');
            return 0;
        }


        const currentHourTemp = ((currentHourData.temp - 32) * 5) / 9;
        const nextHourTemp = ((nextHourData.temp - 32) * 5) / 9;


        const percentageOfHour = currentMinute / 60;


        const interpolatedTemp = currentHourTemp + (nextHourTemp - currentHourTemp) * percentageOfHour;

        return interpolatedTemp;
    } catch (error) {
        console.error('Fehler bei der Temperaturberechnung:', error);
        return 0;
    }
}





function updateCurrentTemperature(weatherData) {

    if (weatherDataSaved) {
        const currentTemp = getCurrentTemperature(weatherData);
        updateTemperatureGaugeCurrent(currentTemp);
    }


}


setInterval(() => {

    updateCurrentTemperature(weatherDataSaved);

}, 6000);

setInterval(() => {

    updateCurrentHumidity(weatherDataSaved);

}, 6000);


function initializeHumidityGaugeCurrent() {
    const ctx = document.getElementById("currentHumidity");
    this.chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Humidity'],
            datasets: [{
                data: [100, 100],
                backgroundColor: [
                    'rgba(255, 0, 0, 0.8)',
                    'rgba(145, 22, 0, 0.63)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '80%',
            rotation: -90,
            circumference: 180,
            plugins: {
                tooltip: { enabled: false },
                legend: { display: false }
            }
        },
        plugins: [{
            id: 'humidityText',
            beforeDraw: function (chart) {
                const { ctx, chartArea, data } = chart;
                const centerX = (chartArea.left + chartArea.right) / 2;
                const centerY = (chartArea.bottom + chartArea.top) / 2 + 20;

                const currentHum = data.datasets[0].data[0].toFixed(2);

                ctx.clearRect(centerX - 50, centerY - 30, 100, 50);

                ctx.font = 'bold 36px Inter, Arial';
                ctx.fillStyle = 'rgba(255, 0, 0, 0.8)';
                ctx.textAlign = 'center';
                ctx.fillText(`${currentHum}%`, centerX, centerY);
            }
        }]
    });
}

function getCurrentHumidity(weatherData) {
    try {
        const now = new Date();
        const currentHour = now.getHours();
        const currentMinute = now.getMinutes();


        if (!weatherData?.days?.[0]?.hours) {
            console.error('Ungültige weatherData Struktur');
            return 0;
        }

        const hourlyData = weatherData.days[0].hours;


        let currentHourData = hourlyData.find(hour => {
            const hourTime = hour.datetime.split(':')[0];
            return parseInt(hourTime) === currentHour;
        });

        let nextHourData = hourlyData.find(hour => {
            const hourTime = hour.datetime.split(':')[0];
            return parseInt(hourTime) === (currentHour + 1) % 24;
        });


        if (!nextHourData) {
            nextHourData = currentHourData;
        }



        if (!currentHourData && weatherData.currentConditions) {
            currentHourData = weatherData.currentConditions;
            nextHourData = currentHourData;
        }


        if (!currentHourData || !nextHourData) {
            console.error('Keine Temperaturdaten verfügbar');
            return 0;
        }


        const currentHourHumidity = currentHourData.humidity;
        const nextHourHumidity = nextHourData.humidity;


        const percentageOfHour = currentMinute / 60;


        const interpolatedHum = currentHourHumidity + (nextHourHumidity - currentHourHumidity) * percentageOfHour;

        return interpolatedHum;
    } catch (error) {
        console.error('Fehler bei der Temperaturberechnung:', error);
        return 0;
    }
}

function updateHumidityGaugeCurrent(hum) {

    const chart = document.getElementById("currentHumidity");
    if (!chart) {
        console.error('Chart ist nicht initialisiert');
        return;
    }


    const normalizedHum = Math.min(Math.max(hum, 0), 100);


    this.chart.data.datasets[0].data = [normalizedHum, 100 - normalizedHum];

    this.chart.update();
}



function updateCurrentHumidity(weatherData) {

    if (weatherDataSaved) {
        const currentHum = getCurrentHumidity(weatherData);

        updateHumidityGaugeCurrent(currentHum);
    }


}









class SensorChart {
    constructor(containerId, title, maxValue = 100, color = '#BA0022') {
        this.containerId = containerId;
        this.title = title;
        this.maxValue = maxValue;
        this.color = color;

        this.createChartCard();
        this.initializeChart();
    }

    createChartCard() {
        const container = document.getElementById('chartsContainer');
        const cardHtml = `
                    <div class="chart-card" id="${this.containerId}-card">
                        <div class="chart-title">${this.title}</div>
                        <div class="chart-container">
                            <canvas id="${this.containerId}"></canvas>
                        </div>
                    </div>
                `;
        container.insertAdjacentHTML('beforeend', cardHtml);
    }

    initializeChart() {
        if (this.containerId === 'temperatureChart') {
            this.initializeTemperatureGauge();
        } else {
            this.initializeLineChart();
        }
    }

    initializeLineChart() {
        const ctx = document.getElementById(this.containerId);
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array(50).fill(''),
                datasets: [{
                    data: Array(50).fill(null),
                    borderColor: this.color,
                    backgroundColor: this.color + '33',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 0 },
                plugins: { legend: { display: false } },
                scales: {
                    x: {
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        ticks: { color: '#e0e0e0' }
                    },
                    y: {
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        ticks: { color: '#e0e0e0' },
                        suggestedMin: 0,
                        suggestedMax: this.maxValue
                    }
                }
            }
        });
    }

    initializeTemperatureGauge() {
        const ctx = document.getElementById(this.containerId);
        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Temperature'],
                datasets: [{
                    data: [50, 50],
                    backgroundColor: [
                        'rgba(126, 63, 255, 0.8)',
                        'rgba(24, 0, 71, 0.63)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '80%',
                rotation: -90,
                circumference: 180,
                plugins: {
                    tooltip: { enabled: false },
                    legend: { display: false }
                }
            },
            plugins: [{
                id: 'temperatureText',
                beforeDraw: function (chart) {
                    const { ctx, chartArea, data } = chart;
                    const centerX = (chartArea.left + chartArea.right) / 2;
                    const centerY = (chartArea.bottom + chartArea.top) / 2 + 20;

                    const currentTemp = data.datasets[0].data[0].toFixed(2);

                    ctx.clearRect(centerX - 50, centerY - 30, 100, 50);

                    ctx.font = 'bold 36px Inter, Arial';
                    ctx.fillStyle = '#7e3fff';
                    ctx.textAlign = 'center';
                    ctx.fillText(`${currentTemp}°C`, centerX, centerY);
                }
            }]
        });
    }

    updateData(labels, data) {
        if (this.containerId === 'temperatureChart') {
            this.updateTemperatureGauge(data[data.length - 1]);
        } else {
            this.chart.data.labels.push(labels[labels.length - 1]);
            this.chart.data.datasets[0].data.push(data[data.length - 1]);

            if (this.chart.data.labels.length > 60) {
                this.chart.data.labels.shift();
                this.chart.data.datasets[0].data.shift();
            }
            this.chart.update();
        }
    }

    updateTemperatureGauge(temp) {
        this.chart.data.datasets[0].data = [temp, 60 - temp];
        this.chart.update();
    }
}

const temperatureChart = new SensorChart('temperatureChart', 'Temperature (°C)', 60);
const humidityChart = new SensorChart('humidityChart', 'Humidity (%)', 100);
const fanSpeedChart = new SensorChart('fanSpeedChart', 'Fan Speed (RPM)', 100, '#4CAF50');

function updateCharts(data) {
    const now = new Date();
    const labels = Array.from({ length: data.temperature.length }, (_, i) => {
        const time = new Date(now.getTime() - (data.temperature.length - 1 - i) * 1000);
        return time.toLocaleTimeString();
    });


    humidityChart.updateData(labels, data.humidity);
    temperatureChart.updateData(labels, data.temperature);
    fanSpeedChart.updateData(labels, data.fan_speed);
}

async function fetchData() {
    try {
        const response = await fetch("http://localhost:5000/data", {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        // Check if the response is okay
        if (response.ok) {
            const data = await response.json();
            updateCharts(data);
        } else {
            console.error("Failed to fetch data, status:", response.status);


        }
    } catch (error) {
        console.error("Error fetching sensor data:", error);
    }
}

async function setFanSpeed(speed) {
    try {
        const response = await fetch("http://localhost:5000/set_fan_speed/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ value: speed }),
        });


        if (!response.ok) {
            console.error("Failed to set fan speed, status:", response.status);
        }
    } catch (error) {
        console.error("Error setting fan speed:", error);
    }
}


setInterval(fetchData, 500);
setFanSpeed(48);

document.getElementById('newSlider').addEventListener('input', function (event) {
    const value = event.target.value;

    setFanSpeed(value);
});