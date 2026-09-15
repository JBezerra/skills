# SDD work folder

Every sdd skill reads and writes one folder per piece of work:

`/Users/josebezerra/source/@specs/<repo>/<KEY>/`

- `<repo>`: basename of the git toplevel (`spark`, `spark-mcp`, ...).
- `<KEY>`: the Jira key from the skill's argument, else from the current branch (`GS-XXXX/...`). With neither, ask the user for a kebab-case slug. Create the folder if missing.

| File | Written by | Holds |
|---|---|---|
| `context.md` | sdd:explore, sdd:design appends facts | facts with sources, open questions Q1..Qn |
| `design.md` | sdd:design | decisions D1..Dn settling each Q, assumptions, non-goals |
| `test-cases.md` | sdd:design | black-box test cases TC-<Section><n>, each citing the Ds that make it normative |
| `spec.md` | sdd:spec, sdd:implement updates status | tasks T-001.. with AC and status |

## Task status

Each task heading in `spec.md` carries its status: `### [ ] T-001: <title>`.

- `[ ]` todo
- `[~]` in progress: implemented, waiting for the user's review
- `[x] (<short sha>)` done: committed
