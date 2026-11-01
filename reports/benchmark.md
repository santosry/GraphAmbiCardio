# Benchmark: pipeline e consultas

Gerado: 2026-11-01T18:20:09Z

- Python: 3.12.13
- Plataforma: Windows-11-10.0.26340-SP0
- RSS: 158.4 → 192.2 MB (Δ 33.8 MB)
- Pico tracemalloc: 15.82 MB

| Operação | Tempo (s) | Resultado |
|---|---:|---|
| read_nodes | 0.0115 | 2238 |
| read_relations | 0.0297 | 4135 |
| read_evidence | 0.0287 | 4639 |
| load_layers | 0.0 | [2238, 4135] |
| build_digraph | 0.001 | [2217, 4120] |
| conceptual_paths | 0.0 | 49 |
| centrality_table | 1.7512 | 1277 |
| 1000_node_lookups | 0.0001 | 1000 |

Tempos descritivos para esta máquina; não são garantia de desempenho.