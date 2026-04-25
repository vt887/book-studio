# Example: /read-book — Clean Code by Robert C. Martin

This example walks through a complete `/read-book` session.

---

## Input
User: `/read-book`
System: "Яку книгу ти хочеш обробити?"
User: 📁 Вставити текст → pastes Chapter 2 excerpt on Meaningful Names

Additional info: Title=Clean Code, Author=Robert C. Martin, Year=2008

---

## Phase 3: Chunking
- book_id: `clean-code`
- 7 chunks generated from Chapter 2 (2300–3800 tokens each, 200-token overlap)
- Directory created: `session-knowledge/clean-code/`

---

## Phase 4: Parallel Output

**extractor-spec** produced (excerpt):
```json
{
  "concepts": [
    {
      "id": "clean-code_meaningful-names",
      "name": "Meaningful Names",
      "definition": "Names should reveal intent, avoiding noise words, encodings, and mental mapping",
      "source_quote": "The name of a variable, function, or class, should answer all the big questions. It should tell you why it exists, what it does, and how it is used.",
      "chapter": "Chapter 2",
      "confidence": 0.97,
      "type": "principle"
    }
  ]
}
```

**summarizer-spec** produced (excerpt):
```json
{
  "tldr": "Clean Code argues that code is read far more often than written, making readability a professional obligation. Martin provides concrete naming conventions, function design principles, and commenting guidelines to help programmers write code that communicates intent clearly.",
  "core_concepts": [
    {
      "name": "Meaningful Names",
      "how_to_apply": "Replace abbreviations and single-letter variables with names that reveal the variable's purpose, type, and scope",
      "anti_pattern": "Using names like d, tmp, data, or info that force the reader to mentally decode intent"
    }
  ]
}
```

---

## Phase 5: Gates

- `EXTRACT-QUALITY`: PASSED (0.94) — 23 concepts, all confidence ≥ 0.80
- `SUMMARY-QUALITY`: PASSED (0.89) — TL;DR 187 words, all chapters covered

---

## Phase 7: unified-knowledge.json
Merged → `session-knowledge/clean-code/unified-knowledge.json`
Total concepts: 23

---

## Phase 8: Auto-trigger
`autoSuggestRoles: true` → `/suggest-roles` triggered automatically.

---

## Final Output
```
✅ COMPLETE
Book: Clean Code by Robert C. Martin (2008)
Concepts extracted: 23
Artifacts: session-knowledge/clean-code/
Next: /suggest-roles (running automatically)
```
