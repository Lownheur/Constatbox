document.addEventListener('DOMContentLoaded', () => {
    // Navigation
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.section-view');

    function switchView(viewId) {
        sections.forEach(s => s.style.display = 'none');
        document.getElementById(viewId).style.display = 'block';

        navItems.forEach(n => n.classList.remove('active'));
        document.querySelector(`[data-view="${viewId}"]`).classList.add('active');

        if (viewId === 'dashboard') loadLatestScan();
        if (viewId === 'history') loadArchivesList();
    }

    navItems.forEach(item => {
        item.addEventListener('click', () => switchView(item.dataset.view));
    });

    // Load initial view
    switchView('dashboard');
});

async function loadLatestScan() {
    try {
        const response = await fetch('/api/last-scan/forensic');
        if (!response.ok) throw new Error('Failed to fetch data');
        const data = await response.json();

        updateDashboard(data);
    } catch (error) {
        console.error('Error loading scan:', error);
    }
}

function updateDashboard(data) {
    if (!data || !data.metadata) return;

    // Update Stats Cards
    document.getElementById('total-packets').textContent = data.metadata.total_packets;
    document.getElementById('total-size').textContent = data.metadata.total_size_mb + ' MB';

    // Update Top Devices Table
    const devicesList = document.getElementById('top-devices-list');
    devicesList.innerHTML = '';

    data.bandwidth_usage.slice(0, 5).forEach(device => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="ip-addr">${device.ip}</td>
            <td>${device.data_kb} KB</td>
            <td>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 1; height: 4px; background: var(--bg-tertiary); border-radius: 2px;">
                        <div style="width: ${device.percentage}%; height: 100%; background: var(--accent-secondary); border-radius: 2px;"></div>
                    </div>
                    <span>${device.percentage}%</span>
                </div>
            </td>
        `;
        devicesList.appendChild(row);
    });

    // Update Top Countries Table
    const countriesList = document.getElementById('top-countries-list');
    countriesList.innerHTML = '';

    data.geography.slice(0, 5).forEach(geo => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${geo.country}</td>
            <td>${geo.hits}</td>
            <td class="text-success">${geo.percent}%</td>
        `;
        countriesList.appendChild(row);
    });
}

async function loadArchivesList() {
    try {
        const response = await fetch('/api/archives');
        const files = await response.json();

        const listContainer = document.getElementById('archives-list');
        listContainer.innerHTML = '';

        files.forEach(file => {
            const item = document.createElement('li');
            item.className = 'history-item';
            item.innerHTML = `
                <div>
                    <div style="color: var(--text-primary); font-weight: bold;">${file}</div>
                    <div style="color: var(--text-muted); font-size: 12px;">Type: JSON Scan Report</div>
                </div>
                <button class="status-badge" style="cursor: pointer;">VIEW</button>
            `;
            item.onclick = (() => loadArchiveDetail(file));
            listContainer.appendChild(item);
        });
    } catch (e) {
        console.error(e);
    }
}

async function loadArchiveDetail(filename) {
    try {
        const response = await fetch(`/api/scan/${filename}`);
        const data = await response.json();

        const detailView = document.getElementById('archive-detail');
        detailView.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <span>File: ${filename}</span>
                    <span class="text-success">${data.timestamp}</span>
                </div>
                <div class="grid">
                     <div class="card">
                        <h3>Interface</h3>
                        <p class="stat-value" style="font-size: 18px">${data.network_info.interface}</p>
                    </div>
                     <div class="card">
                        <h3>Devices Found</h3>
                        <p class="stat-value">${data.devices.length}</p>
                    </div>
                     <div class="card">
                        <h3>Packets</h3>
                        <p class="stat-value">${data.stats.total_packets}</p>
                    </div>
                </div>
                
                <h3>Devices List</h3>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>IP Address</th>
                                <th>MAC Address</th>
                                <th>Vendor</th>
                                <th>Type</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.devices.map(d => `
                                <tr>
                                    <td class="ip-addr">${d.ip} ${d.is_gateway ? '⭐' : ''}</td>
                                    <td class="mac-addr">${d.mac}</td>
                                    <td>${d.vendor}</td>
                                    <td>${d.type}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    } catch (e) {
        console.error(e);
    }
}
