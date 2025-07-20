document.addEventListener("DOMContentLoaded", function() {
    fetch('data.json')
        .then(response => response.json())
        .then(jsonData => {
            console.log('JSON loaded:', jsonData);
            const tableBody = document.getElementById('tableBody');
            console.log('tableBody element:', tableBody);
            const levelCounts = {};

            // = Recorremos todos los repositorios del JSON
            for (const repo in jsonData) {
                const files = jsonData[repo];

                // = Recorremos todos los archivos dentro de cada repo
                for (const file in files) {
                    files[file].forEach(item => {
                        const level = item["Level"];
                        if (levelCounts[level]) {
                            levelCounts[level]++;
                        } else {
                            levelCounts[level] = 1;
                        }

                        // Añadir una fila por cada elemento del archivo
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${item["Class"]}</td>
                            <td>${item["Start Line"]}</td>
                            <td>${item["End Line"]}</td>
                            <td>${item["Displacement"]}</td>
                            <td>${item["Level"]}</td>
                        `;
                        tableBody.appendChild(row);
                    });
                }
            }

            // Datos para la gráfica
            const labels = Object.keys(levelCounts);
            const data = Object.values(levelCounts);

            // Crear gráfica con Chart.js
            const ctx = document.getElementById('myChart').getContext('2d');
            const myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Count of Elements by Level',
                        data: data,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            // Activar DataTables
            $(document).ready(function() {
                $('#dataTable').DataTable();
            });
        })
        .catch(error => console.error('Error loading JSON data:', error));
});
