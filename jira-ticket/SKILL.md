---
name: jira-ticket
description: Create or update Jira tickets (Stories, Tasks, Bugs) using the Jira MCP tools, written as clean product-facing artifacts (user story, description, requirements, acceptance criteria) rather than engineering notes. Use this skill whenever the user asks to file a ticket, write up a story, create a Jira issue, update an existing ticket's description or AC, or turn a conversation/meeting/decision into a trackable piece of work. Also trigger on "/jira-ticket", "create a ticket for X", "update GS-XXXX", "write this up in Jira", or when the user has been discussing a feature/bug/decision and asks you to formalize it. Always asks clarifying questions and confirms the parent epic and owning team before writing anything.
---

# Jira Ticket

You are turning a request, a bug report, or a decision already discussed into a well-formed Jira ticket, or updating one that exists. The ticket is a product-facing artifact: someone who wasn't in this conversation and doesn't read code should be able to understand what's being asked for and why. Engineers will do the technical translation themselves when they pick up the work; your job is to capture intent, scope, and verification steps, not implementation.

## Workflow

1. **Understand the request.** If the conversation already contains the decision (a meeting transcript, a design discussion, a bug the user just described), extract from that first rather than re-asking things already answered. Note what's still missing.

2. **Take a brief look at the codebase.** Enough to sanity-check that the request is coherent and to catch an obviously wrong assumption, a quick grep or a couple of file reads. This is not a research pass: don't spawn subagents, don't trace the full call graph, don't read every related file. If the request needs deep investigation to even understand, say so and ask the user how deep to go rather than quietly doing it yourself.

3. **Search Jira before writing anything new.** Use the Jira MCP tools to check whether a ticket already covers this request (search by keywords, or by component if the project has one). Creating a duplicate is worse than asking "does GS-XXXX already cover this?" first.

4. **Ask clarifying questions.** Whenever the request leaves a gap, scope, acceptance criteria, what "done" looks like, whether an edge case is in or out, ask rather than filling it in silently. Use `AskUserQuestion` when there's a concrete set of options to choose between; ask in plain text when it's more open-ended. A ticket built on a guessed assumption is expensive to unwind later once someone starts building against it.

5. **Resolve the parent epic.** See "Choosing a parent" below. Never leave this blank or guess silently.

6. **Resolve the owning team.** See "Choosing a team" below. Same rule: ask rather than guess.

7. **Confirm your assumptions out loud before drafting.** If you had to infer anything to fill a gap (e.g. "I'm assuming this only applies to admins, since that's how the similar feature works"), say so explicitly and let the user correct you. Don't fold silent inferences into a draft that reads as settled fact.

8. **Present the full draft for confirmation.** Title, user story, description, requirements, acceptance criteria, chosen parent, chosen team, all together, before calling any Jira write tool. Wait for explicit confirmation. This applies to both new tickets and edits to existing ones, if you're updating a ticket, show what's changing, not just the final state.

9. **Write it.** Create or edit via the Jira MCP tools once confirmed.

## Ticket format

**Lede: a single bold user story.**
```
**As a <role>, I want <capability>, so that <benefit>.**
```
The `<role>` is always the consumer of the outcome, the end user, the operator, the customer, an agent acting on their behalf, never "a developer" or "an engineer." Even a pure backend or infrastructure change has a consumer: whoever depends on the system behaving correctly. Find that person.

**`## Description`**
Factual and concise. What exists today, what's wrong or missing, and why it needs to change. This is context-setting, not a solution proposal, and it must not contain file paths, function names, schema names, or any other implementation detail. If you catch yourself writing a path like `web/src/pages/...` or a variable name, that detail belongs in the engineer's own investigation once they pick up the ticket, not in the ticket itself.

**`## Requirements`**
A bullet list of independently testable constraints. Use "must" for hard requirements. Each bullet should stand alone, someone should be able to check it off without needing the others for context.

**`## Acceptance Criteria`**
Numbered steps a reviewer could actually execute to verify the work is done. Cover the main happy path, at least one follow-up or contextual case, and a negative or edge case where one is meaningful. Don't pad this with steps that don't verify anything new.

**Style notes:**
- No em-dashes anywhere in ticket text. Use a comma or split into two sentences instead.
- No file paths, directory names, function/variable names, or schema field names. If a technical detail feels essential to include, that's usually a sign it belongs in a comment for the engineer, not in the ticket body, ask the user which they'd prefer.
- Keep the tone plain and factual. Avoid marketing language ("seamlessly", "robust") and avoid restating the obvious.

## Choosing a parent

Before creating a ticket, find candidate parent epics via the Jira MCP tools (search or JQL against the project). If the user already named a parent, confirm it exists and is the right fit rather than trusting the key blindly, projects drift and epics get renamed. If the user is unsure, list the live candidates you found (key, title, status) and ask them to pick, don't default to "no parent" just because it's ambiguous, an unparented ticket is easy to lose track of.

## Choosing a team

Jira "Team" field values are project-specific and change over time, discover them live (via the issue's edit metadata, or by looking at how recent tickets in the same area are tagged) rather than assuming a fixed list. If the codebase has a documented team-ownership convention (for example a table in a root-level project doc), treat that as a hint for which team likely owns the area, not as the literal Jira field value, confirm the two actually match before setting it. If the user is unsure which team should own the ticket, list the teams you found evidence for and ask.

## Creating vs. updating

- **New ticket:** confirm it doesn't already exist (step 3), then follow the full workflow above.
- **Updating an existing ticket:** fetch the current title, description, and any fields you're about to touch first. Show the user a before/after, not just the new text in isolation, so they can see exactly what's changing. Apply the same format rules (user story lede, Description/Requirements/AC structure, no file paths, no em-dashes) when rewriting a description, even if the original didn't follow them.

## What NOT to do

- Don't create a ticket without showing the full draft first and getting explicit confirmation.
- Don't invent a parent epic or team when the user is unsure, ask and list options.
- Don't carry file paths, function names, or other implementation details into the ticket body.
- Don't do a deep codebase investigation as a substitute for asking the user, a quick sanity check is enough; anything more belongs in a separate research step the user explicitly asks for.
- Don't silently drop a detail from an existing ticket when rewriting it (an open question, a caveat, a linked concern), if you're simplifying or restructuring, call out what you removed and why.
