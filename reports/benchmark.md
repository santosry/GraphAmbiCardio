# Benchmark — pipeline e consultas

Gerado: 2026-10-31T17:39:34Z

- Python: 3.12.13
- Plataforma: Windows-11-10.0.26340-SP0
- RSS: 102.4 → 136.2 MB (Δ 33.8 MB)
- Pico tracemalloc: 15.65 MB

| Operação | Tempo (s) | Resultado |
|---|---:|---|
| read_nodes | 0.0171 | 2238 |
| read_relations | 0.0361 | 4117 |
| read_evidence | 0.0347 | 4613 |
| load_layers | 0.0 | [2238, 4117] |
| build_digraph | 0.0008 | [2217, 4098] |
| conceptual_paths | 0.0 | 27 |
| centrality_table | 2.6978 | 1277 |
| 1000_node_lookups | 0.0002 | 1000 |

Tempos descritivos para esta máquina; não são garantia de desempenho.