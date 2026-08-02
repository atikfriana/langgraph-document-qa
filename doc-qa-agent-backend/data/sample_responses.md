# Sample Responses (Expected Behavior)

This file documents the *expected* answer content and expected `tool_used`
flag for each question in `sample_questions.md`, based on the ground truth
in `sample_document.pdf`. Use it to manually verify a running deployment, or
as the basis for an automated eval script.

Note: exact wording from the LLM will vary — what matters is factual
correctness and the `tool_used` value, not verbatim phrasing.

## Group A — Answerable from the document

| # | Question | Expected key facts | Expected `tool_used` |
|---|---|---|---|
| 1 | Founded / headquarters | Founded 2018, headquartered in Denver, Colorado | `false` |
| 2 | Battery life | 10 hours continuous operation | `false` |
| 3 | Max payload | 25 kilograms | `false` |
| 4 | Recharge time | Approximately 90 minutes | `false` |
| 5 | Obstacle-avoidance sensors | LIDAR, depth cameras, ultrasonic proximity sensors | `false` |
| 6 | Monthly cost | Starting at $1,450 per robot per month | `false` |
| 7 | Safety certification | ANSI/RIA R15.08 | `false` |
| 8 | Technician response time | 8 business hours for critical hardware failures | `false` |
| 9 | Follow-up: unloaded weight | 48 kilograms (must correctly resolve "it" to Aurora M1 from prior turn) | `false` |
| 10 | Follow-up: Austin office | Secondary engineering office (must recall Denver HQ context from prior turn) | `false` |

## Group B — Requires external/current information

| # | Question | Why the tool is required | Expected `tool_used` |
|---|---|---|---|
| 1 | Current stock price | Document contains no financial/market data; Aurora Robotics is a fictional private company in this sample, so a real search will find no matching public stock — the agent should say it could not find this information rather than fabricate a price | `true` |
| 2 | Recent new product announcements | Document is static and undated; "last month" requires current information | `true` |
| 3 | Current competitors | Document contains no competitor information at all | `true` |
| 4 | Today's date | Never contained in a static source document | `true` |
| 5 | Latest regulatory news | Explicitly time-sensitive, external to the document | `true` |

## Group C — Meta / conversational

| # | Question | Expected behavior | Expected `tool_used` |
|---|---|---|---|
| 1 | Summarize conversation so far | Answered from `messages` history alone, no retrieval-dependent facts needed beyond what was already discussed | `false` |
| 2 | Rephrase last answer | Answered from conversation history, no new retrieval or tool call needed | `false` |

## Notes for evaluators

- A `tool_used: true` result on a Group A or Group C question is a **false
  positive** — the router is over-calling the tool when the document already
  had the answer.
- A `tool_used: false` result on a Group B question is a **false negative**
  — the router is under-calling the tool and the model is likely to either
  hallucinate an answer or (correctly, but non-ideally) admit it doesn't
  know when it could have looked it up.
- Because Aurora Robotics / Aurora M1 are fictional entities invented for
  this sample document, Group B web-search results will legitimately come
  back empty or irrelevant — that is expected and correct; the pass
  condition for Group B is that the **tool was called**, not that a
  real-world answer was found.
