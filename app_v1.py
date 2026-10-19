
import sqlite3

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="DataScope",
    page_icon="📊",
    layout="wide",
)

st.title("📊 DataScope")
st.caption("Análise de acesso à internet na América Latina")
st.write("Fonte: Banco Mundial — indicador IT.NET.USER.ZS")

# Consultar nosso banco SQLite
with sqlite3.connect("datascope.db") as conexao:
    df = pd.read_sql_query(
        'SELECT * FROM acesso_internet',
        conexao,
    )

paises = sorted(df["País"].unique())

selecionados = st.multiselect(
    "Selecione os países",
    options=paises,
    default=paises,
)

if not selecionados:
    st.warning("Selecione pelo menos um país.")
    st.stop()

filtrado = df[df["País"].isin(selecionados)].copy()

st.subheader("Evolução do acesso à internet")

grafico = filtrado.pivot(
    index="Ano",
    columns="País",
    values="Acesso à Internet (%)",
).sort_index()

st.line_chart(grafico, y_label="População (%)")

# Ano mais recente com dados de todos os países selecionados
anos = (
    filtrado.groupby("Ano")["País"]
    .nunique()
)
anos_completos = anos[
    anos == len(selecionados)
].index

if len(anos_completos) == 0:
    st.info("Não há um ano comum para comparar esses países.")
    st.stop()

ano = st.select_slider(
    "Ano da comparação",
    options=sorted(anos_completos.tolist()),
    value=int(max(anos_completos)),
)

ranking = (
    filtrado[filtrado["Ano"] == ano]
    .sort_values("Acesso à Internet (%)", ascending=False)
)

st.subheader(f"Ranking em {ano}")

st.dataframe(
    ranking[["País", "Acesso à Internet (%)"]],
    hide_index=True,
    use_container_width=True,
)

st.bar_chart(
    ranking.set_index("País")["Acesso à Internet (%)"],
    y_label="População (%)",
)

st.download_button(
    "📥 Baixar dados filtrados",
    data=filtrado.to_csv(index=False).encode("utf-8-sig"),
    file_name="datascope_dados.csv",
    mime="text/csv",
)
