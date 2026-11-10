from dataclasses import dataclass, field


class ParticipationError(ValueError):
    pass


@dataclass
class Opportunity:
    opportunity_id: str
    mission_id: str
    deliverable: str
    eligible_participants: list[str]
    status: str = "open"
    participant: str | None = None
    evidence_ids: list[str] = field(default_factory=list)
    reviewer: str | None = None
    changes: str | None = None
    payment_status: str = "none"
    payment_amount_usd: float | None = None
    payment_approval: str | None = None
    provider_receipt: str | None = None


class ParticipationRegistry:
    def __init__(self):
        self._opportunities: dict[str, Opportunity] = {}

    def create(self, opportunity_id: str, *, mission_id: str, deliverable: str, eligible_participants: list[str]) -> None:
        if opportunity_id in self._opportunities:
            raise ParticipationError("duplicate opportunity")
        if not eligible_participants:
            raise ParticipationError("eligibility must be explicit")
        self._opportunities[opportunity_id] = Opportunity(opportunity_id, mission_id, deliverable, list(eligible_participants))

    def get(self, opportunity_id: str) -> Opportunity:
        try:
            return self._opportunities[opportunity_id]
        except KeyError as exc:
            raise ParticipationError(f"unknown opportunity {opportunity_id}") from exc

    def claim(self, opportunity_id: str, *, participant: str) -> None:
        opportunity = self.get(opportunity_id)
        if participant not in opportunity.eligible_participants:
            raise ParticipationError("participant is not eligible")
        if opportunity.status not in {"open", "changes_requested"}:
            raise ParticipationError("opportunity is not claimable")
        opportunity.participant = participant
        opportunity.status = "claimed"

    def submit(self, opportunity_id: str, *, participant: str, evidence_ids: list[str]) -> None:
        opportunity = self.get(opportunity_id)
        if opportunity.participant != participant:
            raise ParticipationError("participant must claim the opportunity first")
        if not evidence_ids:
            raise ParticipationError("submission requires evidence")
        opportunity.evidence_ids = list(evidence_ids)
        opportunity.status = "submitted"

    def review(self, opportunity_id: str, *, accepted: bool, reviewer: str, changes: str | None = None) -> None:
        opportunity = self.get(opportunity_id)
        if opportunity.status != "submitted":
            raise ParticipationError("review requires a submitted deliverable")
        if not reviewer.strip():
            raise ParticipationError("reviewer is required")
        opportunity.reviewer = reviewer
        opportunity.changes = changes
        opportunity.status = "accepted" if accepted else "changes_requested"

    def complete(self, opportunity_id: str) -> dict[str, object]:
        opportunity = self.get(opportunity_id)
        if opportunity.status != "accepted":
            raise ParticipationError("accepted review is required before completion")
        opportunity.status = "completed"
        return {"status": "accepted", "mission_event_authorized": True, "evidence_ids": opportunity.evidence_ids}

    def agree_payment(self, opportunity_id: str, *, amount_usd: float) -> None:
        opportunity = self.get(opportunity_id)
        if opportunity.status != "completed":
            raise ParticipationError("payment requires accepted completion")
        if amount_usd < 0:
            raise ParticipationError("payment cannot be negative")
        opportunity.payment_amount_usd = amount_usd
        opportunity.payment_status = "agreed"

    def authorize_payment(self, opportunity_id: str, *, approval_id: str) -> None:
        opportunity = self.get(opportunity_id)
        if opportunity.payment_status != "agreed":
            raise ParticipationError("payment must be agreed before authorization")
        opportunity.payment_approval = approval_id
        opportunity.payment_status = "payable"

    def mark_paid(self, opportunity_id: str, *, provider_receipt: str | None = None) -> None:
        opportunity = self.get(opportunity_id)
        if opportunity.payment_status != "payable" or not opportunity.payment_approval:
            raise ParticipationError("payment authorization is required")
        if not provider_receipt:
            raise ParticipationError("provider receipt is required")
        opportunity.provider_receipt = provider_receipt
        opportunity.payment_status = "paid"
