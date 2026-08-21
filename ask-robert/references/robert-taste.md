# Robert's taste

Standing design rules, each one traceable to something Robert said on a real call. They are
written to apply to any consumer of an interface, a person or an agent, because "who is this
noise for?" reads the same either way.

José maintains this file by hand. The `ask-robert` skill reads it and never writes to it.

## Hide by setting, not by adding a surface

When a capability applies to some users and not others, the answer is a setting that hides it,
not a new tab, panel, or page for it. Everyone still gets the capability; the ones it is noise
for never see it. Federal-focused users have no use for SLED controls, so the profile and the
opportunity view hide those controls instead of presenting a choice nobody wants to make.

Derive the default from something the product already knows: the onboarding answer, the
entitlement, the profile focus. Present the setting so the user can turn it back on.

## The interface can present an experience the backend does not have

Two separate systems can look like one to the user. It does not matter that "ask me anything"
is an agent with tools and the side panel is a single model call; both can launch from one
place, with the view conditional on what the user is looking at. Merging the backend is a
separate job with its own timeline, and it does not block the merged experience.

## Ask whose need this is

Feedback often arrives as a solution, not a problem: "move this here", "this should not drop
down". Acting on it directly misses the mark. Ask whether the request comes from an actual
user, or whether it is the requester's own workflow presented as a user need. Both are worth
building sometimes, and you cannot tell which one you have until you ask.

## Do not build management before you know the scale

Ten items and fifty items are different products. Reordering, favouriting, grouping, and search
are obvious at fifty and pure noise at ten. Establish the number and the job first. When nobody
can say what the number is, that is the fact to go and find, not a gap to design around.

## Data that never changes does not need a query

A fixed list, zip codes or counties, belongs in the response whole. Paging it forces infinite
scroll, breaks sticky headers, and makes the user wait for something that was never going to
change. The equivalent on a tool surface is a paged tool for a static reference set.

## Two names for one capability confuses people

"Ask me anything" and the AI panel read as two products to a user and to marketing, when they
are one capability with two scopes: global, and scoped to the page you are on. One name, one
entry point, and the scope shown in the interface.
