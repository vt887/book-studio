# Rules: Application

Rules governing all /apply-as-* skills, /auto-apply, and role-specific specialist output.

## Citation Rules (CRITICAL)
- Every application output MUST cite at least one concept from the book
- Inline citation format: `[concept: {concept_name}]`
- Cited concepts must exist in the book's unified-knowledge.json — no invented citations
- Citation must appear near the point where the concept drives a decision, not only in the header

## Output Quality Rules
- Output must be actionable: it must contain code, config, diagram, plan, or checklist — not prose description
- No pseudocode — write real, runnable code with correct syntax
- No placeholder comments like `# TODO: implement` or `# add logic here`
- Every output must have the standard artifact header:
  ```
  # {Title}
  - **Book:** {title} by {author}
  - **Role:** {role}
  - **Concept:** {concept_name}
  - **Generated:** {ISO8601}
  - **Gate:** APPLY-VALID PASSED ({score})
  ```

## Role-Specific Output Formats
| Role | Required Output Format |
|------|----------------------|
| developer | working code (correct language), before/after if refactoring |
| architect | complete ADR or trade-off table, no TBD sections |
| tester | runnable test code in user's framework, Given/When/Then |
| devops | valid YAML/HCL configs, include CI provider version pins |
| security | STRIDE table or itemized checklist with severity ratings |
| data | valid SQL or Python, include migration rollback |
| performance | p50/p95/p99 benchmark script, optimization plan with baseline |
| observability | valid YAML/JSON configs, SLO with burn rate alerts |
| techlead | checklist with pass/fail criteria, not aspirational bullets |
| legacy | migration plan with phases, characterization tests, rollback |
| platform | Backstage YAML or golden path doc, parameterized templates |

## Gate Rules
- `APPLY-VALID` gate (threshold: 0.85) runs on every output before saving
- Gate failures trigger one retry with the specific failures passed to the specialist
- Second gate failure: surface BLOCKED status with itemized failures — do not save partial output

## Source Integrity Rules
- Concepts applied must come from the selected book's role-map
- If user requests a concept not in the role-map: ask to run `/suggest-roles` first, or confirm manual override
- Anti-pattern outputs must clearly label them as anti-patterns — never present as best practice

## Save Rules
- Save path: `production/applications/{role}-output/{task_id}.md`
- task_id format: `{book_id}_{role}_{concept_slug}_{YYYYMMDD-HHMMSS}`
- Never overwrite existing artifacts — always use unique timestamps
