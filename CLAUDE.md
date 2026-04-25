# Book Studio — Multi-Agent Reading System

Book Studio — event-driven multi-agent система для глибокого читання книг, побудови knowledge graph, hierarchical memory, експорту в Obsidian та автоматичного пропонування знань у конкретні ролі.

---

## ROUTING TABLE

| Trigger | Director | Skill |
|---------|----------|-------|
| `/start` | — | `.claude/skills/onboarding/start/SKILL.md` |
| `/read-book` | `reading-director` | `.claude/skills/reading/read-book/SKILL.md` |
| `/extract-knowledge` | `reading-director` | `.claude/skills/reading/extract-knowledge/SKILL.md` |
| `/build-graph` | `knowledge-director` | `.claude/skills/knowledge/build-graph/SKILL.md` |
| `/export-obsidian` | `knowledge-director` | `.claude/skills/export/export-obsidian/SKILL.md` |
| `/compare-books` | `synthesis-director` | `.claude/skills/synthesis/compare-books/SKILL.md` |
| `/synthesize-library` | `synthesis-director` | `.claude/skills/synthesis/synthesize-library/SKILL.md` |
| `/review-quality` | `synthesis-director` | `.claude/skills/review/review-quality/SKILL.md` |
| `/suggest-roles` | `role-mapping-director` | `.claude/skills/role-mapping/suggest-roles/SKILL.md` |
| `/auto-apply` | `application-director` | `.claude/skills/role-mapping/auto-apply/SKILL.md` |
| `/apply-as-developer` | `application-director` | `.claude/skills/application/apply-as-developer/SKILL.md` |
| `/apply-as-architect` | `application-director` | `.claude/skills/application/apply-as-architect/SKILL.md` |
| `/apply-as-tester` | `application-director` | `.claude/skills/application/apply-as-tester/SKILL.md` |
| `/apply-as-devops` | `application-director` | `.claude/skills/application/apply-as-devops/SKILL.md` |
| `/apply-as-security` | `application-director` | `.claude/skills/application/apply-as-security/SKILL.md` |
| `/solve-problem` | `application-director` | `.claude/skills/application/solve-problem/SKILL.md` |
| `/generate-playbook` | `application-director` | `.claude/skills/application/generate-playbook/SKILL.md` |
| `/review-implementation` | `application-director` | `.claude/skills/application/review-implementation/SKILL.md` |

---

## ROLE → AGENT MAPPING (Obsidian-First)

| Role | Agent | Output Dir |
|------|-------|-----------|
| `developer` | `developer-spec` | `obsidian-export/{book_id}/ROLES/Developer/` |
| `architect` | `architect-spec` | `obsidian-export/{book_id}/ROLES/Architect/` |
| `tester` | `tester-spec` | `obsidian-export/{book_id}/ROLES/Tester/` |
| `devops` | `devops-spec` | `obsidian-export/{book_id}/ROLES/DevOps/` |
| `security` | `security-spec` | `obsidian-export/{book_id}/ROLES/Security/` |
| `data` | `data-spec` | `obsidian-export/{book_id}/ROLES/Data/` |
| `performance` | `performance-spec` | `obsidian-export/{book_id}/ROLES/Performance/` |
| `observability` | `observability-spec` | `obsidian-export/{book_id}/ROLES/Observability/` |
| `techlead` | `techlead-spec` | `obsidian-export/{book_id}/ROLES/TechLead/` |
| `legacy` | `legacy-spec` | `obsidian-export/{book_id}/ROLES/Legacy/` |
| `platform` | `platform-spec` | `obsidian-export/{book_id}/ROLES/Platform/` |

---

## AGENT DIRECTORY

### Tier-1 Directors
- `.claude/agents/directors/reading-director.md` — chunking, orchestration, extraction pipeline
- `.claude/agents/directors/knowledge-director.md` — graph architecture, Cypher, Obsidian
- `.claude/agents/directors/synthesis-director.md` — cross-book intelligence, conflicts, evolution
- `.claude/agents/directors/role-mapping-director.md` — concept→role автоматичний аналіз
- `.claude/agents/directors/application-director.md` — координація застосування знань

### Tier-2 Specialists
- `.claude/agents/specialists/extractor-spec.md` — facts, quotes, terms, entities
- `.claude/agents/specialists/summarizer-spec.md` — TL;DR, concepts, applications, anti-patterns
- `.claude/agents/specialists/mental-model-spec.md` — problem framing, assumptions, patterns, biases
- `.claude/agents/specialists/graph-builder-spec.md` — Neo4j Cypher, node/edge types
- `.claude/agents/specialists/obsidian-exporter-spec.md` — atomic notes, backlinks, tags
- `.claude/agents/specialists/cross-book-spec.md` — comparison, conflicts, evolution
- `.claude/agents/specialists/validator-spec.md` — completeness, consistency, grounding, format
- `.claude/agents/specialists/role-mapper-spec.md` — concept→role mapping з justification
- `.claude/agents/specialists/developer-spec.md` — code, refactoring, bug analysis
- `.claude/agents/specialists/architect-spec.md` — ADR, trade-offs, patterns, risks
- `.claude/agents/specialists/tester-spec.md` — test cases, edge cases, strategy
- `.claude/agents/specialists/devops-spec.md` — CI/CD, infra as code, monitoring
- `.claude/agents/specialists/security-spec.md` — threat modeling, audit, compliance
- `.claude/agents/specialists/data-spec.md` — schema design, migrations, pipelines
- `.claude/agents/specialists/performance-spec.md` — profiling, benchmarking, optimization
- `.claude/agents/specialists/observability-spec.md` — logging, metrics, tracing, alerting
- `.claude/agents/specialists/techlead-spec.md` — code review standards, onboarding, decisions
- `.claude/agents/specialists/legacy-spec.md` — refactoring, migration, deprecation
- `.claude/agents/specialists/platform-spec.md` — internal dev platform, tooling, golden paths

---

## PIPELINE (Obsidian-First)

```
[Raw Book (PDF/EPUB/TXT)]
    ↓
reading-director → /read-book
    ↓
extractor-spec + summarizer-spec (parallel)
    ↓
[EXTRACT-QUALITY gate] + [SUMMARY-QUALITY gate]
    ↓
mental-model-spec
    ↓
knowledge-director → /build-graph (Neo4j-ready)
    ↓
graph-builder-spec + obsidian-exporter-spec (parallel)
    ↓
[GRAPH-VALID gate] + [OBSIDIAN-READY gate]
    ↓
role-mapping-director → /suggest-roles   ← AUTO-TRIGGERED
    ↓
role-mapper-spec
    ↓
[ROLE-MAP-VALID gate]
    ↓
application-director → /apply-as-{role} × 11 roles (PARALLEL)
    ↓
{role}-spec (all 11 roles: dev, arch, test, devops, sec, data, perf, obs, lead, legacy, platform)
    ↓
[APPLY-VALID gate] × 11
    ↓
FINAL: Consolidate to Single Obsidian Vault
    ↓
obsidian-export/{book_id}/
├── INDEX/                (Navigation)
├── CONCEPTS/             (9 core concepts)
├── ARCHITECTURE/         (12 ADRs + 13 patterns)
├── TESTING/              (52+ test cases)
├── PATTERNS/             (13 design patterns)
├── ROLES/                (11 role-specific guides)
├── GRAPH/                (Neo4j visualization)
└── METADATA/             (Source & provenance)
```

**Key Difference:** All outputs go directly to Obsidian Vault (NO production/ files)

---

## AUTO-SUGGEST WORKFLOW

Після успішного завершення `/read-book` система автоматично запускає `/suggest-roles`.

**Приклад — "Clean Code":**
1. `/read-book` → 23 концепції extracted
2. `/suggest-roles` → система пропонує:
   - 👨‍💻 Developer (12 концепцій) — meaningful names, SRP, unit tests
   - 🏗️ Architect (5 концепцій) — separation of concerns, dependency inversion
   - 🧪 Tester (4 концепцій) — testable design, TDD
   - 👔 TechLead (2 концепцій) — boy scout rule, code standards
3. User selects → `/apply-as-{role}`

---

## QUALITY GATES

| Gate | Threshold | Scope |
|------|-----------|-------|
| `EXTRACT-QUALITY` | 0.85 | Extraction completeness |
| `SUMMARY-QUALITY` | 0.85 | Summary accuracy |
| `GRAPH-VALID` | 0.95 | Graph consistency |
| `OBSIDIAN-READY` | 0.95 | Note atomicity |
| `CROSS-BOOK-SYNC` | 0.80 | Cross-book consistency |
| `ROLE-MAP-VALID` | 0.80 | Mapping specificity |
| `APPLY-VALID` | 0.85 | Output actionability |

See `.claude/gates/gate-definitions.md` for full checklists.

---

## RULES

- `.claude/rules/reading/rules.md`
- `.claude/rules/extraction/rules.md`
- `.claude/rules/knowledge-graph/rules.md`
- `.claude/rules/obsidian/rules.md`
- `.claude/rules/role-mapping/rules.md`
- `.claude/rules/application/rules.md`

---

## OBSIDIAN VAULT LAYOUT (Primary)

```
obsidian-export/
└── {book_id}/                      (e.g., object-oriented-thinking-consolidated)
    ├── INDEX/                      (Navigation & entry points)
    │   ├── _START-HERE.md         ← Entry point
    │   ├── _table-of-contents.md
    │   ├── _roles-overview.md
    │   └── _glossary.md
    │
    ├── CONCEPTS/                   (9 core concepts)
    │   ├── 01-oop.md
    │   ├── 02-class.md
    │   ├── 03-inheritance.md
    │   └── ... (6 more)
    │
    ├── ARCHITECTURE/               (12 ADRs + 13 patterns)
    │   ├── ADR-001 to ADR-012.md
    │   └── _architecture-patterns.md
    │
    ├── TESTING/                    (52+ test cases)
    │   ├── TC-001 to TC-052.md
    │   └── _testing-strategy.md
    │
    ├── PATTERNS/                   (13 design patterns)
    │   ├── factory-pattern.md
    │   └── ... (12 more)
    │
    ├── ROLES/                      (11 professional roles)
    │   ├── Developer/
    │   ├── Architect/
    │   ├── Tester/
    │   ├── TechLead/
    │   ├── DevOps/
    │   ├── Security/
    │   ├── Data/
    │   ├── Performance/
    │   ├── Observability/
    │   ├── Legacy/
    │   └── Platform/
    │
    ├── GRAPH/                      (Knowledge graph data)
    │   ├── _graph-index.md
    │   ├── graph-summary.json
    │   ├── concepts-map.md
    │   └── analysis-insights.md
    │
    └── METADATA/                   (Vault metadata)
        ├── _vault-metadata.json
        └── _source-book.md
```

## SESSION LAYOUT (Cache & Metadata)

```
session-knowledge/
└── {book_id}/                      (e.g., object-oriented-thinking)
    ├── extraction.json             (45KB - 38 concepts)
    ├── summary.json                (35KB - TL;DR)
    ├── mental-model.json           (30KB - 5 layers)
    └── unified-knowledge.json      (60KB - Merged)

production/                         (Kept for backwards compatibility)
├── session-state/active.md
├── session-logs/
├── decisions/
└── role-maps/                      (Machine-readable mappings)
```

---

## HOOKS

| Hook | Trigger | Script |
|------|---------|--------|
| `PostToolUse[session_start]` | Session open | `.claude/hooks/session-start.sh` |
| `PreToolUse[detect_context]` | Before any tool | `.claude/hooks/session-detect-context.sh` |
| `PreCompact` | Context compression | `.claude/hooks/pre-compact.sh` |
| `PostToolUse[decision]` | After decisions | `.claude/hooks/log-decision.sh` |
| `PreToolUse[apply]` | Before application | `.claude/hooks/validate-before-apply.sh` |
| `PostToolUse[gate]` | After gate check | `.claude/hooks/post-gate-check.sh` |
