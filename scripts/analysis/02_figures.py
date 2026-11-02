"""Generate the main figures (matplotlib, non-interactive backend)."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from graphambicardio import config  # noqa: E402
from graphambicardio.graph import analysis  # noqa: E402

COLORS = {
    "Exposure": "#d95f02", "Mechanism": "#7570b3", "Process": "#1b9e77",
    "Phenotype": "#e7298a", "Gene": "#999999", "Pathway": "#66a61e",
    "Variant": "#cccccc", "Indicator": "#666666", "Population": "#666666",
}


def fig_network(nodes, relations):
    node_type = {n["node_id"]: n["type"] for n in nodes}
    G = analysis.build_digraph(relations, nodes, allowed_layers={"observed", "inferred"},
                               allowed_types=analysis.CONCEPTUAL_TYPES)
    plt.figure(figsize=(12, 9))
    pos = nx.spring_layout(G, seed=7, k=1.1 / (G.number_of_nodes() ** 0.5))
    for u, v, d in G.edges(data=True):
        plt.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color="#888888",
                 alpha=0.45, lw=0.6 + 3.5 * float(d["confidence"]), zorder=1)
    for n in G.nodes:
        t = node_type.get(n, "")
        size = 260 + 22 * G.degree(n)
        plt.scatter(*pos[n], s=size, color=COLORS.get(t, "#444"), edgecolor="white", linewidth=1.2, zorder=2)
    for n in G.nodes:
        label = n.split(":", 1)[1].replace("_", " ")
        plt.text(pos[n][0], pos[n][1] + 0.03, label, fontsize=7.5, ha="center", va="bottom", zorder=3)
    handles = [plt.Line2D([], [], marker="o", ls="", color=c, label=t) for t, c in COLORS.items() if t in set(node_type.values())]
    plt.legend(handles=handles, loc="lower left", frameon=False, fontsize=9)
    plt.title("GraphAmbiCardio: curated exposure -> mechanism -> process -> phenotype core\n(edge width = confidence; inferred layers excluded)", fontsize=11)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(config.FIGURES / "fig1_conceptual_core.png", dpi=300)
    plt.close()


def fig_phenotype_evidence(relations):
    rows = []
    for ph in [p["id"] for p in config.PHENOTYPES] + ["CHD:ALL"]:
        rows.append({
            "phenotype": ph.split(":")[1],
            "genes": sum(1 for r in relations if r["target_id"] == ph and r["relation"] == "GENE_ASSOCIATED_WITH_PHENOTYPE"),
            "exposures": sum(1 for r in relations if r["target_id"] == ph and r["relation"] == "EXPOSURE_ASSOCIATED_WITH_PHENOTYPE"),
            "processes": sum(1 for r in relations if r["target_id"] == ph and r["relation"] == "ALTERATION_ASSOCIATED_WITH_PHENOTYPE"),
        })
    df = pd.DataFrame(rows).sort_values("genes", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 6))
    y = range(len(df))
    ax.barh(y, df["genes"], color=COLORS["Gene"], label="genes (HPO/ClinVar/literature)")
    ax.barh(y, df["exposures"], color=COLORS["Exposure"], label="curated exposures")
    ax.barh(y, df["processes"], color=COLORS["Process"], label="developmental processes")
    ax.set_yticks(list(y)); ax.set_yticklabels(df["phenotype"])
    ax.set_xscale("symlog")
    ax.set_xlabel("number of edges (symlog scale)")
    ax.set_title("Evidence density per phenotype (counts are structural, not quality)")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    plt.tight_layout()
    plt.savefig(config.FIGURES / "fig2_phenotype_evidence.png", dpi=300)
    plt.close()


def fig_sensitivity():
    d = pd.read_csv(config.TABLES / "sensitivity_evidence_thresholds.csv")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(d["threshold"], d["n_exposure_phenotype_paths"], marker="o", label="exposure->phenotype paths")
    ax.plot(d["threshold"], d["n_direct_pairs"], marker="s", label="direct pairs")
    ax.plot(d["threshold"], d["n_edges_conceptual"], marker="^", label="conceptual edges")
    ax.set_xlabel("minimum edge confidence")
    ax.set_ylabel("count")
    ax.set_title("Sensitivity of the core graph to the evidence threshold")
    ax.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(config.FIGURES / "fig3_sensitivity_thresholds.png", dpi=300)
    plt.close()


def fig_local():
    d = pd.read_csv("data_processed/sinasc_campos_with_exposure.csv", low_memory=False)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    axes[0].boxplot([d.loc[~d["is_chd"], "win_temperature_2m_max_mean"].dropna(),
                     d.loc[d["is_chd"], "win_temperature_2m_max_mean"].dropna()],
                    tick_labels=["other births", "Q20–Q28"])
    axes[0].set_ylabel("mean Tmax in organogenesis window (C)")
    axes[0].set_title("Area-level heat exposure by Q20–Q28 status")
    ann = pd.read_csv(config.TABLES / "sinasc_annual.csv")
    axes[1].bar(ann["year"].astype(str), ann["chd_cases"], color=COLORS["Phenotype"])
    axes[1].set_ylabel("Q20–Q28 cases (SINASC)")
    axes[1].set_title("Reported Q20–Q28 cases, Campos dos Goytacazes")
    axes[1].tick_params(axis="x", rotation=90)
    plt.tight_layout()
    plt.savefig(config.FIGURES / "fig4_local_data.png", dpi=300)
    plt.close()


if __name__ == "__main__":
    nodes, relations = analysis.load_layers()
    fig_network(nodes, relations)
    fig_phenotype_evidence(relations)
    fig_sensitivity()
    fig_local()
    print("figures written to", config.FIGURES)
