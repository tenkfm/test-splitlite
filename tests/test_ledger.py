import pytest

from splitlite.ledger import Ledger
from splitlite.settle import settle


def make_ledger(*names: str) -> Ledger:
    ledger = Ledger()
    for name in names:
        ledger.add_member(name)
    return ledger


def test_even_split_balances():
    ledger = make_ledger("alice", "bob")
    ledger.add_expense("dinner", 30, "alice")
    assert ledger.balances() == {"alice": 15, "bob": -15}


def test_unknown_payer_rejected():
    ledger = make_ledger("alice")
    with pytest.raises(ValueError):
        ledger.add_expense("taxi", 10, "mallory")


def test_settle_two_people():
    ledger = make_ledger("alice", "bob")
    ledger.add_expense("dinner", 30, "alice")
    payments = settle(ledger)
    assert [(p.debtor, p.creditor, p.amount) for p in payments] == [("bob", "alice", 15.0)]


def test_settle_three_people():
    ledger = make_ledger("alice", "bob", "carol")
    ledger.add_expense("hotel", 90, "alice")
    ledger.add_expense("food", 30, "bob")
    payments = settle(ledger)
    assert sum(p.amount for p in payments) == 50
