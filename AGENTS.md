# Working on quatern-examples

Instructions for anyone, person or coding agent, changing this repository.

## Never commit API keys

- No API keys, Quatern tokens or `credentials` files, ever. Keys belong in
  your environment (`ANTHROPIC_API_KEY`, `QUATERN_API_KEY`) or in
  `~/.quatern/credentials` via `quatern login`, never in this repository.
- CI reads the key from the `QUATERN_API_KEY` repository secret only.
- The pre-commit hooks block `sk-ant-` keys, private keys and `credentials`
  files. Install them with `pre-commit install`.
- Don't commit `.quatern/` data directories, logs, or local agent tooling
  state (anything in `.claude/` except `settings.json`, `hooks/` and
  `skills/`);
  `.gitignore` covers them.

## Coding agents

- READMEs show real output only, pasted from actual runs.
- Commit as `Quatern <hello@quatern.co>`, with no `Co-Authored-By` lines.
- No personal names, anywhere.
- Agent examples (`requires: agent`) need a key and aren't run by hooks.
- READMEs always tell readers `pipx install quatern`.
