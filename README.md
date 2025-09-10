# Modelo de Simulação de Emissões da Pecuária Bovina em Goiás

## Visão Geral

Este projeto apresenta um modelo de dinâmica de sistemas, desenvolvido em Python, para simular a evolução do rebanho bovino de corte no estado de Goiás, Brasil, e projetar as emissões de Gases de Efeito Estufa (GEE) associadas. O modelo analisa e compara dois cenários produtivos ao longo de um período de 10 anos (2025-2035):

1.  **Cenário Extensivo (Linha de Base):** Representa a continuidade das práticas atuais de produção, com índices zootécnicos tradicionais.
2.  **Cenário de Transição para o Intensivo:** Simula uma transição gradual, ao longo de 10 anos, de um sistema extensivo para um sistema intensivo, caracterizado por melhores índices de produtividade.

O objetivo principal é quantificar o impacto da intensificação da pecuária na produção de carne, no tamanho do rebanho, nas emissões totais de GEE e, crucialmente, na **intensidade das emissões** (kg de CO2-eq por kg de carne produzida).

## Funcionalidades Principais

- **Modelagem de Dinâmica de Sistemas:** Utiliza uma abordagem de estoques e fluxos para representar a população do rebanho, dividida por categorias (bezerras, novilhas, vacas, bezerros, novilhos e touros).
- **Análise de Cenários Comparativos:** Avalia um cenário de linha de base contra um cenário de melhoria tecnológica e de manejo.
- **Projeção de KPIs:** Calcula e projeta indicadores-chave de desempenho (KPIs), incluindo:
    - Tamanho total do rebanho.
    - Produção anual de carne (em kg).
    - Emissões totais diárias de GEE (em kg CO2-eq).
    - Intensidade de emissões.
- **Capacidade de Carga:** O modelo incorpora um fator de estresse ambiental que ajusta dinamicamente os parâmetros de produtividade (ganho de peso, taxas de prenhez, mortalidade) caso a população total exceda a capacidade de carga definida para a região.
- **Exportação de Resultados:** Gera um relatório detalhado em formato Excel (`resultados_anuais.xlsx`) com a evolução anual dos principais KPIs para ambos os cenários.
- **Visualização Gráfica:** Produz e exibe gráficos comparativos que ilustram a trajetória dos indicadores ao longo do período de simulação, facilitando a análise visual dos resultados.

## Estrutura do Modelo

O coração do `modelo.py` é a função `run_simulation_with_transition`, que simula a dinâmica do rebanho ao longo do tempo.

### Estoques (Categorias do Rebanho)

A população bovina é dividida nos seguintes estoques:
- `Terneras` (Bezerras)
- `Novillas` (Novilhas)
- `Vacas`
- `Terneros` (Bezerros)
- `Novillos`
- `Toros` (Touros)

### Fluxos Principais

Os estoques são interligados por fluxos que representam processos biológicos e de manejo, como:
- Nascimentos (diferenciados por fêmeas e machos).
- Maturação entre categorias (ex: bezerras para novilhas).
- Conversão de novilhas prenhas em vacas.
- Vendas para descarte (vacas e novilhas não prenhas).
- Vendas de touros para abate.
- Mortalidade em cada categoria.

### Parâmetros

O modelo utiliza um conjunto de parâmetros para definir o comportamento do sistema:
- **Parâmetros Fixos Globais:** Constantes que não variam entre cenários, como rendimento de carcaça e pesos de venda.
- **Parâmetros de Cenário:** Variáveis que definem as características de cada sistema produtivo (extensivo vs. intensivo). Incluem:
    - Ganho de Peso Diário (GDP) para cada categoria.
    - Taxas de prenhez e de partos.
    - Taxas de mortalidade.
    - Percentual de descarte.

## Cenários Analisados

### 1. Cenário Extensivo (Linha de Base)
Este cenário simula a manutenção das práticas atuais. É caracterizado por:
- Menor ganho de peso diário.
- Taxas de prenhez e partos mais baixas.
- Taxas de mortalidade mais elevadas.

### 2. Cenário de Transição para o Intensivo
Este cenário simula uma melhoria contínua e gradual ao longo de 10 anos, adotando práticas de um sistema intensivo, que incluem:
- Maior ganho de peso diário (devido a melhor nutrição).
- Melhores taxas de prenhez e partos.
- Menores taxas de mortalidade (devido a melhor sanidade e manejo).

## Como Usar

### Pré-requisitos

Para executar o modelo, é necessário ter Python instalado, juntamente com as seguintes bibliotecas:
- `numpy`
- `pandas`
- `matplotlib`
- `openpyxl`

Você pode instalar as dependências necessárias executando o seguinte comando no seu terminal:
```bash
pip install numpy pandas matplotlib openpyxl
```

### Execução

Para rodar a simulação, basta executar o script Python a partir do seu terminal:
```bash
python modelo.py
```

### Saídas do Modelo

Após a execução, o script produzirá três saídas principais:

1.  **Resultados no Console:** Um resumo comparativo dos KPIs no final do período de simulação (ano de 2034) será impresso diretamente no console, mostrando a variação percentual do cenário de transição em relação à linha de base.

2.  **Relatório em Excel:** Um arquivo chamado `resultados_anuais.xlsx` será salvo no mesmo diretório. Este arquivo contém quatro abas, cada uma detalhando a evolução anual de um KPI para os dois cenários:
    - `Rebanho_Total`
    - `Producao_Anual_Carne`
    - `Emissoes_Totais_GEE`
    - `Intensidade_Emissoes`

3.  **Visualização Gráfica:** Uma janela será exibida com quatro gráficos comparando a evolução do rebanho, produção de carne, emissões totais e intensidade de emissões para os cenários "Extensivo" e "Intensivo" ao longo dos 10 anos.

## Análise dos Resultados

A análise comparativa dos cenários permite avaliar os trade-offs e sinergias da intensificação da pecuária. Tipicamente, os resultados demonstram que a transição para um sistema mais intensivo pode levar a:
- **Aumento da Produtividade:** Maior produção de carne com um rebanho potencialmente menor ou de crescimento mais lento.
- **Redução da Intensidade de Emissões:** Uma queda significativa na quantidade de GEE emitida por quilo de carne produzido, representando um "desacoplamento" entre a produção e as emissões.
- **Impacto nas Emissões Totais:** O efeito nas emissões absolutas pode variar. A maior eficiência pode levar a uma redução, mas um aumento drástico na produção pode, em alguns casos, mitigar essa redução.

Este modelo serve como uma ferramenta estratégica para formuladores de políticas, produtores e pesquisadores interessados em promover uma pecuária mais sustentável e de baixa emissão em Goiás.
