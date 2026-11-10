from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ContractStatus = Literal["planned", "estimated", "modeled", "verified", "unknown"]
MissionStatus = Literal[
    "proposed", "ready", "active", "verifying", "resolved", "blocked", "failed", "cancelled", "reopened"
]
ArtifactStatus = Literal[
    "local", "validated", "staged", "deployed", "running", "degraded", "stopped", "retired"
]
SolutionStatus = Literal[
    "solved", "partially_solved", "disproven", "superseded", "needs_revalidation"
]


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Provenance(ContractModel):
    status: ContractStatus
    source_ids: list[str] = Field(min_length=1)

    @field_validator("source_ids")
    @classmethod
    def source_ids_must_be_nonempty(cls, values: list[str]) -> list[str]:
        if any(not value.strip() for value in values):
            raise ValueError("source_ids must contain non-empty strings")
        return values


class ProblemContract(ContractModel):
    id: str = Field(min_length=1)
    schema_version: Literal[1]
    statement: str = Field(min_length=1)
    provenance: Provenance


class Budget(ContractModel):
    human_minutes_max: int = Field(ge=0)
    compute_usd_max: float = Field(ge=0)


class MissionContract(ContractModel):
    id: str = Field(min_length=1)
    schema_version: Literal[1]
    problem_id: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    acceptance_tests: list[str] = Field(min_length=1)
    budget: Budget
    status: MissionStatus
    provenance: Provenance

    @field_validator("acceptance_tests")
    @classmethod
    def acceptance_tests_must_be_named(cls, values: list[str]) -> list[str]:
        if any(not value.strip() for value in values):
            raise ValueError("acceptance_tests must contain non-empty strings")
        return values


class TaskContract(ContractModel):
    id: str = Field(min_length=1)
    schema_version: Literal[1]
    mission_id: str = Field(min_length=1)
    deliverable: str = Field(min_length=1)
    status: Literal["unclaimed", "claimed", "active", "submitted", "accepted", "rejected"]
    provenance: Provenance


class EvidenceContract(ContractModel):
    id: str = Field(min_length=1)
    schema_version: Literal[1]
    kind: str = Field(min_length=1)
    source: str = Field(min_length=1)
    status: Literal["pending", "accepted", "rejected"]
    provenance: Provenance


class SolutionContract(ContractModel):
    id: str = Field(min_length=1)
    schema_version: Literal[1]
    problem_signature: str = Field(min_length=1)
    assumptions: list[str]
    procedure: list[str] = Field(min_length=1)
    dependencies: list[str]
    tests: list[str] = Field(min_length=1)
    evidence_ids: list[str] = Field(min_length=1)
    limitations: list[str] = Field(min_length=1)
    status: SolutionStatus
    provenance: Provenance


class CapabilityContract(ContractModel):
    id: str = Field(min_length=1)
    schema_version: Literal[1]
    version: str = Field(min_length=1)
    input_contract: str = Field(min_length=1)
    output_contract: str = Field(min_length=1)
    provenance: Provenance


class ArtifactContract(ContractModel):
    id: str = Field(min_length=1)
    schema_version: Literal[1]
    kind: str = Field(min_length=1)
    content_hash: str = Field(min_length=8)
    source_event_ids: list[str] = Field(min_length=1)
    status: ArtifactStatus = "local"
    provenance: Provenance


class SessionPolicyContract(ContractModel):
    id: str = Field(min_length=1)
    schema_version: Literal[1]
    goal: str = Field(min_length=1)
    human_minutes_max: int = Field(ge=0)
    compute_usd_max: float = Field(ge=0)
    allowed_tools: list[str]
    allowed_environments: list[Literal["local", "staging", "production"]]
    data_scope: list[str]
    required_approvals: list[str]
    completion_tests: list[str] = Field(min_length=1)
    stop_conditions: list[str] = Field(min_length=1)
    provenance: Provenance


CONTRACTS: dict[str, type[ContractModel]] = {
    "problem": ProblemContract,
    "mission": MissionContract,
    "task": TaskContract,
    "evidence": EvidenceContract,
    "solution": SolutionContract,
    "capability": CapabilityContract,
    "artifact": ArtifactContract,
    "session_policy": SessionPolicyContract,
}


def validate_contract(kind: str, payload: dict[str, Any]) -> ContractModel:
    try:
        contract = CONTRACTS[kind]
    except KeyError as exc:
        raise ValueError(f"unknown contract kind: {kind}") from exc
    return contract.model_validate(payload)


def contract_schema_manifest() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "compatibility": "Readers must reject unknown future versions; additive changes require a new version or an explicitly compatible field policy.",
        "contracts": {kind: model.model_json_schema() for kind, model in CONTRACTS.items()},
    }
