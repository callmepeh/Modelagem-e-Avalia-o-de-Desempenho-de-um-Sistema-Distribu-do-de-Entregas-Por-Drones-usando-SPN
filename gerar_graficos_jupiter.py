#!/usr/bin/env python3
"""Regenera as Figuras 3–6 do artigo com métricas exportadas pelo Jupiter.

Execute na raiz do projeto: python3 gerar_graficos_jupiter.py
Saídas: figs/fig_E1..fig_E4 em PDF e PNG, além de figs/dados_figuras.csv.
Os pontos Jupiter são lidos dos CSVs classificados em dados/; a curva CTMC
da Figura 3 vem da validação cruzada documentada em dados/validacao_cruzada_ctmc.csv.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figs"

COLORS = {"blue": "#2456a6", "red": "#bd1830", "lightblue": "#9ecae1"}


def article_number(value, decimals):
    """Format using the truncation displayed in the article's figure labels."""
    scale = 10 ** decimals
    value = int(float(value) * scale) / scale
    return f"{value:.{decimals}f}".replace(".", ",")


def decimal_comma(value, _position):
    return f"{value:g}".replace(".", ",")


def read_metrics(relative_path):
    path = ROOT / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"CSV do experimento não encontrado: {path}")
    df = pd.read_csv(path, sep=";")
    df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]
    if not {"Metric", "Value"}.issubset(df.columns):
        raise ValueError(f"{path}: esperado CSV Jupiter com colunas Metric e Value")
    return {str(row.Metric).strip(): float(row.Value) for row in df.itertuples()}


def collect():
    manifest_path = ROOT / "dados/manifesto_experimentos.csv"
    manifest = pd.read_csv(manifest_path).fillna("")
    required = {"experimento", "lambda_ped_min", "drones_C", "capacidade_N", "arquivo_organizado"}
    if not required.issubset(manifest.columns):
        raise ValueError(f"{manifest_path}: faltam colunas {sorted(required - set(manifest.columns))}")
    rows = []
    for record in manifest.to_dict("records"):
        filename = str(record["arquivo_organizado"]).strip()
        if not filename:
            continue
        metrics = read_metrics(filename)
        for experiment in str(record["experimento"]).split("/"):
            experiment = experiment.strip()
            needed = {"MRT_min", "MPT_min", "MQT_min", "TP_pedidos_por_min",
                      "Utilizacao_frota_pct", "Probabilidade_bloqueio_pct"}
            missing = needed - metrics.keys()
            if missing:
                raise ValueError(f"{filename}: métricas ausentes: {', '.join(sorted(missing))}")
            rows.append({
                "experimento": experiment, "cenario": record.get("cenario", ""),
                "arquivo": filename,
                "lambda_ped_min": float(record["lambda_ped_min"]),
                "drones_C": int(record["drones_C"]),
                "capacidade_N": int(record["capacidade_N"]),
                "MPT_min": metrics["MPT_min"], "MQT_min": metrics["MQT_min"],
                "MRT_min": metrics["MRT_min"],
                "TP_ped_min": metrics["TP_pedidos_por_min"],
                "U_pct": metrics["Utilizacao_frota_pct"],
                "DP_pct": metrics["Probabilidade_bloqueio_pct"],
            })
    data = pd.DataFrame(rows)
    expected = {"E1": 5, "E2": 3, "E3": 3, "E4": 3}
    counts = data.groupby("experimento").size().to_dict()
    if counts != expected:
        raise ValueError(f"O manifesto deve definir {expected}; encontrei {counts}")
    return data


def article_style():
    plt.rcParams.update({
        "font.family": "serif", "font.size": 8,
        "axes.labelsize": 8, "axes.titlesize": 8,
        "legend.fontsize": 7, "xtick.labelsize": 7, "ytick.labelsize": 7,
        "axes.linewidth": 0.8, "pdf.fonttype": 42, "ps.fonttype": 42,
    })


def finish(fig, name):
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_e1(data):
    d = data.query("experimento == 'E1'").sort_values("lambda_ped_min")
    ctmc = pd.read_csv(ROOT / "dados/validacao_cruzada_ctmc.csv")
    ctmc.columns = [str(c).strip() for c in ctmc.columns]
    ctmc = ctmc[ctmc["C"].astype(int).eq(4) & ctmc["N"].astype(int).eq(15)].sort_values("lambda")
    fig, ax = plt.subplots(figsize=(3.48, 2.28))
    right = ax.twinx()
    ax.plot(ctmc["lambda"], ctmc["MRT_CTMC_min"], "--", color=COLORS["blue"], lw=1.3, label="MRT (CTMC)")
    right.plot(ctmc["lambda"], 100 * ctmc["lambda"] * 22 / 4,
               "--", color=COLORS["red"], lw=1.3, label="U (CTMC)")
    ax.scatter(d.lambda_ped_min, d.MRT_min, s=25, color=COLORS["blue"], label="MRT (Jupiter)", zorder=3)
    right.scatter(d.lambda_ped_min, d.U_pct, s=25, marker="s", color=COLORS["red"], label="U (Jupiter)", zorder=3)
    ax.axhline(32.6, color="gray", lw=0.9, ls="-.")
    ax.text(0.031, 33.2, r"limite $U=70\%$", color="gray", fontsize=6.5)
    ax.set(xlabel=r"Taxa de chegada $\lambda$ (pedidos/min)", ylabel="MRT (min)", xlim=(0.025, 0.158), ylim=(20, 38))
    ax.xaxis.set_major_formatter(FuncFormatter(decimal_comma))
    right.set_ylabel(r"Utilização $U$ (%)", color=COLORS["red"])
    right.set_ylim(0, 100)
    ax.tick_params(axis="y", colors=COLORS["blue"])
    right.tick_params(axis="y", colors=COLORS["red"])
    ax.grid(True, ls=":", lw=0.5, alpha=0.7)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = right.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", ncol=2, framealpha=0.95)
    finish(fig, "fig_E1")


def plot_e2(data):
    d = data.query("experimento == 'E2'").sort_values("drones_C")
    fig, ax = plt.subplots(figsize=(3.48, 2.28)); right = ax.twinx()
    x = range(len(d))
    bars = ax.bar(x, d.U_pct, width=0.48, color=COLORS["lightblue"], edgecolor="black", linewidth=0.5, label=r"$U$ (%)")
    mrt = right.plot(x, d.MRT_min, "o-", color=COLORS["red"], lw=1.2, ms=3.5, label="MRT (min)")[0]
    for b, value in zip(bars, d.U_pct): ax.text(b.get_x()+b.get_width()/2, value+1, f"{article_number(value, 1)}%", ha="center", fontsize=6.5)
    for xx, value in zip(x, d.MRT_min): right.annotate(f"{value:.1f}".replace(".", ","), (xx, value), xytext=(12, 4), textcoords="offset points", color=COLORS["red"], fontsize=6.5)
    ax.set_xticks(list(x), [r"$C=2$", r"$C=4$ (ref.)", r"$C=6$"])
    ax.set(xlabel="Tamanho da frota C (drones)", ylabel=r"Utilização $U$ (%)", ylim=(0, 110))
    right.set_ylabel("MRT (min)", color=COLORS["red"]); right.set_ylim(0, 160); right.tick_params(axis="y", colors=COLORS["red"])
    ax.grid(axis="y", ls=":", lw=0.5); ax.set_axisbelow(True)
    ax.legend([bars, mrt], [r"$U$ (%)", "MRT (min)"], loc="upper right", framealpha=0.95)
    finish(fig, "fig_E2")


def plot_e3(data):
    d = data.query("experimento == 'E3'").sort_values("capacidade_N")
    fig, ax = plt.subplots(figsize=(3.48, 2.28)); right = ax.twinx(); x = range(len(d))
    bars = ax.bar(x, d.DP_pct, width=0.48, color="#f4a582", edgecolor="black", hatch="//", linewidth=0.5, label="DP (%)")
    mrt = right.plot(x, d.MRT_min, "o-", color=COLORS["blue"], lw=1.2, ms=3.5, label="MRT (min)")[0]
    for b, value in zip(bars, d.DP_pct):
        label = f"{article_number(value, 2)}%"
        ax.text(b.get_x()+b.get_width()/2, max(value, 0)+0.25, label, ha="center", fontsize=6.5)
    for xx, value in zip(x, d.MRT_min): right.annotate(article_number(value, 2), (xx, value), xytext=(5, 4), textcoords="offset points", color=COLORS["blue"], fontsize=6.5)
    ax.set_xticks(list(x), [r"$N=5$", r"$N=15$ (ref.)", r"$N=30$"])
    ax.set(xlabel="Capacidade do sistema N (slots)", ylabel="Prob. de descarte DP (%)", ylim=(0, 12))
    right.set_ylabel("MRT (min)", color=COLORS["blue"]); right.set_ylim(20, 32); right.tick_params(axis="y", colors=COLORS["blue"])
    ax.grid(axis="y", ls=":", lw=0.5); ax.set_axisbelow(True)
    ax.legend([bars, mrt], ["DP (%)", "MRT (min)"], loc="upper right", framealpha=0.95)
    finish(fig, "fig_E3")


def plot_e4(data):
    d = data.query("experimento == 'E4'").copy()
    d["order"] = d["drones_C"].map({2: 0, 4: 1, 6: 2}); d = d.sort_values("order")
    fig, ax = plt.subplots(figsize=(3.48, 2.28)); right = ax.twinx(); centers = range(len(d)); width = 0.34
    offered = ax.bar([x-width/2 for x in centers], d.lambda_ped_min, width, color="white", edgecolor="black", hatch="..", linewidth=0.6, label=r"$\lambda$ oferecida")
    throughput = ax.bar([x+width/2 for x in centers], d.TP_ped_min, width, color="#bcbddc", edgecolor="black", linewidth=0.5, label="TP (Jupiter)")
    mrt = right.plot(centers, d.MRT_min, "D-", color=COLORS["red"], lw=1.2, ms=3.5, label="MRT (min)")[0]
    for x, value in zip(centers, d.MRT_min): right.annotate(article_number(value, 2), (x, value), xytext=(0, 5), ha="center", textcoords="offset points", color=COLORS["red"], fontsize=6.5)
    ax.set_xticks(list(centers), ["Baixo\n("+r"$\lambda$"+"=0,06; C=2)", "Ref.\n(0,12; 4)", "Pico\n(0,15; 6)"])
    ax.set(xlabel="Cenário combinado (demanda × frota)", ylabel="Vazão (pedidos/min)", ylim=(0, 0.22))
    ax.yaxis.set_major_formatter(FuncFormatter(decimal_comma))
    ax.yaxis.set_major_locator(MultipleLocator(0.05))
    right.set_ylabel("MRT (min)", color=COLORS["red"]); right.set_ylim(15, 45); right.tick_params(axis="y", colors=COLORS["red"])
    ax.grid(axis="y", ls=":", lw=0.5); ax.set_axisbelow(True)
    ax.legend([offered, throughput, mrt], [r"$\lambda$ oferecida", "TP (Jupiter)", "MRT (min)"], loc="upper left", ncol=3, framealpha=0.95)
    finish(fig, "fig_E4")


def main():
    OUT.mkdir(exist_ok=True)
    article_style()
    data = collect()
    data.to_csv(OUT / "dados_figuras.csv", index=False)
    plot_e1(data); plot_e2(data); plot_e3(data); plot_e4(data)
    print(f"Figuras do artigo e dados-fonte gerados em {OUT}")


if __name__ == "__main__":
    main()
