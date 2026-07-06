# Threat model & limitations

`mcp-guard` is a **static heuristic scanner**. Being honest about what that means
matters more for a security tool than for most software, so here it is plainly.

## What it actually does

It reads a tool's `name`, `description`, and `inputSchema` — text — and pattern-matches
that text against a rule list. It never executes the tool, never inspects the server's
actual source code or runtime behavior, and never proves anything.

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

The biggest structural gap (static description vs. actual behavior) is why "live
sandboxed execution probing" is the top roadmap item in the README: actually invoking
each tool with representative inputs inside an isolated sandbox and observing what it
does (syscalls, network destinations, filesystem access) would catch the
description-doesn't-match-behavior case. That's a meaningfully larger undertaking
(needs a real sandbox — containers/gVisor/seccomp — plus a way to synthesize safe
probe inputs from a tool's schema) and hasn't been built yet.
