"""Compliance and hygiene checks for the GraphAmbiCardio repository.

Checks cover naming, forbidden legacy names, credentials, licensing, FAIR
metadata checksums, the non-systematic-review label, and data availability.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports" / "compliance_report.md"
JSON_OUT = ROOT / "reports" / "compliance_report.json"

TEXT_EXT = {".md", ".r", ".py", ".json", ".csv", ".cff", ".toml", ".yml", ".yaml", ".sh", ".css", ".html", ".txt"}
SKIP = {"data_raw", ".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", "rsconnect", "literature", "logs"}

FORBIDDEN = [
    "CEKP", "CardioEnvironment", "BVS", "LILACS",
    "revisor independente", "dois revisores", "two-reviewer",
    "reviewer_2", "auditoria independente", "DOI de arquivamento",
    "archival release",
]
REQUIRED = [
    "README.md", "LICENSE", "CITATION.cff", "pyproject.toml", "Dockerfile",
    "docker-compose.yml", "docs/00_PROTOCOL.md", "docs/13_DECLARACAO_IA.md",
    "docs/14_APP.md", "fair/metadata.json", "fair/datapackage.json",
    "app/global.R", "app/ui.R", "app/server.R", "app/data/nodes.csv",
    "outputs/graph/relations.csv", "data_processed/pm25_campos_mensal.csv",
    "reports/pysus_sinasc_audit.json",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_text_files():
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT_EXT:
            continue
        if any(part in SKIP for part in p.parts):
            continue
        if p.name in {"01_check.py", "compliance_report.json", "compliance_report.md"}:
            continue
        yield p


def main() -> None:
    issues = []
    checks = {}

    # 1. naming / forbidden strings
    hits = []
    for p in iter_text_files():
        try:
            s = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for term in FORBIDDEN:
            if term.lower() in s.lower():
                # ignore scientific text containing NF-kappaB
                if term.lower() == "kappa":
                    continue
                hits.append({"file": str(p.relative_to(ROOT)), "term": term})
    checks["forbidden_strings"] = {"n_hits": len(hits), "hits": hits[:30]}
    if hits:
        issues.append(f"{len(hits)} ocorrências de termos proibidos")

    # 2. secrets (targeted patterns; avoid false positives in article text)
    secret_patterns = [
        re.compile(r"RSCONNECT_SECRET\s*=\s*[A-Za-z0-9]{20,}"),
        re.compile(r"SHINYAPPS_SECRET\s*=\s*[A-Za-z0-9]{20,}"),
        re.compile(r"secret\s*=\s*['\"][A-Za-z0-9]{30,}['\"]", re.I),
    ]
    secret_hits = []
    for p in iter_text_files():
        try:
            s = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pat in secret_patterns:
            if pat.search(s):
                secret_hits.append(str(p.relative_to(ROOT)))
    checks["secrets"] = {"n_hits": len(set(secret_hits)), "files": sorted(set(secret_hits))}
    if secret_hits:
        issues.append("possível segredo no repositório")

    # 3. required files
    missing = [f for f in REQUIRED if not (ROOT / f).exists()]
    checks["required_files"] = {"missing": missing, "n_required": len(REQUIRED)}
    if missing:
        issues.append(f"arquivos obrigatórios ausentes: {missing}")

    # 4. FAIR checksums
    dp = json.loads((ROOT / "fair" / "datapackage.json").read_text(encoding="utf-8"))
    bad = []
    for r in dp.get("resources", []):
        p = ROOT / r["path"]
        if not p.exists():
            bad.append({"path": r["path"], "error": "missing"})
            continue
        expected = r.get("hash", "").replace("sha256:", "")
        if expected and sha256(p) != expected:
            bad.append({"path": r["path"], "error": "checksum mismatch"})
    checks["fair_checksums"] = {"n_resources": len(dp.get("resources", [])), "bad": bad}
    if bad:
        issues.append("checksums FAIR desatualizados")

    # 5. git hygiene
    try:
        tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, timeout=30).stdout.splitlines()
    except Exception:
        tracked = []
    raw_tracked = [f for f in tracked if f.startswith("data_raw/")]
    venv_tracked = [f for f in tracked if f.startswith(".venv/")]
    checks["git"] = {"tracked_files": len(tracked), "data_raw_tracked": raw_tracked[:5], "venv_tracked": venv_tracked[:5]}
    if raw_tracked or venv_tracked:
        issues.append("dados brutos ou ambiente virtual versionados")

    # 6. scientific label and AI declaration
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    checks["non_systematic_label"] = "não é uma revisão sistemática" in readme.lower()
    if not checks["non_systematic_label"]:
        issues.append("rótulo de não revisão sistemática ausente no README")
    ai = (ROOT / "docs/13_DECLARACAO_IA.md").read_text(encoding="utf-8")
    checks["ai_declaration"] = "2.664/2026" in ai
    if not checks["ai_declaration"]:
        issues.append("declaração de IA ausente ou sem referência à portaria")

    # 7. local PM2.5 and pySUS audit
    checks["pm25_series"] = (ROOT / "data_processed/pm25_campos_mensal.csv").exists()
    checks["pysus_audit"] = (ROOT / "reports/pysus_sinasc_audit.json").exists()

    # 8. app self-containment
    app_required = ["app/data/nodes.csv", "app/data/relations.csv", "app/data/evidence.csv",
                    "app/data/pm25_annual.csv", "app/data/pm25_monthly.csv",
                    "app/data/ai_declaration.md", "app/www/metadata.json"]
    checks["app_bundle"] = {"missing": [f for f in app_required if not (ROOT / f).exists()]}
    if checks["app_bundle"]["missing"]:
        issues.append("bundle do app incompleto")

    out = {"generated_at": __import__("datetime").datetime.now(__import__("datetime").UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "passed": not issues, "issues": issues, "checks": checks}
    JSON_OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = ["# Relatório de conformidade e higiene", "", f"Gerado: {out['generated_at']}", "",
             f"**Resultado: {'APROVADO' if out['passed'] else 'REPROVADO'}**", ""]
    if issues:
        lines += ["## Problemas", ""] + [f"- {i}" for i in issues] + [""]
    lines += ["## Verificações", "",
              f"- Termos proibidos: {checks['forbidden_strings']['n_hits']} ocorrências",
              f"- Segredos: {checks['secrets']['n_hits']} arquivo(s)",
              f"- Arquivos obrigatórios ausentes: {len(checks['required_files']['missing'])}",
              f"- Recursos FAIR com checksum inválido: {len(checks['fair_checksums']['bad'])}",
              f"- Arquivos versionados: {checks['git']['tracked_files']}",
              f"- `data_raw/` versionado: {len(checks['git']['data_raw_tracked'])}",
              f"- Rótulo de não revisão sistemática: {checks['non_systematic_label']}",
              f"- Declaração de IA (Portaria 2.664/2026): {checks['ai_declaration']}",
              f"- Série PM2,5 local: {checks['pm25_series']}",
              f"- Auditoria pySUS: {checks['pysus_audit']}",
              f"- Bundle do app incompleto: {len(checks['app_bundle']['missing'])}"]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
