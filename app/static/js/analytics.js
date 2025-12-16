document.addEventListener('DOMContentLoaded', function () {
    const ctxOrders = document.getElementById('ordersChart').getContext('2d');
    const ctxStatus = document.getElementById('statusChart').getContext('2d');
    const ctxFilament = document.getElementById('filamentChart').getContext('2d');
    const ctxPrinter = document.getElementById('printerChart').getContext('2d');

    let charts = {};

    function initCharts() {
        charts.orders = new Chart(ctxOrders, {
            type: 'bar',
            data: { labels: [], datasets: [{ label: 'Orders', data: [], backgroundColor: '#0d6efd' }] },
            options: { responsive: true, maintainAspectRatio: false }
        });

        charts.status = new Chart(ctxStatus, {
            type: 'pie',
            data: { labels: [], datasets: [{ data: [], backgroundColor: ['#ffc107', '#198754', '#0dcaf0', '#6c757d'] }] },
            options: { responsive: true, maintainAspectRatio: false }
        });

        charts.filament = new Chart(ctxFilament, {
            type: 'doughnut',
            data: { labels: [], datasets: [{ data: [], backgroundColor: ['#fd7e14', '#20c997', '#6610f2'] }] },
            options: { responsive: true, maintainAspectRatio: false }
        });

        charts.printer = new Chart(ctxPrinter, {
            type: 'bar',
            data: { labels: [], datasets: [{ label: 'Jobs Assigned', data: [], backgroundColor: '#6f42c1' }] },
            options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false }
        });
    }

    function updateCharts(data) {
        // Orders Per Day
        charts.orders.data.labels = data.orders_per_day.map(d => d.date);
        charts.orders.data.datasets[0].data = data.orders_per_day.map(d => d.count);
        charts.orders.update();

        // Status
        charts.status.data.labels = data.order_status.map(d => d.status);
        charts.status.data.datasets[0].data = data.order_status.map(d => d.count);
        charts.status.update();

        // Filament
        charts.filament.data.labels = data.filament_usage.map(d => d.material);
        charts.filament.data.datasets[0].data = data.filament_usage.map(d => d.grams);
        charts.filament.update();

        // Printer
        charts.printer.data.labels = data.printer_utilization.map(d => d.printer);
        charts.printer.data.datasets[0].data = data.printer_utilization.map(d => d.jobs);
        charts.printer.update();
    }

    function fetchData() {
        const days = document.getElementById('daysFilter').value;
        const printerId = document.getElementById('printerFilter').value;
        const params = new URLSearchParams({ days: days, printer_id: printerId });

        fetch(`/analytics/api/stats?${params}`)
            .then(response => response.json())
            .then(data => {
                updateCharts(data);
            })
            .catch(error => console.error('Error fetching analytics:', error));
    }

    document.getElementById('refreshBtn').addEventListener('click', fetchData);
    document.getElementById('daysFilter').addEventListener('change', fetchData);
    document.getElementById('printerFilter').addEventListener('change', fetchData);

    initCharts();
    fetchData();
});
