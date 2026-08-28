# MCP Cheat Sheet — Fast Rules & Hints

Model Context Protocol · current spec: **2026-07-28** · Python-oriented training notes (concepts apply to all SDKs) · optimized for quick design/review

**Start here:** [Decision Guide](#decision-guide) → [Quick Cheat Sheet](#quick-cheat-sheet) → [Security & Production](#security--production-review-checklist) → [Anti-patterns](#anti-patterns)

Priority: **MUST** = do this / **SHOULD** = strongly preferred / **MAY** = situational. Kind: **Spec** = protocol/release claim · **Practice** = design guidance (not a protocol requirement). **MUST + Practice** means a training/design rule, not a protocol MUST.

**MRTR** = Multi Round-Trip Request: server returns `resultType: "input_required"`; client retries with answers (or use host approval when that is enough).

---

## Decision Guide

| Question | If YES | If NO | Example | Fast rule |
|----------|--------|-------|---------|-----------|
| Should the model decide to perform an action? | Use a **TOOL** | Continue | `search_orders()` | Model acts → Tool |
| Is it data the application can load as context? | Use a **RESOURCE** | Continue | `config://app` | App reads → Resource |
| Is it a reusable interaction the user explicitly chooses? | Use a **PROMPT** | Continue | `/review-code` | User chooses → Prompt |
| Does the operation cause an external side effect? | Add idempotency + authorization + audit | Normal read safeguards | `send_email()` | Retries must be safe |
| Is the operation destructive/irreversible? | Require MRTR `input_required` and/or host approval (MUST Practice) | Normal mutation policy | `delete_project()` | Danger → confirm |
| Can the result be very large? | Return summary/IDs, add `get_details()` | Return structured result | `search_docs()` → doc IDs | Progressive disclosure |
| Can it take minutes? | Return task/job handle (`io.modelcontextprotocol/tasks`) | Normal tool call | `run_analysis()` → `task_id` | Long job → Task |
| Does the backend already know a constraint? | Put it in schema/server validation | Document semantics | enum, min/max, pattern | Schema > prompt |
| Does a parameter represent caller identity/permission? | Remove it; derive from auth context | Keep if it's domain data | Don't accept `is_admin` | Identity comes from auth |
| Are you exposing an internal endpoint almost unchanged? | Reconsider and make it semantic | Likely OK | `POST /v1/foo` → `create_alert()` | MCP ≠ REST mirror |
| Do you have dozens/hundreds of tools? | Group/discover/cache; reduce surface | Keep simple | `flight.*`, `alerts.*` | Small catalog wins |

---

## Quick Cheat Sheet

| Area | Rule / Hint | Use when | Avoid | Priority | Kind | Source |
|------|-------------|----------|-------|----------|------|--------|
| Primitive | Tool = model decides to perform an action | Search, create, update, calculate, send | Using tools just to dump static/reference context | MUST | Practice | [Python SDK](https://py.sdk.modelcontextprotocol.io/) |
| Primitive | Resource = application/client loads data as context | Configs, records, docs, catalogs, reference data | Turning every read-only datum into a tool | MUST | Practice | [Resources docs](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/servers/resources.md) |
| Primitive | Prompt = user-selectable reusable message template | Slash commands, guided workflows, repeatable interactions | Treating prompts as hidden autonomous agent logic | MUST | Practice | [Prompts docs](https://py.sdk.modelcontextprotocol.io/servers/prompts/) |
| Tool design | Expose semantic operations, not raw HTTP/SQL | `search_flights()`, `create_alert()` | `execute_request(url,...)`, `run_sql(sql)` | MUST | Practice | — |
| Tool design | Keep each tool narrow and obvious | One understandable responsibility | Mega-tools with many unrelated modes | MUST | Practice | — |
| Tool design | Descriptions are part of the agent API | Tell the model when to use / not use a tool | Descriptions like "Searches stuff" | SHOULD | Practice | [Python SDK](https://py.sdk.modelcontextprotocol.io/) |
| Schema | Encode known constraints in JSON Schema | Enums, ranges, formats, required fields, alternatives | Relying on prompt text to enforce backend constraints | MUST | Practice | [spec](https://modelcontextprotocol.io/specification/2026-07-28) |
| Schema | Prefer the smallest useful input surface | Expose only parameters the agent actually needs | Mirroring every internal API parameter | SHOULD | Practice | — |
| Tool design | Set tool annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) — hints for hosts, not AuthZ | Host policy, routing, confirmation UX | Leaving every tool unmarked; treating hints as permission checks | SHOULD | Practice | [spec](https://modelcontextprotocol.io/specification/2026-07-28) |
| Output | Return concise structured results | Normalized records, IDs, summaries | Multi-MB raw payloads | MUST | Practice | — |
| Output | Use follow-up detail tools for large objects | `search()` → ids/summaries → `get_details(id)` | Returning everything in one call | MAY | Practice | — |
| State | Keep application state explicit with IDs/handles | `search_id`, `task_id`, `job_id` | Hidden sticky-session state | SHOULD | Practice | — |
| Protocol | Design new servers around stateless MCP core | Horizontally scaled HTTP deployments | Assuming old mandatory initialize/session flow | SHOULD | Spec | [release](https://blog.modelcontextprotocol.io/posts/2026-07-28/) · [spec](https://modelcontextprotocol.io/specification/2026-07-28) |
| Protocol | Clients MAY call `server/discover` for up-front capabilities | Capability probing before first tool use | Treating discover as mandatory | MAY | Spec | [release](https://blog.modelcontextprotocol.io/posts/2026-07-28/) · [spec](https://modelcontextprotocol.io/specification/2026-07-28) |
| Protocol | Spec does not require initialize/session affinity | Stateless / horizontally scaled deployments | Building sticky sessions around initialize | SHOULD | Spec | [release](https://blog.modelcontextprotocol.io/posts/2026-07-28/) · [spec](https://modelcontextprotocol.io/specification/2026-07-28) |
| Protocol | List responses may carry `ttlMs` / `cacheScope` | Caching `tools/list`, `resources/list`, etc. | Refetching full catalogs on every reconnect | SHOULD | Spec | [release](https://blog.modelcontextprotocol.io/posts/2026-07-28/) · [spec](https://modelcontextprotocol.io/specification/2026-07-28) |
| Transport | Prefer stdio for local; Streamable HTTP for remote | Editor-local servers vs production services | Building new systems around legacy SSE transport | SHOULD | Practice | [release](https://blog.modelcontextprotocol.io/posts/2026-07-28/) · [spec](https://modelcontextprotocol.io/specification/2026-07-28) |
| Transport | Streamable HTTP: send `Mcp-Method` / `Mcp-Name` headers | Gateways, routing, rate limits, WAF | Parsing JSON bodies just to route | SHOULD | Spec | [release](https://blog.modelcontextprotocol.io/posts/2026-07-28/) · [spec](https://modelcontextprotocol.io/specification/2026-07-28) |
| Transport | stdio: never write logs to stdout | Local subprocess servers | `print()` / `console.log()` on the protocol stream | MUST | Spec | [Build server](https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server) |
| Security | Treat the model as an untrusted caller | Every tool invocation | Trusting model intent or supplied identity | MUST | Practice | — |
| Security | Treat tool names/descriptions/results as untrusted text | Avoid prompt injection / tool poisoning | Secrets or instructions hidden in descriptions; unsanitized URL/path args | MUST | Practice | — |
| Security | Authorization is server-side | Tenant/user/object permissions | Passing `user_id`/`admin=true` and trusting it | MUST | Practice | — |
| Security | Use least privilege | Scopes, DB roles, API tokens | Prod admin credentials behind MCP | MUST | Practice | — |
| Security | Separate read/write/destructive operations | Policy, approvals, auditing | One tool that can both inspect and mutate anything | SHOULD | Practice | — |
| Auth | Prefer CIMD; DCR is deprecated for new work | Remote OAuth clients | Treating Dynamic Client Registration as the long-term path | SHOULD | Spec | [release](https://blog.modelcontextprotocol.io/posts/2026-07-28/) · [spec](https://modelcontextprotocol.io/specification/2026-07-28) |
| Reliability | Make side-effecting tools idempotent | Bookings, tickets, messages, payments | Duplicates after timeout/retry | MUST | Practice | — |
| Reliability | Errors should tell the agent how to recover | Validation and downstream failures | `500 Something went wrong` | SHOULD | Practice | [Python SDK](https://py.sdk.modelcontextprotocol.io/) |
| Long jobs | Use `io.modelcontextprotocol/tasks` handles for long-running work | Deployments, analysis, generation jobs | Holding one call open for many minutes | SHOULD | Spec | [release](https://blog.modelcontextprotocol.io/posts/2026-07-28/) · [spec](https://modelcontextprotocol.io/specification/2026-07-28) |
| Confirmation | Require MRTR (`resultType: input_required`) and/or host approval for dangerous actions | Delete, payment, irreversible actions | Hoping the LLM remembers to ask | MUST | Practice | [release](https://blog.modelcontextprotocol.io/posts/2026-07-28/) · [spec](https://modelcontextprotocol.io/specification/2026-07-28) |
| Observability | Log tool, actor, duration, outcome, request/trace IDs | Production MCP servers | Logging secrets/full sensitive payloads | SHOULD | Practice | — |
| Scale | Keep tool catalogs small and discoverable | Larger servers/gateways | 150 undifferentiated tools loaded at once | SHOULD | Practice | — |
| Architecture | MCP should be an agent-facing facade over services | Existing APIs/databases | 1:1 exposing every internal endpoint | SHOULD | Practice | — |
| Testing | Test schemas + behavior, not only handler functions | Tool choice, invalid args, permissions, retries | Only unit-testing underlying service methods | SHOULD | Practice | [Get started](https://py.sdk.modelcontextprotocol.io/get-started/) |

---

## Security & Production Review Checklist

| Category | Check | Why | Bad smell | Target | Done? |
|----------|-------|-----|-----------|--------|-------|
| Auth | Remote server uses standard OAuth/OIDC where appropriate (CIMD preferred; DCR deprecated) | Avoid custom auth mistakes | Custom bearer token scheme with no lifecycle | Required | ☐ |
| AuthZ | Every sensitive action re-checks permissions server-side | Model input is untrusted | Tool accepts `user_id`/admin flag | Required | ☐ |
| Least privilege | MCP credentials have minimum scopes/roles | Limit blast radius | Admin DB/API token | Required | ☐ |
| Tenancy | Tenant isolation enforced below MCP layer | Prevent cross-tenant access | Tenant selected only from tool arg | Required | ☐ |
| Validation | Server validates all arguments | Schemas help but are not a trust boundary | Assumes model always conforms | Required | ☐ |
| Injection | Tool descriptions/results carry no secrets or hidden instructions; sanitize URL/path args | Tool text reaches the model | “Tool poisoning” via description; SSRF-style fetch tools | Required | ☐ |
| Writes | Read/write/destructive tools are clearly separated (annotations are hints, not AuthZ) | Simpler policy + review | Generic `mutate()` tool; all tools unmarked | Recommended | ☐ |
| Approval | Destructive/high-cost actions use MRTR `input_required` and/or host approval | Human control for risky actions | Immediate delete/pay/send | Required for risky ops | ☐ |
| Idempotency | External side effects support duplicate-safe retries | Agents/networks retry | Two bookings/messages after timeout | Required | ☐ |
| Timeouts | Downstream timeouts and cancellation are defined | Bound latency/resources | Calls hang indefinitely | Required | ☐ |
| Long jobs | Long work returns a task handle (`io.modelcontextprotocol/tasks`) | Scalable execution | 10-minute open request | Recommended | ☐ |
| Rate limits | Limits by user/client/tool as needed | Protect services/cost | Unlimited expensive tool | Recommended | ☐ |
| Output limits | Rows/bytes/results capped | Protect context and costs | Returns entire DB table | Required | ☐ |
| Secrets | Secrets never appear in tool output/logs | Avoid model/context leakage | Debug response includes token | Required | ☐ |
| Logging | Audit actor/tool/outcome without dumping sensitive args | Forensics + compliance | Full raw request logging | Required | ☐ |
| stdio | Local servers log to stderr only (never stdout) | stdout is the JSON-RPC stream | `print` / `console.log` on stdio | Required for stdio | ☐ |
| Tracing | Request/trace IDs propagate to downstream services | Debug distributed calls | MCP is a tracing black hole | Recommended | ☐ |
| Errors | Errors are structured and recoverable | Agent can correct itself | Opaque 500 | Recommended | ☐ |
| Deployment | Remote server can run statelessly/horizontally | Scale and failover | Sticky MCP protocol session required | Recommended | ☐ |
| Versioning | Tool contracts change compatibly or are versioned | Agent/client stability | Rename/remove args silently | Required | ☐ |
| Testing | Permission/validation/retry/timeout tests exist | Production behavior matters | Only happy-path tests | Required | ☐ |

---

## Anti-patterns

| Anti-pattern | Why it hurts | Better pattern | Severity |
|--------------|--------------|----------------|----------|
| `execute_request(url, method, headers, body)` | Gives agent a low-level generic escape hatch | Expose semantic domain tools | Critical |
| `run_sql(sql)` | Huge security and correctness surface | Read-only semantic queries/views | Critical |
| One tool with 40+ optional parameters | Hard tool choice and argument generation | Split by intent; expose essential params | High |
| Returning raw upstream payloads | Context bloat and unstable contracts | Normalize + summarize | High |
| Passing `user_id` / `is_admin` in arguments | Caller can spoof authorization context | Derive identity/scopes from authenticated context | Critical |
| One generic `mutate()` tool | Hard to authorize/audit and easy to misuse | Explicit create/update/delete tools | High |
| Hidden server session state | Breaks scaling/retries/routing | Explicit `search_id`/`task_id`/etc. | High |
| Long synchronous tool calls | Timeouts and wasted connections | Task/job handles (`io.modelcontextprotocol/tasks`) | High |
| No idempotency on writes | Retry can duplicate real-world effects | Idempotency key / operation ID | Critical |
| Opaque errors | Agent can't self-correct | Structured code + corrective message | Medium |
| Logging all arguments | Sensitive-data leakage | Selective/redacted audit logging | Critical |
| Writing logs to stdout on stdio servers | Corrupts JSON-RPC and breaks the host connection | Log to stderr / a logging library | Critical |
| REST endpoint = MCP tool 1:1 | Too many tools and wrong abstraction | Agent-facing facade | High |
| Trusting schema as authorization | Validation is not permission checking | Schema + server authZ | Critical |
| Old SSE-first architecture for new build | Legacy/deprecated direction | Streamable HTTP for remote servers | Medium |
| Hoping the model asks before destructive actions | Approvals are skipped under pressure | MRTR `input_required` / host approval | Critical |
| Secrets or instructions in tool descriptions | Prompt injection / tool poisoning | Keep descriptions operational; validate side-effecting string args | Critical |

---

## Official MCP Sources & Cookbook Links

| Resource | What to use it for | URL | Notes |
|----------|--------------------|-----|-------|
| 2026-07-28 specification release | Protocol changes, stateless core, auth, caching, tasks, MRTR | https://blog.modelcontextprotocol.io/posts/2026-07-28/ | Best current overview of major spec changes |
| Official MCP docs | Protocol concepts/specification | https://modelcontextprotocol.io/ | Primary documentation hub |
| 2026-07-28 specification | Normative protocol requirements | https://modelcontextprotocol.io/specification/2026-07-28 | Prefer this over the blog when citing Spec rows |
| Build a server | First server + stdio logging rules | https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server | Language tutorials |
| MCP Inspector | Test tools/resources without an LLM | https://github.com/modelcontextprotocol/inspector | Preferred local debug loop |
| Python SDK v2 | Python server/client implementation | https://py.sdk.modelcontextprotocol.io/ | Current stable Python SDK line |
| TypeScript SDK v2 | TypeScript/JS server/client implementation | https://github.com/modelcontextprotocol/typescript-sdk | Tier 1; split `@modelcontextprotocol/server` + `client` |
| Python SDK get started | Runnable tutorial + Inspector workflow | https://py.sdk.modelcontextprotocol.io/get-started/ | Examples are tested in SDK repository |
| Resources docs | Resource design and URI templates | https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/servers/resources.md | Explains Tool vs Resource split |
| Prompts docs | User-selected prompt templates | https://py.sdk.modelcontextprotocol.io/servers/prompts/ | Explains user-controlled prompts |
| Official servers repo | Reference/example MCP servers | https://github.com/modelcontextprotocol/servers | Useful as examples; review security before production use |
| 2026 release candidate deep dive | Architecture rationale and migrations | https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/ | Detailed rationale for stateless protocol, extensions, JSON Schema |
