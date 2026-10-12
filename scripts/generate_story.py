"""Write today's Kid Logic episode with an LLM and save it as stories/<date>-<slug>.json.

Usage:  python3 scripts/generate_story.py            -> prints the story path
Env:
  GITHUB_TOKEN   used for GitHub Models (free in GitHub Actions with `permissions: models: read`)
  LLM_BASE_URL   OpenAI-compatible endpoint (default: GitHub Models)
  LLM_API_KEY    key for that endpoint (default: GITHUB_TOKEN)
  LLM_MODEL      comma-separated models to try in order (default: openai/gpt-4.1,openai/gpt-4o)
  LLM_MOCK_FILE  skip the API and use this JSON file as the model answer (for testing)

The story is checked against the channel rules (cast, actions, simple English, length).
If it breaks a rule, the errors are sent back to the model to fix, up to 3 times.
"""
import datetime as dt
import json, os, random, re, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIBLE = json.loads((ROOT / "channel" / "bible.json").read_text())
HISTORY_PATH = ROOT / "channel" / "history.json"

ACTIONS = {"idle", "talk", "point", "shrug", "facepalm", "think", "surprised", "laugh", "phone", "phone_call",
           "cross_arms", "celebrate", "hug_pillow"}
EXPRESSIONS = {"neutral", "happy", "smug", "annoyed", "sad", "surprised", "worried"}
BACKGROUNDS = {"living_room", "kitchen", "classroom", "park", "office"}
PROPS = {"paper", "test_paper", "icecream"}

SITUATIONS = [
    "report card day", "homework excuses", "cleaning your room", "screen time rules", "bedtime",
    "family dinner: eat your vegetables", "grandpa and the smartphone", "fighting with big sister Mia",
    "a birthday gift for Mom", "saving pocket money", "family road trip: 'are we there yet?'",
    "Dad's 'back in my day' stories", "asking for a pet", "Dad cooks dinner", "the school trip",
    "the class presentation", "a pop quiz", "parent-teacher meeting", "school lunch", "PE class",
    "phones in class", "school picture day", "the new student", "the spelling test", "Mom's diet",
    "Dad's nap time", "Grandpa babysits", "the science project", "washing the car", "the dentist visit",
]


# ------------------------------------------------------------------ prompt
def load_history():
    if HISTORY_PATH.exists():
        return json.loads(HISTORY_PATH.read_text())
    return {"episodes": []}


def pick_situation(history, today):
    used = [e.get("situation") for e in history["episodes"][-12:]]
    pool = [s for s in SITUATIONS if s not in used] or SITUATIONS
    return random.Random(today.isoformat()).choice(pool)


def build_prompt(history, situation, episode, score):
    template = (ROOT / "prompts" / "story.md").read_text()
    past = "\n".join(f"- #{e['episode']} \"{e['title']}\" (rule: {e.get('rule', '?')}; situation: {e.get('situation', '?')})"
                     for e in history["episodes"][-30:]) or "- (none yet, this is the first episode)"
    cast = "\n".join(f"- `{cid}` ({c['look']}, {c['gender']}): {c['personality']}" for cid, c in BIBLE["cast"].items())
    return (template.replace("{{SITUATION}}", situation)
                    .replace("{{HISTORY}}", past)
                    .replace("{{CAST}}", cast)
                    .replace("{{EPISODE}}", str(episode))
                    .replace("{{SCORE_KID}}", str(score["kid"]))
                    .replace("{{SCORE_ADULTS}}", str(score["adults"]))
                    .replace("{{TRENDS}}", "(not used)"))


# ------------------------------------------------------------------ llm
def chat(messages):
    mock = os.getenv("LLM_MOCK_FILE")
    if mock:
        return Path(mock).read_text()
    base = os.getenv("LLM_BASE_URL", "https://models.github.ai/inference").rstrip("/")
    key = os.getenv("LLM_API_KEY") or os.getenv("GITHUB_TOKEN")
    if not key:
        sys.exit("No LLM_API_KEY / GITHUB_TOKEN set")
    last_err = None
    for model in os.getenv("LLM_MODEL", "openai/gpt-4.1,openai/gpt-4o").split(","):
        body = {"model": model.strip(), "messages": messages, "temperature": 0.9,
                "response_format": {"type": "json_object"}}
        req = urllib.request.Request(f"{base}/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read())
            print(f"  model: {model.strip()}", file=sys.stderr)
            return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            last_err = f"{model}: HTTP {e.code} {e.read()[:300]!r}"
            print(f"  ! {last_err}", file=sys.stderr)
        except Exception as e:  # network / timeout
            last_err = f"{model}: {e}"
            print(f"  ! {last_err}", file=sys.stderr)
    sys.exit(f"All models failed. Last error: {last_err}")


def extract_json(text):
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    if m:
        text = m.group(1)
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end + 1])


# ------------------------------------------------------------------ checks
def words(text):
    return [w for w in re.sub(r"[*]", "", text).split() if re.search(r"[A-Za-z0-9]", w)]


def validate(story):
    errs = []
    cast = BIBLE["cast"]
    for key in ("id", "title", "rule", "hook", "scenes"):
        if key not in story:
            errs.append(f"missing top-level field '{key}'")
    if errs:
        return errs
    if len(words(story["title"])) > 6:
        errs.append("title must be max 6 words")

    def check_line(ln, where, on_stage):
        if ln.get("speaker") not in on_stage:
            errs.append(f"{where}: speaker '{ln.get('speaker')}' is not on stage {sorted(on_stage)}")
        if ln.get("action") not in ACTIONS:
            errs.append(f"{where}: unknown action '{ln.get('action')}'")
        if ln.get("expression") not in EXPRESSIONS:
            errs.append(f"{where}: unknown expression '{ln.get('expression')}'")
        n = len(words(ln.get("text", "")))
        if n == 0 or n > 12:
            errs.append(f"{where}: line has {n} words, must be 1-12: \"{ln.get('text')}\"")
        for lis in [ln.get("listener")] + list((ln.get("listeners") or {}).values()):
            if lis and (lis.get("action") not in ACTIONS or lis.get("expression") not in EXPRESSIONS):
                errs.append(f"{where}: bad listener reaction {lis}")
        for w in words(ln.get("text", "")):
            if len(re.sub(r"[^A-Za-z]", "", w)) > 11:
                errs.append(f"{where}: word '{w}' is too long/hard, use a simpler word")

    def check_scene(sc, where):
        on = {sc.get(k) for k in ("left", "center", "right") if sc.get(k)}
        if not on:
            errs.append(f"{where}: no characters on stage")
        for cid in on:
            if cid not in cast:
                errs.append(f"{where}: '{cid}' is not in the cast {sorted(cast)}")
        if sc.get("background") not in BACKGROUNDS:
            errs.append(f"{where}: unknown background '{sc.get('background')}'")
        for cid, prop in (sc.get("props") or {}).items():
            if prop not in PROPS:
                errs.append(f"{where}: unknown prop '{prop}'")
        return on

    hook = story["hook"]
    on = check_scene(hook.get("scene", {}), "hook.scene")
    hl = hook.get("lines", [])
    if not 1 <= len(hl) <= 2:
        errs.append("hook must have 1 or 2 lines")
    for i, ln in enumerate(hl):
        check_line(ln, f"hook line {i + 1}", on)
    if hl and "*" not in hl[0].get("text", ""):
        errs.append("hook line 1 must mark the key word with *asterisks*")

    total, punch = len(hl), 0
    if not 2 <= len(story["scenes"]) <= 4:
        errs.append("use 2 to 4 scenes")
    for si, sc in enumerate(story["scenes"]):
        on = check_scene(sc, f"scene {si + 1}")
        for i, ln in enumerate(sc.get("lines", [])):
            check_line(ln, f"scene {si + 1} line {i + 1}", on)
            punch += bool(ln.get("punchline"))
            total += 1
    last = story["scenes"][-1] if story["scenes"] else {}
    if "leo" not in {last.get("left"), last.get("center"), last.get("right")}:
        errs.append("Leo must be on stage in the last scene (he says the sign-off)")
    if punch != 1:
        errs.append(f"exactly one line must have \"punchline\": true (found {punch})")
    if not 11 <= total <= 18:
        errs.append(f"use 11-18 lines in total (found {total})")
    spoken = sum(len(words(ln["text"])) for ln in hl) + sum(len(words(ln["text"])) for sc in story["scenes"] for ln in sc.get("lines", []))
    est = spoken / 2.6 + total * 0.35 + 6
    if not 28 <= est <= 46:
        errs.append(f"estimated length {est:.0f}s, must be 30-45s: {'add' if est < 28 else 'cut'} some lines")
    return errs


# ------------------------------------------------------------------ main
def main():
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).date()
    history = load_history()
    episode = (history["episodes"][-1]["episode"] + 1) if history["episodes"] else 1
    prev = history["episodes"][-1]["score"] if history["episodes"] else {"kid": 0, "adults": 0}
    score = {"kid": prev["kid"] + 1, "adults": prev["adults"]}
    situation = os.getenv("SITUATION") or pick_situation(history, today)
    print(f"Episode #{episode}, situation: {situation}", file=sys.stderr)

    messages = [
        {"role": "system", "content": "You are the head writer of a hit family comedy channel. You answer with JSON only."},
        {"role": "user", "content": build_prompt(history, situation, episode, score)},
    ]
    story, errs = None, ["no answer"]
    for attempt in range(4):
        answer = chat(messages)
        try:
            story = extract_json(answer)
            errs = validate(story)
        except Exception as e:
            errs = [f"invalid JSON: {e}"]
        if not errs:
            break
        print(f"  attempt {attempt + 1}: {len(errs)} problems: {errs[:5]}", file=sys.stderr)
        if os.getenv("LLM_MOCK_FILE"):
            break
        messages += [{"role": "assistant", "content": answer},
                     {"role": "user", "content": "Fix these problems and answer with the full corrected JSON only:\n- " + "\n- ".join(errs)}]
    if errs:
        sys.exit("Story still breaks the rules:\n- " + "\n- ".join(errs))

    slug = re.sub(r"[^a-z0-9]+", "-", story.get("id", story["title"]).lower()).strip("-")[:40] or "episode"
    story.update(id=f"ep{episode:03d}-{slug}", episode=episode, score=score, situation=situation, date=today.isoformat())
    story.pop("characters", None)  # cast always comes from the bible
    out = ROOT / "stories" / f"{today.isoformat()}-ep{episode:03d}.json"
    out.write_text(json.dumps(story, indent=1, ensure_ascii=False))
    print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
