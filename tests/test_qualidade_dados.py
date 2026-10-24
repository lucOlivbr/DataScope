import sqlite3
import unittest
from pathlib import Path

import pandas as pd

from qualidade_dados import COLUNAS, validar_dados


class QualidadeDadosTests(unittest.TestCase):
    def base(self):
        return pd.DataFrame([["Brasil", "2024", "84.46"], ["Chile", 2023, 94.5]], columns=COLUNAS)

    def test_normaliza_tipos_e_ordena_sem_mutar_origem(self):
        origem = self.base()
        copia = origem.copy(deep=True)
        dados = validar_dados(origem)
        self.assertEqual(dados["Ano"].tolist(), [2023, 2024])
        self.assertEqual(dados.iloc[1][COLUNAS[2]], 84.46)
        pd.testing.assert_frame_equal(origem, copia)

    def test_rejeita_colunas_ausentes(self):
        with self.assertRaisesRegex(ValueError, "Colunas"):
            validar_dados(self.base().drop(columns="Ano"))

    def test_rejeita_base_vazia(self):
        with self.assertRaisesRegex(ValueError, "Nenhum dado"):
            validar_dados(pd.DataFrame(columns=COLUNAS))

    def test_rejeita_duplicatas_apos_normalizar_ano(self):
        dados = pd.DataFrame([["Brasil", "2024", 84], ["Brasil", 2024, 85]], columns=COLUNAS)
        with self.assertRaisesRegex(ValueError, "duplicadas"):
            validar_dados(dados)

    def test_rejeita_percentuais_invalidos(self):
        for valor in (-0.01, 100.01, float("inf"), float("-inf"), "abc", None):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                dados = self.base()
                dados.loc[0, COLUNAS[2]] = valor
                validar_dados(dados)

    def test_rejeita_anos_invalidos(self):
        for ano in (1999, 2025, 2023.5, "inválido", float("inf")):
            with self.subTest(ano=ano), self.assertRaisesRegex(ValueError, "Ano inválido"):
                dados = self.base()
                dados.loc[0, "Ano"] = ano
                validar_dados(dados)

    def test_rejeita_pais_desconhecido(self):
        dados = self.base()
        dados.loc[0, "País"] = "Desconhecido"
        with self.assertRaisesRegex(ValueError, "País fora"):
            validar_dados(dados)

    def test_limites_zero_e_cem_sao_validos(self):
        dados = self.base()
        dados[COLUNAS[2]] = [0, 100]
        self.assertEqual(set(validar_dados(dados)[COLUNAS[2]]), {0, 100})

    def test_csv_versionado_preserva_dados_no_sqlite(self):
        csv = Path(__file__).resolve().parents[1] / "dados" / "acesso_internet.csv"
        dados = validar_dados(pd.read_csv(csv))
        with sqlite3.connect(":memory:") as conexao:
            dados.to_sql("acesso_internet", conexao, index=False)
            recuperados = pd.read_sql_query('SELECT * FROM acesso_internet ORDER BY "Ano", "País"', conexao)
        pd.testing.assert_frame_equal(dados, recuperados)
        self.assertEqual(set(dados["País"]), {"Brasil", "Argentina", "Chile"})


if __name__ == "__main__":
    unittest.main()

