"""Validated local dataset shared by the CLI and dashboard (no network on import)."""
import csv
import math
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "dados" / "acesso_internet.csv"
COLUMNS = ("País", "Ano", "Acesso à Internet (%)")


def validar_registros(registros):
    resultado, chaves = [], set()
    for linha, registro in enumerate(registros, 2):
        try:
            pais = registro["País"].strip()
            ano_num = float(registro["Ano"])
            ano = int(ano_num)
            valor = float(registro["Acesso à Internet (%)"])
            if not pais or ano != ano_num or not 1900 <= ano <= 2100:
                raise ValueError("país ou ano inválido")
            if not math.isfinite(valor) or not 0 <= valor <= 100:
                raise ValueError("percentual fora de 0 a 100")
            if (pais, ano) in chaves:
                raise ValueError("país/ano duplicado")
        except (KeyError, TypeError, ValueError, OverflowError, AttributeError) as erro:
            raise ValueError(f"Linha {linha}: {erro}") from erro
        chaves.add((pais, ano))
        resultado.append(dict(zip(COLUMNS, (pais, ano, valor))))
    if not resultado:
        raise ValueError("Base vazia")
    return sorted(resultado, key=lambda r: (r["Ano"], r["País"]))


def carregar_registros(csv_path=CSV_PATH):
    with Path(csv_path).open(encoding="utf-8-sig", newline="") as arquivo:
        return validar_registros(csv.DictReader(arquivo))


def criar_tabela(conexao, registros):
    # Validate everything before replacing the previous dataset.
    dados = validar_registros(registros)
    with conexao:
        conexao.execute('DROP TABLE IF EXISTS acesso_internet')
        conexao.execute('''CREATE TABLE acesso_internet (
            "País" TEXT NOT NULL, "Ano" INTEGER NOT NULL,
            "Acesso à Internet (%)" REAL NOT NULL CHECK ("Acesso à Internet (%)" BETWEEN 0 AND 100),
            PRIMARY KEY ("País", "Ano"))''')
        conexao.executemany('INSERT INTO acesso_internet VALUES (?, ?, ?)',
                            [tuple(r[c] for c in COLUMNS) for r in dados])


def ranking_mais_recente(conexao, paises=None):
    if paises is None:
        paises = [r[0] for r in conexao.execute('SELECT DISTINCT "País" FROM acesso_internet')]
    paises = list(dict.fromkeys(paises))
    if not paises:
        return []
    marcadores = ",".join("?" for _ in paises)
    # Parameters bind country names; only placeholder syntax is interpolated.
    consulta = f'''
        WITH ano_comum AS (
            SELECT "Ano" FROM acesso_internet
            WHERE "País" IN ({marcadores})
            GROUP BY "Ano" HAVING COUNT(DISTINCT "País") = ?
            ORDER BY "Ano" DESC LIMIT 1
        )
        SELECT "País", "Ano", ROUND("Acesso à Internet (%)", 2)
        FROM acesso_internet
        WHERE "Ano" = (SELECT "Ano" FROM ano_comum)
          AND "País" IN ({marcadores})
        ORDER BY "Acesso à Internet (%)" DESC, "País"
    '''
    return conexao.execute(consulta, [*paises, len(paises), *paises]).fetchall()
