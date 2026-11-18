"""Regenera productos con una semilla nueva y registra el resultado."""

import argparse
import datetime as dt
import json
import secrets
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build_pack import build, print_pdfs  # noqa: E402


def regenerate(out=ROOT / "products", log_dir=ROOT / "ops" / "log", count=6, seed=None):
    seed = secrets.randbits(64) if seed is None else seed
    out = Path(out)
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc)
    entry = {"timestamp_utc": timestamp.isoformat(), "seed": seed, "count": count, "status": "error"}
    try:
        build(out, seed, count)
        pdfs = print_pdfs(out)
        entry["pdf_bytes"] = {path.name: path.stat().st_size for path in pdfs}
        entry["status"] = "ok"
        return entry
    except Exception as exc:
        entry["error"] = str(exc)
        raise
    finally:
        with (log_dir / "regeneraciones.jsonl").open("a", encoding="utf-8") as log:
            log.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "products")
    parser.add_argument("--log-dir", type=Path, default=ROOT / "ops" / "log")
    parser.add_argument("--n", type=int, default=6)
    args = parser.parse_args()
    result = regenerate(args.out, args.log_dir, args.n)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
