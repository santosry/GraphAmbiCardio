# Benchmark: pipeline e consultas

Gerado: 2026-11-01T19:01:00Z

- Python: 3.12.13
- Plataforma: Windows-11-10.0.26340-SP0
- RSS: 158.2 → 192.0 MB (Δ 33.9 MB)
- Pico tracemalloc: 15.87 MB

| Operação | Tempo (s) | Resultado |
|---|---:|---|
| read_nodes | 0.0178 | 2238 |
| read_relations | 0.0421 | 4146 |
| read_evidence | 0.0402 | 4659 |
| load_layers | 0.0 | [2238, 4146] |
| build_digraph | 0.001 | [2217, 4131] |
| conceptual_paths | 0.0 | 60 |
| centrality_table | 2.0944 | 1277 |
| 1000_node_lookups | 0.0002 | 1000 |

Tempos descritivos para esta máquina; não são garantia de desempenho.