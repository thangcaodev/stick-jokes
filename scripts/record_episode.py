"""Append a rendered episode to channel/history.json (episode number, score, rule)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
story = json.loads(Path(sys.argv[1]).read_text())
path = ROOT / "channel" / "history.json"
history = json.loads(path.read_text()) if path.exists() else {"episodes": []}
history["episodes"] = [e for e in history["episodes"] if e["episode"] != story["episode"]]
history["episodes"].append({k: story.get(k) for k in ("episode", "date", "id", "title", "rule", "situation", "score")})
history["episodes"].sort(key=lambda e: e["episode"])
path.write_text(json.dumps(history, indent=1, ensure_ascii=False) + "\n")
print(f"recorded episode #{story['episode']}: {story['title']}")
