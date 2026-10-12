# KID LOGIC — episode {{EPISODE}}

You write one episode of **KID LOGIC**, a stick-figure comedy series for YouTube Shorts, TikTok
and Reels. 30–45 seconds. Viewers come from everywhere; many speak English as a second
language and watch with the sound OFF. Every joke must be understood by a 10-year-old who
learned English at school.

## The show (never change this)
Leo is 8. An adult gives Leo a simple RULE. Leo follows the rule EXACTLY as it was said —
word for word — and the adult loses. Leo always wins. Adults never learn.
Current scoreboard before this episode: KID LOGIC {{SCORE_KID}} : {{SCORE_ADULTS}} ADULTS (it goes up by one automatically).

Recurring cast — use 2 to 4 of them, keep their personalities:
{{CAST}}

Today's situation: **{{SITUATION}}**

Past episodes — do NOT repeat the rule, the premise or the punchline:
{{HISTORY}}

## Episode formula
1. **COLD OPEN (hook, 2 lines).** The funniest disaster from the END of the story.
   Line 1: an adult shouts a short question. Mark the 1–2 key words with *asterisks*
   (e.g. "Leo! You told the *WHOLE* class about my *DONUTS?!*").
   Line 2: Leo answers calmly with the rule (e.g. "Ms. Lee said: be *honest.*").
   It shows the consequence, NOT the punchline. Viewers must think "wait, what happened?!"
2. **THE RULE.** Right after the rewind, an adult says the rule clearly, in 2–4 words
   ("Be honest!", "Clean your room!", "Don't touch the cake!"). Put it in *asterisks*.
3. **THREE BEATS.** Leo follows the rule literally three times. Each beat is bigger and
   funnier than the last (rule of three). Each beat is ONE clear picture the viewer can
   imagine. The adult reacts after each one.
4. **TWIST.** The rule comes back and hits the adult. The punchline is the SHORTEST line
   (max 6 words) and it is a surprise. Then nobody explains the joke.
5. Do NOT write the sign-off ("Kid logic. Easy.") or the scoreboard — they are added
   automatically. Leo must be on stage in the last scene.

## Simple English rules (very important)
- CEFR A2 level: the 1500 most common English words. Short sentences. Present tense.
- Max 12 words per line, most lines 4–8 words.
- No idioms, no puns, no wordplay, no slang, no sarcasm that needs tone of voice,
  no cultural references (no sports teams, TV shows, holidays from one country).
- The joke must work as a PICTURE: someone who only reads the subtitles understands it.
- Use names, not pronouns, when it could be unclear who "he" or "she" is.
- Numbers and objects are great (29 years old, 100 donuts, a pizza, the cat).

## Make people click and watch to the end
- **Title**: max 6 words, ends with "…", creates curiosity, names Leo or the adult and a
  strong word: "Leo Was TOO Honest…", "Mom Said: Clean EVERYTHING…", "Grandpa Asked Leo For Help…".
  One word in CAPITALS. Never give away the ending.
- Every line must move the story or be a joke. No small talk, no "hello".
- Give the viewer a reason to wait: the cold open promises a disaster, the rule tells them
  it is coming, beat 3 is the biggest.
- Clean family humour only: no insults, no violence, no body jokes, nothing mean about
  any group. Adults lose, but in a sweet way.

## Output: JSON only
```json
{
  "id": "short-kebab-slug",
  "title": "Leo Was TOO Honest…",
  "rule": "Be honest!",
  "hook": {
    "caption": "THIS MORNING…",
    "scene": { "background": "kitchen", "left": "leo", "right": "dad" },
    "lines": [ <line>, <line> ]
  },
  "scenes": [
    { "background": "classroom", "caption": "AT SCHOOL", "board": "MY FAMILY",
      "left": "leo", "right": "ms_lee", "props": { "leo": "paper" },
      "lines": [ <line>, ... ] },
    { "background": "kitchen", "caption": "THAT EVENING", "left": "leo", "center": "dad", "right": "mom",
      "lines": [ <line>, ... ] }
  ],
  "outro": { "actions": { "leo": "shrug", "dad": "facepalm" }, "expressions": { "leo": "smug", "dad": "sad" } }
}
```
`<line>`:
`{ "speaker": "<cast id>", "text": "...", "action": "<action>", "expression": "<expression>",
   "listener": { "action": "<action>", "expression": "<expression>" }, "pause_after": 0.3 }`
With three characters on stage use `"listeners": { "<id>": {...}, "<id>": {...} }` instead of `listener`.
Add `"punchline": true` to exactly one line (the twist).

- backgrounds: living_room, kitchen, classroom, park
- `board` (classroom only): 1–3 words written on the chalkboard
- props: paper (homework), test_paper (a test with a red 0), icecream
- actions: idle, talk, point, shrug, facepalm, think, surprised, laugh, phone, phone_call,
  cross_arms, celebrate, hug_pillow
- expressions: neutral, happy, smug, annoyed, sad, surprised, worried
- Positions: "left", "right", and "center" when 3 are on stage. Leo is usually "left".
- 2–3 scenes plus the hook. 11–18 lines in total (hook included).
- `pause_after`: 0.3 normally, 0.5–0.7 before the twist, 1.5 after the punchline.
