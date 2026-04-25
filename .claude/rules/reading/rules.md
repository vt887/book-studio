# Rules: Reading

Rules governing the `/read-book` pipeline and all reading-director operations.

## Chunking Rules
- Chunk size: 2000–4000 tokens per chunk
- Overlap between adjacent chunks: 200 tokens
- Each chunk must carry metadata: `book_id`, `chapter`, `section`, `chunk_index`, `page_range`
- Never split a sentence across a chunk boundary
- Chapter boundaries always start a new chunk

## Extraction Rules
- Extract ONLY content present in the source text — zero hallucination tolerance
- Every extracted item must have a source reference (chapter + page/section)
- Confidence ≥ 0.8 required for all items in final output
- Items with confidence < 0.8 go to `needs_review`, not main output
- Duplicate concepts across chunks: merge with highest confidence retained
- Anti-patterns must be labeled explicitly — never presented as positive advice

## Summarization Rules
- TL;DR must be 150–250 words
- Every chapter must have a summary — none may be skipped
- Applications must be concrete: "verb + object + context", not generic labels
- Anti-patterns must come directly from book text — not inferred

## Mental Model Rules
- Biases are identified analytically, labeled as `possible_bias`, never as facts
- Every assumption must cite evidence from extraction.json or summary.json
- Worldview axes scored -1.0 to +1.0 with justification

## Output Integrity Rules
- `unified-knowledge.json` must be produced before any downstream director runs
- All concept IDs must follow: `{book_id}_{concept_slug}` format
- `needs_review` items are surfaced to the user — never silently dropped
- After completion: append summary to `production/session-logs/{date}.md`

## Auto-trigger Rule
- If `autoSuggestRoles: true` in settings.json: automatically invoke `/suggest-roles` after successful `/read-book` completion
