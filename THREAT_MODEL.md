# Threat model & limitations

`mcp-guard` has two modes with very different guarantees. Being honest about what
each one means matters more for a security tool than for most software, so here it
is plainly.

## `scan` — static heuristic analysis

It reads a tool's `name`, `description`, and `inputSchema` — text — and pattern-matches
that text against a rule list. It never executes the tool, never inspects the server's
actual source code or runtime behavior, and never proves anything.

## `probe` — live execution, network-isolated only

`probe` actually launches the server and calls every tool once with synthesized
arguments, inside a sandbox built on Linux network namespaces (`unshare --net`).
Be precise about what that sandbox does and doesn't cover:

- **Isolated: outbound network access.** The probed process gets an empty network
  namespace — no route to anything, including localhost services outside its own
  namespace. This is real and verified (`tests/test_sandbox_integration.py` proves
  it against a tool that makes a genuine connection attempt), not a claim.
- **NOT isolated: the filesystem.** A probed tool can read and write real files with
  the same permissions this process has. If you probe a server you don't trust, and
  one of its tools deletes files or writes somewhere unexpected, `probe` will not
  stop it — it will happen for real. This is the single biggest caveat: don't run
  `probe` against a server you're not willing to have full filesystem access to your
  machine.
- **NOT isolated: PID namespace is separate but not a security boundary** — it
  prevents the probed process from seeing/signaling unrelated host processes, but
  offers no protection against filesystem or resource abuse.
- **Arguments are synthesized, not adversarial.** Placeholder values (empty-ish
  strings, zeros, `false`) are enough to exercise a tool's real code path, but
  `probe` makes no attempt at fuzzing, injection payloads, or adversarial inputs —
  it's checking "does this tool's actual behavior match a benign call," not
  penetration-testing the server.
- **One call per tool, no state.** Multi-step exploits, or behavior that only
  triggers on the second call or a specific argument combination, won't be observed.

## What this catches

- MCP servers that are honest (or careless) in their tool descriptions about what
  they do — most are, because the description is also what the calling LLM reads to
  decide when to use the tool, so vague or dishonest descriptions make the tool
  useless in practice.
- Obviously overbroad capability grants stated in plain language ("run any shell
  command", "read any file").
- The class of prompt-injection cue that shows up in the description text itself.

## What this does NOT catch

- **A tool that says "gets the weather" but actually exfiltrates data.** Nothing in
  a static description scan can detect behavior that isn't described. This is the
  single most important limitation — a clean `mcp-guard` report is not an
  attestation that a server is safe, only that its *stated* capabilities don't match
  known-risky phrasing.
- **Server-side logic bugs** (e.g. a path-traversal bug in a tool that's supposed to
  be scoped to one directory). That requires actual code review or dynamic testing,
  not description analysis.
- **Prompt injection delivered through tool *output*** at call time (e.g. a
  `fetch_url` tool returning a page that contains injected instructions). This is a
  runtime concern that a pre-connection scan structurally cannot see.
- **Rule evasion.** The rules are regexes over natural-language phrasing. A server
  author (or an adversary distributing a malicious server) who wants to dodge a rule
  can trivially reword the description. This is a triage tool for the common,
  unsophisticated case — not a defense against an adversary who knows the rule set.

## How to use findings

Treat every finding as "this needs a human to look closer," not "this is malicious"
or (absence of findings) "this is safe." `mcp-guard` is meant to move a large pile of
unaudited MCP servers into a smaller, prioritized pile — it is not a substitute for
actually reading the code of anything you give real permissions to.

## Roadmap toward reducing these gaps

The remaining structural gap is filesystem isolation for `probe` — tracked in the
README roadmap as a bubblewrap/Docker backend that would confine writes to a
scratch directory and make the real filesystem read-only. Until that lands, treat
`probe` as: safe from network exfiltration, but not safe from a malicious or buggy
tool that damages the local filesystem.
