"""Build the local SQLite snapshot and display the latest comparable ranking."""
import sqlite3
from pipeline import ROOT, carregar_registros, criar_tabela, ranking_mais_recente


def main():
    registros = carregar_registros()
    with sqlite3.connect(ROOT / "datascope.db") as conexao:
        criar_tabela(conexao, registros)
        ranking = ranking_mais_recente(conexao)
    if not ranking:
        raise ValueError("Não há ano comum para todos os países")
    print("Ranking no ano mais recente em comum:")
    for pais, ano, acesso in ranking:
        print(f"{pais}: {acesso:.2f}% ({ano})")


if __name__ == "__main__":
    main()
