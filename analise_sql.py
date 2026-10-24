
import sqlite3
import pandas as pd
from qualidade_dados import validar_dados

# Carregar os dados coletados
df = validar_dados(pd.read_csv("dados/acesso_internet.csv"))

# Criar o banco e executar a análise
with sqlite3.connect("datascope.db") as conexao:
    df.to_sql(
        "acesso_internet",
        conexao,
        if_exists="replace",
        index=False
    )

    consulta = """
    WITH ano_comum AS (
        SELECT "Ano"
        FROM acesso_internet
        GROUP BY "Ano"
        HAVING COUNT(DISTINCT "País") = 3
        ORDER BY "Ano" DESC
        LIMIT 1
    )
    SELECT
        a."País",
        a."Ano",
        ROUND(a."Acesso à Internet (%)", 2)
            AS "Acesso (%)"
    FROM acesso_internet AS a
    JOIN ano_comum AS c
        ON a."Ano" = c."Ano"
    ORDER BY a."Acesso à Internet (%)" DESC;
    """

    resultado = pd.read_sql_query(consulta, conexao)

print("\nRanking no ano mais recente em comum:")
print(resultado.to_string(index=False))
print("\nConsulta SQL executada com sucesso!")

