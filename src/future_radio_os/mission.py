from dataclasses import dataclass, field
from typing import Literal


MissionStatus = Literal[
    "proposed", "ready", "active", "verifying", "resolved", "blocked", "failed", "cancelled", "reopened"
]
TaskStatus = Literal["unclaimed", "claimed", "accepted"]


class InvalidMissionTransition(ValueError):
    """Raised when a mission or task transition violates its contract."""


@dataclass
class TaskRecord:
    task_id: str
    depends_on: list[str] = field(default_factory=list)
    status: TaskStatus = "unclaimed"
    claimed_by: str | None = None
    evidence_ids: list[str] = field(default_factory=list)


@dataclass
class MissionStateMachine:
    mission_id: str
    problem_id: str
    goal: str
    acceptance_tests: list[str]
    status: MissionStatus = "proposed"
    tasks: dict[str, TaskRecord] = field(default_factory=dict)
    completion_evidence: dict[str, list[str]] = field(default_factory=dict)
    failure: dict[str, object] | None = None

    def __post_init__(self) -> None:
        if not self.mission_id.strip() or not self.problem_id.strip() or not self.goal.strip():
            raise ValueError("mission_id, problem_id, and goal are required")
        if not self.acceptance_tests or any(not item.strip() for item in self.acceptance_tests):
            raise ValueError("at least one acceptance test is required")
        if len(set(self.acceptance_tests)) != len(self.acceptance_tests):
            raise ValueError("acceptance tests must be unique")

    def add_task(self, task_id: str, depends_on: list[str] | None = None) -> None:
        if not task_id.strip():
            raise ValueError("task_id is required")
        if task_id in self.tasks:
            raise InvalidMissionTransition(f"task {task_id!r} already exists")
        dependencies = list(depends_on or [])
        if task_id in dependencies:
            raise InvalidMissionTransition("task cannot depend on itself")
        unknown = [item for item in dependencies if item not in self.tasks]
        if unknown:
            raise KeyError(unknown[0])
        self.tasks[task_id] = TaskRecord(task_id=task_id, depends_on=dependencies)

    def transition(self, target: MissionStatus, *, authorized: bool = False) -> None:
        allowed: dict[str, set[str]] = {
            "proposed": {"ready", "cancelled"},
            "ready": {"active", "blocked", "cancelled"},
            "active": {"verifying", "blocked", "failed", "cancelled"},
            "verifying": {"resolved", "failed", "reopened"},
            "blocked": {"ready", "cancelled"},
            "failed": {"reopened", "cancelled"},
            "reopened": {"active", "cancelled"},
            "resolved": {"reopened"},
            "cancelled": set(),
        }
        if target not in allowed.get(self.status, set()):
            raise InvalidMissionTransition(f"cannot transition {self.status!r} to {target!r}")
        if target == "resolved":
            if not authorized:
                raise InvalidMissionTransition("resolved requires authorized sign-off")
            missing = [item for item in self.acceptance_tests if item not in self.completion_evidence]
            if missing:
                raise InvalidMissionTransition(
                    f"acceptance evidence missing for: {', '.join(missing)}"
                )
        self.status = target

    def claim_task(self, task_id: str, *, actor_id: str) -> None:
        task = self._task(task_id)
        if not actor_id.strip():
            raise ValueError("actor_id is required")
        if task.status == "accepted":
            raise InvalidMissionTransition(f"task {task_id!r} is already accepted")
        task.status = "claimed"
        task.claimed_by = actor_id

    def complete_task(self, task_id: str, *, actor_id: str, evidence_ids: list[str]) -> None:
        task = self._task(task_id)
        self._require_dependencies(task)
        if task.status != "claimed" or task.claimed_by != actor_id:
            raise InvalidMissionTransition(f"task {task_id!r} must be claimed by actor {actor_id!r}")
        if not evidence_ids:
            raise InvalidMissionTransition("task completion requires evidence")
        task.status = "accepted"
        task.evidence_ids = list(evidence_ids)

    def record_acceptance(self, test_name: str, *, evidence_ids: list[str]) -> None:
        if test_name not in self.acceptance_tests:
            raise KeyError(test_name)
        if test_name in self.completion_evidence:
            raise InvalidMissionTransition(f"acceptance test {test_name!r} already recorded")
        if not evidence_ids:
            raise InvalidMissionTransition("acceptance requires evidence")
        self.completion_evidence[test_name] = list(evidence_ids)

    def fail(self, *, reason: str, evidence_ids: list[str]) -> None:
        if self.status not in {"active", "verifying"}:
            raise InvalidMissionTransition(f"cannot fail mission from {self.status!r}")
        if not reason.strip() or not evidence_ids:
            raise InvalidMissionTransition("failure requires a reason and evidence")
        self.failure = {"reason": reason, "evidence_ids": list(evidence_ids)}
        self.status = "failed"

    def reopen(self) -> None:
        if self.status not in {"failed", "resolved"}:
            raise InvalidMissionTransition(f"cannot reopen mission from {self.status!r}")
        self.status = "active"

    def _task(self, task_id: str) -> TaskRecord:
        try:
            return self.tasks[task_id]
        except KeyError as exc:
            raise KeyError(task_id) from exc

    def _require_dependencies(self, task: TaskRecord) -> None:
        incomplete = [
            dependency for dependency in task.depends_on if self.tasks[dependency].status != "accepted"
        ]
        if incomplete:
            raise InvalidMissionTransition(
                f"task {task.task_id!r} has incomplete dependency: {incomplete[0]}"
            )
