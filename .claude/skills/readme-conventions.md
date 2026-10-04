# Example README conventions

Shared by the `add-example`, `refresh-example-output` and `diagnose-case-study`
skills. AGENTS.md keeps a short summary.

Each example README has these sections, in this order:

1. **A title**, then a callout saying what it needs:
   `> **No key needed.**` or
   `> **Needs sign-in (free) or an Anthropic key.** Run \`quatern login\` (GitHub, free monthly usage) or set \`ANTHROPIC_API_KEY\`.`
2. **What it shows**: one paragraph.
3. **Run it**: the exact commands, one command where possible. They must
   match `run.sh`. If `run.sh` works on a copy (`mktemp -d`), say so under
   the block.
4. **Expected output**: real output, trimmed. Say "Trimmed."
   - Paste from an actual run. Never write output by hand.
   - Cut machine paths. The runner's scratch data dir
     (`/var/folders/.../quatern-example-XXXX/...`, `/tmp/...`) and your home
     dir become `~/.quatern/...`.
   - Cut toolchain lines and progress noise (spinners, download bars,
     compiler chatter).
   - Keep the lines a reader needs to compare against. Mark long cuts with
     `[...]`.
   - Don't edit the numbers. Drift, scores, PWM caps and timings stay exactly
     as printed.
   - Replace the account name: `quatern whoami` and the sign-in banner print
     it.
   - Label each block with the command it came from when there are several.
   - Agent transcripts: say that the wording changes from run to run, and
     name what doesn't (the diff, the verdict).
5. **What to look for in the run record**: the receipt fields (or stack, or
   config) that show the result, with their real names, e.g.
   `findings[0].fix.verified`. Check the names against `--json` output; don't
   guess them.
6. **Docs**: links to the matching page at https://quatern.co/docs/, with an
   anchor that exists (open the page and check).

Until the release is on PyPI, add the build line under "Trimmed." (see
`refresh-example-output`), with the version from `pip show quatern` and no
commit SHA:
`Trimmed. From a run against a development build of quatern (\`0.3.0\`).`

Write plainly. No personal names, usernames, emails or local paths anywhere,
including pasted output.
