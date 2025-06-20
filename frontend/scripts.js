const URL = 'http://127.0.0.1:8000';

// Theme Toggle
function toggleTheme() {
    document.body.setAttribute('data-theme',
        document.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'
    );
}

// Live Feed Controls
function togglePause() {
    const btn = document.querySelector('.btn-pause');
    btn.textContent = btn.textContent.includes('Pause') ? '▶️ Resume' : '🔴 Pause';
}

function toggleGrid() {
    const grid = document.querySelector('.grid-overlay');
    const btn = document.querySelector('.btn-grid');
    grid.style.opacity = grid.style.opacity === '0' ? '0.2' : '0';
    btn.textContent = btn.textContent.includes('Hide') ? '🔵 Show Grid' : '🔵 Hide Grid';
}

function toggleSource(element) {
    document.querySelectorAll('.source .badge').forEach(badge => {
        badge.classList.remove('badge-selected');
    });
    element.classList.add('badge-selected');
}

// Populate Vehicle List from Django API
async function populateVehicleList() {
    const vehicleList = document.getElementById('vehicleList');
    try {
        const res = await fetch(`${URL}/api/vehicles/recent/`);
        const data = await res.json();
        vehicleList.innerHTML = data.map(vehicle => `
            <div class="vehicle-item">
                <span class="arrow ${vehicle.action}">${vehicle.action === 'entry' ? '↓' : '↑'}</span>
                <span class="icon">${vehicle.action === 'entry' ? '🚗' : '🚚'}</span>
                <span class="timestamp">${new Date(vehicle.timestamp).toLocaleString()}</span>
                <span class="status ${vehicle.action}">${vehicle.action.charAt(0).toUpperCase() + vehicle.action.slice(1)}</span>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading vehicle data:', error);
    }
}

// Initialize Charts with Real Data + Update DOM stats
async function initializeCharts() {
    try {
        // Vehicles Over Time Chart
        const overTimeRes = await fetch(`${URL}/api/vehicles/stats/`);
        const overTimeData = await overTimeRes.json();
        const dates = overTimeData.map(d => d.date);
        const counts = overTimeData.map(d => d.count);

        new Chart(document.getElementById('vehiclesOverTime'), {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Total Vehicles',
                    data: counts,
                    borderColor: '#4299e1',
                    tension: 0.4,
                    fill: true,
                    backgroundColor: 'rgba(66, 153, 225, 0.1)'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Vehicles In/Out Chart and Update DOM
        const statusRes = await fetch(`${URL}/api/status/`);
        const statusData = await statusRes.json();

        const totalCapacity = 100;
        const occupied = statusData.currently_parked;
        const available = totalCapacity - occupied;
        const occupancyRate = Math.round((occupied / totalCapacity) * 100);

        // Update DOM elements
        document.querySelector('.space-item.available .value').textContent = `${available}/${totalCapacity}`;
        document.querySelector('.space-item.occupied .value').textContent = `${occupied}/${totalCapacity}`;
        document.querySelector('.progress').style.width = `${occupancyRate}%`;
        document.querySelector('.occupancy-rate').textContent = `${occupancyRate}% Occupancy Rate`;

        new Chart(document.getElementById('vehiclesInOut'), {
            type: 'bar',
            data: {
                labels: ['Entries', 'Exits', 'Currently Parked'],
                datasets: [{
                    label: 'Count',
                    data: [statusData.total_entered, statusData.total_exited, occupied],
                    backgroundColor: ['#48bb78', '#fc8181', '#f6ad55']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error loading chart data:', error);
    }
}


// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
    populateVehicleList();
    initializeCharts();

    // Auto-refresh recent vehicle list every 15 seconds
    setInterval(populateVehicleList, 15000);

    // Auto-refresh charts every 60 seconds
    setInterval(initializeCharts, 60000);
});
