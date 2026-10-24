import sqlite3
import tempfile
import unittest
from pathlib import Path
from pipeline import carregar_registros, criar_tabela, ranking_mais_recente, validar_registros


def row(pais="Brasil", ano=2024, valor=80):
    return {"País": pais, "Ano": ano, "Acesso à Internet (%)": valor}


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)

    def test_snapshot_real_possui_ranking(self):
        dados = carregar_registros()
        criar_tabela(self.db, dados)
        ranking = ranking_mais_recente(self.db)
        self.assertEqual(len(ranking), 3)
        self.assertEqual(len({r[1] for r in ranking}), 1)

    def test_ano_comum_nao_e_ultimo_ano_isolado(self):
        criar_tabela(self.db, [row(), row("Chile", 2024, 90), row("Brasil", 2025, 95)])
        self.assertEqual(ranking_mais_recente(self.db), [("Chile", 2024, 90.0), ("Brasil", 2024, 80.0)])

    def test_funciona_com_quatro_paises(self):
        criar_tabela(self.db, [row(p) for p in ["A", "B", "C", "D"]])
        self.assertEqual(len(ranking_mais_recente(self.db)), 4)

    def test_selecao_um_pais_e_repeticao(self):
        criar_tabela(self.db, [row(), row("Brasil", 2025, 95), row("Chile", 2024, 90)])
        self.assertEqual(ranking_mais_recente(self.db, ["Brasil", "Brasil"]), [("Brasil", 2025, 95.0)])

    def test_sem_ano_comum_ou_selecao_vazia(self):
        criar_tabela(self.db, [row(), row("Chile", 2023)])
        self.assertEqual(ranking_mais_recente(self.db), [])
        self.assertEqual(ranking_mais_recente(self.db, []), [])
        self.assertEqual(ranking_mais_recente(self.db, ["Inexistente"]), [])

    def test_nome_com_aspas_e_parametrizado(self):
        nome = "D'Água"
        criar_tabela(self.db, [row(nome)])
        self.assertEqual(ranking_mais_recente(self.db, [nome])[0][0], nome)

    def test_rejeita_dados_invalidos(self):
        for dados in [[], [row(valor=-1)], [row(valor=101)], [row(valor=float("nan"))],
                      [row(valor=float("inf"))], [row(ano=2024.5)], [row(pais=" ")],
                      [row(), row()], [{}]]:
            with self.subTest(dados=dados), self.assertRaises(ValueError):
                validar_registros(dados)

    def test_validacao_preserva_base_anterior(self):
        criar_tabela(self.db, [row()])
        with self.assertRaises(ValueError):
            criar_tabela(self.db, [row(valor=200)])
        self.assertEqual(ranking_mais_recente(self.db), [("Brasil", 2024, 80.0)])

    def test_csv_bom_e_caminho_explicito(self):
        with tempfile.TemporaryDirectory() as pasta:
            csv = Path(pasta) / "base.csv"
            csv.write_text("País,Ano,Acesso à Internet (%)\nBrasil,2024,80\n", encoding="utf-8-sig")
            self.assertEqual(carregar_registros(csv), [row()])


if __name__ == "__main__":
    unittest.main()
