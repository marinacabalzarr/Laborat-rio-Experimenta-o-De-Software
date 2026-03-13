import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timezone

# 1. Carregar os dados do CSV gerado na coleta
# Usamos sep=';' porque foi assim que salvamos o arquivo
try:
    df = pd.read_csv('repositorios.csv', sep=';')
    print("✅ Dados carregados com sucesso!")
except FileNotFoundError:
    print("❌ Erro: Arquivo 'repositorios.csv' não encontrado. Certifique-se de que ele está na mesma pasta.")
    exit()

# 2. Preparar e Calcular as novas colunas
# Convertendo as strings de data para objetos de data reais (considerando o fuso horário UTC do GitHub)
df['Data de Criacao'] = pd.to_datetime(df['Data de Criacao'])
df['Data de Atualizacao'] = pd.to_datetime(df['Data de Atualizacao'])
hoje = datetime.now(timezone.utc)

# RQ 01: Idade do repositório em anos
df['Idade (Anos)'] = (hoje - df['Data de Criacao']).dt.days / 365.25

# RQ 04: Tempo desde a última atualização em dias
df['Dias sem Atualizacao'] = (hoje - df['Data de Atualizacao']).dt.days

# RQ 06: Razão de Issues Fechadas (evitando divisão por zero)
# Onde Total de Issues for maior que zero, calcula a razão. Se não, coloca 0.
df['Razao Issues Fechadas'] = df.apply(
    lambda row: (row['Issues Fechadas'] / row['Total de Issues']) * 100 if row['Total de Issues'] > 0 else 0, 
    axis=1
)

# 3. Sumarização dos Dados (Cálculo das Medianas)
print("\n" + "="*50)
print("RESULTADOS DAS MEDIANAS (Para o Relatório)")
print("="*50)

print(f"RQ 01 - Mediana de Idade: {df['Idade (Anos)'].median():.2f} anos")
print(f"RQ 02 - Mediana de PRs Aceitos: {df['Pull Requests Aceitos'].median():.0f}")
print(f"RQ 03 - Mediana de Releases: {df['Total de Releases'].median():.0f}")
print(f"RQ 04 - Mediana de Dias sem Atualização: {df['Dias sem Atualizacao'].median():.0f} dias")
print(f"RQ 06 - Mediana da Taxa de Issues Fechadas: {df['Razao Issues Fechadas'].median():.2f}%")

print("\nRQ 05 - Linguagens Primárias mais Populares (Top 10):")
contagem_linguagens = df['Linguagem Primaria'].value_counts().head(10)
print(contagem_linguagens)

print("="*50)

# 4. Visualização dos Dados (Gráficos)
print("\nGerando gráficos...")

# Define o estilo dos gráficos
plt.style.use('ggplot')

# Figura com 2 linhas e 2 colunas para agrupar os gráficos
fig, axs = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('Análise dos Repositórios Populares no GitHub', fontsize=16)

# Gráfico 1: Distribuição da Idade (Histograma)
axs[0, 0].hist(df['Idade (Anos)'], bins=20, color='skyblue', edgecolor='black')
axs[0, 0].set_title('Distribuição de Idade dos Repositórios (RQ 01)')
axs[0, 0].set_xlabel('Idade (Anos)')
axs[0, 0].set_ylabel('Quantidade de Repositórios')

# Gráfico 2: Linguagens mais populares (Gráfico de Barras Horizontais)
contagem_linguagens.sort_values().plot(kind='barh', ax=axs[0, 1], color='coral', edgecolor='black')
axs[0, 1].set_title('Top 10 Linguagens Primárias (RQ 05)')
axs[0, 1].set_xlabel('Quantidade de Repositórios')

# Gráfico 3: Taxa de Issues Fechadas (Histograma)
axs[1, 0].hist(df['Razao Issues Fechadas'], bins=20, color='lightgreen', edgecolor='black')
axs[1, 0].set_title('Distribuição da Taxa de Issues Fechadas (RQ 06)')
axs[1, 0].set_xlabel('Taxa de Conclusão (%)')
axs[1, 0].set_ylabel('Quantidade de Repositórios')

# Gráfico 4: Tempo sem atualização (Boxplot)
axs[1, 1].boxplot(df['Dias sem Atualizacao'], vert=False, patch_artist=True, boxprops=dict(facecolor='plum'))
axs[1, 1].set_title('Dias desde a última atualização (RQ 04)')
axs[1, 1].set_xlabel('Dias')

# Ajusta o layout para não sobrepor os textos e exibe os gráficos na tela
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

# =========================================================
# BÔNUS: ANÁLISE DA RQ 07
# =========================================================
print("\n" + "="*50)
print("="*50)

# 1. Defina aqui as linguagens citadas na reportagem do professor
linguagens_da_reportagem = ['Python', 'TypeScript', 'JavaScript', 'Go', 'Rust'] 

# 2. Cria uma nova coluna separando os repositórios em dois times
df['Grupo'] = df['Linguagem Primaria'].apply(
    lambda x: 'Linguagens Populares' if x in linguagens_da_reportagem else 'Outras Linguagens'
)

# 3. Agrupa e tira a mediana apenas das 3 métricas pedidas na RQ 07
comparacao_rq07 = df.groupby('Grupo')[['Pull Requests Aceitos', 'Total de Releases', 'Dias sem Atualizacao']].median()

# Renomeando as colunas só para o print ficar mais bonito e fácil de ler
comparacao_rq07.columns = ['Mediana de PRs', 'Mediana de Releases', 'Dias sem Atualizar']

print(comparacao_rq07)
print("="*50)

# (Opcional) Gráfico de barras simples para a RQ07 para você colocar no relatório
fig2, ax2 = plt.subplots(1, 3, figsize=(15, 5))
fig2.suptitle('Comparação: Linguagens Populares vs Outras (RQ 07)', fontsize=16)

comparacao_rq07['Mediana de PRs'].plot(kind='bar', ax=ax2[0], color=['gold', 'silver'], edgecolor='black')
ax2[0].set_title('Contribuição Externa (PRs)')
ax2[0].set_ylabel('Quantidade Mediana')
ax2[0].tick_params(axis='x', rotation=0)

comparacao_rq07['Mediana de Releases'].plot(kind='bar', ax=ax2[1], color=['gold', 'silver'], edgecolor='black')
ax2[1].set_title('Frequência de Releases')
ax2[1].tick_params(axis='x', rotation=0)

comparacao_rq07['Dias sem Atualizar'].plot(kind='bar', ax=ax2[2], color=['gold', 'silver'], edgecolor='black')
ax2[2].set_title('Tempo sem Atualizar (Menos é Melhor)')
ax2[2].set_ylabel('Dias')
ax2[2].tick_params(axis='x', rotation=0)

plt.tight_layout()
plt.show()

print("✅ Análise e visualização concluídas!")