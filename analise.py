# ==========================================================
# Projeto: Público do Botafogo-SP no Paulistão (2022 a 2026)
# Autor: Caio Missão
# Objetivo: analisar a evolução da torcida do Botafogo-SP nos
# jogos do Paulistão, comparando jogos contra os grandes da
# capital e contra os demais times.
# Fonte: boletins financeiros da Federação Paulista de Futebol
# ==========================================================

# ----------------------------------------------------------
# Etapa 1: Importação da biblioteca
# ----------------------------------------------------------
import pandas as pd  # biblioteca para trabalhar com tabelas

# ----------------------------------------------------------
# Etapa 2: Leitura dos dados
# ----------------------------------------------------------
# Lê a planilha com os jogos do Botafogo-SP no Paulistão
dados = pd.read_excel("DadosJogos.xlsx")

# Mostra as 5 primeiras linhas e o tamanho da tabela (linhas, colunas)
print(dados.head())
print(dados.shape)

# ----------------------------------------------------------
# Etapa 3: Preparação dos dados
# ----------------------------------------------------------
# Cria a coluna "ano" a partir da data do jogo
dados["ano"] = dados["Data do jogo"].dt.year

# Mantém só os jogos de 2022 em diante
# (2018 e 2019 ficam de fora porque os boletins da época não separam
# torcida visitante e menores de 12 anos; 2020 e 2021 não entram
# por causa da pandemia)
dados = dados[dados["ano"] >= 2022].copy()

# Lista dos grandes da capital
grandes = ["São Paulo", "Corinthians", "Palmeiras", "Santos"]

# Classifica cada adversário como "Grandes" ou "Outros"
# (o strip() remove espaços sobrando no nome do time)
dados["grupo"] = dados["Adversário"].str.strip().apply(
    lambda time: "Grandes" if time in grandes else "Outros"
)

# Função que define o resultado do jogo a partir dos gols
def resultado(jogo):
    if jogo["Gols do Botafogo"] > jogo["Gols do adversário"]:
        return "Vitória"
    elif jogo["Gols do Botafogo"] == jogo["Gols do adversário"]:
        return "Empate"
    else:
        return "Derrota"

# Aplica a função em cada linha da tabela
dados["resultado"] = dados.apply(resultado, axis=1)

# Público visitante: público total menos a torcida do Botafogo
dados["visitantes"] = dados["Público total"] - dados["Público de torcedores do Botafogo"]

# Separa os jogos em casa (mandante) e fora (visitante)
casa = dados[dados["Mando de campo"] == "Mandante"].copy()
fora = dados[dados["Mando de campo"] == "Visitante"].copy()

print("\nJogos em casa (linhas, colunas):", casa.shape)

# ----------------------------------------------------------
# Análise 1: Média da torcida do Botafogo em casa, por grupo
# ----------------------------------------------------------
resumo = casa.groupby("grupo")["Público de torcedores do Botafogo"].mean().round()

print("\nMédia da torcida do Botafogo em casa (2022-2026):")
print(resumo)

# ----------------------------------------------------------
# Análise 2: Torcida do Botafogo em casa, por ano e por grupo
# ----------------------------------------------------------
# Quantidade de jogos e média de torcedores do Botafogo
por_ano = casa.groupby(["ano", "grupo"]).agg(
    jogos=("Público de torcedores do Botafogo", "size"),
    media=("Público de torcedores do Botafogo", "mean"),
).round()

print("\nTorcida do Botafogo em casa, por ano e grupo:")
print(por_ano.unstack())

# ----------------------------------------------------------
# Análise 3: Percentual de menores de 12 anos na torcida
# ----------------------------------------------------------
# Médias de menores de 12 e da torcida do Botafogo, por ano e grupo
medias = casa.groupby(["ano", "grupo"])[
    ["Público menor de 12 anos", "Público de torcedores do Botafogo"]
].mean()

# Percentual de menores de 12 em relação à torcida do Botafogo
proporcao = (
    medias["Público menor de 12 anos"]
    / medias["Público de torcedores do Botafogo"] * 100
).round(1)

print("\nPercentual de menores de 12 anos na torcida do Botafogo:")
print(proporcao.unstack())

# ----------------------------------------------------------
# Análise 4: Torcida do Botafogo fora de casa
# ----------------------------------------------------------
# Quantidade de jogos fora e total de torcedores que viajaram, por ano
viagem = fora.groupby("ano").agg(
    jogos=("Público de torcedores do Botafogo", "size"),
    total=("Público de torcedores do Botafogo", "sum"),
)

print("\nTorcedores do Botafogo fora de casa:")
print(viagem)

# ----------------------------------------------------------
# Análise 5: Torcida visitante dos grandes no Santa Cruz
# ----------------------------------------------------------
# Filtra os jogos em casa contra os grandes
jogos_grandes = casa[casa["grupo"] == "Grandes"]

# Quantidade de jogos e média de visitantes, por ano
print("\nVisitantes dos grandes em Ribeirão Preto:")
print(jogos_grandes.groupby("ano")["visitantes"].agg(["count", "mean"]).round())

# ----------------------------------------------------------
# Análise 6: Desempenho em campo
# ----------------------------------------------------------
# Vitórias, empates e derrotas por ano (todos os jogos)
print("\nDesempenho por ano:")
print(pd.crosstab(dados["ano"], dados["resultado"]))

# ----------------------------------------------------------
# Etapa final: Exportação para o Power BI
# ----------------------------------------------------------
# Salva a tabela tratada, com as colunas novas, para o dashboard
dados.to_excel("botafogo_powerbi.xlsx", index=False)

print("\nTabela salva para o Power BI!")