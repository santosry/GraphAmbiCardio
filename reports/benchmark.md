# Benchmark — pipeline e consultas

Gerado: 2026-10-31T18:04:27Z

- Python: 3.12.13
- Plataforma: Windows-11-10.0.26340-SP0
- RSS: 158.3 → 192.1 MB (Δ 33.8 MB)
- Pico tracemalloc: 15.73 MB

| Operação | Tempo (s) | Resultado |
|---|---:|---|
| read_nodes | 0.0118 | 2238 |
| read_relations | 0.0348 | 4117 |
| read_evidence | 0.0299 | 4613 |
| load_layers | 0.0 | [2238, 4117] |
| build_digraph | 0.0037 | [2217, 4098] |
| conceptual_paths | 0.0 | 27 |
| centrality_table | 2.2109 | 1277 |
| 1000_node_lookups | 0.0002 | 1000 |

Tempos descritivos para esta máquina; não são garantia de desempenho.