import sqlite3
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Callable


class LedgerError(ValueError):
    pass


@dataclass(frozen=True)
class LedgerEntry:
    entry_id: str
    kind: str
    mission_id: str
    category: str
    amount: Decimal
    unit: str
    status: str
    provenance: str
    provider_receipt: str | None = None


class MissionLedger:
    REVENUE_STATUSES = {"quoted", "contracted", "invoiced", "received", "earned"}

    def __init__(self, path: str | Path | None = None):
        self._memory = path is None
        if path is not None:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(":memory:" if path is None else Path(path))
        self._connection.row_factory = sqlite3.Row
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS ledger (
                entry_id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                mission_id TEXT NOT NULL,
                category TEXT NOT NULL,
                amount TEXT NOT NULL,
                unit TEXT NOT NULL,
                status TEXT NOT NULL,
                provenance TEXT NOT NULL,
                provider_receipt TEXT
            )
            """
        )
        self._connection.commit()

    def add_expense(self, *, mission_id: str, category: str, amount: str, unit: str, provenance: str) -> LedgerEntry:
        value = self._validate(mission_id, category, amount, unit, provenance)
        entry_id = self._next_id("expense")
        return self._insert(LedgerEntry(entry_id, "expense", mission_id, category, value, unit, "paid", provenance))

    def add_revenue(self, *, mission_id: str, category: str, amount: str, unit: str, status: str, provenance: str) -> LedgerEntry:
        value = self._validate(mission_id, category, amount, unit, provenance)
        if status not in self.REVENUE_STATUSES:
            raise LedgerError(f"invalid revenue status: {status}")
        if status == "received":
            raise LedgerError("received revenue requires provider readback")
        entry_id = self._next_id("revenue")
        return self._insert(LedgerEntry(entry_id, "revenue", mission_id, category, value, unit, status, provenance))

    def mark_received(self, entry_id: str, *, provider_receipt: str, readback: Callable[[str], bool]) -> LedgerEntry:
        entry = self.get(entry_id)
        if entry.kind != "revenue" or entry.status not in {"contracted", "invoiced"}:
            raise LedgerError("only contracted or invoiced revenue can become received")
        if not provider_receipt or not readback(provider_receipt):
            raise LedgerError("provider receipt readback failed; revenue remains unreceived")
        updated = LedgerEntry(entry.entry_id, entry.kind, entry.mission_id, entry.category, entry.amount, entry.unit, "received", entry.provenance, provider_receipt)
        self._connection.execute("UPDATE ledger SET status = ?, provider_receipt = ? WHERE entry_id = ?", ("received", provider_receipt, entry_id))
        self._connection.commit()
        return updated

    def get(self, entry_id: str) -> LedgerEntry:
        row = self._connection.execute("SELECT * FROM ledger WHERE entry_id = ?", (entry_id,)).fetchone()
        if row is None:
            raise LedgerError(f"unknown ledger entry {entry_id}")
        return _row(row)

    def balance(self, *, mission_id: str) -> Decimal:
        revenue = self.incremental_revenue(mission_id=mission_id)
        expenses = self.incremental_cost(mission_id=mission_id)
        return revenue - expenses

    def incremental_cost(self, *, mission_id: str) -> Decimal:
        self._assert_single_unit(mission_id)
        rows = self._connection.execute("SELECT amount FROM ledger WHERE kind = 'expense' AND mission_id = ?", (mission_id,)).fetchall()
        return sum((Decimal(row["amount"]) for row in rows), Decimal("0"))

    def incremental_revenue(self, *, mission_id: str) -> Decimal:
        self._assert_single_unit(mission_id)
        rows = self._connection.execute("SELECT amount FROM ledger WHERE kind = 'revenue' AND mission_id = ? AND status IN ('received', 'earned')", (mission_id,)).fetchall()
        return sum((Decimal(row["amount"]) for row in rows), Decimal("0"))

    def close(self) -> None:
        self._connection.close()

    def _assert_single_unit(self, mission_id: str) -> None:
        units = self._connection.execute("SELECT DISTINCT unit FROM ledger WHERE mission_id = ?", (mission_id,)).fetchall()
        if len(units) > 1:
            raise LedgerError("mission cannot aggregate mixed ledger units without an explicit conversion")

    def _insert(self, entry: LedgerEntry) -> LedgerEntry:
        existing_units = self._connection.execute("SELECT DISTINCT unit FROM ledger WHERE mission_id = ?", (entry.mission_id,)).fetchall()
        if existing_units and any(row["unit"] != entry.unit for row in existing_units):
            raise LedgerError("mission cannot mix ledger units without an explicit conversion")
        self._connection.execute("INSERT INTO ledger VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (entry.entry_id, entry.kind, entry.mission_id, entry.category, str(entry.amount), entry.unit, entry.status, entry.provenance, entry.provider_receipt))
        self._connection.commit()
        return entry

    def _next_id(self, prefix: str) -> str:
        count = self._connection.execute("SELECT COUNT(*) AS n FROM ledger WHERE kind = ?", (prefix,)).fetchone()["n"]
        return f"{prefix}-{count + 1:03d}"

    @staticmethod
    def _validate(mission_id: str, category: str, amount: str, unit: str, provenance: str) -> Decimal:
        if not mission_id.strip() or not category.strip():
            raise LedgerError("mission and category are required")
        if not unit.strip():
            raise LedgerError("unit is required")
        if not provenance.strip():
            raise LedgerError("provenance is required")
        try:
            value = Decimal(amount)
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise LedgerError("amount must be numeric") from exc
        if not value.is_finite():
            raise LedgerError("amount must be finite")
        if value < 0:
            raise LedgerError("amount cannot be negative")
        return value


def _row(row: sqlite3.Row) -> LedgerEntry:
    return LedgerEntry(row["entry_id"], row["kind"], row["mission_id"], row["category"], Decimal(row["amount"]), row["unit"], row["status"], row["provenance"], row["provider_receipt"])
