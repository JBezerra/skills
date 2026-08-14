---
name: gs:create-alpha
description: >
  Cut an alpha build release for a Spark pull request by dispatching the
  `create-alpha-build-release.yml` GitHub Actions workflow, picking the next
  sequence number automatically and reusing the flags from the PR's previous
  build. Use whenever asked to create an alpha, generate an alpha link, deploy a
  branch to alpha, bump the alpha build, or "give me an alpha for this PR".
  Spark repo only (smartprocure/spark).
---

# gs:create-alpha

Dispatch the alpha build workflow for a PR. The workflow only creates a
prerelease tag; a downstream workflow watches for that tag and does the actual
deploy.

## Preconditions

- In `smartprocure/spark`, on the PR's branch.
- **The branch is pushed.** The release is cut from the *remote* branch head
  (`target_commitish`), so unpushed commits will not be in the alpha. Check with
  `git status -sb` and push first if needed.
- `gh` network calls fail inside the sandbox (`authentication method negotiation
  failed`). Run them with `dangerouslyDisableSandbox: true`.

## Steps

1. **PR number** — `gh pr view --json number,title,headRefName`

2. **Next sequence number** — list the PR's existing alphas and take the highest
   `seqNum` plus one:

   ```bash
   gh release list --limit 200 | grep "^<prNum>\."
   ```

   Tags look like `20562.5-govspend-URL-BACK-alpha`, i.e.
   `<prNum>.<seqNum>-<sites>[-URL][-BACK]-alpha`. If the user names a build
   number, use theirs, but say so if it collides with an existing tag.

3. **Flags** — default to whatever the PR's most recent alpha used; that is
   almost always what they want again. Only ask if there is no previous build
   and the request gives no hint.

   | input | notes |
   |---|---|
   | `sites` | `govspend`, `bidsearch`, or `govspend-bidsearch` |
   | `URL` | `true` publishes it at `https://alpha.<site>.com`. **A request for an alpha *link* implies `URL=true`.** |
   | `BACK` | `true` also spins up a job-processing instance. Needed for anything exercising Temporal jobs, signals, or ingest. |

4. **Dispatch**

   ```bash
   gh workflow run create-alpha-build-release.yml \
     -f branchName=<branch> \
     -f prNum=<n> \
     -f seqNum=<n> \
     -f sites=govspend \
     -f URL=true \
     -f BACK=true
   ```

5. **Verify** — poll the run, then confirm the tag exists:

   ```bash
   gh run view <runId> --json status,conclusion
   gh release view <tag> --json tagName,url
   ```

## Reporting back

Give the user the run URL, the tag, and the alpha link (`https://alpha.govspend.com`
/ `https://alpha.bidsearch.com`), and state the inputs used so wrong flags are
caught immediately. Flag anything that makes the build differ from what they
likely expect — most often a `develop` merge you pushed along with their change,
since the alpha is cut from the branch head, not from their commit alone.

The release tag appearing is not the deploy finishing. The environment takes a
while after the tag lands; say that rather than implying the link is live.
