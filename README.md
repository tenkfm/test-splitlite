# splitlite

Split shared expenses in a group and work out the fewest payments that settle everyone up.

```bash
pip install -e ".[dev]"
splitlite examples/trip.json
pytest -q
```

## Layout

- `splitlite/ledger.py` — members, expenses, per-person balances
- `splitlite/settle.py` — turns balances into payments
- `splitlite/cli.py` — JSON file in, payments out
