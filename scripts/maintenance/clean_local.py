"""Remove local, re-downloadable or regenerable files to save disk space.

Nothing here is tracked by Git. Processed/derived data remain in data_processed,
outputs and literature. Use --dry-run to see sizes before deleting.

Examples:
  python scripts/maintenance/clean_local.py --dry-run
  python scripts/maintenance/clean_local.py --yes --http-cache --literature-raw --heavy-graph
  python scripts/maintenance/clean_local.py --yes --datasus-raw
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGETS = {
    "http-cache": [ROOT / "data_raw" / "http_cache"],
    "literature-raw": [ROOT / "data_raw" / "literature" / "full"],
    "datasus-raw": [ROOT / "data_raw" / "sinasc", ROOT / "data_raw" / "sih"],
    "heavy-graph": [ROOT / "outputs" / "graph" / "screened_studies.graphml", ROOT / "outputs" / "graph" / "screened_studies.json"],
}


def size(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--yes", action="store_true", help="actually delete")
    ap.add_argument("--dry-run", action="store_true", help="only report")
    for name in TARGETS:
        ap.add_argument(f"--{name}", action="store_true")
    args = ap.parse_args()
    selected = [name for name in TARGETS if getattr(args, name.replace("-", "_"))]
    if not selected:
        selected = list(TARGETS)
    total = 0
    for name in selected:
        for path in TARGETS[name]:
            n = size(path)
            total += n
            print(f"{human(n):>10}  {path.relative_to(ROOT)}")
            if args.yes and not args.dry_run and path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
    print(f"{'TOTAL':>10}  {human(total)}")
    if not args.yes:
        print("Dry run. Add --yes to delete. Tracked files are never touched.")


if __name__ == "__main__":
    main()
