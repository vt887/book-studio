# Book Studio

> Event-driven multi-agent system for deep reading, knowledge graph construction,
> hierarchical memory, Obsidian export, and automatic knowledge application across
> 11 professional roles.

---

## Overview

Book Studio is a **Claude-native multi-agent pipeline** that transforms raw books
(PDF / EPUB / TXT) into structured, role-specific knowledge vaults ready for use
in Obsidian.

The system extracts concepts, builds a Neo4j-compatible knowledge graph, maps
every concept to relevant professional roles, and generates actionable artefacts
(code, ADRs, test suites, CI/CD configs, threat models, …) — all grounded in the
source text.

---

## Quick Start

```
/start              — onboarding & context detection
/read-book          — ingest a book and run the full extraction pipeline
/suggest-roles      — auto-map extracted concepts to 11 professional roles
/apply-as-{role}    — generate role-specific artefacts
```

Drop a PDF into the project root and run `/read-book` in Claude.

---

## Pipeline

```
[Raw Book (PDF/EPUB/TXT)]
    ↓
reading-director → /read-book
    ↓
extractor-spec + summarizer-spec (parallel)
    ↓
[EXTRACT-QUALITY 0.85] + [SUMMARY-QUALITY 0.85]
    ↓
mental-model-spec
    ↓
knowledge-director → /build-graph
    ↓
graph-builder-spec + obsidian-exporter-spec (parallel)
    ↓
[GRAPH-VALID 0.95] + [OBSIDIAN-READY 0.95]
    ↓
role-mapping-director → /suggest-roles  ← AUTO-TRIGGERED
    ↓
role-mapper-spec
    ↓
[ROLE-MAP-VALID 0.80]
    ↓
application-director → /apply-as-{role} × 11 (parallel)
    ↓
[APPLY-VALID 0.85] × 11
    ↓
obsidian-export/{book_id}/
```

---

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Onboarding & session detection |
| `/read-book` | Full extraction pipeline |
| `/extract-knowledge` | Standalone extraction pass |
| `/build-graph` | Neo4j knowledge graph |
| `/export-obsidian` | Export to Obsidian vault |
| `/suggest-roles` | Auto-map concepts → 11 roles |
| `/auto-apply` | Let the system pick the best role |
| `/apply-as-developer` | Code, refactoring, bug analysis |
| `/apply-as-architect` | ADRs, trade-offs, patterns |
| `/apply-as-tester` | Test cases, edge cases, strategy |
| `/apply-as-devops` | CI/CD, infra-as-code, monitoring |
| `/apply-as-security` | Threat models, audit, compliance |
| `/compare-books` | Cross-book analysis |
| `/synthesize-library` | Library-wide synthesis |
| `/solve-problem` | Problem-solving with book knowledge |
| `/generate-playbook` | Role-specific playbook |
| `/review-implementation` | Implementation review |
| `/review-quality` | Quality gate review |

---

## Supported Roles

| # | Role | Agent | Output |
|---|------|-------|--------|
| 1 | Developer | `developer-spec` | Code, refactoring plans |
| 2 | Architect | `architect-spec` | ADRs, pattern analysis |
| 3 | Tester | `tester-spec` | Test suites, strategies |
| 4 | DevOps | `devops-spec` | Pipelines, deployment configs |
| 5 | Security | `security-spec` | Threat models, checklists |
| 6 | Data Engineer | `data-spec` | Schemas, migrations, pipelines |
| 7 | Performance | `performance-spec` | Benchmarks, optimisation plans |
| 8 | Observability | `observability-spec` | Dashboards, alert rules |
| 9 | TechLead | `techlead-spec` | Review standards, onboarding docs |
| 10 | Legacy | `legacy-spec` | Migration plans, compatibility code |
| 11 | Platform | `platform-spec` | Golden paths, service templates |

---

## Obsidian Vault Layout

```
obsidian-export/{book_id}/
├── INDEX/          — Navigation & entry points
├── CONCEPTS/       — Core concepts (atomic notes)
├── ARCHITECTURE/   — ADRs + design patterns
├── TESTING/        — Test cases + strategy
├── PATTERNS/       — Design patterns
├── ROLES/          — 11 role-specific guides
├── GRAPH/          — Neo4j graph data
└── METADATA/       — Source & provenance
```

---

## Quality Gates

| Gate | Threshold | Scope |
|------|-----------|-------|
| `EXTRACT-QUALITY` | 0.85 | Extraction completeness |
| `SUMMARY-QUALITY` | 0.85 | Summary accuracy |
| `GRAPH-VALID` | 0.95 | Graph consistency |
| `OBSIDIAN-READY` | 0.95 | Note atomicity |
| `CROSS-BOOK-SYNC` | 0.80 | Cross-book consistency |
| `ROLE-MAP-VALID` | 0.80 | Mapping specificity |
| `APPLY-VALID` | 0.85 | Output actionability |

---

## Project Structure

```
book-studio/
├── CLAUDE.md                    — Agent routing table & system spec
├── README.md                    — This file
├── .claude/
│   ├── agents/
│   │   ├── directors/           — 5 Tier-1 orchestrators
│   │   └── specialists/         — 19 Tier-2 specialists
│   ├── skills/                  — Step-by-step skill scripts
│   ├── gates/                   — Quality gate definitions
│   ├── rules/                   — Domain rules
│   └── hooks/                   — Shell lifecycle hooks
├── session-knowledge/           — Per-book extraction cache (JSON)
├── production/                  — Session state, logs, decisions
└── docs/                        — ADR templates, runbooks, examples
```

---

## Requirements

- [Claude](https://claude.ai) with MCP / agent support
- Neo4j (optional — for graph visualisation)
- Obsidian (optional — for vault viewing)

No Python runtime required; all agents are prompt-based.

---
