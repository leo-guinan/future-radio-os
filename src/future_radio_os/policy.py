from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from future_radio_os.contracts import SessionPolicyContract


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    action: str
    reason: str
    recorded_at: str


class ExecutionPolicy:
    """Fail-closed authority boundary for bounded local execution."""

    def __init__(self, contract: SessionPolicyContract):
        self.contract = contract
        self.spent_compute_usd = 0.0
        self.spent_human_minutes = 0
        self._approvals: dict[str, str] = {}
        self._revoked_reason: str | None = None
        self.decisions: list[PolicyDecision] = []

    def approve(self, action: str, *, approval_id: str) -> None:
        if action not in self.contract.required_approvals:
            raise ValueError(f"{action!r} is not an approval-gated action")
        if not approval_id.strip():
            raise ValueError("approval_id is required")
        self._approvals[action] = approval_id

    def revoke(self, reason: str) -> None:
        if not reason.strip():
            raise ValueError("revocation reason is required")
        self._revoked_reason = reason
        self._record(False, "authority_revoked", f"authority revoked: {reason}")

    def authorize(
        self,
        *,
        tool: str,
        environment: str,
        action: str,
        compute_usd: float,
        human_minutes: int,
        data_scope: list[str] | None = None,
        context_text: str | None = None,
    ) -> PolicyDecision:
        del context_text  # Untrusted text never changes authority.
        if compute_usd < 0 or human_minutes < 0:
            return self._record(False, action, "negative resource request")
        if self._revoked_reason:
            return self._record(False, action, f"authority revoked: {self._revoked_reason}")
        if tool not in self.contract.allowed_tools:
            return self._record(False, action, f"tool {tool!r} is not allowed")
        if environment not in self.contract.allowed_environments:
            return self._record(False, action, f"environment {environment!r} is not allowed")
        requested_scope = set(data_scope or [])
        allowed_scope = set(self.contract.data_scope)
        if not requested_scope.issubset(allowed_scope):
            return self._record(False, action, "data scope exceeds policy")
        if self.spent_compute_usd + compute_usd > self.contract.compute_usd_max:
            return self._record(False, action, "compute budget exhausted")
        if self.spent_human_minutes + human_minutes > self.contract.human_minutes_max:
            return self._record(False, action, "human time budget exhausted")
        if action in self.contract.required_approvals and action not in self._approvals:
            return self._record(False, action, f"explicit approval required for {action}")
        self.spent_compute_usd += compute_usd
        self.spent_human_minutes += human_minutes
        return self._record(True, action, "authorized")

    def _record(self, allowed: bool, action: str, reason: str) -> PolicyDecision:
        decision = PolicyDecision(
            allowed=allowed,
            action=action,
            reason=reason,
            recorded_at=datetime.now(timezone.utc).isoformat(),
        )
        self.decisions.append(decision)
        return decision
