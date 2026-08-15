"""Tests for Nhan Thuat runtime components with deep behavior coverage."""

import pytest

from nhan_thuat.models import EvidenceSummary, KnowledgeUnit
from nhan_thuat.runtime.evaluator import KnowledgeEvaluator
from nhan_thuat.runtime.graph import CircularDependencyError, KnowledgeGraph
from nhan_thuat.runtime.prompt_builder import PromptBuilder
from nhan_thuat.runtime.resolver import KnowledgeResolver


@pytest.fixture
def base_unit():
    return lambda id, deps=(), title="Unit", unit_type="principle", risks=(): KnowledgeUnit(
        id=id,
        type=unit_type,
        status="frozen",
        version="1.0",
        title=title,
        summary="Summary of " + title,
        primary_domain="tu-than",
        secondary_domains=(),
        definition="Definition.",
        conditions=(),
        exceptions=(),
        applications={},
        risks=risks,
        evidence=EvidenceSummary(level="supported", references=["ref1"]),
        relations={"depends_on": deps},
        tags=(title.lower().replace(" ", ""),)
    )

@pytest.fixture
def graph_units(base_unit):
    return [
        base_unit("NT-PRINCIPLE-0001", ("NT-PRINCIPLE-0002",), "Node A"),
        base_unit("NT-PRINCIPLE-0002", ("NT-PRINCIPLE-0003",), "Node B"),
        base_unit("NT-PRINCIPLE-0003", (), "Node C"),
        base_unit("NT-PRINCIPLE-0004", (), "Node D"),
    ]

@pytest.fixture
def circular_units(base_unit):
    return [
        base_unit("NT-PRINCIPLE-0001", ("NT-PRINCIPLE-0002",), "Node A"),
        base_unit("NT-PRINCIPLE-0002", ("NT-PRINCIPLE-0001",), "Node B"),
    ]

# GRAPH TESTS
def test_graph_empty():
    graph = KnowledgeGraph([])
    assert graph.get_dependencies("ANY") == []

def test_graph_isolated_node(graph_units):
    graph = KnowledgeGraph(graph_units)
    deps = graph.get_dependencies("NT-PRINCIPLE-0004")
    assert len(deps) == 0

def test_graph_dependency_chain(graph_units):
    graph = KnowledgeGraph(graph_units)
    deps = graph.get_dependencies("NT-PRINCIPLE-0001")
    assert any(u.id == "NT-PRINCIPLE-0002" for u in deps)

def test_graph_circular_dependency(circular_units):
    with pytest.raises(CircularDependencyError):
        graph = KnowledgeGraph(circular_units)
        graph.get_transitive_dependencies("NT-PRINCIPLE-0001")

def test_graph_invalid_dependency(base_unit):
    units = [base_unit("NT-PRINCIPLE-0001", ("NT-MISSING-0001",), "Node A")]
    graph = KnowledgeGraph(units)
    deps = graph.get_dependencies("NT-PRINCIPLE-0001")
    assert len(deps) == 0

# RESOLVER TESTS
@pytest.fixture
def resolver_units(base_unit):
    return [
        base_unit("NT-PRINCIPLE-0001", title="Apple Banana"),
        base_unit("NT-PRINCIPLE-0002", title="Banana Cherry"),
        base_unit("NT-PRINCIPLE-0003", title="Date Elderberry"),
    ]

def test_resolver_no_match(resolver_units):
    resolver = KnowledgeResolver(resolver_units)
    assert resolver.resolve("Zebra") == []

def test_resolver_empty_query(resolver_units):
    resolver = KnowledgeResolver(resolver_units)
    assert resolver.resolve("") == []

def test_resolver_ambiguous_multiple_matches(resolver_units):
    resolver = KnowledgeResolver(resolver_units)
    results = resolver.resolve("Banana")
    assert len(results) == 2

def test_resolver_ranking(resolver_units):
    resolver = KnowledgeResolver(resolver_units)
    results = resolver.resolve("Apple")
    assert len(results) >= 1
    assert results[0].id == "NT-PRINCIPLE-0001"

# PROMPT BUILDER TESTS
def test_prompt_builder_empty():
    builder = PromptBuilder()
    assert builder.build_context([]).strip() == "# Nhan Thuat Knowledge Context"

def test_prompt_builder_duplicate_units(base_unit):
    builder = PromptBuilder()
    u1 = base_unit("NT-PRINCIPLE-0001", title="Unique")
    context = builder.build_context([u1, u1])
    assert context.count("NT-PRINCIPLE-0001") >= 1

def test_prompt_builder_ordering(base_unit):
    builder = PromptBuilder()
    u1 = base_unit("NT-PRINCIPLE-0001", title="First")
    u2 = base_unit("NT-PRINCIPLE-0002", title="Second")
    context = builder.build_context([u1, u2])
    idx1 = context.find("NT-PRINCIPLE-0001")
    idx2 = context.find("NT-PRINCIPLE-0002")
    assert idx1 != -1 and idx2 != -1
    assert idx1 < idx2

def test_prompt_builder_oversized_context(base_unit):
    builder = PromptBuilder()
    units = [base_unit(f"NT-PRINCIPLE-{i:04d}", title=f"Unit {i}") for i in range(100)]
    context = builder.build_context(units)
    assert len(context) > 0

# EVALUATOR TESTS
@pytest.fixture
def evaluator_units(base_unit):
    ap1 = base_unit("NT-ANTI-PATTERN-0001", title="Micromanagement", unit_type="anti-pattern", risks=("Burnout", "Low morale"))
    ap2 = base_unit("NT-ANTI-PATTERN-0002", title="Silo Thinking", unit_type="anti-pattern", risks=("Poor communication",))
    return [ap1, ap2]

def test_evaluator_no_anti_pattern(evaluator_units):
    evaluator = KnowledgeEvaluator()
    res = evaluator.evaluate("The team is highly autonomous.", evaluator_units)
    assert len(res["violations"]) == 0

def test_evaluator_single_anti_pattern(evaluator_units):
    evaluator = KnowledgeEvaluator()
    res = evaluator.evaluate("I constantly monitor my employees causing Burnout.", evaluator_units)
    assert len(res["violations"]) > 0

def test_evaluator_multiple_anti_patterns(evaluator_units):
    evaluator = KnowledgeEvaluator()
    res = evaluator.evaluate("Burnout from Micromanagement and Poor communication from Silo Thinking.", evaluator_units)
    assert len(res["violations"]) >= 2

def test_evaluator_contradiction_edge_case(evaluator_units):
    evaluator = KnowledgeEvaluator()
    res = evaluator.evaluate("We avoid Burnout.", evaluator_units)
    assert "score" in res
