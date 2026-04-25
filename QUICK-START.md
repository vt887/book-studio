# Book Studio — Quick Start Guide (v3.0.0)

**All outputs now go directly into Obsidian. No more scattered files!**

---

## 5-Minute Setup

### 1. Start Book Studio
```bash
/start
```

### 2. Process a Book
```bash
/read-book
```
→ Choose your book (PDF, EPUB, TXT, or paste text)  
→ System extracts 40+ concepts

### 3. Get Role Recommendations
```bash
/suggest-roles
```
→ System suggests which roles benefit most  
→ Shows: Developer, Architect, Tester, DevOps, etc.

### 4. Apply to Your Role
```bash
/apply-as-developer        # Or your role
/apply-as-architect
/apply-as-tester
# ... any of 11 roles
```
→ Generates role-specific guides  
→ With code, ADRs, test cases, security threat models, etc.

### 5. Open in Obsidian
```
File → Open Vault
→ /Users/tymoshv/MyPetProjects/book-studio/obsidian-export/{book_id}/
```

### 6. Read: `INDEX/_START-HERE.md`

---

## What You Get

**For a single book:**

- 🧠 **9 Core Concepts** (OOP, Class, Inheritance, etc.)
- 🏗️ **12 Architectural Decisions** (ADRs with rationale)
- 🎨 **13 Design Patterns** (with code examples)
- 🧪 **52+ Test Cases** (organized by complexity)
- 👥 **11 Role-Specific Guides:**
  - 👨‍💻 Developer (code patterns, refactoring)
  - 🏗️ Architect (system design, trade-offs)
  - 🧪 Tester (test strategy, edge cases)
  - 🚀 DevOps (CI/CD, infrastructure)
  - 🔒 Security (threat modeling, access control)
  - 📊 Data (schema design, pipelines)
  - ⚡ Performance (optimization, benchmarking)
  - 📡 Observability (logging, metrics, tracing)
  - 👔 TechLead (code standards, mentoring)
  - 🏚️ Legacy (refactoring, modernization)
  - 🛠️ Platform (IDP, golden paths)

**All in one Obsidian Vault with 1000+ backlinks!**

---

## Obsidian Tips

### View Concept Relationships
Press `Ctrl+G` (or `Cmd+G`) to see the knowledge graph.

### Search Everything
`Ctrl+F` / `Cmd+F` to search across all concepts.

### Find Related Files
Right sidebar shows backlinks to current file.

### Filter by Role
Use tags like `#role-developer` to see role-specific content.

### Follow Links
Click `[[concept-name]]` to jump to related concepts.

---

## Full Commands

### Core
- `/read-book` — Process a new book
- `/suggest-roles` — Get role recommendations
- `/apply-as-{role}` — Generate role-specific guide

### All 11 Roles
```
/apply-as-developer
/apply-as-architect
/apply-as-tester
/apply-as-devops
/apply-as-security
/apply-as-data
/apply-as-performance
/apply-as-observability
/apply-as-techlead
/apply-as-legacy
/apply-as-platform
```

### Advanced
- `/build-graph` — Build Neo4j knowledge graph
- `/compare-books` — Compare multiple books
- `/synthesize-library` — Combine knowledge from all books

---

## Where Everything Lives

**All outputs are in one place:**
```
/Users/tymoshv/MyPetProjects/book-studio/obsidian-export/
└── {book_id}/
    ├── INDEX/              ← Start here
    ├── CONCEPTS/           ← 9 concepts
    ├── ARCHITECTURE/       ← ADRs + patterns
    ├── TESTING/            ← Test cases
    ├── ROLES/              ← 11 role guides
    ├── GRAPH/              ← Knowledge visualization
    └── METADATA/           ← Info about vault
```

**No more searching in production/ directories!**

---

## Step-by-Step Example

### Step 1: Read "Clean Code" Book
```bash
/read-book
# Choose: "Clean Code by Robert C. Martin"
# Wait: ~5 minutes for processing
```

### Step 2: Get Recommendations
```bash
/suggest-roles
# Shows: Developer (95%), Architect (88%), Tester (82%)
```

### Step 3: Generate Developer Guide
```bash
/apply-as-developer
# Gets: Code patterns, refactoring tips, implementation roadmap
```

### Step 4: Generate Architect Guide
```bash
/apply-as-architect
# Gets: System design, ADRs, pattern catalog, risk register
```

### Step 5: Open in Obsidian
```
Open: /Users/tymoshv/MyPetProjects/book-studio/obsidian-export/clean-code/
Read: INDEX/_START-HERE.md
Explore: All concepts with backlinks!
```

### Step 6: Choose Your Path

**If Developer:**
1. Read `ROLES/Developer/_dev-index.md`
2. Browse `code-snippets.md`
3. Follow `implementation-roadmap.md`

**If Architect:**
1. Read `ROLES/Architect/_arch-index.md`
2. Study `ARCHITECTURE/ADR-001.md` through `ADR-012.md`
3. Reference `ROLES/Architect/design-framework.md`

**If Tester:**
1. Read `ROLES/Tester/_test-index.md`
2. Browse `TESTING/TC-001.md` through `TC-052.md`
3. Follow `ROLES/Tester/testable-design.md`

---

## Common Questions

### Q: Where are the files?
**A:** Everything is in `obsidian-export/{book_id}/`. Just open it in Obsidian.

### Q: Can I edit the notes?
**A:** Yes! Obsidian notes are plain Markdown. Edits are saved locally.

### Q: How do I add my own notes?
**A:** Create a new file in the vault and use backlinks: `[[concept-name]]`

### Q: Can I use multiple roles?
**A:** Yes! Run `/apply-as-{role}` for each role you need.

### Q: What if I want to process another book?
**A:** Just run `/read-book` again. Each book gets its own vault folder.

### Q: Can I compare books?
**A:** Yes! Use `/compare-books` after processing 2+ books.

---

## Need Help?

1. **Start here:** `/INDEX/_START-HERE.md` in your Obsidian Vault
2. **Full docs:** `OBSIDIAN-FIRST-WORKFLOW.md` in project root
3. **Config docs:** `.claude/README.md` for technical details

---

**Version:** 3.0.0-obsidian-first  
**Ready to use!** 🚀

Let's go: `/start`
