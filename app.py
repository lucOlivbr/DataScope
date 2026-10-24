
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
from qualidade_dados import validar_dados

# --------------------------------------------------
# CONFIGURAÇÃO
# --------------------------------------------------

st.set_page_config(
    page_title="DataScope | Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp {
        background: #0B1020;
        color: #E8ECF8;
    }

    [data-testid="stSidebar"] {
        background: #11182B;
        border-right: 1px solid #29344C;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    h1, h2, h3 {
        color: #F0F3FF !important;
        letter-spacing: -0.5px;
    }

    div[data-testid="stMetric"] {
        background: #151E33;
        border: 1px solid #2B3853;
        border-radius: 16px;
        padding: 20px;
    }

    div[data-testid="stMetricLabel"] {
        color: #9BA9C4;
    }

    div[data-testid="stMetricValue"] {
        color: #F0F3FF;
    }

    .hero {
        padding: 24px 28px;
        border-radius: 18px;
        background: linear-gradient(
            115deg, #172341, #221B49
        );
        border: 1px solid #344064;
        margin-bottom: 26px;
    }

    .hero-label {
        color: #A5B4FC;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
    }

    .hero-title {
        font-size: clamp(30px, 4vw, 46px);
        font-weight: 800;
        margin: 8px 0;
        color: #FFFFFF;
    }

    .hero-subtitle {
        color: #B9C5DD;
        font-size: 15px;
    }

    .insight {
        background: #14273A;
        border-left: 4px solid #38BDF8;
        padding: 20px;
        border-radius: 12px;
        margin: 16px 0;
        line-height: 1.7;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# CARREGAR DADOS DO SQLITE
# --------------------------------------------------


@st.cache_data
def carregar_dados():
    pasta = Path(__file__).parent
    banco = pasta / "datascope.db"
    csv = pasta / "dados" / "acesso_internet.csv"

    if banco.exists():
        with sqlite3.connect(banco) as conexao:
            dados = pd.read_sql_query(
                "SELECT * FROM acesso_internet",
                conexao
            )
    else:
        # Na nuvem, recria a tabela SQL a partir do CSV
        origem = pd.read_csv(csv)

        with sqlite3.connect(":memory:") as conexao:
            origem.to_sql(
                "acesso_internet",
                conexao,
                if_exists="replace",
                index=False
            )
            dados = pd.read_sql_query(
                "SELECT * FROM acesso_internet",
                conexao
            )

    return validar_dados(dados)


try:
    df = carregar_dados()
except (sqlite3.Error, FileNotFoundError, ValueError) as erro:
    st.error(f"Não foi possível carregar os dados: {erro}")
    st.info("Execute primeiro: python analise_sql.py")
    st.stop()

if df.empty:
    st.error("O banco de dados está vazio.")
    st.stop()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("◈ DataScope")
    st.caption("Analytics Platform · v2.0")

    st.divider()

    st.subheader("Filtros")

    paises = sorted(df["País"].unique().tolist())

    selecionados = st.multiselect(
        "Países para comparar",
        options=paises,
        default=paises
    )

    if not selecionados:
        st.warning("Selecione pelo menos um país.")
        st.stop()

    filtrado = df[
        df["País"].isin(selecionados)
    ].copy()

    contagem = (
        filtrado.groupby("Ano")["País"]
        .nunique()
    )

    anos_comuns = sorted(
        contagem[
            contagem == len(selecionados)
        ].index.tolist()
    )

    if not anos_comuns:
        st.error("Não existem anos comuns para a seleção.")
        st.stop()

    ano = st.selectbox(
        "Ano de referência",
        options=anos_comuns,
        index=len(anos_comuns) - 1
    )

    st.divider()

    st.caption("FONTE DOS DADOS")
    st.write("Banco Mundial")
    st.code("IT.NET.USER.ZS", language=None)
    st.caption(
        "Indivíduos que usam a internet "
        "(% da população)"
    )


# --------------------------------------------------
# CABEÇALHO
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <div class="hero-label">
        DATA INTELLIGENCE / LATIN AMERICA
    </div>
    <div class="hero-title">
        DataScope Analytics
    </div>
    <div class="hero-subtitle">
        Explorando a evolução do acesso à internet
        com dados reais, Python e SQL.
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# INDICADORES
# --------------------------------------------------

atual = (
    filtrado[filtrado["Ano"] == ano]
    .sort_values(
        "Acesso à Internet (%)",
        ascending=False
    )
)

lider = atual.iloc[0]
valor_lider = float(lider["Acesso à Internet (%)"])

brasil = df[
    (df["País"] == "Brasil") &
    (df["Ano"] == ano)
]

valor_brasil = (
    float(brasil.iloc[0]["Acesso à Internet (%)"])
    if not brasil.empty else None
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🏆 Líder da seleção",
        str(lider["País"]),
        f"{valor_lider:.2f}% da população",
        delta_color="off"
    )

with col2:
    st.metric(
        "🇧🇷 Brasil (referência)",
        (
            f"{valor_brasil:.2f}%"
            if valor_brasil is not None else "Sem dados"
        )
    )

with col3:
    if valor_brasil is not None:
        diferenca = valor_lider - valor_brasil
        st.metric(
            "📊 Diferença líder × Brasil",
            f"{diferenca:+.2f} p.p."
        )
    else:
        st.metric(
            "📊 Diferença líder × Brasil",
            "N/D"
        )

st.caption(
    f"Indicadores para {ano}. "
    "Líder calculado entre os países selecionados; "
    "Brasil exibido como referência."
)

st.divider()


# --------------------------------------------------
# EVOLUÇÃO HISTÓRICA
# --------------------------------------------------

st.subheader("📈 Evolução histórica")

st.caption(
    "Percentual da população que utiliza a internet "
    "ao longo do tempo."
)

grafico = filtrado.pivot_table(
    index="Ano",
    columns="País",
    values="Acesso à Internet (%)",
    aggfunc="mean"
).sort_index()

st.line_chart(
    grafico,
    height=350,
    y_label="População (%)",
    x_label="Ano",
    use_container_width=True
)


# --------------------------------------------------
# RANKING E TABELA
# --------------------------------------------------

st.divider()
st.subheader(f"🌎 Comparação entre países · {ano}")

esquerda, direita = st.columns([1.4, 1])

with esquerda:
    barras = atual.set_index("País")[
        "Acesso à Internet (%)"
    ]

    st.bar_chart(
        barras,
        horizontal=True,
        height=300,
        x_label="População (%)"
    )

with direita:
    tabela = atual[
        ["País", "Acesso à Internet (%)"]
    ].copy()

    tabela["Acesso à Internet (%)"] = (
        tabela["Acesso à Internet (%)"].round(2)
    )

    st.dataframe(
        tabela,
        hide_index=True,
        use_container_width=True
    )


# --------------------------------------------------
# INSIGHT AUTOMÁTICO
# --------------------------------------------------

st.divider()
st.subheader("💡 Insight dos dados")

nome_lider = str(lider["País"])

if valor_brasil is None:
    mensagem = (
        f"Em {ano}, {nome_lider} apresentou o maior "
        f"percentual da seleção: {valor_lider:.2f}%. "
        "Não há dado disponível para o Brasil nesse ano."
    )
else:
    diferenca = valor_lider - valor_brasil

    if abs(diferenca) < 0.01:
        mensagem = (
            f"Em {ano}, o Brasil liderou ou empatou "
            f"na seleção, com {valor_brasil:.2f}% "
            "da população utilizando a internet."
        )
    elif diferenca > 0:
        mensagem = (
            f"Em {ano}, {nome_lider} liderou os países "
            f"selecionados com {valor_lider:.2f}%. "
            f"O Brasil registrou {valor_brasil:.2f}%, "
            f"uma diferença de {diferenca:.2f} "
            "pontos percentuais."
        )
    else:
        mensagem = (
            f"Em {ano}, o Brasil apresentou "
            f"{valor_brasil:.2f}%, superando o líder "
            f"da seleção em {abs(diferenca):.2f} "
            "pontos percentuais."
        )

st.markdown(
    f'<div class="insight">{mensagem}</div>',
    unsafe_allow_html=True
)

st.caption(
    "Insight descritivo gerado automaticamente "
    "a partir dos valores observados. "
    "Não representa previsão nem relação causal."
)


# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------

st.divider()

st.download_button(
    "⬇️ Exportar dados filtrados (CSV)",
    data=filtrado.to_csv(
        index=False
    ).encode("utf-8-sig"),
    file_name="datascope_export.csv",
    mime="text/csv"
)

st.caption(
    "DataScope v2.0 · Python · Pandas · SQLite · Streamlit"
)

