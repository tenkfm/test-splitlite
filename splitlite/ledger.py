"""Core ledger: people, expenses and balances for a shared group."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Expense:
    description: str
    amount: float
    paid_by: str
    participants: list[str]

    def share(self) -> float:
        return self.amount / len(self.participants)


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

    def balances(self) -> dict[str, float]:
        """Positive balance: the group owes this person. Negative: they owe."""
        result = {name: 0.0 for name in self.members}
        for expense in self.expenses:
            result[expense.paid_by] += expense.amount
            for person in expense.participants:
                result[person] -= expense.share()
        return result
