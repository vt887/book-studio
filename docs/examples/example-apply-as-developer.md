# Example: /apply-as-developer — Open/Closed Principle from Clean Code

---

## Input
- Book: Clean Code
- Concept: Open/Closed Principle
- Task: Write code applying OCP to a payment processor

---

## Generated Output (developer-spec)

```markdown
# Payment Processor — Open/Closed Principle Applied
- **Book:** Clean Code by Robert C. Martin
- **Role:** developer
- **Concept:** Open/Closed Principle
- **Generated:** 2026-04-25T15:00:00
- **Gate:** APPLY-VALID PASSED (0.90)

## Concept
[concept: Open/Closed Principle]: Software entities should be open for extension, closed for modification.
Adding a new payment method must NOT require modifying existing PaymentProcessor code.

## BEFORE — Violates OCP
```python
class PaymentProcessor:
    def process(self, method: str, amount: float) -> bool:
        if method == "credit_card":
            return self._charge_card(amount)
        elif method == "paypal":
            return self._charge_paypal(amount)
        elif method == "crypto":           # ← new method requires modifying this class
            return self._charge_crypto(amount)
        raise ValueError(f"Unknown method: {method}")
```

## AFTER — OCP Applied
```python
# [concept: Open/Closed Principle]
# Adding a new payment method = add a new class, zero changes to existing code.

from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    def charge(self, amount: float) -> bool:
        ...

class CreditCardPayment(PaymentMethod):
    def charge(self, amount: float) -> bool:
        return credit_gateway.charge(amount)

class PayPalPayment(PaymentMethod):
    def charge(self, amount: float) -> bool:
        return paypal_api.transfer(amount)

class CryptoPayment(PaymentMethod):           # new method: no existing code changed
    def charge(self, amount: float) -> bool:
        return crypto_wallet.send(amount)

class PaymentProcessor:
    def __init__(self, method: PaymentMethod):
        self._method = method

    def process(self, amount: float) -> bool:
        return self._method.charge(amount)

# Usage
processor = PaymentProcessor(CryptoPayment())
processor.process(99.99)
```

## Anti-pattern Avoided
[concept: OCP violation]: "Stringly-typed dispatch" (if/elif chains) grows with every new payment type, accumulating risk of regression with each change.
```
