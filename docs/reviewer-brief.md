# Translation reviewer brief - GetBackers Dakkanya: Jigoku no Scaramouche

You review a JP->English fan translation. Read-only: no edits, no git, no subagents.
Mechanical validity (ids, `{br}`/printf codes, encodable characters, width, speaker labels) is already enforced by
`tools/batches.py check` - judge translation quality. Return the report as your final message: subagents cannot
write files, so the controller saves it.

## Inputs (paths in your dispatch)
- Pairs file: every translated entry as `>> id | form speaker | JP / EN`, in story order (neighbours are context;
  each line is one dialogue-box page, quotes run over several pages). Read ALL of it, in passes if large.
- `glossary.md` (rulings at the top), `docs/style-reference.md`, `docs/synopsis.md`.

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly (a one-letter slip is what players notice); honorifics kept and stable
  (蛮ちゃん = Ban-chan); quote marks across multi-page speech (open on the first page, close on the last).
- Things players caught that reviewers missed: jokes/wordplay losing their punch; ordinal suffix after a variable
  ("1th"); abbreviated names or terms; stock phrases that read awkwardly in English ("... GET!").
- Naturalness and voice: Ban cocky and slangy, Ginji earnest, villains formal; would a fan-translation reader
  stumble?

## Report
### Issues
#### Critical (meaning reversed, broken placeholder grammar, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, abbreviation)
#### Minor (style - these are deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN`.
### Assessment
Approved | Needs fixes - one sentence why.
