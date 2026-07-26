# Sprint 3 Architecture Freeze

## Goal

Sprint 3 turns the parsed medical JSON from Sprint 2 into structured reasoning output. The parser remains the source of facts; the graph only interprets and summarizes those facts.

## Shared State

The graph should pass one shared state object through every node.

```text
GraphState
{
  analysis_id,
  parsed_json,
  abnormal_findings,
  risk_assessment,
  consultation,
  summary,
  validation,
  retry_count,
  execution_log
}
```

Recommended semantics:

- `parsed_json` is the Sprint 2 output and must not be mutated in place.
- `abnormal_findings` stores factual flags such as LOW, HIGH, or NORMAL.
- `risk_assessment` stores the overall report risk.
- `consultation` stores the recommendation or referral advice.
- `summary` stores the patient-friendly explanation.
- `validation` stores pass/fail state plus any validation messages.
- `retry_count` tracks how many times the Summary Agent has been retried.
- `execution_log` records node execution order for debugging and UI progress.

## Node Responsibilities

### Supervisor

- Orchestrates routing only.
- Does not interpret medical facts.
- Chooses the first node and retry target.

### Anomaly Agent

- Reads `parsed_json`.
- Writes `abnormal_findings`.
- Outputs factual status only.

### Risk Agent

- Reads `abnormal_findings`.
- Writes `risk_assessment`.
- Produces report-level risk only.

### Consult Agent

- Reads `risk_assessment`.
- Writes `consultation`.
- Produces advice only.

### Summary Agent

- Reads `parsed_json`, `abnormal_findings`, `risk_assessment`, and `consultation`.
- Writes `summary`.
- Produces patient-friendly language only.

### Validation Agent

- Reads the graph state and the generated summary.
- Writes `validation`.
- Requests a retry only when the summary is inconsistent with the available facts.

## Routing Rules

### After Anomaly Agent

- If `abnormal_findings` is empty, route directly to `Summary Agent`.
- If abnormalities exist, route to `Risk Agent`.

### After Risk Agent

- If risk is `Moderate` or `High`, route to `Consult Agent`.
- Otherwise route to `Summary Agent`.

### After Validation Agent

- If validation passes, end the graph.
- If validation fails and `retry_count` is below the limit, retry `Summary Agent` only.
- Never restart the whole graph for a summary-only correction.

## Retry Policy

- Retry limit: 2 summary retries.
- Only the failing summary path is retried.
- Validation should not trigger a new parsing pass.

## Execution Sequence

### Normal Report

1. Supervisor
2. Anomaly Agent
3. Summary Agent
4. Validation Agent
5. End

### Abnormal Report

1. Supervisor
2. Anomaly Agent
3. Risk Agent
4. Consult Agent when needed
5. Summary Agent
6. Validation Agent
7. End or retry Summary Agent

## Prompt Files

The prompt layer should be added after the graph contract is stable.

- `anomaly_prompt.py`
- `risk_prompt.py`
- `consult_prompt.py`
- `summary_prompt.py`

These files should describe behavior, not implementation details.

## UI Progress States

The frontend should eventually display stages such as:

- Parsing document
- Detecting abnormalities
- Assessing risk
- Generating consultation advice
- Creating summary
- Validating results

## Non-Goals For Sprint 3

- No change to parsing logic.
- No RAG or conversation memory.
- No diagnosis generation.
- No medical interpretation inside the parser.