import random

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


def test_ticket_repro_settles_to_zero():
    ledger = Ledger()
    for n in "abcd":
        ledger.add_member(n)
    ledger.add_expense("x", 32.18, "a")

    balances = ledger.balances()
    creditor_total = sum(b for b in balances.values() if b > 0)
    payments = settle(ledger)

    assert abs(sum(p.amount for p in payments) - creditor_total) < 0.005
    assert all(p.amount != 0.0 for p in payments)

    for p in payments:
        balances[p.debtor] += p.amount
        balances[p.creditor] -= p.amount
    for name, b in balances.items():
        assert abs(b) < 0.005, f"{name} not settled: {b}"


def test_seeded_random_settles_to_zero():
    rng = random.Random(1234)
    for trial in range(200):
        n = rng.randint(2, 6)
        names = [f"p{i}" for i in range(n)]
        ledger = Ledger()
        for name in names:
            ledger.add_member(name)
        for i in range(rng.randint(1, 5)):
            cents = rng.randint(100, 100_000)
            while cents % n == 0:
                cents = rng.randint(100, 100_000)
            amount = cents / 100
            payer = rng.choice(names)
            ledger.add_expense(f"e{i}", amount, payer)

        balances = ledger.balances()
        payments = settle(ledger)
        assert all(p.amount != 0.0 for p in payments), f"zero payment on trial {trial}"

        for p in payments:
            balances[p.debtor] += p.amount
            balances[p.creditor] -= p.amount
        for name, b in balances.items():
            assert abs(b) < 0.005, f"trial {trial}: {name} not settled: {b}"


def _shares_from_balances_cents(ledger: Ledger, amount: float, payer: str) -> dict[str, int]:
    """Recover each participant's per-expense debit in cents from balances()."""
    b = ledger.balances()
    total_cents = round(amount * 100)
    shares: dict[str, int] = {}
    for name, bal in b.items():
        induced_debit = -round(bal * 100)
        if name == payer:
            induced_debit += total_cents
        shares[name] = induced_debit
    return shares


def test_distribute_payer_participant_gets_leftover_cents_first():
    ledger = make_ledger("a", "b", "c", "d")
    ledger.add_expense("x", 32.18, "a")
    shares = _shares_from_balances_cents(ledger, 32.18, "a")
    assert sum(shares.values()) == 3218
    assert shares["a"] == 805
    assert shares["a"] >= max(shares.values())
    assert shares["b"] == 805
    assert shares["c"] == 804
    assert shares["d"] == 804


def test_distribute_payer_not_participant_leftover_by_list_order():
    ledger = make_ledger("a", "b", "c", "d", "e")
    ledger.add_expense("x", 32.18, "e", participants=["a", "b", "c", "d"])
    b = ledger.balances()
    shares = {name: -round(bal * 100) for name, bal in b.items() if name != "e"}
    assert sum(shares.values()) == 3218
    assert shares["a"] == 805
    assert shares["b"] == 805
    assert shares["c"] == 804
    assert shares["d"] == 804
    assert round(b["e"] * 100) == 3218


def test_expense_share_is_float_quantized_to_cents():
    ledger = make_ledger("a", "b", "c", "d")
    exp = ledger.add_expense("x", 32.18, "a")
    s = exp.share()
    assert isinstance(s, float)
    assert round(s, 2) == s
