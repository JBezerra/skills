---
name: clean-inbox
description: >
  Cleans up the user's Gmail inbox by reading all unread emails and marking
  the unimportant ones as read, leaving only the ones that actually need
  attention. Trigger whenever the user says "/clean-inbox", "clean my inbox",
  "clear unread emails", "triage my inbox", or anything similar asking to
  mark emails as read or reduce inbox noise. Also proactively suggest this
  skill if the user mentions having too many unread emails.
---

# Clean Inbox

Fetch every unread email in the inbox, classify each thread as **important**
or **noise**, and mark the noise threads as read. Leave the important ones
untouched so the user notices them.

---

## Step 1 — Fetch all unread threads

Use `search_threads` with:
- `query`: `is:unread in:inbox`
- `pageSize`: 50
- `view`: `THREAD_VIEW_MINIMAL`

Paginate using `nextPageToken` until no more pages are returned. Collect
every thread ID + its metadata (sender, subject, snippet, labelIds).

---

## Step 2 — Classify each thread

For each thread, decide: **keep unread** or **mark as read**.

### KEEP UNREAD — things the user genuinely cares about

1. **GitHub PR review requests** — `notifications@github.com` where
   the snippet or subject contains phrases like "requested your review".
   Someone is specifically asking this user to review their code.

3. **Human comments on GitHub PRs** — `notifications@github.com` where
   a real person (not a bot) left a comment. Signs it's human:
   snippet has `@username commented` or `@username left a comment` and
   the username does NOT contain `[bot]` and is NOT `decrapifier`.
   Signs it's a bot or noise: `[bot]`, `decrapifier`, `pushed N commit`,
   `approved this pull request`, `Merged #`.

4. **Jira direct mentions** — `jira@govspend.atlassian.net` where the
   subject contains `"mentioned you on"`. Someone is tagging the user
   specifically in a conversation thread.

5. **Recruiter outreach** — emails from outside `govspend.com` that are
   clearly reaching out about job opportunities. Signals: sender domain
   is not govspend.com, words like "opportunity", "role", "position",
   "your background", "your profile", "Senior", "Engineer" in a
   cold-outreach tone. Use judgment — a genuine business partner email
   is not a recruiter.

6. **Notion digests** — sender is `notify@mail.notion.so` or
   `team@mail.notion.so`. These are workspace notifications the user
   wants to see.

7. **Forwarded internal threads** — subject starts with `Fwd:` AND
   sender is `@govspend.com`. A colleague forwarding something usually
   means they want the user's input or awareness.

---

### MARK AS READ — noise the user doesn't want to see

These are patterns that should be silently cleaned up:

- **Elasticsearch / infrastructure autoscaling alerts** — sender
  `cloud-admin@ess.cloud.elastic.co` or similar infrastructure alert
  senders. Subject like "Your deployment has reached its autoscaling
  maximum size".

- **CI/CD pipeline failures** — subject contains "PR run failed",
  "workflow run", "Build and Push Docker Image … failed", or similar.

- **Monitoring alerts that are purely informational** — e.g. Axiom
  "Datasets exceeded field limits" (`no-reply@mail.axiom.co`). Generic
  quota/limit warnings that don't require immediate action.

- **GitHub noise** — `notifications@github.com` threads that are:
  - Bot comments (`augmentcode[bot]`, `decrapifier`, `mergify`, etc.)
  - PR approvals (`@X approved this pull request`)
  - Commit push notifications (`@X pushed N commit`)
  - PR merged notifications (`Merged #NNN`)
  - CI status changes

- **Automated Jira updates** — `jira@govspend.atlassian.net` where the
  subject does NOT contain `"mentioned you on"`. Status transitions,
  sprint changes, field updates by Automation for Jira are noise.

- **Calendar invites** — subject starts with `Invitation:` or
  `Updated invitation:`. The user checks their calendar directly.

- **Newsletters & developer digests** — `support@codepen.io`,
  `announcements@figma.com`, `info@mail.zapier.com`, and similar
  mailing list / product announcement senders.

- **Promotional / marketing emails** — MBA programs, courses, education
  offers, cold sales pitches (non-recruiter). Sender domains like
  `@decision.edu.br`, or subjects about discounts/courses.

- **Security & login notifications** — "New sign-in detected",
  "authentication with your Login.gov account", and similar automated
  security emails that are informational but don't need inbox attention.

- **Incident / FSD response requests** — `spdevelopment@govspend.com`
  subjects like "Your incident … requires a response" when they are
  automated follow-ups.

- **Privacy policy & ToS updates** — Automated emails from services
  updating their terms. Recognized by subjects like "We're updating our
  Privacy Policy" or "Terms of Service".

---

## Step 3 — Mark noise as read

For every thread classified as noise, call `unlabel_thread` with
`labelIds: ["UNREAD"]`. Do all calls in parallel to be fast.

---

## Step 4 — Report

After finishing, give the user a brief summary:

- How many threads were marked as read (cleaned)
- How many were left unread (kept)
- A short grouped list of what was kept, e.g.:
  - 2 GitHub PR review requests
  - 1 Jira mention
  - 1 recruiter email

Keep the summary tight — the user just wants to know the inbox is clean
and what still needs their attention.

---

## Edge cases

- **Ambiguous senders**: when unsure whether an email is noise or
  important, **leave it unread**. It's better to leave one extra email
  than to accidentally hide something the user needs.

- **Pagination**: always exhaust all pages before starting to mark
  threads. You need the full picture before acting.

- **Large inboxes**: if there are more than 200 unread threads, inform
  the user before proceeding — that volume is unusual and they may want
  to confirm.
