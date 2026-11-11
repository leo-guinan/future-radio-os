from decimal import Decimal
from pathlib import Path

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
