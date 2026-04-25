# Skill: /export-obsidian

**Trigger:** `/export-obsidian`
**Director:** `knowledge-director`
**Purpose:** Export processed book knowledge to an Obsidian vault as atomic notes.

---

## Steps

### Phase 1: Select Book + Vault Path
If multiple books: ask which one.
Ask for Obsidian vault directory path (or use default: `obsidian-export/{book_id}/`).

### Phase 2: Spawn obsidian-exporter-spec
Agent: `obsidian-exporter-spec`
Input: `session-knowledge/{book_id}/unified-knowledge.json`
Output: `obsidian-export/{book_id}/`
- One `.md` file per concept
- `_index-{book_id}.md`
- `_tags.md`

### Phase 3: Gate Check
Run `[OBSIDIAN-READY]` (threshold: 0.95).
On fail: retry with specific corrections (missing backlinks, frontmatter issues, etc.).

### Phase 4: Copy to Vault
If vault path provided:
```bash
cp -r obsidian-export/{book_id}/ {vault_path}/{book_id}/
```
Confirm: "Copied {N} notes to {vault_path}/{book_id}/"

### Verdict
```
✅ COMPLETE
Notes created: {N_concepts} concept notes + 1 index + 1 tags
Vault: {vault_path}/{book_id}/
```
