# Verdict Format

Standard format for all quality gate verdicts produced by validator-spec.

---

## PASS Verdict
```
╔══════════════════════════════════════════╗
║  GATE: {GATE_NAME}  ✅ PASSED            ║
║  Score: {score:.2f} / Threshold: {threshold:.2f}  ║
║  Checks: {passed}/{total} passed         ║
╚══════════════════════════════════════════╝

Book: {book_id}
Artifact: {artifact_path}
Validated at: {ISO8601}
```

---

## FAIL Verdict
```
╔══════════════════════════════════════════╗
║  GATE: {GATE_NAME}  ❌ FAILED            ║
║  Score: {score:.2f} / Threshold: {threshold:.2f}  ║
║  Checks: {passed}/{total} passed         ║
╚══════════════════════════════════════════╝

Book: {book_id}
Artifact: {artifact_path}
Validated at: {ISO8601}

FAILED CHECKS:
  ✗ {check_1}
      Location: {field_name or line_number or concept_id}
      Detail: {specific reason}

  ✗ {check_2}
      Location: {location}
      Detail: {detail}

RETRY GUIDANCE:
  - {specific instruction for specialist to fix check_1}
  - {specific instruction for specialist to fix check_2}

Next: Retry {specialist_name} with the above corrections.
      If second attempt also fails, surface BLOCKED verdict.
```

---

## BLOCKED Verdict (second failure)
```
╔══════════════════════════════════════════╗
║  GATE: {GATE_NAME}  🚫 BLOCKED           ║
║  Score: {score:.2f} — second attempt failed  ║
╚══════════════════════════════════════════╝

Persistent failures after 2 attempts:
  ✗ {check_1}: {detail}
  ✗ {check_2}: {detail}

Action required: Human review needed.
  Artifact: {artifact_path}
  Suggested: Review source material for this section,
             then manually correct the artifact,
             then re-run /review-quality to re-validate.
```

---

## JSON Schema for Programmatic Use
```json
{
  "gate_name": "string",
  "status": "PASSED|FAILED|BLOCKED",
  "score": 0.0,
  "threshold": 0.0,
  "passed_checks": 0,
  "total_checks": 0,
  "book_id": "string",
  "artifact_path": "string",
  "validated_at": "ISO8601",
  "failures": [
    {
      "check": "string",
      "location": "string",
      "detail": "string",
      "retry_instruction": "string"
    }
  ]
}
```
