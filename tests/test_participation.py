import pytest

from future_radio_os.participation import ParticipationError, ParticipationRegistry


def test_bounded_opportunity_requires_claim_and_review_before_acceptance():
    registry = ParticipationRegistry()
    registry.create("opp-001", mission_id="mission-001", deliverable="test report", eligible_participants=["alice"])
    with pytest.raises(ParticipationError, match="claim"):
        registry.submit("opp-001", participant="alice", evidence_ids=["e-001"])
    registry.claim("opp-001", participant="alice")
    registry.submit("opp-001", participant="alice", evidence_ids=["e-001"])
    with pytest.raises(ParticipationError, match="review"):
        registry.complete("opp-001")
    registry.review("opp-001", accepted=True, reviewer="leo")
    receipt = registry.complete("opp-001")
    assert receipt["status"] == "accepted"
    assert receipt["mission_event_authorized"] is True


def test_rejected_submission_can_request_changes_and_unanswered_is_not_consent():
    registry = ParticipationRegistry()
    registry.create("opp-002", mission_id="mission-001", deliverable="review", eligible_participants=["alice"])
    assert registry.get("opp-002").status == "open"
    registry.claim("opp-002", participant="alice")
    registry.submit("opp-002", participant="alice", evidence_ids=["e-002"])
    registry.review("opp-002", accepted=False, reviewer="leo", changes="include reproduction steps")
    assert registry.get("opp-002").status == "changes_requested"
    assert registry.get("opp-002").changes == "include reproduction steps"


def test_eligibility_expiration_scope_and_payment_states_are_explicit():
    registry = ParticipationRegistry()
    registry.create("opp-003", mission_id="mission-001", deliverable="report", eligible_participants=["alice"])
    with pytest.raises(ParticipationError, match="eligible"):
        registry.claim("opp-003", participant="bob")
    registry.claim("opp-003", participant="alice")
    registry.submit("opp-003", participant="alice", evidence_ids=["e-003"])
    registry.review("opp-003", accepted=True, reviewer="leo")
    registry.complete("opp-003")
    registry.agree_payment("opp-003", amount_usd=25)
    assert registry.get("opp-003").payment_status == "agreed"
    with pytest.raises(ParticipationError, match="authorization"):
        registry.mark_paid("opp-003")
    registry.authorize_payment("opp-003", approval_id="pay-approval")
    registry.mark_paid("opp-003", provider_receipt="provider-001")
    assert registry.get("opp-003").payment_status == "paid"
