document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM carregado. Funções disponíveis.");

    let myChart; // Declara myChart no escopo global

    async function preencherModalidades() {
        try {
            const response = await fetch('/api/modalidades');
            if (!response.ok) {
                throw new Error(`Erro na requisição: ${response.status} - ${response.statusText}`);
            }
            const modalidades = await response.json();
            const selectModalidade = document.getElementById('modalidade'); // Correção: referência a "modalidade"

            modalidades.forEach(modalidade => {
                const option = document.createElement('option');
                option.value = modalidade;
                option.text = modalidade;
                selectModalidade.add(option);
            });
        } catch (error) {
            console.error("Erro ao buscar modalidades:", error);
            alert("Erro ao carregar as modalidades esportivas.");
        }
    }

    window.fetchFilteredData = async function fetchFilteredData() {
        const estado = document.getElementById('estado').value;
        const remuneracao = document.getElementById('remuneracao').value;
        const modalidade = document.getElementById('modalidade').value; // Correção: referência a "modalidade"
        const genero = document.getElementById('genero').value;
        const estadoCivil = document.getElementById('estadoCivil').value;
        const escolaridade = document.getElementById('escolaridade').value;

        try {
            let url = '/api/dados?';

            // Construindo a URL com os parâmetros de filtro
            if (estado) url += `estado=${estado}&`;
            if (remuneracao) url += `remuneracao=${remuneracao}&`;
            if (modalidade) url += `modalidade=${modalidade}&`; // Correção: referência a "modalidade"
            if (genero) url += `genero=${genero}&`;
            if (estadoCivil) url += `estadoCivil=${estadoCivil}&`;
            if (escolaridade) url += `escolaridade=${escolaridade}&`;

            if (url.endsWith('&')) {
                url = url.slice(0, -1);
            }

            console.log(`Buscando dados da URL: ${url}`);

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Erro na requisição: ${response.status} - ${response.statusText}`);
            }

            const data = await response.json();
            console.log("Dados recebidos:", data);

            updateChart(data);
        } catch (error) {
            console.error("Erro ao buscar dados:", error);
            alert("Houve um problema ao buscar os dados. Verifique a conexão com a API e os filtros aplicados. " + error.message);
        }
    };

    function updateChart(data) {
        if (myChart) {
            myChart.destroy();
        }

        const labels = data.map(item => item.modalidade || "Desconhecida"); // Correção: referência a "modalidade"
        const values = data.map(item => item.remuneracao || 0);

        const ctx = document.getElementById('myChart').getContext('2d');

        myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Remuneração por Modalidade (R$)', // Correção: referência a "modalidade"
                    data: values,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });
    }

    preencherModalidades();
});
