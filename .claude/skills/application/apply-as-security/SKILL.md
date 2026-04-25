# Skill: /apply-as-security

**Trigger:** `/apply-as-security`
**Director:** `application-director`
**Specialist:** `security-spec`
**Purpose:** Apply book concepts as a security engineer — threat modeling, security audits, compliance, secrets management.

---

## Steps

### Phase 1: Select Book + Concept
Show security-relevant concepts from role-map.

### Phase 2: Select Task
```
AskUserQuestion {
  "question": "Яке security завдання вирішити?",
  "options": [
    "🗺️ Threat model (STRIDE analysis)",
    "✅ Security checklist для компонента/системи",
    "🔍 Security audit існуючого коду/конфігурації",
    "🔐 Secrets management план",
    "📋 Remediation plan для знайдених вразливостей",
    "🛡️ Compliance checklist (OWASP / NIST / SOC2)"
  ]
}
```

Ask: system description, tech stack, compliance framework if needed.

### Phase 3: Load Context
Read concept from `unified-knowledge.json`.
If book is threat modeling related: extract STRIDE/PASTA concepts.
Extract: security principles, anti-patterns (vulnerabilities to avoid).

### Phase 4: Generate Output
Agent: `security-spec`

Threat model: full STRIDE table with likelihood × impact risk scores, mitigations roadmap.
Checklist: itemized checks with pass/fail criteria per OWASP category.
Audit: findings list with severity (Critical/High/Medium/Low), evidence, remediation.
Secrets management: Vault/KMS setup, rotation schedule, access control.
Remediation plan: prioritized steps, verification method per finding.

### Phase 5: Gate Check
Run `[APPLY-VALID]` (threshold: 0.85).

### Phase 6: Save
`production/applications/security-output/{task_id}.md`

### Verdict
```
✅ COMPLETE
Concept: {concept_name} | Findings/Items: {N}
Artifact: production/applications/security-output/{task_id}.md
```
