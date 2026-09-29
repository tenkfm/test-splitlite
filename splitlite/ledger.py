"""Core ledger: people, expenses and balances for a shared group."""

from __future__ import annotations

from dataclasses import dataclass, field


def _to_cents(amount: float) -> int:
    return round(round(amount, 2) * 100)


def _distribute_cents(total_cents: int, participants: list[str], paid_by: str) -> dict[str, int]:
    """Largest-remainder split. Leftover cents go to the payer first (when the
    payer is a participant), then to remaining participants in list order."""
    n = len(participants)
    base, rem = divmod(total_cents, n)
    shares = {p: base for p in participants}
    order: list[str] = []
    if paid_by in shares:
        order.append(paid_by)
    for p in participants:
        if p != paid_by and p not in order:
            order.append(p)
    for i in range(rem):
        shares[order[i]] += 1
    return shares


@dataclass
class Expense:
    description: str
    amount: float
    paid_by: str
    participants: list[str]

    def share(self) -> float:
        return (_to_cents(self.amount) // len(self.participants)) / 100


@dataclass
class Ledger:
    members: set[str] = field(default_factory=set)
    expenses: list[Expense] = field(default_factory=list)

    def add_member(self, name: str) -> None:
        self.members.add(name)

    def add_expense(
        self,
        description: str,
        amount: float,
        paid_by: str,
        participants: list[str] | None = None,
    ) -> Expense:
        if paid_by not in self.members:
            raise ValueError(f"unknown member: {paid_by}")
        participants = participants or sorted(self.members)
        for person in participants:
            if person not in self.members:
                raise ValueError(f"unknown member: {person}")
        expense = Expense(description, amount, paid_by, participants)
        self.expenses.append(expense)
        return expense

    def _balances_cents(self) -> dict[str, int]:
        result = {name: 0 for name in self.members}
        for expense in self.expenses:
            total = _to_cents(expense.amount)
            result[expense.paid_by] += total
            for person, share_cents in _distribute_cents(
                total, expense.participants, expense.paid_by
            ).items():
                result[person] -= share_cents
        return result

    def balances(self) -> dict[str, float]:
        """Positive balance: the group owes this person. Negative: they owe."""
        return {name: cents / 100 for name, cents in self._balances_cents().items()}
