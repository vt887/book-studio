# Gate Definitions

All quality gates used in Book Studio, with checklists, thresholds, and retry policies.

---

## EXTRACT-QUALITY
**Threshold:** 0.85 | **Agent:** validator-spec | **Artifact:** extraction.json

### Checklist
- [ ] All concept items have `confidence ≥ 0.8`
- [ ] Every concept has a non-empty `source_quote`
- [ ] Every concept has a `chapter` reference
- [ ] No duplicate concept IDs (all IDs unique)
- [ ] `needs_review` count < 20% of total extracted items
- [ ] All facts have `chapter` + `confidence` fields
- [ ] All quotes are verbatim (not summaries or paraphrases)
- [ ] Concepts count > 0 (at least one concept extracted)

**Retry policy:** On fail, retry extractor-spec once with itemized failure list appended to prompt.

---

## SUMMARY-QUALITY
**Threshold:** 0.85 | **Agent:** validator-spec | **Artifact:** summary.json

### Checklist
- [ ] `tldr` is 150–250 words
- [ ] Every chapter in the book has a corresponding chapter_summary
- [ ] Every `core_concept` has a non-empty `how_to_apply` field
- [ ] Every `anti_pattern` has both `consequence` and `alternative` fields
- [ ] `key_takeaways` has 5–10 items
- [ ] All takeaways start with a verb (actionable)
- [ ] No takeaway is generic ("use good practices")

**Retry policy:** On fail, retry summarizer-spec once targeting specific failures.

---

## GRAPH-VALID
**Threshold:** 0.95 | **Agent:** validator-spec | **Artifact:** cypher-statements.cypher

### Checklist
- [ ] All Cypher statements are syntactically valid (parseable)
- [ ] All node MERGE statements use MERGE not CREATE
- [ ] No orphan nodes (every node has ≥ 1 edge after all statements execute)
- [ ] All float properties are in range [0.0, 1.0]
- [ ] All concept IDs match pattern `{book_id}_{slug}` (lowercase, no spaces)
- [ ] APPLICABLE_AS edges exist for every concept node
- [ ] Role names in APPLICABLE_AS match exactly: developer|architect|tester|devops|security|data|performance|observability|techlead|legacy|platform
- [ ] Section comments present: `// === BOOK NODES ===` etc.

**Retry policy:** On fail, retry graph-builder-spec once with Cypher validator output.

---

## OBSIDIAN-READY
**Threshold:** 0.95 | **Agent:** validator-spec | **Artifact:** obsidian-export/ directory

### Checklist
- [ ] Every concept note has valid YAML frontmatter (title, book, author, type, confidence, tags)
- [ ] All backlinks are bidirectional (A→B means B→A exists)
- [ ] All tags follow taxonomy (#domain/, #role/, #book/, type tags)
- [ ] Tag names are lowercase kebab-case
- [ ] Source quotes in `> quote` blocks are verbatim
- [ ] Index note (`_index-{book_id}.md`) links to every concept note
- [ ] All file names are kebab-case `.md`
- [ ] `_tags.md` lists all tags used in this book's notes

**Retry policy:** On fail, retry obsidian-exporter-spec with specific failing notes listed.

---

## CROSS-BOOK-SYNC
**Threshold:** 0.80 | **Agent:** validator-spec | **Artifact:** synthesis-report.json + conflicts.json

### Checklist
- [ ] Minimum 2 books were compared
- [ ] All concept_alignment entries have `alignment_type` set
- [ ] Conflict records include verbatim quotes from both books
- [ ] Conflict `resolution_suggestion` is labeled as suggestion (not conclusion)
- [ ] Evolution chains are chronologically ordered by year
- [ ] No concept appears in conflict list with only one book's position

**Retry policy:** On fail, retry cross-book-spec with alignment and conflict-specific corrections.

---

## ROLE-MAP-VALID
**Threshold:** 0.80 | **Agent:** validator-spec | **Artifact:** role-map.json

### Checklist
- [ ] Every concept from unified-knowledge.json appears in `concept_mappings`
- [ ] Every concept has at least one `applicable_role`
- [ ] Every `justification` is specific (contains concept name + action + context — not generic)
- [ ] Every `application_idea` follows format "Використай X щоб Y у Z"
- [ ] Every `complexity` is one of: simple|medium|complex
- [ ] No `concept_id` in output that doesn't exist in source unified-knowledge.json
- [ ] `role_summary.{role}.count` matches actual count of concepts mapped to that role

**Retry policy:** On fail, retry role-mapper-spec targeting specific failed concepts.

---

## APPLY-VALID
**Threshold:** 0.85 | **Agent:** validator-spec | **Artifact:** application output .md

### Checklist
- [ ] Output contains at least one `[concept: {name}]` citation
- [ ] Cited concept names exist in the book's unified-knowledge.json
- [ ] Output contains role-appropriate artifact format (code/ADR/tests/config/etc.)
- [ ] Artifact header contains: Book, Role, Concept, Generated, Gate fields
- [ ] No placeholder comments (`# TODO: implement`, `# add logic here`)
- [ ] Output is not pure prose — contains code, config, table, or checklist
- [ ] No anti-patterns presented as positive advice

**Retry policy:** On fail, retry role-specific spec once with gate failures appended to prompt.
