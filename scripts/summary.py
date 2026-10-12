"""Markdown summary of a story for the GitHub Actions run page."""
import json, sys
s = json.load(open(sys.argv[1]))
out = [f"## KID LOGIC #{s.get('episode', '?')}: {s['title']}", "",
       f"**Rule:** {s.get('rule', '')}  ·  **Situation:** {s.get('situation', '')}", "", "### Script", ""]
hook = s.get("hook") or {}
for ln in hook.get("lines", []):
    out.append(f"- *(cold open)* **{ln['speaker']}:** {ln['text']}")
for i, sc in enumerate(s["scenes"]):
    out.append(f"\n**Scene {i + 1} — {sc.get('caption', '')} ({sc['background']})**")
    for ln in sc["lines"]:
        out.append(f"- **{ln['speaker']}:** {ln['text']}{'  ← punchline' if ln.get('punchline') else ''}")
print("\n".join(out))
