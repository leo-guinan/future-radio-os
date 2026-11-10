import pytest

from future_radio_os.graph import TemporalGraph, GraphError


def test_graph_preserves_typed_provenance_and_as_of_projection():
    graph = TemporalGraph()
    graph.add_node("person-1", "person")
    graph.add_node("project-1", "project")
    graph.add_edge("person-1", "created", "project-1", confidence=0.99, observed_at="2026-01-01T00:00:00Z", recorded_at="2026-01-02T00:00:00Z", source_ids=["source-1"])
    graph.add_edge("person-1", "created", "project-1", confidence=0.99, observed_at="2026-02-01T00:00:00Z", recorded_at="2026-02-02T00:00:00Z", source_ids=["source-2"])

    assert len(graph.edges_as_of("2026-01-15T00:00:00Z")) == 1
    assert graph.edges_as_of("2026-01-15T00:00:00Z")[0].source_ids == ["source-1"]


def test_missing_edge_is_hypothesis_not_verified_fact():
    graph = TemporalGraph()
    graph.add_node("project-1", "project")
    graph.add_node("capability-1", "capability")

    hypothesis = graph.propose_missing_edge("project-1", "depends_on", "capability-1", evidence_ids=["e-001"], estimated_cost_usd=2.0, falsifier="source contradicts dependency")

    assert hypothesis.status == "hypothesis"
    assert hypothesis.verified is False
    assert hypothesis.falsifier == "source contradicts dependency"


def test_low_confidence_edges_cannot_be_presented_as_verified():
    graph = TemporalGraph()
    graph.add_node("a", "project")
    graph.add_node("b", "problem")
    graph.add_edge("a", "solves", "b", confidence=0.4, observed_at="2026-01-01T00:00:00Z", recorded_at="2026-01-01T00:00:00Z", source_ids=["e"])
    with pytest.raises(GraphError, match="verified"):
        graph.verified_edges()


def test_invalid_edges_and_node_types_fail_closed():
    graph = TemporalGraph()
    graph.add_node("a", "project")
    with pytest.raises(GraphError, match="node"):
        graph.add_edge("a", "solves", "missing", confidence=1, observed_at="2026-01-01T00:00:00Z", recorded_at="2026-01-01T00:00:00Z", source_ids=["e"])
