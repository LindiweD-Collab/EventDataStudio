document.addEventListener('DOMContentLoaded', function() {
    // --- Render Event Types Chart (Pie Chart) ---
    const typeCtx = document.getElementById('typeCountsChart')?.getContext('2d');
    if (typeCtx && typeCountsData && typeCountsData.labels.length > 0) {
        new Chart(typeCtx, {
            type: 'pie', // Or 'doughnut'
            data: {
                labels: typeCountsData.labels,
                datasets: [{
                    label: 'Events by Type',
                    data: typeCountsData.data,
                    backgroundColor: [ // Add more colors if needed
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(153, 102, 255, 0.7)',
                        'rgba(255, 159, 64, 0.7)'
                    ],
                    borderColor: [ // Optional borders
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: false, // Already in card header
                        // text: 'Events by Type'
                    }
                }
            }
        });
    } else if(typeCtx) {
         typeCtx.canvas.parentNode.innerHTML = '<p class="text-muted text-center mt-3">No event type data found to display chart.</p>';
    }

    // --- Render Event Locations Chart (Bar Chart) ---
    const locationCtx = document.getElementById('locationCountsChart')?.getContext('2d');
     if (locationCtx && locationCountsData && locationCountsData.labels.length > 0) {
        new Chart(locationCtx, {
            type: 'bar',
            data: {
                labels: locationCountsData.labels,
                datasets: [{
                    label: 'Events by Location',
                    data: locationCountsData.data,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y', // Make it horizontal for better readability if many locations
                 scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { // Ensure only integers are shown on axis
                            stepSize: 1,
                            callback: function(value) {if (Math.floor(value) === value) {return value;}}
                        }
                    }
                },
                plugins: {
                    legend: { display: false }, // Label is clear enough
                    title: { display: false }
                }
            }
        });
    } else if(locationCtx) {
        locationCtx.canvas.parentNode.innerHTML = '<p class="text-muted text-center mt-3">No location data found to display chart.</p>';
    }


    // --- Render Monthly Events Chart (Line Chart) ---
     const monthlyCtx = document.getElementById('monthlyCountsChart')?.getContext('2d');
     if (monthlyCtx && monthlyCountsData && monthlyCountsData.labels.length > 0) {
        new Chart(monthlyCtx, {
            type: 'line',
            data: {
                labels: monthlyCountsData.labels, // Should be sorted YYYY-MM
                datasets: [{
                    label: 'Number of Events',
                    data: monthlyCountsData.data,
                    fill: false,
                    borderColor: 'rgb(54, 162, 235)',
                    tension: 0.1 // Slight curve to the line
                }]
            },
             options: {
                responsive: true,
                 scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { // Ensure only integers are shown on axis
                            stepSize: 1,
                             callback: function(value) {if (Math.floor(value) === value) {return value;}}
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    title: { display: false }
                }
            }
        });
    } else if(monthlyCtx) {
         monthlyCtx.canvas.parentNode.innerHTML = '<p class="text-muted text-center mt-3">No monthly event data found to display chart.</p>';
    }

});