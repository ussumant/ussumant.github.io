"""Pull the newest Run Receipt into content/site.json + assets/, then rebuild.

    python3 scripts/refresh_run_receipt.py && python3 scripts/build_site.py

Reads the live wall's receipts.json (forrest-gump-run-receipts.netlify.app),
picks the newest run by (date, id), copies its halftone photo into
assets/run-receipt-latest.png so the home page never hotlinks, and writes the
fields the home-page receipt card needs into site.json["run_receipt"].
"""

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WALL = "https://forrest-gump-run-receipts.netlify.app"
PHOTO = ROOT / "assets" / "run-receipt-latest.png"
SITE = ROOT / "content" / "site.json"


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()


def main() -> None:
    runs = json.loads(fetch(f"{WALL}/receipts.json"))
    latest = max(runs, key=lambda run: (run["date"], run["id"]))
    PHOTO.write_bytes(fetch(f"{WALL}/{latest['thumb']}"))
    data = json.loads(SITE.read_text(encoding="utf-8"))
    keep = {k: data.get("run_receipt", {}).get(k, "") for k in ("app_url", "feed_url")}
    data["run_receipt"] = {**keep,
        "wall_url": f"{WALL}/",
        "url": f"{WALL}/r/{latest['id']}.html",
        "order": str(latest["id"])[-4:],
        "date": latest["date"],
        "name": latest["name"],
        "km": f"{latest['distanceKm']:.2f}".rstrip("0").rstrip("."),
        "pace": latest["pace"],
        "photo": "/assets/run-receipt-latest.png",
    }
    SITE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"latest run: {latest['date']} {latest['name']} {latest['distanceKm']} km -> site.json + {PHOTO.name}")


if __name__ == "__main__":
    main()
