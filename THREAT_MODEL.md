# Threat model & limitations

`mcp-guard` has two modes with very different guarantees. Being honest about what
each one means matters more for a security tool than for most software, so here it
is plainly.

## `scan` — static heuristic analysis

It reads a tool's `name`, `description`, and `inputSchema` — text — and pattern-matches
that text against a rule list. It never executes the tool, never inspects the server's
actual source code or runtime behavior, and never proves anything.

## `probe` — live execution, sandboxed

`probe` actually launches the server and calls every tool once with synthesized
arguments, inside a sandbox built entirely on Linux namespaces (`unshare` — no
Docker/bubblewrap dependency). Be precise about what that sandbox does and
doesn't cover — every claim below is backed by a test in
`tests/test_sandbox_integration.py` that proves it against a tool making a
genuine attempt, not a simulated one:

- **Isolated: outbound network access.** The probed process gets an empty network
  namespace — no route to anything, including localhost services outside its own
  namespace.
- **Isolated: filesystem writes outside a scratch directory.** The root filesystem
  is bind-mounted back onto itself and remounted read-only inside the sandbox's
  private mount namespace; `/tmp` is a fresh tmpfs the process can write to
  freely. Any write elsewhere fails at the kernel level (`EROFS`).
- **NOT isolated: filesystem reads.** The probed tool sees the real filesystem
  (read-only), so it can still read anything this process could — including
  secrets. Combined with network isolation this blocks *network* exfiltration,
  but **not exfiltration through the tool's own return value**: if a tool reads
  a file and returns its contents as the call result, that result travels back
  over the same stdio pipe `probe` is talking to it on, and will show up in
  `probe`'s own output. `probe` doesn't redact or inspect return values for this.
- **Isolated: separately-mounted filesystems too.** The sandbox walks
  `/proc/self/mountinfo` and bind-remounts every real mountpoint read-only, not
  just `/` — so a second disk, a Docker volume, or a network share mounted
  elsewhere on the host is covered, not only whatever filesystem the target's
  working directory happens to live on. Pseudo-filesystems (`proc`, `sysfs`,
  `devpts`, ...) are skipped since remounting those read-only doesn't add a
  security boundary and can break normal process behavior. Verified against a
  filesystem mounted outside the sandbox specifically to test this
  (`tests/test_sandbox_integration.py`).
- **PID namespace is not a security boundary.** It prevents the probed process
  from seeing/signaling unrelated host processes, but that's isolation of
  visibility, not a defense against filesystem/network abuse (which the other
  two namespaces above actually provide).
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

## Operational note: `npx`-launched servers

Both `scan --stdio` and `probe --stdio` have a `--timeout` (default 30s) precisely
because launching a server via `npx -y <package>` — a common pattern in MCP server
documentation — can hang the initialize handshake indefinitely rather than
erroring, for reasons specific to how npx manages its child process. This isn't a
security property, just an interop rough edge: if you hit it, resolve the command
to the actual interpreter and entry point (e.g. `node .../dist/index.js ...`)
instead of going through `npx`.

## Roadmap toward reducing these gaps

The remaining gap for `probe` is return-value exfiltration (a tool can still hand
back the contents of anything it can read, over the same stdio channel `probe`
talks to it on) — there's no way to close that without restricting what the tool
can read in the first place, which would defeat the point of observing real
behavior. Don't treat `probe` as a guarantee against a sophisticated,
deliberately adversarial server; it's a large step up from static analysis, not
a full sandbox audit.
