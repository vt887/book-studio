# Skill: /apply-as-devops

**Trigger:** `/apply-as-devops`
**Director:** `application-director`
**Specialist:** `devops-spec`
**Purpose:** Apply book concepts as a DevOps engineer — CI/CD pipelines, infra as code, monitoring, deployment strategies.

---

## Steps

### Phase 1: Select Book + Concept
Show devops-relevant concepts from role-map.

### Phase 2: Select Task
```
AskUserQuestion {
  "question": "Яке DevOps завдання вирішити?",
  "options": [
    "🔄 CI/CD pipeline (GitHub Actions / GitLab CI)",
    "🏗️ Infrastructure as Code (Terraform / Pulumi)",
    "☸️ Kubernetes / Docker конфігурація",
    "📊 Monitoring setup (Prometheus / Grafana)",
    "🚀 Deployment strategy (blue-green / canary / rolling)",
    "📋 Deployment runbook"
  ]
}
```

Ask: CI provider, cloud provider, stack details if needed.

### Phase 3: Load Context
Read concept from `unified-knowledge.json`.
If book is "Accelerate": extract DORA metrics targets.
Extract: how_to_apply in DevOps context, applicable patterns.

### Phase 4: Generate Output
Agent: `devops-spec`

Pipeline: valid YAML for chosen CI provider, with stages and concept citations.
IaC: Terraform HCL or Kubernetes YAML, production-ready.
Monitoring: Prometheus rules or Grafana dashboard JSON.
Deployment strategy: step-by-step with rollback procedure.
Runbook: pre-deployment checklist, steps, rollback, success criteria.

### Phase 5: Gate Check
Run `[APPLY-VALID]` (threshold: 0.85).

### Phase 6: Save
`production/applications/devops-output/{task_id}.md`
Also save configs to `production/runbooks/` if runbook.

### Verdict
```
✅ COMPLETE
Concept: {concept_name} | Output: {output_type}
Artifact: production/applications/devops-output/{task_id}.md
```
