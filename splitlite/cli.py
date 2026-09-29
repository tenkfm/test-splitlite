"""Minimal CLI: `splitlite FILE` reads a JSON group file and prints who pays whom.

File format:
    {
      "members": ["alice", "bob"],
      "expenses": [
        {"description": "dinner", "amount": 30, "paid_by": "alice"}
      ]
    }
"""

from __future__ import annotations

import argparse
import json
import sys

from splitlite.ledger import Ledger
from splitlite.settle import settle


def load(path: str) -> Ledger:
    with open(path) as fh:
        data = json.load(fh)
    ledger = Ledger()
    for name in data["members"]:
        ledger.add_member(name)
    for item in data["expenses"]:
        ledger.add_expense(
            item["description"],
            item["amount"],
            item["paid_by"],
            item.get("participants"),
        )
    return ledger


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="splitlite")
    parser.add_argument("file")
    args = parser.parse_args(argv)
    ledger = load(args.file)
    for payment in settle(ledger):
        print(f"{payment.debtor} -> {payment.creditor}: {payment.amount:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
