# ==========================================================
# Script: torcida visitante dos times do interior no Paulistão 2026
# Lê os boletins financeiros (PDF) da FPF e soma o público visitante
#
# Critério: conta só ingressos pagos (gratuidades ficam de fora,
# porque os boletins não as identificam do mesmo jeito em todos os jogos)
#
# Os PDFs foram baixados manualmente do site da FPF, só dos jogos
# em que um time do interior foi visitante (fase de grupos).
# Eles não estão no repositório: para rodar, salvei na pasta
# "BoletinsFinanceiros/Paulistão 2026".
# ==========================================================

import pdfplumber   # lê PDF
import glob         # lista arquivos da pasta
import re           # procura padrões dentro de um texto
import pandas as pd # trabalha com tabelas

# ----------------------------------------------------------
# Etapa 1: Leitura dos boletins
# ----------------------------------------------------------
arquivos = glob.glob("BoletinsFinanceiros/Paulistão 2026/*.pdf")
print(len(arquivos), "PDFs encontrados")

# Palavras que indicam gratuidade (essas linhas não entram na conta)
gratuidades = ["GRATUIDADE", "MENOR", "LEI N"]

linhas = []  # um resultado por jogo

for arquivo in arquivos:
    try:
        # Lê o texto de todas as páginas do PDF
        with pdfplumber.open(arquivo) as pdf:
            texto = "\n".join(pagina.extract_text() or "" for pagina in pdf.pages)

        # Data do jogo
        data = re.search(r"Data:\s*(\d{2}/\d{2}/\d{4})", texto).group(1)

        # Nomes dos clubes na divisão da renda: "Nome - (100%)"
        # O primeiro é o mandante e o segundo é o visitante
        clubes = re.findall(r"^(.+?) - \(\d+%\)", texto, re.MULTILINE)
        mandante = clubes[0].strip()
        visitante = clubes[1].strip()

        # Soma a coluna "vendidos" dos setores de torcida visitante
        total = 0
        for linha in texto.splitlines():
            texto_linha = linha.upper()

            # Regra geral: setor com a palavra VISITANTE
            eh_visitante = "VISITANTE" in texto_linha

            # Exceção: no estádio do Velo Clube, os visitantes
            # ficam na arquibancada descoberta sul
            if "VELO CLUBE" in mandante.upper() and "DESCOBERTA SUL" in texto_linha:
                eh_visitante = True

            # Ignora as linhas de gratuidade
            if any(palavra in texto_linha for palavra in gratuidades):
                eh_visitante = False

            if eh_visitante:
                parte = linha.split("R$")[0]         # só o texto antes do preço
                numeros = re.findall(r"\d+", parte)  # números dessa parte
                if numeros:
                    total += int(numeros[-1])        # último número = vendidos

        # Conferência: mostra os jogos que ficaram com zero visitantes
        if total == 0:
            print("\nZerado:", mandante, "x", visitante)

        linhas.append({
            "data": data,
            "mandante": mandante,
            "visitante": visitante,
            "torcida_visitante": total,
        })

    except Exception as erro:
        # Se algum PDF der problema, mostra qual foi e segue para o próximo
        print("Problema no arquivo:", arquivo, "-", erro)

# Junta tudo numa tabela
tabela = pd.DataFrame(linhas)

# Transforma a coluna em decimal, para aceitar "sem dado" (vazio)
tabela["torcida_visitante"] = tabela["torcida_visitante"].astype(float)

# ----------------------------------------------------------
# Etapa 2: Correções manuais (valores conferidos no próprio PDF)
# ----------------------------------------------------------
# Capivariano x Portuguesa: boletim sem setor visitante identificado
# 61 inteira + 96 meia = 157
correcao = tabela["mandante"].str.contains("Capivariano") & tabela["visitante"].str.contains("Portuguesa")
tabela.loc[correcao, "torcida_visitante"] = 157

# Novorizontino x Guarani: setor B sem o nome "visitante"
# 14 + 65 = 79
correcao = tabela["mandante"].str.contains("Novorizontino") & tabela["visitante"].str.contains("Guarani")
tabela.loc[correcao, "torcida_visitante"] = 79

# Santos x Bragantino (Neo Química Arena): o boletim não separa
# torcida visitante e mandante no setor sul, então fica sem dado
correcao = tabela["mandante"].str.contains("Santos") & tabela["visitante"].str.contains("Bragantino")
tabela.loc[correcao, "torcida_visitante"] = None

# Torcida única: times de Campinas não podem levar torcida
# visitante contra os grandes do estado, então fica sem dado
grandes_estado = "São Paulo|Corinthians|Palmeiras|Santos"
campinas = "Guarani|Ponte Preta"
correcao = tabela["mandante"].str.contains(grandes_estado) & tabela["visitante"].str.contains(campinas)
tabela.loc[correcao, "torcida_visitante"] = None

# Dérbi de Campinas: torcida única. O boletim mostra setor "visitante",
# mas não houve torcida visitante de verdade, então fica sem dado
derbi = (
    (tabela["mandante"].str.contains("Guarani") & tabela["visitante"].str.contains("Ponte Preta"))
    | (tabela["mandante"].str.contains("Ponte Preta") & tabela["visitante"].str.contains("Guarani"))
)
tabela.loc[derbi, "torcida_visitante"] = None

print(tabela)

# Salva a tabela jogo a jogo
tabela.to_excel("torcida_visitante_2026.xlsx", index=False)
print("Tabela salva!")

# ----------------------------------------------------------
# Etapa 3: Ranking de torcida visitante por time
# ----------------------------------------------------------
ranking = tabela.groupby("visitante")["torcida_visitante"].agg(
    jogos="count",   # jogos com dado (os "sem dado" não contam)
    media="mean",    # média de torcedores por jogo fora
    total="sum",     # total de torcedores que viajaram
).round().sort_values("media", ascending=False)

print("\nRanking de torcida visitante (Paulistão 2026):")
print(ranking)

# Sem index=False: o nome dos times está no índice e vira a primeira coluna
ranking.to_excel("ranking_visitantes_2026.xlsx")
print("Ranking salvo!")