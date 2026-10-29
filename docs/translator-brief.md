# Translator brief - GetBackers Dakkanya: Jigoku no Scaramouche (GBA, 2002)

You translate part of the Japanese script of GetBackers Dakkanya: Jigoku no Scaramouche into English for a fan patch.
It is an RPG of the GetBackers manga/anime: Ban Mido and Ginji Amano, the "GetBackers" retrieval duo of Shinjuku,
take a job that drags them into a foreign investor's (Scaramouche's) takeover of Ura-Shinjuku. Tone: shonen action
comedy - cocky banter, slapstick, broke-and-hungry gags, then serious villain scenes.
Work only on the batches named in your dispatch, one at a time in the order given, each to a passing check before the
next. Do all translation yourself; do not dispatch subagents.

## Read first
1. `docs/style-reference.md` - character voices and approved example pairs. Match this voice.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch (full table in `glossary.md` if you need more).
3. `docs/synopsis.md` - plot, who is who and the late reveals. Don't give a reveal away early.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`, in story (script) order: use neighbours for context.
- form: dlg (speech) | narration (examine text, signs, inner monologue) | menu (help bar) | name (item name) | choice.
- Each line is ONE page of the dialogue box. A speaker's quote often runs over several pages: the first page starts
  `蛮「`, middle pages have no brackets, the last ends `」`. The speaker column names who is talking on every page.
  Translate each page as its own page, but make the pages read as one continuous utterance.
- limit: box pages hold 3 lines x 216 px (about 120 characters; the tool word-wraps for you). menu = one line of
  232 px and at most 47 bytes (with `%s` counted as 10). name = 40 bytes.
- `{br}`: a forced line break in the JP. Write exactly as many `{br}` as the JP has, at the matching place, and no
  others (the tool wraps everything else).
- `%s` `%3d` `%6d`: values the game fills in (a name, a number). Keep each one, in the same order.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes, `...`, `--`, `~`; no tabs,
no Japanese or fullwidth characters, no `\uXXXX`, no `\n`. If the JP starts or ends with a blank (a fullwidth space),
start/end the English with one space.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it prints OK.
Dry-run a long page: `python -X utf8 tools/batches.py fit "Ban: \"text...\""` prints the wrapped lines and widths.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese
  doesn't state; don't summarise or skip. Jokes, puns and Ban's sweet-talk keep their punch even if the literal
  meaning shifts (no translator notes).
- Speakers: `蛮「...」` -> `Ban: "..."`; `銀次：...` -> `Ginji: ...` (no quotes, as the JP has none). A first page
  that opens a quote gets the opening `"` only; a last page gets the closing `"` only; a middle page has none.
  A line starting `「` with no name -> `"..."` (an unseen speaker, a PA, a door lock).
- Speaker labels and names exactly as in the glossary, every time (the check enforces the speaker label).
- Honorifics kept, hyphenated, Western name order: 蛮ちゃん -> Ban-chan, 卑弥呼ちゃん -> Himiko-chan, 〜さん -> -san,
  〜様 -> -sama, 〜くん/君 -> -kun. Generic titles are translated (お兄さん -> mister / big guy by context; お母さん -> Mom).
- Never abbreviate a name or term to fit; every page has room. If a line still can't fit, keep the meaning and
  report `LONG: id`.
- Punctuation: 「」 -> "...", 『』 -> '...' (inside speech) or "..." (in narration), …… / ・・・ -> `...`,
  ！？ -> `?!`, ～ (drawn-out) -> `~` or a stretched word ("Hungryyy~"), ーーー -> stretched letters, （ ） -> ( ) for
  asides/thoughts, 【 】 -> [ ]. Full-width digits and letters -> ASCII (`１００％` -> `100%`, `ＨＥＶＮ` -> `Hevn`
  per glossary).
- Sound effects and cries: English onomatopoeia (ドカッ -> WHAM!, キャアアア -> Kyaaaah!).
- Register: casual modern English. Ban: cocky, slangy, rude, mild swearing ("damn", "hell") is fine; Ginji: cheerful,
  earnest, a bit dim. Villains: formal and menacing. Shopkeepers, kids, punks: give each a recognisable voice.
- Placeholders: no suffixes glued to a variable ("Lv %3d", never "%3dth"); no a/an right before `%s`; item and skill
  names inside `%s` messages are in quotes in the JP (「%s」を習得した！ -> `Learned "%s"!`).
- Fragments that the game joins: `“` (0x30F4C) + item name + `”を見つけた。` (0x30F50) or `”はもう持ちきれない。`
  (0x30F60). The `“` prefix is shared by both messages, so it stays a bare `"`; the suffixes carry the verb:
  `" found!` and `" -- you can't carry any more.` Make the joined result read right.

## Notes from earlier batches
- (none yet)

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
