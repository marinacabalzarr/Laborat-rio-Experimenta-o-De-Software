import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timezone
import os # Biblioteca para manipulação de caminhos de arquivos

# Define o estilo dos gráficos para todos
plt.style.use('ggplot')

# 1. Carregar os dados do CSV gerado na coleta
# Usamos sep=';' porque foi assim que salvamos o arquivo
nome_arquivo_csv = 'repositorios.csv'
try:
    df = pd.read_csv(nome_arquivo_csv, sep=';')
    print(f"✅ Dados carregados com sucesso de '{nome_arquivo_csv}'!")
except FileNotFoundError:
    print(f"❌ Erro: Arquivo '{nome_arquivo_csv}' não encontrado. Certifique-se de que ele está na mesma pasta.")
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
print("📊 RESULTADOS DAS MEDIANAS (Para o Relatório)")
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

# 4. Visualização dos Dados (Gerando gráficos SEPARADOS)
print("\nGerando gráficos separados...")

# --- Gráfico 1: Distribuição da Idade (Histograma) - RQ 01 ---
plt.figure(figsize=(10, 6)) # Cria uma figura nova e exclusiva para este gráfico
plt.hist(df['Idade (Anos)'], bins=20, color='skyblue', edgecolor='black')
plt.title('Distribuição de Idade dos Repositórios (RQ 01)', fontsize=14)
plt.xlabel('Idade (Anos)', fontsize=12)
plt.ylabel('Quantidade de Repositórios', fontsize=12)
plt.grid(axis='y', alpha=0.75)
plt.tight_layout() # Ajusta o layout para não cortar textos
plt.savefig('grafico_rq01_idade.png', dpi=300) # Salva este gráfico individualmente
print("✅ Salvo: 'grafico_rq01_idade.png'")
plt.close() # Fecha a figura atual para liberar memória

# --- Gráfico 2: Linguagens mais populares (Barras Horizontais) - RQ 05 ---
plt.figure(figsize=(10, 8))
# Usamos o plot do pandas sem passar 'ax' para que ele crie na figura atual
contagem_linguagens.sort_values().plot(kind='barh', color='coral', edgecolor='black')
plt.title('Top 10 Linguagens Primárias (RQ 05)', fontsize=14)
plt.xlabel('Quantidade de Repositórios', fontsize=12)
plt.ylabel('Linguagem Primária', fontsize=12)
plt.tight_layout()
plt.savefig('grafico_rq05_linguagens.png', dpi=300)
print("✅ Salvo: 'grafico_rq05_linguagens.png'")
plt.close()

# --- Gráfico 3: Taxa de Issues Fechadas (Histograma) - RQ 06 ---
plt.figure(figsize=(10, 6))
plt.hist(df['Razao Issues Fechadas'], bins=20, color='lightgreen', edgecolor='black')
plt.title('Distribuição da Taxa de Issues Fechadas (RQ 06)', fontsize=14)
plt.xlabel('Taxa de Conclusão (%)', fontsize=12)
plt.ylabel('Quantidade de Repositórios', fontsize=12)
plt.grid(axis='y', alpha=0.75)
plt.tight_layout()
plt.savefig('grafico_rq06_issues.png', dpi=300)
print("✅ Salvo: 'grafico_rq06_issues.png'")
plt.close()

# --- Gráfico 4: Tempo sem atualização (Boxplot) - RQ 04 ---
plt.figure(figsize=(10, 4)) # Boxplots horizontais costumam ficar bons em formatos mais "achatados"
plt.boxplot(df['Dias sem Atualizacao'], vert=False, patch_artist=True, boxprops=dict(facecolor='plum'))
plt.title('Dias desde a última atualização (RQ 04)', fontsize=14)
plt.xlabel('Dias', fontsize=12)
# Remove o eixo Y que não é informativo para boxplots horizontais
plt.yticks([]) 
plt.tight_layout()
plt.savefig('grafico_rq04_atualizacao.png', dpi=300)
print("✅ Salvo: 'grafico_rq04_atualizacao.png'")
plt.close()

# =========================================================
# 🌟 BÔNUS: ANÁLISE DA RQ 07 (Gerando gráfico SEPARADO)
# =========================================================
print("\n" + "="*50)
print("🌟 RESULTADOS DO BÔNUS (RQ 07)")
print("="*50)

# 1. Defina aqui as linguagens citadas na reportagem do professor
# Certifique-se de que estas são as linguagens exatas da reportagem!
linguagens_da_reportagem = ['TypeScript', 'Python', 'JavaScript', 'Java', 'C++', 'C#'] 

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

# (Opcional) Gráfico de barras comparativo separado para a RQ07
print("Gerando gráfico do bônus separado...")
plt.figure(figsize=(15, 6))

# Define as posições das barras no eixo X
r = range(len(comparacao_rq07))
barWidth = 0.25

# Cria as barras para cada métrica
plt.bar(r, comparacao_rq07['Mediana de PRs'], color='gold', width=barWidth, edgecolor='grey', label='Mediana de PRs')
plt.bar([x + barWidth for x in r], comparacao_rq07['Mediana de Releases'], color='silver', width=barWidth, edgecolor='grey', label='Mediana de Releases')
plt.bar([x + 2*barWidth for x in r], comparacao_rq07['Dias sem Atualizar'], color='peru', width=barWidth, edgecolor='grey', label='Dias sem Atualizar')

# Adiciona legendas e formatação ao gráfico
plt.xlabel('Grupo de Linguagens', fontsize=12)
plt.ylabel('Quantidade / Dias', fontsize=12)
plt.title('Comparação de Métricas: Linguagens da Reportagem vs Outras (RQ 07)', fontsize=14)
plt.xticks([x + barWidth for x in r], comparacao_rq07.index) # Define os nomes dos grupos no eixo X
plt.legend() # Mostra a legenda das barras
plt.grid(axis='y', alpha=0.5)
plt.tight_layout()
plt.savefig('grafico_rq07_bonus.png', dpi=300)
print("✅ Salvo: 'grafico_rq07_bonus.png'")
plt.close()

print("\n🎉 Análise e visualização concluídas com sucesso!")
print("Todos os gráficos foram salvos como arquivos individuais na sua pasta.")