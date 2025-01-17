

async function fetchEnergyData() {
    try {
        const data = await fetchPrice();
        console.log(data);
        createPriceChart(data);
        updateCurrentPrice();


    } catch (error) {
        console.error("Error fetching sensor data:", error);
    }
}

async function fetchDrain() {
    const energy_drain = await fetch("/api/energyDrain/");
    const energy_drain_data = await energy_drain.json();

    return energy_drain_data;
}

async function fetchPrice() {
    const energy_price = await fetch("/api/energyData/");
    const energy_price_data = await energy_price.json();

    return energy_price_data;
}

async function fetchLoad() {
    const pc_load = await fetch("/api/loadCheck/");
    const pc_load_data = await pc_load.json();

    console.log(pc_load_data);


    return pc_load_data;
}

function calculatePowerCost(timestamp, wattage, priceData) {
    const megawattage = wattage / 1000000;


    if (!Array.isArray(priceData)) {
        return {
            success: false,
            error: "Invalid price data format"
        };
    }

    const priceEntry = priceData.find(entry =>
        timestamp >= entry.start_timestamp &&
        timestamp < entry.end_timestamp
    );

    if (!priceEntry) {
        return {
            success: false,
            error: "Kein Preis für diesen Zeitpunkt gefunden"
        };
    }

    const hourlyPrice = priceEntry.marketprice * megawattage;

    return {
        success: true,
        result: {
            hourlyPrice: hourlyPrice,
            pricePerMWh: priceEntry.marketprice,
            timestamp: timestamp,
            timeRange: {
                start: new Date(priceEntry.start_timestamp).toLocaleString(),
                end: new Date(priceEntry.end_timestamp).toLocaleString()
            }
        }
    };
}

function createPriceChart(apiData) {

    function convertTimestampToLocalTime(timestamp) {
        const date = new Date(timestamp);

        date.setHours(date.getHours() + 1);
        return date.toLocaleTimeString('de-DE');
    }


    const labels = apiData.data.data.map(item => convertTimestampToLocalTime(item.start_timestamp));
    const prices = apiData.data.data.map(item => item.marketprice);


    const ctx = document.getElementById('priceChart').getContext('2d');
    const priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Strompreis (€/MWh)',
                data: prices,
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
                    suggestedMax: Math.max(...prices) + 20
                }
            }
        }
    });
}



let priceChartCurrent;
initializeEnergyCostGaugeCurrent();
function initializeEnergyCostGaugeCurrent() {
    const ctx = document.getElementById("currentPrice");
    priceChartCurrent = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Price'],
            datasets: [{
                data: [1, 1],
                backgroundColor: [
                    'rgba(0, 255, 0, 0.93)',
                    'rgba(35, 148, 0, 0.59)'
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
            id: 'priceText',
            beforeDraw: function (chart) {
                const { ctx, chartArea, data } = chart;
                const centerX = (chartArea.left + chartArea.right) / 2;
                const centerY = (chartArea.bottom + chartArea.top) / 2 + 20;

                const currentPrice = data.datasets[0].data[0].toFixed(2);

                ctx.clearRect(centerX - 50, centerY - 30, 100, 50);

                ctx.font = 'bold 36px Inter, Arial';
                ctx.fillStyle = 'rgba(0, 255, 0, 0.93)';
                ctx.textAlign = 'center';
                ctx.fillText(`${currentPrice}€/h`, centerX, centerY);
            }
        }]
    });
}



function updatePriceGaugeCurrent(price) {
    if (!priceChartCurrent) {
        console.error('Chart ist nicht initialisiert');
        return;
    }
    const normalizedPrice = Math.min(Math.max(price, 0), 0.05);
    priceChartCurrent.data.datasets[0].data = [normalizedPrice, 0.05 - normalizedPrice];
    priceChartCurrent.update();
}



async function updateCurrentPrice() {

    const timestamp = new Date();
    const energy_drain_data = await fetchDrain();
    const data = await fetchPrice();


    const priceCalculation = calculatePowerCost(timestamp, energy_drain_data, data.data.data);
    if (priceCalculation.success) {
        updatePriceGaugeCurrent(priceCalculation.result.hourlyPrice);
    } else {
        console.error(priceCalculation.error);
    }



}

setInterval(updateCurrentPrice, 10000);





let loadChartCurrent;
let cpuLoadCurrent;
let memoryLoadCurrent;
initializeLoadGaugeCurrent();

function initializeLoadGaugeCurrent() {
    const ctx = document.getElementById("currentLoad");
    const cpuCtx = document.getElementById("cpuLoad");
    const memoryCtx = document.getElementById("memoryLoad");


    loadChartCurrent = chartInit(ctx, 'rgb(255, 115, 0)', "rgba(151, 48, 0, 0.82)", "%");
    cpuLoadCurrent = chartInit(cpuCtx, 'rgb(255, 115, 0)', "rgba(151, 48, 0, 0.82)", "%");
    memoryLoadCurrent = chartInit(memoryCtx, 'rgb(255, 115, 0)', "rgba(151, 48, 0, 0.82)", "%");
}



function chartInit(chatElement, forgroundColor, backgroundColor, suffix) {

    return new Chart(chatElement, {
        type: 'doughnut',
        data: {
            labels: ['Load'],
            datasets: [{
                data: [50, 50],
                backgroundColor: [
                    forgroundColor,
                    backgroundColor
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
            id: 'loadText',
            beforeDraw: function (chart) {
                const { ctx, chartArea, data } = chart;
                const centerX = (chartArea.left + chartArea.right) / 2;
                const centerY = (chartArea.bottom + chartArea.top) / 2 + 20;

                const currentLoad = data.datasets[0].data[0].toFixed(2);

                ctx.clearRect(centerX - 50, centerY - 30, 100, 50);

                ctx.font = 'bold 36px Inter, Arial';
                ctx.fillStyle = forgroundColor;
                ctx.textAlign = 'center';
                ctx.fillText(`${currentLoad}${suffix}`, centerX, centerY);
            }
        }]
    });

}

const modal = document.getElementById("loadModal");
const closeBtn = document.getElementById("closeModal");
const energyCard = document.getElementById("currentLoad-card");

energyCard.onclick = function () {
    modal.style.display = "block";
    modal.style.visibility = 'visible';
    console.log("CLICK");

}

closeBtn.onclick = function () {
    modal.style.display = 'none';
}

modal.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}



function updateLoadGaugeCurrent(load, updateChart) {
    if (!updateChart) {
        console.error('Chart ist nicht initialisiert');
        return;
    }
    const normalizedLoad = Math.min(Math.max(load, 0), 100);
    updateChart.data.datasets[0].data = [normalizedLoad, 100 - normalizedLoad];
    updateChart.update();
}

async function updateCurrentLoad() {
    try {
        const load = await fetchLoad();
        console.log(load);

        if (load.status === 'success') {
            updateLoadGaugeCurrent(load.result.current_load, loadChartCurrent);
            updateLoadGaugeCurrent(load.result.cpu_usage, cpuLoadCurrent);
            updateLoadGaugeCurrent(load.result.memory_usage, memoryLoadCurrent);
        } else {
            console.error('Failed to fetch load data');
        }
    } catch (error) {
        console.error('Error updating current load:', error);
    }
}

setInterval(updateCurrentLoad, 1000);