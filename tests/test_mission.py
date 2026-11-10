import pytest

from future_radio_os.mission import InvalidMissionTransition, MissionStateMachine


def make_mission() -> MissionStateMachine:
    return MissionStateMachine(
        mission_id="mission-001",
        problem_id="problem-001",
        goal="Complete a bounded build",
        acceptance_tests=["test-a", "test-b"],
    )


def test_mission_requires_valid_order_and_acceptance_evidence_before_resolution():
    mission = make_mission()
    mission.add_task("task-a")
    mission.add_task("task-b", depends_on=["task-a"])

    mission.transition("ready")
    mission.transition("active")
    with pytest.raises(InvalidMissionTransition, match="dependency"):
        mission.complete_task("task-b", actor_id="agent", evidence_ids=["e-b"])

    mission.claim_task("task-a", actor_id="agent")
    mission.complete_task("task-a", actor_id="agent", evidence_ids=["e-a"])
    mission.claim_task("task-b", actor_id="agent")
    mission.complete_task("task-b", actor_id="agent", evidence_ids=["e-b"])
    mission.record_acceptance("test-a", evidence_ids=["e-a"])
    mission.transition("verifying")
    with pytest.raises(InvalidMissionTransition, match="acceptance"):
        mission.transition("resolved", authorized=True)

    mission.record_acceptance("test-b", evidence_ids=["e-b"])
    mission.transition("resolved", authorized=True)
    assert mission.status == "resolved"
    assert mission.completion_evidence == {"test-a": ["e-a"], "test-b": ["e-b"]}


def test_agent_assertion_cannot_resolve_mission_without_authorized_transition():
    mission = make_mission()
    mission.transition("ready")
    mission.transition("active")
    mission.record_acceptance("test-a", evidence_ids=["e-a"])
    mission.record_acceptance("test-b", evidence_ids=["e-b"])
    mission.transition("verifying")

    with pytest.raises(InvalidMissionTransition, match="authorized"):
        mission.transition("resolved", authorized=False)
    assert mission.status == "verifying"


def test_failed_experiment_preserves_evidence_and_can_reopen():
    mission = make_mission()
    mission.transition("ready")
    mission.transition("active")
    mission.fail(reason="adapter unavailable", evidence_ids=["failure-evidence"])

    assert mission.status == "failed"
    assert mission.failure == {"reason": "adapter unavailable", "evidence_ids": ["failure-evidence"]}

    mission.reopen()
    assert mission.status == "active"


def test_unknown_tasks_and_duplicate_acceptance_are_rejected():
    mission = make_mission()
    with pytest.raises(KeyError, match="task-x"):
        mission.claim_task("task-x", actor_id="agent")
    with pytest.raises(KeyError, match="test-x"):
        mission.record_acceptance("test-x", evidence_ids=["e-x"])

    mission.record_acceptance("test-a", evidence_ids=["e-a"])
    with pytest.raises(InvalidMissionTransition, match="already recorded"):
        mission.record_acceptance("test-a", evidence_ids=["e-a-2"])
