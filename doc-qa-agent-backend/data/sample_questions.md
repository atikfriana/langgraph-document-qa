# Sample Questions

These questions are designed against `sample_document.pdf` (Aurora Robotics /
Aurora M1 product overview) and are split into two groups: questions the
document can answer directly (tool should **not** be called), and questions
that require information outside the document (tool **should** be called).

See `sample_responses.md` for expected answer content and expected
`tool_used` value for each.

## Group A — Answerable from the document (tool should NOT be called)

1. When was Aurora Robotics founded, and where is it headquartered?
2. What is the battery life of the Aurora M1?
3. What is the maximum payload capacity of the Aurora M1?
4. How long does the Aurora M1 take to fully recharge?
5. What sensors does the Aurora M1 use for obstacle avoidance?
6. How much does the Aurora M1 cost per month?
7. What safety standard is the Aurora M1 certified to?
8. What is the guaranteed on-site technician response time for critical
   hardware failures?
9. Follow-up (multi-turn): After asking Q2, ask "And how heavy is it when
   unloaded?" — tests conversation memory within the same session.
10. Follow-up (multi-turn): After asking Q1, ask "What about the Austin
    office — what's that for?" — tests memory + document grounding together.

## Group B — Requires external/current information (tool SHOULD be called)

1. What is Aurora Robotics' current stock price?
2. Has Aurora Robotics announced any new products in the last month?
3. Who are Aurora Robotics' main competitors in the warehouse robotics
   market today?
4. What is today's date?
5. What is the latest news about warehouse automation regulations in the
   United States?

## Group C — Meta / conversational (tool should NOT be called)

1. Can you summarize what we've talked about so far?
2. Can you rephrase your last answer more simply?
