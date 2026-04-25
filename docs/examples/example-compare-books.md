# Example: /compare-books — Clean Code vs. A Philosophy of Software Design

This example shows a cross-book comparison session.

---

## Input
Books selected: `clean-code`, `philosophy-of-software-design`
Both previously processed.

---

## Phase 3 Output: cross-book-spec

### Concept Alignment (excerpt)
```json
{
  "concept": "Function Length",
  "alignment_type": "conflict",
  "books": ["clean-code", "philosophy-of-software-design"],
  "consensus": "conflict",
  "synthesis_note": "Martin prescribes very short functions (2-4 lines ideal), while Ousterhout argues that many short functions increase complexity through interfaces and cognitive overhead."
}
```

### Conflict Record
```json
{
  "concept": "Function Length",
  "book_a": {
    "book_id": "clean-code",
    "position": "Functions should be small. Very small. Short functions, 2-4 lines, are easier to name, understand, and test.",
    "quote": "The first rule of functions is that they should be small. The second rule of functions is that they should be smaller than that."
  },
  "book_b": {
    "book_id": "philosophy-of-software-design",
    "position": "A large number of small functions/classes creates additional interfaces that increase complexity.",
    "quote": "It's better to have a small number of large, general-purpose functions than a large number of small ones."
  },
  "conflict_type": "prescriptive",
  "resolution_suggestion": "Consider context: Martin's advice applies to functions doing multiple things (SRP violation), while Ousterhout's targets over-decomposition of already-focused logic. Apply Martin when refactoring God functions; apply Ousterhout when evaluating abstraction depth."
}
```

---

## Phase 4 Gate: CROSS-BOOK-SYNC PASSED (0.84)

---

## Phase 5 Summary Presented to User
```
📊 Comparison: Clean Code vs. A Philosophy of Software Design

Common concepts: 8
  ✅ Consensus: 5 (naming, abstraction, comments, tests, complexity)
  ⚠️  Partial: 1 (module design)
  ❌ Conflicts: 2 (function length, class size)

Unique to Clean Code: 15
Unique to Philosophy of Software Design: 11

Top conflict: Function Length
  Martin: "Functions should be very small (2-4 lines)"
  Ousterhout: "Many small functions increase complexity"
```
