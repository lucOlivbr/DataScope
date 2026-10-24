
import requests
import pandas as pd
import matplotlib.pyplot as plt
from qualidade_dados import validar_dados

# Dados do Banco Mundial:
# população que utiliza a internet (%)
url = (
    "https://api.worldbank.org/v2/country/"
    "BRA;ARG;CHL/indicator/IT.NET.USER.ZS"
)

print("Buscando dados reais do Banco Mundial...")

resposta = requests.get(
    url,
    params={
        "format": "json",
        "date": "2000:2024",
        "per_page": 1000
    },
    timeout=30
)
resposta.raise_for_status()

dados = resposta.json()[1]

paises = {
    "BRA": "Brasil",
    "ARG": "Argentina",
    "CHL": "Chile"
}

registros = []

for item in dados:
    if item["value"] is not None:
        registros.append({
            "País": paises[item["countryiso3code"]],
            "Ano": int(item["date"]),
            "Acesso à Internet (%)": item["value"]
        })

df = pd.DataFrame(registros)

if df.empty:
    raise RuntimeError("Nenhum dado disponível.")

df = validar_dados(df)
from pathlib import Path

Path("dados").mkdir(exist_ok=True)

df.to_csv(
    "dados/acesso_internet.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Base de dados CSV salva com sucesso!")

for pais, grupo in df.groupby("País"):
    plt.plot(
        grupo["Ano"],
        grupo["Acesso à Internet (%)"],
        label=pais
    )

plt.title("Evolução do acesso à internet")
plt.xlabel("Ano")
plt.ylabel("População conectada (%)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("grafico_internet.png", dpi=160)

print("Gráfico gerado com sucesso!")

