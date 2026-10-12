# KID LOGIC — automated stick-figure comedy series

Story JSON → voice (Supertonic) → Remotion render → vertical MP4 (1080×1920).

## Run locally
```bash
npm install
pip install -r requirements.txt
npm run tts -- stories/demo.json      # writes public/build/demo/{audio.wav,timeline.json}
npm run render -- stories/demo.json   # writes out/demo.mp4
npm run studio                        # live preview in the browser
```
Supertonic downloads its model from Hugging Face on first run.
Alternative voice: `TTS_ENGINE=kokoro` (put kokoro.onnx + voices.bin from the kokoro-onnx GitHub release in `models/`).
Audio: 48 kHz, voices + procedurally generated music (ducked under speech) + SFX. Video: 30 fps by default (FPS=60 for smoother motion), CRF 16.

## Story format (stories/*.json)
- `characters.<id>`: look, gender, scale. Voices are cast automatically to match gender.
- `hook`: cold open (1–2 shocking lines + its own scene), followed by a rewind caption
- `scenes[]`: background (living_room, park, office), caption, left/right cast, props, `enter` (walk-in), lines
- `lines[]`: speaker, text (`*word*` = emphasis), action, expression, listener, speed, pause_after, punchline
- `prompts/story.md`: the prompt the daily generator gives the LLM (variety, cold open, twist, 30–45 s)

## Channel identity
`channel/bible.json` is the show bible: series name, recurring cast (look, fixed voice, personality),
episode formula, sign-off line and scoreboard. Every episode reads it, so the channel always looks
and sounds like the same show. `channel/history.json` keeps every episode (number, rule, score).

## Daily automation (GitHub Actions)
`.github/workflows/episode.yml` runs every day at 08:00 (Vietnam) and on demand (Actions → Kid Logic episode → Run workflow):
1. `scripts/generate_story.py` writes the episode with GitHub Models (free, uses `GITHUB_TOKEN`),
   checks it against the rules (cast, actions, 12-word lines, 30–45 s) and asks the model to fix problems.
2. `scripts/tts.py` makes voices + music, `scripts/render.mjs` renders the MP4.
3. The video is uploaded as a run artifact; the story and `history.json` are committed back.
Use another OpenAI-compatible LLM with `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`.

## Layout
- `scripts/tts.py`   voice per line, rimshot sting, word timings, mouth envelope
- `scripts/render.mjs` bundles and renders with Remotion (`CHROME_PATH` optional)
- `src/poses.ts`     pose/action library with 2-bone IK for hands
- `src/StickFigure.tsx`, `src/Background.tsx`, `src/JokeVideo.tsx`
