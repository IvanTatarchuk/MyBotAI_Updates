# Ideas backlog — parked, not now

Ideas explored and worth revisiting, but **not before mcp-guard has a first real
public release and initial user feedback**. Written down here specifically so
they don't compete for attention with mcp-guard while it's mid-flight.

## Cost tracker for AI coding agents

FinOps/observability tool for AI agent spend (Claude Code, Cursor, Codex, etc).
Niche is real but not empty: 4 independent attempts found on GitHub (max 2
stars each), one (`llm-governance-dashboard`) reasonably mature
(LiteLLM proxy + BigQuery + FastAPI). Recurring unsolved problems across all of
them: streaming-response token undercounting, and no correlation between spend
and actual outcome (PR merged / tests passed). Differentiation angle: "cost per
outcome" instead of "cost per token", plus a GitHub Action cost-gate on PRs
(same distribution pattern as mcp-guard's action.yml).

## AI agent tournament / arena platform

Players configure a "loadout" (model + tools + strategy + turn budget, salary-cap
style) and enter it into live, sandboxed coding challenges (real GitHub issues or
held-out benchmark tasks), watched live, objectively scored, leaderboard-ranked.
Validated as a genuine gap: searches for "prediction market for AI agents",
"fantasy league LLM models", "bet on AI models arena" all returned zero GitHub
results.

Two real-money paths discussed, in increasing legal complexity:
1. Virtual currency (no cashout), premium analytics subscription, AI-lab
   sponsorships — ordinary commercial models, no gambling regulation involved.
2. Entry-fee tournaments with real prize pools — needs actual legal
   consultation (skill-contest vs gambling classification varies by
   jurisdiction; Ukraine's KRAIL, US state-by-state fantasy sports law, EU
   per-country rules all apply differently) **before** writing any payment code.

Technical architecture would reuse mcp-guard's sandbox work (network+filesystem
isolation via namespaces) but at a much larger scale (concurrent multi-tenant
execution — likely needs real containers/microVMs, not just `unshare`).

Community/co-building angle if pursued: open-source the scoring engine and
loadout templates, let players author and monetize their own challenges
(revenue share), founder status for early contributors — same OSS-contribution
model as mcp-guard's rules system, applied to game content instead of security
rules.

## Revisit condition

Come back to this file after: mcp-guard v0.2.0 is published to PyPI, has been
posted publicly (HN/Reddit/relevant communities), and has collected real
external feedback (issues, PRs, or usage signal) — not just internal testing.

**Status update (2026-07-06): overridden deliberately.** Decided to start the AI
agent tournament/arena platform now, before the condition above was met — this
is a conscious choice (confirmed when explicitly asked), not an unflagged pivot.
Monetization resolved to cosmetics/skins only, no cashout, no real-money
wagering — sidesteps the gambling-law complexity entirely, so section 2 above
("entry-fee tournaments") is *not* the model being built. mcp-guard is not
abandoned; it's paused mid-flight (v0.2.0 ready, unpublished) while this is
built as a second, parallel project.
