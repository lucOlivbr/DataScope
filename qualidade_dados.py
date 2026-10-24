"""Contrato dos dados usados pelo ETL e pelo dashboard do DataScope."""

import pandas as pd

COLUNAS = ["País", "Ano", "Acesso à Internet (%)"]
PAISES = {"Brasil", "Argentina", "Chile"}


def validar_dados(origem: pd.DataFrame) -> pd.DataFrame:
    """Valida sem descartar erros silenciosamente; devolve uma cópia ordenada.

    O contrato acompanha o escopo atual da coleta: três países, 2000–2024,
    percentual entre 0 e 100 e uma observação por país/ano. Ausência de um
    país/ano é permitida, pois a fonte pode não publicar todas as observações.
    """
    faltantes = set(COLUNAS) - set(origem.columns)
    if faltantes:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(sorted(faltantes))}")
    if origem.empty:
        raise ValueError("Nenhum dado disponível.")
    dados = origem[COLUNAS].copy()
    if dados.isna().any().any():
        raise ValueError("Há valores ausentes em colunas obrigatórias.")
    if not dados["País"].isin(PAISES).all():
        raise ValueError("País fora do escopo da coleta.")

    anos = pd.to_numeric(dados["Ano"], errors="coerce")
    if not (anos.between(2000, 2024) & anos.mod(1).eq(0)).all():
        raise ValueError("Ano inválido: esperado inteiro entre 2000 e 2024.")
    valores = pd.to_numeric(dados["Acesso à Internet (%)"], errors="coerce")
    if not valores.between(0, 100).all():
        raise ValueError("Percentual inválido: esperado número finito entre 0 e 100.")
    dados["Ano"] = anos.astype(int)
    dados["Acesso à Internet (%)"] = valores.astype(float)
    if dados.duplicated(["País", "Ano"]).any():
        raise ValueError("Observações duplicadas para o mesmo país e ano.")
    return dados.sort_values(["Ano", "País"]).reset_index(drop=True)

