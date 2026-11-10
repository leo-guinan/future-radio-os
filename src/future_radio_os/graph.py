from dataclasses import dataclass


class GraphError(ValueError):
    pass


@dataclass(frozen=True)
class Node:
    node_id: str
    node_type: str


@dataclass(frozen=True)
class Edge:
    source_id: str
    relation: str
    target_id: str
    confidence: float
    observed_at: str
    recorded_at: str
    source_ids: list[str]
    status: str = "observed"
    verified: bool = False


@dataclass(frozen=True)
class MissionHypothesis:
    source_id: str
    relation: str
    target_id: str
    evidence_ids: list[str]
    estimated_cost_usd: float
    falsifier: str
    status: str = "hypothesis"
    verified: bool = False


class TemporalGraph:
    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []
        self.hypotheses: list[MissionHypothesis] = []

    def add_node(self, node_id: str, node_type: str) -> None:
        if not node_id.strip() or not node_type.strip():
            raise GraphError("node ID and type are required")
        self.nodes[node_id] = Node(node_id, node_type)

    def add_edge(self, source_id: str, relation: str, target_id: str, *, confidence: float, observed_at: str, recorded_at: str, source_ids: list[str]) -> Edge:
        if source_id not in self.nodes or target_id not in self.nodes:
            raise GraphError("edge endpoints must reference known node")
        if not 0 <= confidence <= 1:
            raise GraphError("confidence must be between 0 and 1")
        if not source_ids:
            raise GraphError("edge provenance is required")
        edge = Edge(source_id, relation, target_id, confidence, observed_at, recorded_at, list(source_ids), verified=confidence >= 0.9)
        self.edges.append(edge)
        return edge

    def edges_as_of(self, recorded_at: str) -> list[Edge]:
        latest: dict[tuple[str, str, str], Edge] = {}
        for edge in self.edges:
            if edge.recorded_at <= recorded_at:
                key = (edge.source_id, edge.relation, edge.target_id)
                if key not in latest or latest[key].recorded_at < edge.recorded_at:
                    latest[key] = edge
        return list(latest.values())

    def verified_edges(self) -> list[Edge]:
        low_confidence = [edge for edge in self.edges if not edge.verified]
        if low_confidence:
            raise GraphError("low-confidence edge cannot be presented as verified")
        return list(self.edges)

    def propose_missing_edge(self, source_id: str, relation: str, target_id: str, *, evidence_ids: list[str], estimated_cost_usd: float, falsifier: str) -> MissionHypothesis:
        if source_id not in self.nodes or target_id not in self.nodes:
            raise GraphError("hypothesis endpoints must reference known node")
        if not evidence_ids or estimated_cost_usd < 0 or not falsifier.strip():
            raise GraphError("hypothesis requires evidence, non-negative cost, and falsifier")
        hypothesis = MissionHypothesis(source_id, relation, target_id, list(evidence_ids), estimated_cost_usd, falsifier)
        self.hypotheses.append(hypothesis)
        return hypothesis
