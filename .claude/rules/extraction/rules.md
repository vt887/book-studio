# Rules: Extraction

Rules governing the extractor-spec and the structure of extraction.json.

## Concept Extraction Rules
- A concept is a reusable idea the author presents as a principle, pattern, or technique
- Concepts must have: id, name, definition, source_quote, chapter, confidence, type
- Concept types: `principle` | `pattern` | `technique` | `anti-pattern` | `mental-model`
- Anti-patterns: labeled with type=`anti-pattern`, never presented positively
- Related concepts: listed by concept ID, not by name, to enable linking

## Quote Rules
- Quotes must be verbatim — character-for-character exact
- Quotes must have speaker attribution and chapter reference
- Paraphrases go in `facts`, not `quotes`

## Confidence Scoring Rules
- 0.95–1.0: Explicitly stated, unambiguous, directly quoted
- 0.85–0.94: Clearly implied, strong contextual evidence
- 0.80–0.84: Reasonably inferred, moderate evidence
- < 0.80: Do not include in main output — move to `needs_review`
- When in doubt: lower the score, never inflate it

## Deduplication Rules
- Two concepts are duplicates if their names differ but definitions are >90% semantically equivalent
- On duplicate: keep the one with higher confidence; merge source_quotes from both
- Cross-chapter duplicates: merge with chapter list, not just one chapter

## Entity Rules
- Entity types: `person` | `org` | `system` | `book` | `concept`
- Entities are referenced objects, not standalone concepts
- Do not create concept entries for entities — keep them in the `entities` list

## Output Completeness Rules
- Every chunk must be processed — no skipping due to length or difficulty
- `needs_review` list must be shown to the user after extraction completes
- Final extraction.json must pass `EXTRACT-QUALITY` gate before downstream use
