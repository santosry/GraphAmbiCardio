"""Export the high-confidence core subgraph and a layer-specific edge list."""
import sys
from pathlib import Path

import networkx as nx
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from graphambicardio import config  # noqa: E402
from graphambicardio.graph import analysis  # noqa: E402
from graphambicardio.io_utils import get_logger  # noqa: E402


def main() -> None:
    log = get_logger("export_core")
    nodes, relations = analysis.load_layers()
    df = pd.DataFrame(relations)
    core = df[(df["layer"].isin(["observed", "inferred"])) & (df["confidence"].astype(float) >= 0.55)]
    core.to_csv(config.GRAPH_OUT / "core_edges.csv", index=False)
    G = analysis.build_digraph(core.to_dict("records"), nodes, allowed_layers={"observed", "inferred"}, min_confidence=0.55)
    nx.write_graphml(G, config.GRAPH_OUT / "core_graph.graphml")
    log.info("core subgraph: %s nodes, %s edges -> %s", G.number_of_nodes(), G.number_of_edges(), config.GRAPH_OUT / "core_graph.graphml")


if __name__ == "__main__":
    main()
