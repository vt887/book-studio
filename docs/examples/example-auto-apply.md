# Example: /auto-apply — Developer + SRP + Refactor Legacy Service

This example shows a complete `/auto-apply` session where the user applies the Single Responsibility Principle from "Clean Code" to refactor a legacy OrderService.

---

## User Input
- Book: Clean Code
- Role: Developer (auto-selected — highest score: 0.91)
- Concept: SRP (auto-selected — highest relevance + complexity=medium)
- Task: Refactor legacy OrderService

User confirms: "Я вибрав: роль **developer**, концепція **Single Responsibility Principle**. Підтверджуєш?" → ✅

---

## Generated Output (developer-spec)

```markdown
# Refactor: OrderService → SRP Applied
- **Book:** Clean Code by Robert C. Martin
- **Role:** developer
- **Concept:** Single Responsibility Principle
- **Generated:** 2026-04-25T14:30:00
- **Gate:** APPLY-VALID PASSED (0.92)

## Anti-Pattern Identified
[concept: Single Responsibility Principle]: OrderService currently has 4 reasons to change:
1. Validation rules change
2. Pricing logic changes
3. Database schema changes
4. Notification channel changes

## BEFORE
```python
class OrderService:
    def create_order(self, items: list, user_id: str) -> str:
        # Reason 1: validation
        if not items:
            raise ValueError("Order must have items")
        if any(i['price'] <= 0 for i in items):
            raise ValueError("Invalid price")

        # Reason 2: pricing
        total = sum(i['price'] * i['quantity'] for i in items)
        discount = 0.1 if total > 100 else 0
        final_total = total * (1 - discount)

        # Reason 3: persistence
        order_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO orders VALUES (?, ?, ?)",
            (order_id, user_id, final_total)
        )

        # Reason 4: notification
        email.send(
            to=user_id,
            subject="Order Confirmed",
            body=f"Your order total: ${final_total:.2f}"
        )
        return order_id
```

## AFTER — SRP Applied
```python
# [concept: Single Responsibility Principle]
# Each class has exactly one reason to change.

class OrderValidator:
    """Reason to change: validation rules."""
    def validate(self, items: list) -> None:
        if not items:
            raise ValueError("Order must have items")
        if any(i['price'] <= 0 for i in items):
            raise ValueError("Invalid price in items")


class OrderPricer:
    """Reason to change: pricing/discount logic."""
    BULK_THRESHOLD = 100.0
    BULK_DISCOUNT = 0.10

    def calculate(self, items: list) -> float:
        total = sum(i['price'] * i['quantity'] for i in items)
        discount = self.BULK_DISCOUNT if total > self.BULK_THRESHOLD else 0
        return total * (1 - discount)


class OrderRepository:
    """Reason to change: persistence mechanism."""
    def save(self, user_id: str, total: float) -> str:
        order_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO orders VALUES (?, ?, ?)",
            (order_id, user_id, total)
        )
        return order_id


class OrderNotifier:
    """Reason to change: notification channel."""
    def notify_created(self, user_id: str, total: float) -> None:
        email.send(
            to=user_id,
            subject="Order Confirmed",
            body=f"Your order total: ${total:.2f}"
        )


class OrderService:
    """Orchestrator — thin, delegates to focused classes."""
    def __init__(
        self,
        validator: OrderValidator,
        pricer: OrderPricer,
        repository: OrderRepository,
        notifier: OrderNotifier,
    ):
        self._validator = validator
        self._pricer = pricer
        self._repository = repository
        self._notifier = notifier

    def create_order(self, items: list, user_id: str) -> str:
        self._validator.validate(items)
        total = self._pricer.calculate(items)
        order_id = self._repository.save(user_id, total)
        self._notifier.notify_created(user_id, total)
        return order_id
```

## Refactoring Steps (incremental — each step leaves system working)
1. Extract `OrderValidator` — replace inline validation, run tests
2. Extract `OrderPricer` — replace inline pricing, run tests
3. Extract `OrderRepository` — replace db calls, run tests
4. Extract `OrderNotifier` — replace email call, run tests
5. Slim `OrderService` to orchestrator only, run full suite
```

---

## Saved Artifact
`production/applications/developer-output/clean-code_developer_srp_20260425-143000.md`
