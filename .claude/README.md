# .claude Configuration — Book Studio v3.0.0 (Obsidian-First)

## Overview

This directory contains the configuration for Book Studio's multi-agent reading system with **Obsidian-first output**.

## Key Files

### `settings.json`
**Main configuration file** for all directors, agents, and quality gates.

- `version`: 3.0.0-obsidian-first
- `directors`: 5 tier-1 orchestrators
- `available_roles`: 11 professional roles
- `role_agent_map`: Mapping from role → specialist agent
- `obsidian`: Output paths for Obsidian vault
- `session`: Cache & state directory paths
- `quality_gates`: Thresholds for validation gates

**Key Changes:**
- New `obsidian` section with vault paths
- `roleMapOutputDir` points to Obsidian: `obsidian-export/{book_id}/ROLES/`
- `roleMapArchiveDir` keeps JSON copies in production for reference

### `settings.local.json`
**Local environment configuration** (do NOT commit to version control).

- `obsidian_vault_path`: Path to your Obsidian vault
- `obsidian_first`: Set to `true` to use Obsidian-first workflow
- `permissions`: MCP permissions for reading/writing

**Key Changes:**
- `obsidian_first: true` enables new workflow
- Permissions for writing to `obsidian-export/**`

## Hooks

All hooks in `.claude/hooks/` have been updated for Obsidian-first workflow:

### `session-detect-context.sh`
Detects current session context:
- ✅ Lists processed books from `session-knowledge/`
- ✅ Shows Obsidian vaults from `obsidian-export/`
- ✅ Displays last command executed

### `validate-before-apply.sh`
Validates prerequisites before applying knowledge:
- ✅ Checks `session-knowledge/{book_id}/` exists
- ✅ Confirms `obsidian-export/{book_id}/` directory structure
- ✅ Validates role names
- ✅ Checks for role-maps

### `session-start.sh`
Initializes session state (unchanged).

### `log-decision.sh`
Logs architectural decisions (unchanged).

### `post-gate-check.sh`
Posts gate check results (unchanged).

### `pre-compact.sh`
Prepares for context compression (unchanged).

## Directory Structure

```
.claude/
├── settings.json                    ← Main config
├── settings.local.json              ← Local config (git-ignored)
├── hooks/                           ← Updated for Obsidian
│   ├── session-detect-context.sh
│   ├── validate-before-apply.sh
│   └── ... (5 more)
├── agents/
│   ├── directors/                   ← 5 tier-1 orchestrators
│   │   ├── reading-director.md
│   │   ├── knowledge-director.md
│   │   ├── synthesis-director.md
│   │   ├── role-mapping-director.md
│   │   └── application-director.md
│   └── specialists/                 ← 19 tier-2 specialists
│       ├── extractor-spec.md
│       ├── summarizer-spec.md
│       ├── mental-model-spec.md
│       ├── graph-builder-spec.md
│       ├── obsidian-exporter-spec.md
│       ├── role-mapper-spec.md
│       ├── developer-spec.md
│       ├── architect-spec.md
│       ├── tester-spec.md
│       ├── devops-spec.md
│       ├── security-spec.md
│       ├── data-spec.md
│       ├── performance-spec.md
│       ├── observability-spec.md
│       ├── techlead-spec.md
│       ├── legacy-spec.md
│       ├── platform-spec.md
│       ├── cross-book-spec.md
│       └── validator-spec.md
├── skills/                          ← Command skill definitions
│   ├── onboarding/
│   ├── reading/
│   ├── knowledge/
│   ├── export/
│   ├── synthesis/
│   ├── role-mapping/
│   ├── application/
│   └── review/
├── gates/                           ← Quality gate definitions
│   ├── gate-definitions.md
│   └── verdict-format.md
├── rules/                           ← Workflow rules by phase
│   ├── reading/rules.md
│   ├── extraction/rules.md
│   ├── knowledge-graph/rules.md
│   ├── obsidian/rules.md
│   ├── role-mapping/rules.md
│   └── application/rules.md
└── README.md                        ← This file
```

## Quality Gates

All gates now output to Obsidian vault and are tracked in `production/session-logs/`:

| Gate | Threshold | Purpose |
|------|-----------|---------|
| EXTRACT-QUALITY | 0.85 | Extraction completeness |
| SUMMARY-QUALITY | 0.85 | Summary accuracy |
| GRAPH-VALID | 0.95 | Graph consistency |
| OBSIDIAN-READY | 0.95 | Note atomicity |
| CROSS-BOOK-SYNC | 0.80 | Cross-book consistency |
| ROLE-MAP-VALID | 0.80 | Mapping specificity |
| APPLY-VALID | 0.85 | Output actionability |

## Pipeline

### Full Pipeline (with Obsidian output)

```
[Raw Book] → /read-book
    ↓
[Extraction + Summarization] (parallel)
    ↓
[Quality Gates]
    ↓
[Mental Model Building]
    ↓
[Knowledge Graph Building]
    ↓
/suggest-roles (AUTO)
    ↓
[Role Recommendations]
    ↓
/apply-as-{role} × 11 roles (PARALLEL)
    ↓
FINAL: obsidian-export/{book_id}/ ← All outputs here!
```

## Key Differences from v2.0.0

### Output Directory
- **Before**: `production/applications/{role}-output/`
- **After**: `obsidian-export/{book_id}/ROLES/{Role}/`

### Role Maps
- **Before**: `production/role-maps/`
- **After**: `obsidian-export/{book_id}/ROLES/` (with JSON backup in production/)

### Atomicity
- **Before**: Separate files in role-specific folders
- **After**: Everything in one unified Obsidian Vault with backlinks

### Knowledge Consolidation
- **Before**: Manual consolidation needed
- **After**: Automatic consolidation with Obsidian graph view

## For Developers

If you're writing new agents or skills:

1. Output paths use variables:
   - `{book_id}` — Slugified book title
   - `{role}` — Role name (lowercase)

2. Use these output paths:
   ```
   obsidian-export/{book_id}/
   └── ROLES/{Role}/
       └── {role}-specific-files.md
   ```

3. Generate Obsidian-compatible files:
   - YAML frontmatter with `tags` and `aliases`
   - Wiki-style links: `[[concept-name]]`
   - Use slugified filenames

4. Quality gates must still pass:
   - See `.claude/gates/gate-definitions.md`

## For Users

If you're using Book Studio:

1. Process a book: `/read-book`
2. Get recommendations: `/suggest-roles`
3. Apply to your role: `/apply-as-{role}`
4. Open in Obsidian: `File → Open Vault → obsidian-export/{book_id}/`
5. Start with: `INDEX/_START-HERE.md`

## Configuration Changes to Make

### Step 1: Update Vault Path (if needed)
Edit `.claude/settings.local.json`:
```json
{
  "obsidian_vault_path": "/path/to/your/obsidian/vault/",
  "obsidian_first": true
}
```

### Step 2: Test Setup
Run `/start` to verify configuration:
```bash
/start
```

Should show:
- ✅ Obsidian vault path detected
- ✅ Session state initialized
- ✅ Ready for `/read-book`

## Troubleshooting

### "Vault path not found"
- Check `.claude/settings.local.json`
- Ensure `obsidian_vault_path` is correct
- Vault directory must exist

### "Permission denied writing to obsidian-export"
- Check permissions: `chmod 755 obsidian-export/`
- Verify write access: `touch obsidian-export/test.md`

### "Role output not in Obsidian"
- Check `roleOutputDir` in `settings.json`
- Should be: `obsidian-export/{book_id}/ROLES/`
- Run `/suggest-roles` before `/apply-as-{role}`

---

**Version:** 3.0.0-obsidian-first  
**Last Updated:** 2026-04-25  
**Status:** Production-Ready ✅
