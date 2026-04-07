import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import streamlit as st
from pathlib import Path
from matplotlib.patches import Patch

# Configuração da página
st.set_page_config(
    page_title="State of Data Brazil 2024",
    page_icon="📊",
    layout="wide",
)

# Paleta
COR_PRINCIPAL = "#4F8EF7"
COR_DESTAQUE  = "#F7874F"
COR_AMARELO   = "#F7C44F"

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "#F8F9FA",
    "axes.grid":        True,
    "grid.color":       "#E0E0E0",
    "grid.linestyle":   "--",
    "font.family":      "sans-serif",
})

fmt_reais = mticker.FuncFormatter(lambda x, _: f"R${x:,.0f}")

# Carregamento e preparo dos dados
@st.cache_data
def carregar_dados():
    csv_path = Path(__file__).parent / "data" / "output" / "output_final.csv"
    df = pd.read_csv(csv_path)

    CARGO_LABELS = {
        "Analista de Dados/Data Analyst":                              "Analista de Dados",
        "Cientista de Dados/Data Scientist":                           "Cientista de Dados",
        "Engenheiro de Dados/Data Engineer/Data Architect":            "Engenheiro de Dados",
        "Analista de BI/BI Analyst":                                   "Analista de BI",
        "Analytics Engineer":                                          "Analytics Engineer",
        "Analista de Negócios/Business Analyst":                       "Business Analyst",
        "Engenheiro de Machine Learning/ML Engineer/AI Engineer":      "ML / AI Engineer",
        "Desenvolvedor/ Engenheiro de Software/ Analista de Sistemas": "Dev / Engenheiro de Software",
        "Outra Opção":                                                 "Outra Opção",
    }
    df["cargo_label"] = df["cargo"].map(CARGO_LABELS).fillna(df["cargo"])

    df_plot = df[
        (df["cargo"]      != "Não informado") &
        (df["regiao"]     != "Não informado") &
        (df["salario_mid"].notna())
    ].copy()

    return df, df_plot

df, df_plot = carregar_dados()

CARGOS_PRINCIPAIS = [
    "Analista de Dados", "Analista de BI", "Analytics Engineer",
    "Cientista de Dados", "Engenheiro de Dados",
]

FERRAMENTAS = {
    "SQL":      "usa_sql",
    "Python":   "usa_python",
    "Power BI": "usa_powerbi",
    "AWS":      "aws",
    "Azure":    "azure",
    "R":        "usa_r",
    "GCP":      "gcp",
    "Tableau":  "tableau",
}

# Cabeçalho
st.title("📊 State of Data Brazil 2024")
st.markdown(
    "Análise exploratória da pesquisa anual sobre o mercado de dados no Brasil. "
    "Fonte: [State of Data Brazil](https://stateofdata.com.br)"
)

col1, col2, col3 = st.columns(3)
col1.metric("Respondentes no Brasil", f"{len(df):,}")
col2.metric("Respondentes analisados", f"{len(df_plot):,}")
col3.metric("Cargos mapeados", df_plot["cargo_label"].nunique())

st.divider()

# Abas
aba_salario, aba_stack, aba_perfil, aba_experiencia = st.tabs([
    "💰 Salário", "🛠️ Stack", "👤 Perfil", "📈 Experiência"
])


# ABA 1 — SALÁRIO

with aba_salario:
    st.subheader("Análise Salarial")
    st.caption(
        "Salário médio calculado pelo ponto médio de cada faixa declarada. "
        "Faixa aberta superior (> R$40k) estimada em R$45k."
    )

    # Filtro de região
    regioes = sorted(df_plot["regiao"].unique())
    regiao_sel = st.multiselect(
        "Filtrar por região", regioes, default=regioes, key="regiao_sal"
    )
    df_sal = df_plot[df_plot["regiao"].isin(regiao_sel)] if regiao_sel else df_plot

    col_a, col_b = st.columns(2)

    # Salário por cargo
    with col_a:
        media_cargo = df_sal.groupby("cargo_label")["salario_mid"].mean().sort_values()
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(media_cargo.index, media_cargo.values, color=COR_PRINCIPAL)
        ax.set_title("Média Salarial por Cargo", fontweight="bold")
        ax.set_xlabel("Salário Médio (R$)")
        ax.xaxis.set_major_formatter(fmt_reais)
        for i, v in enumerate(media_cargo.values):
            ax.text(v + 150, i, f"R${v:,.0f}", va="center", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Salário por região
    with col_b:
        media_regiao = df_sal.groupby("regiao")["salario_mid"].mean().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(7, 5))
        bars = ax.bar(media_regiao.index, media_regiao.values, color=COR_PRINCIPAL)
        bars[0].set_color(COR_DESTAQUE)
        ax.set_title("Média Salarial por Região", fontweight="bold")
        ax.set_ylabel("Salário Médio (R$)")
        ax.yaxis.set_major_formatter(fmt_reais)
        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 150,
                f"R${bar.get_height():,.0f}",
                ha="center", fontsize=9,
            )
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.divider()

    col_c, col_d = st.columns(2)

    # Python faz diferença?
    with col_c:
        media_python = (
            df_sal.groupby("usa_python")["salario_mid"]
            .mean()
            .rename({0.0: "Não usa Python", 1.0: "Usa Python"})
        )
        fig, ax = plt.subplots(figsize=(5, 4))
        bars2 = ax.bar(
            media_python.index, media_python.values,
            color=[COR_DESTAQUE, COR_PRINCIPAL], width=0.4,
        )
        ax.set_title("Python faz diferença no salário?", fontweight="bold")
        ax.set_ylabel("Salário Médio (R$)")
        ax.yaxis.set_major_formatter(fmt_reais)
        for bar in bars2:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 150,
                f"R${bar.get_height():,.0f}",
                ha="center", fontsize=11, fontweight="bold",
            )
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Progressão por nível
    with col_d:
        df_nivel = df_sal[df_sal["nivel"].isin(["Júnior", "Pleno", "Sênior"])]
        media_nivel = df_nivel.groupby("nivel")["salario_mid"].mean().reindex(["Júnior", "Pleno", "Sênior"])
        fig, ax = plt.subplots(figsize=(5, 4))
        bars3 = ax.bar(media_nivel.index, media_nivel.values, color=COR_PRINCIPAL, width=0.5)
        bars3[2].set_color(COR_DESTAQUE)
        ax.set_title("Progressão Salarial por Nível", fontweight="bold")
        ax.set_ylabel("Salário Médio (R$)")
        ax.yaxis.set_major_formatter(fmt_reais)
        for bar in bars3:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 150,
                f"R${bar.get_height():,.0f}",
                ha="center", fontsize=11, fontweight="bold",
            )
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    if len(media_nivel.dropna()) == 3:
        mult = media_nivel["Sênior"] / media_nivel["Júnior"]
        st.info(f"📌 Sênior ganha em média **{mult:.1f}x** mais do que Júnior na seleção atual.")

    st.divider()

    # Boxplot salário por cargo e nível
    st.subheader("Distribuição salarial por cargo e nível")
    st.caption("Cada caixa mostra mediana, quartis e outliers dentro do cargo.")

    df_box = df_sal[
        df_sal["cargo_label"].isin(CARGOS_PRINCIPAIS) &
        df_sal["nivel"].isin(["Júnior", "Pleno", "Sênior"])
    ].copy()

    cores_nivel = {"Júnior": "#6BCB77", "Pleno": COR_PRINCIPAL, "Sênior": COR_DESTAQUE}
    fig, axes = plt.subplots(1, len(CARGOS_PRINCIPAIS), figsize=(18, 6), sharey=True)
    fig.suptitle("Distribuição Salarial por Cargo e Nível", fontsize=14, fontweight="bold")

    for ax, cargo in zip(axes, CARGOS_PRINCIPAIS):
        dados = [
            df_box[(df_box["cargo_label"] == cargo) & (df_box["nivel"] == nivel)]["salario_mid"].dropna()
            for nivel in ["Júnior", "Pleno", "Sênior"]
        ]
        bp = ax.boxplot(dados, patch_artist=True, widths=0.5,
                        medianprops=dict(color="black", linewidth=2))
        for patch, nivel in zip(bp["boxes"], ["Júnior", "Pleno", "Sênior"]):
            patch.set_facecolor(cores_nivel[nivel])
        ax.set_title(cargo, fontsize=9, fontweight="bold")
        ax.set_xticklabels(["Júnior", "Pleno", "Sênior"], fontsize=8)
        if ax == axes[0]:
            ax.set_ylabel("Salário (R$)")
            ax.yaxis.set_major_formatter(fmt_reais)

    legend_elements = [Patch(facecolor=cor, label=nivel) for nivel, cor in cores_nivel.items()]
    fig.legend(handles=legend_elements, loc="lower center", ncol=3, fontsize=10, frameon=False)
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    st.pyplot(fig)
    plt.close()


# ABA 2 — STACK

with aba_stack:
    st.subheader("Stack Tecnológica")

    col_a, col_b = st.columns([1, 2])

    # Ferramentas mais usadas
    with col_a:
        total = len(df_plot)
        uso = {nome: df_plot[col].sum() / total * 100 for nome, col in FERRAMENTAS.items()}
        uso_ord = dict(sorted(uso.items(), key=lambda x: x[1], reverse=True))

        fig, ax = plt.subplots(figsize=(6, 5))
        bars = ax.barh(list(uso_ord.keys()), list(uso_ord.values()), color=COR_PRINCIPAL)
        bars[0].set_color(COR_DESTAQUE)
        bars[1].set_color(COR_AMARELO)
        ax.set_title("Ferramentas Mais Usadas", fontsize=13, fontweight="bold")
        ax.set_xlabel("% de Profissionais")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
        ax.invert_yaxis()
        for i, (_, val) in enumerate(uso_ord.items()):
            ax.text(val + 0.5, i, f"{val:.1f}%", va="center", fontsize=10, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Stack por cargo
    with col_b:
        cargo_sel = st.multiselect(
            "Cargos exibidos", CARGOS_PRINCIPAIS, default=CARGOS_PRINCIPAIS, key="cargo_stack"
        )
        if cargo_sel:
            df_cargo = df_plot[df_plot["cargo_label"].isin(cargo_sel)].copy()
            matriz = pd.DataFrame({
                nome: df_cargo.groupby("cargo_label")[col].mean() * 100
                for nome, col in FERRAMENTAS.items()
            }).loc[[c for c in cargo_sel if c in df_cargo["cargo_label"].unique()]]

            x = np.arange(len(cargo_sel))
            n = len(FERRAMENTAS)
            largura = 0.10
            cores = [COR_PRINCIPAL, COR_DESTAQUE, COR_AMARELO,
                     "#6BCB77", "#845EC2", "#FF9671", "#00C9A7", "#C34B4B"]

            fig, ax = plt.subplots(figsize=(11, 5))
            for i, (nome, cor) in enumerate(zip(FERRAMENTAS.keys(), cores)):
                offset = (i - n / 2) * largura + largura / 2
                ax.bar(x + offset, matriz[nome], largura, label=nome, color=cor)

            ax.set_title("Uso de Ferramentas por Cargo (%)", fontsize=13, fontweight="bold")
            ax.set_ylabel("% de Uso")
            ax.set_xticks(x)
            ax.set_xticklabels(cargo_sel, rotation=10, ha="right")
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:.0f}%"))
            ax.legend(loc="upper right", fontsize=9, ncol=2)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        else:
            st.warning("Selecione ao menos um cargo.")


# ABA 3 — PERFIL

with aba_perfil:
    st.subheader("Perfil dos Profissionais de Dados")

    col_a, col_b = st.columns(2)

    with col_a:
        contagem_cargo = df_plot["cargo_label"].value_counts().sort_values()
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(contagem_cargo.index, contagem_cargo.values, color=COR_PRINCIPAL)
        ax.set_title("Distribuição de Cargos", fontweight="bold")
        ax.set_xlabel("Quantidade de Profissionais")
        for i, v in enumerate(contagem_cargo.values):
            ax.text(v + 5, i, str(v), va="center", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_b:
        df_form = df_plot[df_plot["formacao"] != "Não informado"]
        contagem_form = df_form["formacao"].value_counts().sort_values()
        cores_form = [
            COR_DESTAQUE if i == len(contagem_form) - 1 else COR_PRINCIPAL
            for i in range(len(contagem_form))
        ]
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(contagem_form.index, contagem_form.values, color=cores_form)
        ax.set_title("Formação Acadêmica", fontweight="bold")
        ax.set_xlabel("Quantidade de Profissionais")
        for i, v in enumerate(contagem_form.values):
            ax.text(v + 5, i, str(v), va="center", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.divider()
    st.subheader("Distribuição geográfica")

    contagem_regiao = df_plot["regiao"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(contagem_regiao.index, contagem_regiao.values, color=COR_PRINCIPAL)
    bars[0].set_color(COR_DESTAQUE)
    ax.set_title("Respondentes por Região", fontweight="bold")
    ax.set_ylabel("Quantidade")
    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 5,
            str(int(bar.get_height())),
            ha="center", fontsize=10,
        )
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()


# ABA 4 — EXPERIÊNCIA

with aba_experiencia:
    st.subheader("Salário por Tempo de Experiência")
    st.caption("Considera apenas respondentes com cargo e salário informados.")

    ORDEM_EXP = [
        "Menos de 1 ano",
        "de 1 a 2 anos",
        "de 3 a 4 anos",
        "de 5 a 6 anos",
        "de 7 a 10 anos",
        "Mais de 10 anos",
    ]

    # Filtro de cargo
    cargo_exp = st.multiselect(
        "Filtrar por cargo", CARGOS_PRINCIPAIS, default=CARGOS_PRINCIPAIS, key="cargo_exp"
    )
    df_exp_base = df_plot[df_plot["cargo_label"].isin(cargo_exp)] if cargo_exp else df_plot
    df_exp = df_exp_base[df_exp_base["exp_dados"].isin(ORDEM_EXP)]
    media_exp = df_exp.groupby("exp_dados")["salario_mid"].mean().reindex(ORDEM_EXP)

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(media_exp.index, media_exp.values, color=COR_PRINCIPAL, width=0.6)
    if len(bars):
        bars[-1].set_color(COR_DESTAQUE)
    ax.set_title("Salário Médio por Tempo de Experiência em Dados", fontsize=14, fontweight="bold")
    ax.set_ylabel("Salário Médio (R$)")
    ax.yaxis.set_major_formatter(fmt_reais)
    ax.set_xticklabels(ORDEM_EXP, rotation=15, ha="right")
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + 200,
                f"R${h:,.0f}",
                ha="center", fontsize=9, fontweight="bold",
            )
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.divider()
    st.subheader("Comparativo: Experiência em Dados vs. Experiência em TI")
    st.caption("Ambos os eixos mostram o salário médio para cada faixa de tempo.")

    ORDEM_TI = [
        "Menos de 1 ano",
        "de 1 a 2 anos",
        "de 3 a 4 anos",
        "de 5 a 6 anos",
        "de 7 a 10 anos",
        "Mais de 10 anos",
    ]

    df_ti = df_exp_base[df_exp_base["exp_ti"].isin(ORDEM_TI)]
    media_ti = df_ti.groupby("exp_ti")["salario_mid"].mean().reindex(ORDEM_TI)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    axes[0].bar(media_exp.index, media_exp.values, color=COR_PRINCIPAL, width=0.6)
    axes[0].set_title("Experiência em Dados", fontweight="bold")
    axes[0].set_ylabel("Salário Médio (R$)")
    axes[0].yaxis.set_major_formatter(fmt_reais)
    axes[0].set_xticklabels(ORDEM_EXP, rotation=20, ha="right")

    axes[1].bar(media_ti.index, media_ti.values, color=COR_DESTAQUE, width=0.6)
    axes[1].set_title("Experiência em TI", fontweight="bold")
    axes[1].set_xticklabels(ORDEM_TI, rotation=20, ha="right")

    plt.suptitle("Salário Médio: Experiência em Dados vs. TI", fontsize=13, fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ── Rodapé ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Projeto de portfólio · State of Data Brazil 2024 · "
    "Dados: [stateofdata.com.br](https://stateofdata.com.br)"
)
