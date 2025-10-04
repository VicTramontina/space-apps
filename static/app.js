// LCZ Temperature Analysis Application
let map;
let lczLayer;
let temperatureLayer;
let lczData = null;
let lczClasses = {};
let selectedZone = null;
let selectedFeature = null;

// Initialize map
function initMap() {
    map = L.map('map').setView([-29.4667, -51.9667], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    loadLCZData();
    loadLCZClasses();
}

// Load LCZ data from API
async function loadLCZData() {
    try {
        const response = await fetch('/api/lcz-data');
        const data = await response.json();

        if (data.success) {
            lczData = data;
            displayLCZLayer(data.geojson);

            if (data.center) {
                map.setView(data.center, 13);
            }
        } else {
            console.error('Error loading LCZ data:', data.error);
            alert('Erro ao carregar dados de LCZ: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao conectar com o servidor');
    }
}

// Load LCZ class definitions
async function loadLCZClasses() {
    try {
        const response = await fetch('/api/lcz-classes');
        const data = await response.json();

        if (data.success) {
            lczClasses = data.classes;
            populateLCZSelect();
            createLegend();
        }
    } catch (error) {
        console.error('Error loading LCZ classes:', error);
    }
}

// Display LCZ layer on map
function displayLCZLayer(geojson) {
    if (lczLayer) {
        map.removeLayer(lczLayer);
    }

    lczLayer = L.geoJSON(geojson, {
        style: function(feature) {
            const lczClass = feature.properties.lcz_class;
            const color = lczClasses[lczClass]?.color || '#gray';

            return {
                fillColor: color,
                weight: 2,
                opacity: 1,
                color: 'white',
                fillOpacity: 0.6
            };
        },
        onEachFeature: function(feature, layer) {
            const lczClass = feature.properties.lcz_class;
            const lczName = lczClasses[lczClass]?.name || 'Unknown';

            layer.bindPopup(`
                <strong>LCZ ${lczClass}</strong><br>
                ${lczName}
            `);

            layer.on('click', function(e) {
                selectZone(feature, layer, e.latlng);
            });
        }
    }).addTo(map);
}

// Select a zone for analysis
async function selectZone(feature, layer, latlng) {
    selectedZone = feature;
    selectedFeature = layer;

    const lczClass = feature.properties.lcz_class;
    const lczName = lczClasses[lczClass]?.name || 'Unknown';

    // Highlight selected zone
    if (selectedFeature) {
        lczLayer.resetStyle(selectedFeature);
    }

    layer.setStyle({
        weight: 4,
        color: '#ffff00',
        fillOpacity: 0.8
    });

    // Update UI
    document.getElementById('selected-zone-info').style.display = 'block';
    document.getElementById('current-lcz').textContent = `LCZ ${lczClass} - ${lczName}`;
    document.getElementById('current-temp').textContent = 'Carregando...';

    // Fetch temperature
    try {
        const response = await fetch(`/api/temperature?lat=${latlng.lat}&lon=${latlng.lng}`);
        const data = await response.json();

        if (data.success) {
            selectedZone.temperature = data.temperature;
            document.getElementById('current-temp').textContent = `${data.temperature.toFixed(1)} °C`;
        } else {
            document.getElementById('current-temp').textContent = 'N/A';
            alert('Erro ao buscar temperatura: ' + data.error);
        }
    } catch (error) {
        console.error('Error fetching temperature:', error);
        document.getElementById('current-temp').textContent = 'Erro';
    }
}

// Populate LCZ select dropdown
function populateLCZSelect() {
    const select = document.getElementById('new-lcz-select');
    select.innerHTML = '<option value="">Selecione uma nova LCZ...</option>';

    for (const [lczNum, lczInfo] of Object.entries(lczClasses)) {
        const option = document.createElement('option');
        option.value = lczNum;
        option.textContent = `LCZ ${lczNum} - ${lczInfo.name}`;
        select.appendChild(option);
    }
}

// Calculate scenario when LCZ is changed
async function calculateScenario() {
    const newLCZ = parseInt(document.getElementById('new-lcz-select').value);

    if (!newLCZ) {
        alert('Por favor, selecione uma nova LCZ');
        return;
    }

    if (!selectedZone || selectedZone.temperature === undefined) {
        alert('Por favor, selecione uma zona no mapa primeiro');
        return;
    }

    const fromLCZ = selectedZone.properties.lcz_class;
    const baseTemp = selectedZone.temperature;

    try {
        const response = await fetch('/api/calculate-scenario', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                zone_id: selectedZone.properties.name || 'zone',
                from_lcz: fromLCZ,
                to_lcz: newLCZ,
                base_temperature: baseTemp
            })
        });

        const data = await response.json();

        if (data.success) {
            displayScenarioResult(data.result);
        } else {
            alert('Erro ao calcular cenário: ' + data.error);
        }
    } catch (error) {
        console.error('Error calculating scenario:', error);
        alert('Erro ao calcular cenário');
    }
}

// Display scenario calculation result
function displayScenarioResult(result) {
    const resultDiv = document.getElementById('scenario-result');
    const delta = result.delta;
    const deltaClass = delta > 0 ? 'negative' : '';

    const deltaSymbol = delta > 0 ? '+' : '';
    const deltaText = delta > 0 ? 'aumento' : delta < 0 ? 'redução' : 'sem mudança';

    resultDiv.className = `scenario-result ${deltaClass}`;
    resultDiv.innerHTML = `
        <h3 style="margin-bottom: 10px;">Resultado da Simulação</h3>
        <p><strong>De:</strong> LCZ ${result.from_lcz} (${result.from_name})</p>
        <p><strong>Para:</strong> LCZ ${result.to_lcz} (${result.to_name})</p>
        <hr style="margin: 10px 0;">
        <p><strong>Temperatura Base:</strong> ${result.base_temperature.toFixed(1)} °C</p>
        <p><strong>Nova Temperatura:</strong> ${result.new_temperature.toFixed(1)} °C</p>
        <p style="font-size: 18px; margin-top: 10px;">
            <strong>Diferença:</strong>
            <span style="color: ${delta > 0 ? '#d9534f' : '#5cb85c'}">
                ${deltaSymbol}${delta.toFixed(2)} °C
            </span>
        </p>
        <p style="margin-top: 10px; font-size: 13px; color: #666;">
            ${result.explanation}
        </p>
    `;
    resultDiv.style.display = 'block';
}

// Load temperature layer
async function loadTemperatureLayer() {
    const btn = event.target;
    btn.textContent = '⏳ Carregando...';
    btn.disabled = true;

    try {
        const response = await fetch('/api/temperature-grid');
        const data = await response.json();

        if (data.success) {
            displayTemperatureLayer(data.data);
            alert('Camada de temperatura carregada com sucesso!');
        } else {
            alert('Erro ao carregar temperatura: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao carregar camada de temperatura');
    } finally {
        btn.textContent = '📊 Carregar Camada de Temperatura';
        btn.disabled = false;
    }
}

// Display temperature layer
function displayTemperatureLayer(tempData) {
    if (temperatureLayer) {
        map.removeLayer(temperatureLayer);
    }

    // Create heat map markers
    const markers = [];

    for (let i = 0; i < tempData.coordinates.length; i++) {
        const coord = tempData.coordinates[i];
        const temp = tempData.values[i];

        if (temp !== null) {
            const color = getTemperatureColor(temp);

            const circle = L.circleMarker([coord.lat, coord.lon], {
                radius: 5,
                fillColor: color,
                color: color,
                weight: 1,
                opacity: 0.6,
                fillOpacity: 0.6
            }).bindPopup(`Temperatura: ${temp.toFixed(1)} °C`);

            markers.push(circle);
        }
    }

    temperatureLayer = L.layerGroup(markers).addTo(map);
}

// Get color for temperature value
function getTemperatureColor(temp) {
    // Color scale from blue (cold) to red (hot)
    if (temp < 10) return '#313695';
    if (temp < 15) return '#4575b4';
    if (temp < 20) return '#74add1';
    if (temp < 25) return '#abd9e9';
    if (temp < 30) return '#fee090';
    if (temp < 35) return '#fdae61';
    if (temp < 40) return '#f46d43';
    return '#d73027';
}

// Create legend
function createLegend() {
    const legendDiv = document.getElementById('legend');
    legendDiv.innerHTML = '';

    for (const [lczNum, lczInfo] of Object.entries(lczClasses)) {
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.innerHTML = `
            <div class="legend-color" style="background-color: ${lczInfo.color}"></div>
            <span>LCZ ${lczNum}: ${lczInfo.name}</span>
        `;
        legendDiv.appendChild(item);
    }
}

// Toggle legend visibility
function toggleLegend() {
    const legend = document.getElementById('legend-container');
    legend.style.display = legend.style.display === 'none' ? 'block' : 'none';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initMap);
