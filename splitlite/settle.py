"""Turn balances into a short list of payments that settles the group."""

from __future__ import annotations

from dataclasses import dataclass

from splitlite.ledger import Ledger


@dataclass(frozen=True)
class Payment:
    debtor: str
    creditor: str
    amount: float


def settle(ledger: Ledger) -> list[Payment]:
    balances = ledger.balances()
    debtors = sorted((b, n) for n, b in balances.items() if b < 0)
    creditors = sorted(((b, n) for n, b in balances.items() if b > 0), reverse=True)

    payments: list[Payment] = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        debt, debtor = debtors[i]
        credit, creditor = creditors[j]
        amount = min(-debt, credit)
        payments.append(Payment(debtor, creditor, round(amount, 2)))
        debtors[i] = (debt + amount, debtor)
        creditors[j] = (credit - amount, creditor)
        if debtors[i][0] == 0:
            i += 1
        if creditors[j][0] == 0:
            j += 1
    return payments
