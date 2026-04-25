# Rules: Role Mapping

Rules governing the role-mapping-director, role-mapper-spec, and all /suggest-roles operations.

## Coverage Rules
- EVERY concept from unified-knowledge.json MUST appear in concept_mappings
- Zero-concept-left-behind: no concept may be skipped, even if it seems obscure
- A concept with zero applicable roles is invalid — find at least one or flag for human review

## Role Assignment Rules
- `applicable_roles`: list every role that can meaningfully use the concept in day-to-day work
- `primary_role`: the single role that benefits MOST — not the most popular role, the most relevant one
- Do not assign all roles to every concept — be selective and specific
- A concept about "naming conventions" applies to developer + techlead, not to security or data

## Justification Rules
- Justification MUST be specific: name the concept + the specific action + the specific context
- VALID: "Architect can use Dependency Inversion to decouple OrderService from concrete PaymentGateway implementations"
- INVALID: "Useful for architects" / "Корисно для розробників" / "Can be applied in many situations"
- Generic justifications cause `ROLE-MAP-VALID` gate failure

## Application Ideas Rules
- Format is mandatory: "Використай {{concept}} щоб {{конкретна дія}} у {{конкретному контексті}}"
- VALID: "Використай SRP щоб розбити AuthController на AuthValidator + TokenIssuer у REST API"
- INVALID: "Використай SRP у своєму коді" / "Apply SRP for better design"
- 2–3 ideas per concept per applicable role
- Ideas must be actionable within 1 sprint — not theoretical

## Complexity Rules
- `simple`: practitioner can apply in 1–2 days with existing knowledge, no team coordination needed
- `medium`: requires ~1 week, may need team discussion, tooling, or minor refactoring
- `complex`: requires 1+ month, architectural change, significant rework, or team training
- Complexity is per-concept, not per-role — use the same value across roles for one concept

## Output Format Rules
- role-map MUST be saved in two formats: JSON (machine) + Markdown (human-readable)
- JSON path: `production/role-maps/{book_id}-role-map.json`
- Markdown path: `production/role-maps/{book_id}-role-map.md`
- Markdown format: role sections → concepts table → quick wins highlighted

## Auto-Suggest Rule
- After `/read-book` completes (when `autoSuggestRoles: true`): role-mapping-director runs automatically
- User is presented with `AskUserQuestion` listing roles with ≥1 concept, sorted by score
- Roles with 0 concepts for this book are omitted from the options list
