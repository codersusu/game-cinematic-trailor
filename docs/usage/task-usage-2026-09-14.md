# Cinematic task: recorded token usage and development time

The main assistant and nine development agents used **492,822,212 tokens** in the recorded work through the V13 publication and cleanup. Of the **491,378,442 input tokens**, **481,773,696 were cached** (98.05%). Output was **1,443,770 tokens**.

Including the task's automatic approval-review threads, the broader recorded total is **555,032,779 tokens**. These are local telemetry totals, not an invoice or a measurement of subscription quota consumed.

This fixed snapshot ends immediately before the accounting request on **14 September 2026 at 23:18:44 CEST / 21:18:44 UTC**. It excludes the work to prepare and publish this report. The preceding development/upload/cleanup turn finished on **13 September at 19:21:59 CEST**.

## Token breakdown

“Cached” means cached input tokens, interpreting the request's “catch tokens.” Cached input is already included in input. Reasoning output is already included in output. Neither should be added again to the total.

| Scope | Input, including cached | Cached input | Uncached input | Output | Total input + output |
|---|---:|---:|---:|---:|---:|
| Main assistant | 304,066,947 | 300,099,200 | 3,967,747 | 787,201 | 304,854,148 |
| Nine development agents | 187,311,495 | 181,674,496 | 5,636,999 | 656,569 | 187,968,064 |
| **Development combined** | **491,378,442** | **481,773,696** | **9,604,746** | **1,443,770** | **492,822,212** |
| Automatic approval reviews, separately | 62,134,026 | 52,004,352 | 10,129,674 | 76,541 | 62,210,567 |
| **All recorded task usage** | **553,512,468** | **533,778,048** | **19,734,420** | **1,520,311** | **555,032,779** |

Development output includes **527,378 reasoning tokens**; all recorded output includes **558,062 reasoning tokens**. The local `cache_write_input_tokens` field reports zero throughout; this reports the field as recorded and does not establish that the service performed no cache writes.

These large input totals count repeated context across thousands of model responses: instructions, conversation history and tool results can be processed again on each response. They are not the size of the finished screenplay or code. Cached input is a subset of input, consistent with [OpenAI's prompt-caching usage documentation](https://developers.openai.com/api/docs/guides/prompt-caching).

## Elapsed and active time

| Measurement | Recorded duration |
|---|---:|
| Conversation start → this accounting request | **4 days, 2 hours, 23 minutes, 8 seconds** |
| Conversation start → completed V13 publication/cleanup | **2 days, 22 hours, 26 minutes, 23 seconds** |
| Active development wall time, main + agents with overlap removed | **28 hours, 51 minutes, 15 seconds**, approximately |
| Main assistant active time alone | 28 hours, 50 minutes, 53 seconds |
| Sum of main + individual agent active times, including parallel overlap | 35 hours, 12 minutes, 24 seconds |

The first recorded main turn began **10 September 2026, 20:55:36 CEST / 18:55:36 UTC**. “Active development” includes research, design discussions, coding, downloads, rendering, tool waits, verification, uploads and cleanup while assistant turns were running. It excludes idle gaps between turns. Parallel agents are counted once in active wall time; summing their durations is a different measure.

One main turn on 12 September lacks its completion event. Its last recorded response provides the conservative endpoint; the next turn begins **2 minutes 38 seconds** later. Consequently the reconstructed active wall time is roughly **28h 51m–28h 54m**. The logs do not provide a reliable separate total for pure coding, model compute time, or all background Blender runtime. The active figure must not be described as 29 hours of uninterrupted coding.

## Accounting method and checks

The [machine-readable report](task-usage-2026-09-14.json) includes each agent's totals, timing intervals, coverage gaps and a digest of its retained usage evidence. The [audit script](../../scripts/audit_task_usage.py) reads the local Codex state database in read-only mode, follows recorded parent relationships within this workspace, and exports aggregate metadata only.

- Scope: the main task, nine development agents and 28 automatic approval-review threads. This includes the earlier walking-diagnosis agent, which is no longer in the currently displayed agent list.
- Use durable `token_usage_record.thread_token_usage` once per owning thread after checking monotonicity. Do not add repeated cumulative snapshots or use the app's account-wide remaining-limit percentages.
- Independently sum `usage` for distinct `response_id` values. All **4,109 retained development responses** reconcile exactly with their thread totals. Across development and approval reviews there are **4,541 retained unique responses**, with no duplicated response IDs.
- Five approval-review logs have compacted histories: their durable cumulative totals contain **22,052,991 tokens** from earlier responses whose individual records are no longer present. The JSON identifies these cumulative-only portions. This is why approval-review overhead is reported separately rather than claiming every response remains independently auditable.
- Some `event_msg.token_count` summaries and database `tokens_used` values disagree with lifetime totals after context changes. They are not the source for this report.
- Count only turn IDs belonging to each thread's own usage records. Forked parent-history events do not become extra child development time. Merge overlapping main/agent intervals; use recorded durations, with one explicitly noted incomplete interval.
- No raw conversations, tool outputs, credentials, response identifiers or local user paths are published. A digest is evidence for later local comparison, not independent public verification of private logs.

This report does not measure Meshy/ElevenLabs service usage, hidden or unrecorded service work, financial charges, or the current accounting turn. It records what the available task telemetry supports.

To reproduce locally, supply the root task ID from your own Codex session metadata; raw session data is intentionally absent from Git:

```sh
python3 scripts/audit_task_usage.py \
  --root-thread YOUR_LOCAL_ROOT_TASK_ID \
  --cutoff 2026-09-14T21:18:44.973Z \
  --output task-usage-recomputed.json
```

The report describes the project through commit `b977ef87fa5a744a81e470034c5752035d32a7ff`. The V13 film and all previously published source assets remain unchanged.
