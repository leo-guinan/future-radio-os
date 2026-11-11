from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import pytest

from future_radio_os.ledger import LedgerError, MissionLedger


def test_ledger_records_expenses_and_revenue_with_provenance_and_mission():
    ledger = MissionLedger()
    expense = ledger.add_expense(mission_id="mission-001", category="compute", amount="0.04", unit="USD", provenance="receipt://compute-1")
    revenue = ledger.add_revenue(mission_id="mission-001", category="sponsor", amount="100", unit="USD", status="quoted", provenance="proposal://sponsor-1")

    assert expense.amount == Decimal("0.04")
    assert revenue.status == "quoted"
    assert ledger.balance(mission_id="mission-001") == Decimal("-0.04")


def test_quote_cannot_appear_as_received_and_provider_readback_is_required():
    ledger = MissionLedger()
    ledger.add_revenue(mission_id="mission-001", category="sponsor", amount="100", unit="USD", status="quoted", provenance="proposal://1")
    with pytest.raises(LedgerError, match="received"):
        ledger.mark_received("revenue-001", provider_receipt="provider-1", readback=lambda _: False)

    ledger.add_revenue(mission_id="mission-001", category="sponsor", amount="50", unit="USD", status="invoiced", provenance="invoice://2")
    receipt = ledger.mark_received("revenue-002", provider_receipt="provider-2", readback=lambda value: value == "provider-2")
    assert receipt.status == "received"
    assert ledger.balance(mission_id="mission-001") == Decimal("50")


def test_incremental_cost_is_derived_from_recorded_inputs_and_survives_restart(tmp_path: Path):
    path = tmp_path / "ledger.sqlite3"
    first = MissionLedger(path)
    first.add_expense(mission_id="mission-001", category="compute", amount="1.25", unit="USD", provenance="receipt://1")
    first.add_expense(mission_id="mission-001", category="storage", amount="0.75", unit="USD", provenance="receipt://2")
    first.close()

    second = MissionLedger(path)
    assert second.incremental_cost(mission_id="mission-001") == Decimal("2.00")
    second.close()


def test_invalid_units_statuses_and_unprovenanced_amounts_fail_closed():
    ledger = MissionLedger()
    with pytest.raises(LedgerError, match="unit"):
        ledger.add_expense(mission_id="mission-001", category="compute", amount="1", unit="", provenance="receipt://1")
    with pytest.raises(LedgerError, match="status"):
        ledger.add_revenue(mission_id="mission-001", category="sponsor", amount="1", unit="USD", status="cash", provenance="receipt://1")
    with pytest.raises(LedgerError, match="provenance"):
        ledger.add_expense(mission_id="mission-001", category="compute", amount="1", unit="USD", provenance="")
    with pytest.raises(LedgerError, match="finite"):
        ledger.add_expense(mission_id="mission-001", category="compute", amount="NaN", unit="USD", provenance="receipt://nan")
    with pytest.raises(LedgerError, match="numeric"):
        ledger.add_expense(mission_id="mission-001", category="compute", amount=cast(Any, None), unit="USD", provenance="receipt://none")


def test_file_backed_ledger_creates_parent_directory(tmp_path: Path):
    ledger = MissionLedger(tmp_path / "nested" / "ledger.sqlite3")
    ledger.add_expense(mission_id="mission-001", category="compute", amount="1", unit="USD", provenance="receipt://1")
    assert ledger.incremental_cost(mission_id="mission-001") == Decimal("1")
    ledger.close()


def test_mission_cannot_mix_units_without_an_explicit_conversion():
    ledger = MissionLedger()
    ledger.add_expense(mission_id="mission-001", category="compute", amount="1", unit="USD", provenance="receipt://usd")
    with pytest.raises(LedgerError, match="unit"):
        ledger.add_expense(mission_id="mission-001", category="compute", amount="1", unit="credits", provenance="receipt://credits")


def test_aggregation_rejects_preexisting_mixed_units(tmp_path: Path):
    ledger = MissionLedger(tmp_path / "ledger.sqlite3")
    ledger.add_expense(mission_id="mission-001", category="compute", amount="1", unit="USD", provenance="receipt://usd")
    ledger._connection.execute("INSERT INTO ledger VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", ("expense-999", "expense", "mission-001", "compute", "1", "credits", "paid", "receipt://credits", None))
    ledger._connection.commit()
    with pytest.raises(LedgerError, match="unit"):
        ledger.incremental_cost(mission_id="mission-001")
