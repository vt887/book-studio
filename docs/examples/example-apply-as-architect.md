# Example: /apply-as-architect — Dependency Inversion from Clean Code

---

## Input
- Book: Clean Code
- Concept: Dependency Inversion Principle
- Task: ADR for switching from PostgreSQL to DynamoDB

---

## Generated Output (architect-spec)

```markdown
# ADR-002: Database Layer Abstraction via Dependency Inversion
- **Book:** Clean Code by Robert C. Martin
- **Role:** architect
- **Concept:** Dependency Inversion Principle
- **Generated:** 2026-04-25T16:00:00
- **Gate:** APPLY-VALID PASSED (0.91)

---

# ADR-002: Repository Abstraction for Database Independence

**Date:** 2026-04-25
**Status:** Proposed
**Concept Applied:** [Dependency Inversion Principle] from *Clean Code*

## Context

The OrderService currently imports PostgreSQL-specific drivers directly.
Three forces drive this decision:
1. A potential migration from PostgreSQL to DynamoDB for scale reasons
2. Testing requires a live database (no testable seam exists)
3. Adding read replicas requires modifying business logic

[concept: Dependency Inversion Principle]: High-level modules (OrderService) should not depend on low-level modules (PostgresDriver). Both should depend on abstractions.

## Decision

We will introduce a `OrderRepository` interface. `OrderService` depends only on the interface. Concrete implementations (`PostgresOrderRepository`, `DynamoOrderRepository`) implement it. The DI container wires the concrete at startup.

## Rationale

Applying [concept: Dependency Inversion Principle]: by inverting the dependency, OrderService becomes independent of the storage mechanism. Adding DynamoDB requires adding one new class — zero changes to OrderService or its tests.

## Consequences

**Positive:**
- OrderService can be unit-tested with an in-memory repository
- Switching databases = swap the wired implementation
- Read replica routing can be added in the repository layer

**Negative:**
- Additional abstraction layer adds indirection
- Repository interface must be kept stable — breaking changes ripple to all implementations

**Risks:**
- Interface may grow too large over time → mitigation: apply Interface Segregation, split into ReadRepository + WriteRepository if needed

## Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| Direct DynamoDB migration | Requires rewriting OrderService business logic |
| ORM abstraction only | Leaks database-specific query patterns into business layer |

## Review Date

2026-10-25 — Review if DynamoDB migration is confirmed or cancelled.
```
