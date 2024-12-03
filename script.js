document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM carregado. Funções disponíveis.");

    let myChart; // Variável global para armazenar o gráfico. Permite que o gráfico seja atualizado dinamicamente.

    // Função para buscar as modalidades disponíveis na API e preenchê-las no select
    async function preencherModalidade() {
        try {
            // Faz uma requisição para a rota `/api/modalidade` para obter as modalidades esportivas
            const response = await fetch('/api/modalidade');
            if (!response.ok) {
                // Caso a resposta não seja bem-sucedida, lança um erro
                throw new Error(`Erro na requisição: ${response.status} - ${response.statusText}`);
            }
            
            // Converte a resposta da API para JSON
            const modalidade = await response.json();
            const selectModalidade = document.getElementById('modalidade'); // Localiza o elemento select no DOM

            // Para cada modalidade recebida, cria uma opção no select
            modalidade.forEach(modalidade => {
                const option = document.createElement('option');
                option.value = modalidade; // Define o valor da opção
                option.text = modalidade; // Define o texto visível da opção
                selectModalidade.add(option); // Adiciona a opção ao select
            });
        } catch (error) {
            // Exibe um erro no console e alerta o usuário em caso de falha
            console.error("Erro ao buscar modalidades:", error);
            alert("Erro ao carregar as modalidades esportivas.");
        }
    }

    // Função para buscar os dados filtrados com base nos critérios selecionados no formulário
    window.fetchFilteredData = async function fetchFilteredData() {
        // Obtém os valores dos filtros selecionados no formulário
        const estado = document.getElementById('estado').value;
        const remuneracao = document.getElementById('remuneracao').value;
        const modalidade = document.getElementById('modalidade').value;
        const genero = document.getElementById('genero').value;
        const estadoCivil = document.getElementById('estadoCivil').value;
        const escolaridade = document.getElementById('escolaridade').value;

        try {
            // Construção da URL para a API com os parâmetros de filtro
            let url = '/api/dados?';
            if (estado) url += `estado=${estado}&`;
            if (remuneracao) url += `remuneracao=${remuneracao}&`;
            if (modalidade) url += `modalidade=${modalidade}&`;
            if (genero) url += `genero=${genero}&`;
            if (estadoCivil) url += `estadoCivil=${estadoCivil}&`;
            if (escolaridade) url += `escolaridade=${escolaridade}&`;

            // Remove o último "&" da URL, se presente
            if (url.endsWith('&')) {
                url = url.slice(0, -1);
            }

            console.log(`Buscando dados da URL: ${url}`);

            // Faz uma requisição para a API com os filtros aplicados
            const response = await fetch(url);
            if (!response.ok) {
                // Caso a resposta não seja bem-sucedida, lança um erro
                throw new Error(`Erro na requisição: ${response.status} - ${response.statusText}`);
            }

            // Converte a resposta para JSON e atualiza o gráfico com os dados recebidos
            const data = await response.json();
            console.log("Dados recebidos:", data);

            updateChart(data); // Atualiza o gráfico com os dados recebidos
        } catch (error) {
            // Exibe um erro no console e alerta o usuário em caso de falha
            console.error("Erro ao buscar dados:", error);
            alert("Houve um problema ao buscar os dados. Verifique a conexão com a API e os filtros aplicados. " + error.message);
        }
    };

    // Função para atualizar o gráfico com os novos dados
    function updateChart(data) {
        // Destroi o gráfico anterior se existir, para evitar sobreposição
        if (myChart) {
            myChart.destroy();
        }

        // Mapeia os dados recebidos para obter as etiquetas e os valores
        const labels = data.map(item => item.modalidade || "Desconhecida");
        const values = data.map(item => item.remuneracao || 0);

        // Seleciona o elemento canvas do DOM onde o gráfico será renderizado
        const ctx = document.getElementById('myChart').getContext('2d');

        // Cria um novo gráfico usando Chart.js
        myChart = new Chart(ctx, {
            type: 'bar', // Tipo do gráfico: barras
            data: {
                labels: labels, // Etiquetas do eixo X
                datasets: [{
                    label: 'Remuneração por Modalidade (R$)', // Rótulo do conjunto de dados
                    data: values, // Valores correspondentes às etiquetas
                    backgroundColor: 'rgba(54, 162, 235, 0.2)', // Cor de fundo das barras
                    borderColor: 'rgba(54, 162, 235, 1)', // Cor da borda das barras
                    borderWidth: 1 // Largura da borda
                }]
            },
            options: {
                responsive: true, // Torna o gráfico responsivo
                plugins: {
                    legend: {
                        position: 'top', // Posiciona a legenda no topo
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true, // Garante que o eixo Y comece no zero
                    },
                },
            },
        });
    }

    // Chama a função para preencher as opções de modalidade ao carregar a página
    preencherModalidade();
});
