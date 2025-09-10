import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# Nota: Pode ser necessário instalar a biblioteca openpyxl para exportar para Excel
# Execute no seu terminal: pip install openpyxl

# --- PARÂMETROS FIXOS GLOBAIS ---
# Estes são valores constantes que não mudam entre os cenários
PESO_VENDA_NOVILHAS_DESCARTE = 380
PESO_VENDA_VACAS_DESCARTE = 450
RENDIMENTO_CANAL_NOVILHAS = 0.52
RENDIMENTO_CANAL_VACAS = 0.52
RENDIMENTO_CANAL_TOROS = 0.52
PESO_FINAL_TERNERA_H = 190
RATIO_TOROS_POR_VACA = 25
PESO_FINAL_TERNERO_M = 230
PESO_INICIAL_NOVILLO_M = 230
PESO_FINAL_NOVILLO_M = 300
PESO_INICIAL_TORO = 300
PESO_FINAL_TORO = 530
FACTOR_EMISION_TERNERA = 2.31
FACTOR_EMISION_NOVILLA = 3.68
FACTOR_EMISION_VACA = 4.41
FACTOR_EMISION_TERNERO = 2.50
FACTOR_EMISION_NOVILLO = 4.45
FACTOR_EMISION_TORO = 6.06

def run_simulation_with_transition(start_params, end_params, capacidade_de_carga):
    """
    Executa uma simulação do modelo de gado implementando uma transição gradual
    de parâmetros de um cenário inicial para um final ao longo de 10 anos,
    e considera uma capacidade de carga dinâmica.
    Retorna os resultados e o estado final detalhado.
    """
    # --- 1. CONFIGURAÇÃO DA SIMULAÇÃO ---
    t_inicial = 0
    t_final = 3650  # 10 anos
    dt = 1
    pasos = int((t_final - t_inicial) / dt)
    tiempo = np.linspace(t_inicial, t_final, pasos + 1)

    # --- 2. INICIALIZAÇÃO DE ESTOQUES ---
    Terneras, Novillas, Vacas = np.zeros(pasos + 1), np.zeros(pasos + 1), np.zeros(pasos + 1)
    Terneros, Novillos, Toros = np.zeros(pasos + 1), np.zeros(pasos + 1), np.zeros(pasos + 1)
    Carne_Producida_Acumulada = np.zeros(pasos + 1)
    Carne_Producida_Diaria = np.zeros(pasos + 1) 
    Emisiones_Acumuladas = np.zeros(pasos + 1)
    Emisiones_Totais_GEI = np.zeros(pasos + 1)
    Intensidad_de_Emisiones = np.zeros(pasos + 1)

    # População inicial
    Terneras[0] = 2372988
    Novillas[0] = 2372988
    Vacas[0] = 10915744
    Terneros[0] = 2847585
    Novillos[0] = 2372988
    Toros[0] = 2847585

    # --- 4. LOOP DE SIMULAÇÃO ---
    for i in range(1, pasos + 1):
        progreso = (i - 1) / pasos
        params = {key: start_params[key] + (end_params[key] - start_params[key]) * progreso for key in start_params}
        
        poblacion_total_anterior = Terneras[i-1] + Novillas[i-1] + Vacas[i-1] + Terneros[i-1] + Novillos[i-1] + Toros[i-1]
        factor_de_estres = max(0, (poblacion_total_anterior / capacidade_de_carga) - 1)

        # Ajuste dinâmico de parâmetros
        porc_novillas_preñadas_ajustado = params['porc_novillas_preñadas'] / (1 + factor_de_estres)
        porc_vacas_preñadas_ajustado = params['porc_vacas_preñadas'] / (1 + factor_de_estres)
        gdp_ternera_h_ajustada = params['ganancia_peso_diario_ternera_h'] / (1 + factor_de_estres)
        gdp_novilla_ajustada = params['ganancia_peso_diario_novilla'] / (1 + factor_de_estres)
        gdp_ternero_m_ajustada = params['ganancia_peso_diario_ternero_m'] / (1 + factor_de_estres)
        gdp_novillo_m_ajustada = params['ganancia_peso_diario_novillo_m'] / (1 + factor_de_estres)
        gdp_toro_ajustada = params['ganancia_peso_diario_toro'] / (1 + factor_de_estres)
        tasa_muerte_terneras_ajustada = params['tasa_muerte_terneras'] * (1 + factor_de_estres)
        tasa_muerte_novillas_ajustada = params['tasa_muerte_novillas'] * (1 + factor_de_estres)
        tasa_muerte_vacas_ajustada = params['tasa_muerte_vacas'] * (1 + factor_de_estres)
        tasa_muerte_terneros_ajustada = params['tasa_muerte_terneros'] * (1 + factor_de_estres)
        tasa_muerte_novillos_ajustada = params['tasa_muerte_novillos'] * (1 + factor_de_estres)

        # Cálculo de fluxos
        Tiempo_Maduracion_Ternera = (PESO_FINAL_TERNERA_H - params['peso_inicial_ternera_h']) / gdp_ternera_h_ajustada if gdp_ternera_h_ajustada > 0 else float('inf')
        Tiempo_Maduracion_Novilla = (params['peso_final_novilla'] - params['peso_inicial_novilla']) / gdp_novilla_ajustada if gdp_novilla_ajustada > 0 else float('inf')
        Tiempo_Maduracion_Ternero_a_Novillo = (PESO_FINAL_TERNERO_M - params['peso_inicial_ternero_m']) / gdp_ternero_m_ajustada if gdp_ternero_m_ajustada > 0 else float('inf')
        Tiempo_Maduracion_Novillo_a_Toro = (PESO_FINAL_NOVILLO_M - PESO_INICIAL_NOVILLO_M) / gdp_novillo_m_ajustada if gdp_novillo_m_ajustada > 0 else float('inf')
        Tiempo_Engorde_Toro = (PESO_FINAL_TORO - PESO_INICIAL_TORO) / gdp_toro_ajustada if gdp_toro_ajustada > 0 else float('inf')
        Nacimientos_de_Novillas = Novillas[i-1] * porc_novillas_preñadas_ajustado * params['porc_partos_novillas']
        Nacimientos_de_Vacas = Vacas[i-1] * porc_vacas_preñadas_ajustado * params['porc_partos_vacas']
        Nacimientos_Totales = (Nacimientos_de_Novillas + Nacimientos_de_Vacas) / 365
        flujo_nac_hembras = Nacimientos_Totales * params['porc_hembra']
        flujo_nac_machos = Nacimientos_Totales * (1 - params['porc_hembra'])
        flujo_mad_terneras = Terneras[i-1] / Tiempo_Maduracion_Ternera if Tiempo_Maduracion_Ternera > 0 else 0
        novillas_no_preñadas = Novillas[i-1] * (1 - porc_novillas_preñadas_ajustado)
        flujo_venta_novillas = (novillas_no_preñadas * params['porc_descarte_novillas_no_preñadas']) / 365
        novillas_preñadas = Novillas[i-1] * porc_novillas_preñadas_ajustado
        flujo_conv_a_vacas = novillas_preñadas / Tiempo_Maduracion_Novilla if Tiempo_Maduracion_Novilla > 0 else 0
        flujo_venta_vacas = Vacas[i-1] * params['porc_descarte_vacas'] / 365
        toros_requeridos = Vacas[i-1] / RATIO_TOROS_POR_VACA
        toros_excedentes = max(0, Toros[i-1] - toros_requeridos)
        flujo_mad_terneros = Terneros[i-1] / Tiempo_Maduracion_Ternero_a_Novillo if Tiempo_Maduracion_Ternero_a_Novillo > 0 else 0
        flujo_mad_novillos = Novillos[i-1] / Tiempo_Maduracion_Novillo_a_Toro if Tiempo_Maduracion_Novillo_a_Toro > 0 else 0
        flujo_venta_toros = toros_excedentes / Tiempo_Engorde_Toro if Tiempo_Engorde_Toro > 0 else 0
        flujo_mue_terneras = Terneras[i-1] * tasa_muerte_terneras_ajustada / 365
        flujo_mue_novillas = Novillas[i-1] * tasa_muerte_novillas_ajustada / 365
        flujo_mue_vacas = Vacas[i-1] * tasa_muerte_vacas_ajustada / 365
        flujo_mue_terneros_m = Terneros[i-1] * tasa_muerte_terneros_ajustada / 365
        flujo_mue_novillos_m = Novillos[i-1] * tasa_muerte_novillos_ajustada / 365
        flujo_mue_toros_m = Toros[i-1] * params['tasa_muerte_toros'] / 365
        
        produccion_carne_novillas = flujo_venta_novillas * PESO_VENDA_NOVILHAS_DESCARTE * RENDIMENTO_CANAL_NOVILHAS
        produccion_carne_vacas = flujo_venta_vacas * PESO_VENDA_VACAS_DESCARTE * RENDIMENTO_CANAL_VACAS
        produccion_carne_toros = flujo_venta_toros * PESO_FINAL_TORO * RENDIMENTO_CANAL_TOROS
        flujo_produccion_carne_total = produccion_carne_novillas + produccion_carne_vacas + produccion_carne_toros

        # Atualização de estoques
        Terneras[i] = Terneras[i-1] + (flujo_nac_hembras - flujo_mad_terneras - flujo_mue_terneras) * dt
        Novillas[i] = Novillas[i-1] + (flujo_mad_terneras - flujo_conv_a_vacas - flujo_venta_novillas - flujo_mue_novillas) * dt
        Vacas[i] = Vacas[i-1] + (flujo_conv_a_vacas - flujo_venta_vacas - flujo_mue_vacas) * dt
        Terneros[i] = Terneros[i-1] + (flujo_nac_machos - flujo_mad_terneros - flujo_mue_terneros_m) * dt
        Novillos[i] = Novillos[i-1] + (flujo_mad_terneros - flujo_mad_novillos - flujo_mue_novillos_m) * dt
        Toros[i] = Toros[i-1] + (flujo_mad_novillos - flujo_venta_toros - flujo_mue_toros_m) * dt
        Terneras[i], Novillas[i], Vacas[i] = max(0, Terneras[i]), max(0, Novillas[i]), max(0, Vacas[i])
        Terneros[i], Novillos[i], Toros[i] = max(0, Terneros[i]), max(0, Novillos[i]), max(0, Toros[i])

        # Atualização de métricas
        emisiones_h = (Terneras[i] * FACTOR_EMISION_TERNERA) + (Novillas[i] * FACTOR_EMISION_NOVILLA) + (Vacas[i] * FACTOR_EMISION_VACA)
        emisiones_m = (Terneros[i] * FACTOR_EMISION_TERNERO) + (Novillos[i] * FACTOR_EMISION_NOVILLO) + (Toros[i] * FACTOR_EMISION_TORO)
        Emisiones_Totais_GEI[i] = emisiones_h + emisiones_m
        Carne_Producida_Diaria[i] = flujo_produccion_carne_total 
        Carne_Producida_Acumulada[i] = Carne_Producida_Acumulada[i-1] + flujo_produccion_carne_total * dt
        Emisiones_Acumuladas[i] = Emisiones_Acumuladas[i-1] + Emisiones_Totais_GEI[i] * dt
        Intensidad_de_Emisiones[i] = Emisiones_Acumuladas[i] / Carne_Producida_Acumulada[i] if Carne_Producida_Acumulada[i] > 0 else 0

    # --- 5. EMPACOTAR RESULTADOS ---
    anos = 2025 + (tiempo / 365)
    df = pd.DataFrame({
        'Ano': anos, 'Total_Rebanho': Terneras + Novillas + Vacas + Terneros + Novillos + Toros,
        'Carne_Producida_Anual': Carne_Producida_Diaria, 'Emissoes_Totais_GEI': Emisiones_Totais_GEI,
        'Intensidade_de_Emissoes': Intensidad_de_Emisiones
    }).set_index('Ano')
    
    final_stocks = {'Bezerras': Terneras[-1], 'Novilhas': Novillas[-1], 'Vacas': Vacas[-1],
                    'Bezerros': Terneros[-1], 'Novilhos': Novillos[-1], 'Touros': Toros[-1]}
    final_emissions = {
        'Bezerras': Terneras[-1] * FACTOR_EMISION_TERNERA, 'Novilhas': Novillas[-1] * FACTOR_EMISION_NOVILLA,
        'Vacas': Vacas[-1] * FACTOR_EMISION_VACA, 'Bezerros': Terneros[-1] * FACTOR_EMISION_TERNERO,
        'Novilhos': Novillos[-1] * FACTOR_EMISION_NOVILLO, 'Touros': Toros[-1] * FACTOR_EMISION_TORO
    }
    return df, final_stocks, final_emissions

# --- CONFIGURAÇÃO DE CENÁRIOS ---
CAPACIDADE_DE_CARGA_REGION = 26_000_000 
escenario_extensivo = {
    'peso_inicial_ternera_h': 28, 'ganancia_peso_diario_ternera_h': 0.50, 'peso_inicial_novilla': 190, 
    'peso_final_novilla': 450, 'ganancia_peso_diario_novilla': 0.25, 'peso_inicial_ternero_m': 28, 
    'ganancia_peso_diario_ternero_m': 0.50, 'ganancia_peso_diario_novillo_m': 0.25, 'ganancia_peso_diario_toro': 0.50,
    'porc_novillas_preñadas': 0.65, 'porc_vacas_preñadas': 0.65, 'porc_partos_novillas': 0.85, 'porc_partos_vacas': 0.85,
    'porc_hembra': 0.50, 'porc_descarte_novillas_no_preñadas': 0.35, 'porc_descarte_vacas': 0.35, 
    'tasa_muerte_terneras': 0.05, 'tasa_muerte_novillas': 0.05, 'tasa_muerte_vacas': 0.05,
    'tasa_muerte_terneros': 0.05, 'tasa_muerte_novillos': 0.05, 'tasa_muerte_toros': 0.02
}
escenario_intensivo = {
    'peso_inicial_ternera_h': 40, 'ganancia_peso_diario_ternera_h': 0.70, 'peso_inicial_novilla': 190, 
    'peso_final_novilla': 450, 'ganancia_peso_diario_novilla': 0.50, 'peso_inicial_ternero_m': 40, 
    'ganancia_peso_diario_ternero_m': 0.70, 'ganancia_peso_diario_novillo_m': 0.50, 'ganancia_peso_diario_toro': 0.75,
    'porc_novillas_preñadas': 0.70, 'porc_vacas_preñadas': 0.70, 'porc_partos_novillas': 0.90, 'porc_partos_vacas': 0.90,
    'porc_hembra': 0.50, 'porc_descarte_novillas_no_preñadas': 0.30, 'porc_descarte_vacas': 0.30, 
    'tasa_muerte_terneras': 0.02, 'tasa_muerte_novillas': 0.02, 'tasa_muerte_vacas': 0.02,
    'tasa_muerte_terneros': 0.02, 'tasa_muerte_novillos': 0.02, 'tasa_muerte_toros': 0.02
}

# --- EXECUÇÃO DAS SIMULAÇÕES ---
print("Executando simulações...")
df_base, final_stocks_base, final_emissions_base = run_simulation_with_transition(escenario_extensivo, escenario_extensivo, CAPACIDADE_DE_CARGA_REGION)
df_transicion, final_stocks_trans, final_emissions_trans = run_simulation_with_transition(escenario_extensivo, escenario_intensivo, CAPACIDADE_DE_CARGA_REGION)
print("Simulações concluídas.")

# --- CÁLCULO DE KPIS E CONTRIBUIÇÕES ---
df_base_anual = df_base.groupby(df_base.index.astype(int))['Carne_Producida_Anual'].sum().iloc[:-1]
df_transicion_anual = df_transicion.groupby(df_transicion.index.astype(int))['Carne_Producida_Anual'].sum().iloc[:-1]

kpi_rebano_base = df_base['Total_Rebanho'].loc[df_base.index < 2035].iloc[-1]
kpi_rebano_trans = df_transicion['Total_Rebanho'].loc[df_transicion.index < 2035].iloc[-1]
kpi_carne_base = df_base_anual.loc[2034]
kpi_carne_trans = df_transicion_anual.loc[2034]
kpi_emisiones_base = df_base['Emissoes_Totais_GEI'].loc[df_base.index < 2035].iloc[-1]
kpi_emisiones_trans = df_transicion['Emissoes_Totais_GEI'].loc[df_transicion.index < 2035].iloc[-1]
kpi_intensidad_base = df_base['Intensidade_de_Emissoes'].loc[df_base.index < 2035].iloc[-1]
kpi_intensidad_trans = df_transicion['Intensidade_de_Emissoes'].loc[df_transicion.index < 2035].iloc[-1]

def diff_percent(new, old):
    return ((new - old) / old) * 100 if old != 0 else 0

print("\n--- INDICADORES-CHAVE AO FINAL DO PERÍODO (ANO 2034) ---")
print(f"* Rebanho Total: {diff_percent(kpi_rebano_trans, kpi_rebano_base):.2f}%")
print(f"* Produção Anual de Carne: {diff_percent(kpi_carne_trans, kpi_carne_base):.2f}%")
print(f"* Emissões Totais Diárias: {diff_percent(kpi_emisiones_trans, kpi_emisiones_base):.2f}%")
print(f"* Intensidade de Emissões: {diff_percent(kpi_intensidad_trans, kpi_intensidad_base):.2f}%")

def print_contributions(title, data):
    total = sum(data.values())
    print(f"\n--- {title} ---")
    if total == 0:
        print("Não há dados para mostrar.")
        return
    print(f"{'Categoria':<12} | {'Contribuição (%)'}")
    print("-" * 30)
    for key, value in data.items():
        print(f"{key:<12} | {((value / total) * 100):.2f}%")

print("\n--- ANÁLISE DE CONTRIBUIÇÃO POR CATEGORIA (ANO 2034) ---")
print("\nCENÁRIO LINHA DE BASE (EXTENSIVO):")
print_contributions("Composição do Rebanho", final_stocks_base)
print_contributions("Contribuição para Emissões", final_emissions_base)
print("\nCENÁRIO INTENSIVO:")
print_contributions("Composição do Rebanho", final_stocks_trans)
print_contributions("Contribuição para Emissões", final_emissions_trans)


# --- EXPORTAÇÃO PARA EXCEL ---
print("\nExportando resultados anuais para Excel...")

# Preparar dados anuais
# Rebanho: Pegar o último valor de cada ano
df_rebano_anual = pd.concat([
    df_base['Total_Rebanho'].groupby(df_base.index.astype(int)).last().iloc[:-1],
    df_transicion['Total_Rebanho'].groupby(df_transicion.index.astype(int)).last().iloc[:-1]
], axis=1)
df_rebano_anual.columns = ['Extensivo (Linha de Base)', 'Intensivo']

# Carne: Já está calculado anualmente
df_carne_anual = pd.concat([df_base_anual, df_transicion_anual], axis=1)
df_carne_anual.columns = ['Extensivo (Linha de Base)', 'Intensivo']

# Emissões: Pegar o último valor de cada ano
df_emissoes_anual = pd.concat([
    df_base['Emissoes_Totais_GEI'].groupby(df_base.index.astype(int)).last().iloc[:-1],
    df_transicion['Emissoes_Totais_GEI'].groupby(df_transicion.index.astype(int)).last().iloc[:-1]
], axis=1)
df_emissoes_anual.columns = ['Extensivo (Linha de Base)', 'Intensivo']

# Intensidade: Pegar o último valor de cada ano
df_intensidade_anual = pd.concat([
    df_base['Intensidade_de_Emissoes'].groupby(df_base.index.astype(int)).last().iloc[:-1],
    df_transicion['Intensidade_de_Emissoes'].groupby(df_transicion.index.astype(int)).last().iloc[:-1]
], axis=1)
df_intensidade_anual.columns = ['Extensivo (Linha de Base)', 'Intensivo']

# Escrever para o arquivo Excel
with pd.ExcelWriter('resultados_anuais.xlsx') as writer:
    df_rebano_anual.to_excel(writer, sheet_name='Rebanho_Total')
    df_carne_anual.to_excel(writer, sheet_name='Producao_Anual_Carne')
    df_emissoes_anual.to_excel(writer, sheet_name='Emissoes_Totais_GEE')
    df_intensidade_anual.to_excel(writer, sheet_name='Intensidade_Emissoes')

print("Arquivo 'resultados_anuais.xlsx' salvo com sucesso.")


# --- VISUALIZAÇÃO COMPARATIVA ---
print("\nGerando gráficos comparativos...")
plt.style.use('seaborn-v0_8-whitegrid')
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 14), dpi=300)
formatter = plt.FuncFormatter(lambda x, pos: f'{int(x):,}')

# Graficar resultados
df_base['Total_Rebanho'].plot(ax=ax1, color='red', linestyle='--', label='Extensivo (Linha de Base)')
df_transicion['Total_Rebanho'].plot(ax=ax1, color='blue', label='Intensivo')
df_base_anual.plot(ax=ax2, color='red', linestyle='--', label='Extensivo (Linha de Base)')
df_transicion_anual.plot(ax=ax2, color='blue', label='Intensivo')
df_base['Emissoes_Totais_GEI'].iloc[1:].plot(ax=ax3, color='red', linestyle='--', label='Extensivo (Linha de Base)')
df_transicion['Emissoes_Totais_GEI'].iloc[1:].plot(ax=ax3, color='blue', label='Intensivo')
df_base['Intensidade_de_Emissoes'].iloc[1:].plot(ax=ax4, color='red', linestyle='--', label='Extensivo (Linha de Base)')
df_transicion['Intensidade_de_Emissoes'].iloc[1:].plot(ax=ax4, color='blue', label='Intensivo')
    
# Configuração dos eixos
ax1.set(title='Evolução do Rebanho Total', ylabel='Número de Animais', xlabel='Ano', ylim=(0, None))
ax2.set(title='Produção Anual de Carne', ylabel='Carne Produzida (kg/ano)', xlabel='Ano', ylim=(0, None))
ax3.set(title='Evolução das Emissões Totais de GEE', ylabel='Emissões GEE (kg CO2-eq/dia)', xlabel='Ano', ylim=(0, None))
ax4.set(title='Evolução da Intensidade de Emissões', ylabel='kg CO2-eq / kg Carne', xlabel='Ano', ylim=(0, None))

for ax in [ax1, ax2, ax3, ax4]:
    ax.grid(True)
    ax.get_yaxis().set_major_formatter(formatter)
    ax.legend()

fig.suptitle('Análise de Transição Gradual (Extensivo para Intensivo)', fontsize=20, y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
print("Gráficos exibidos.")

