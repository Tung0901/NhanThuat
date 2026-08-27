from backend.app.engine.philosophies.router import PhilosophyRouter, PhilosophyType


def test_philosophy_router_initialization() -> None:
    router = PhilosophyRouter()
    assert len(router.engines) == 9
    assert PhilosophyType.RHETORIC in router.engines
    assert PhilosophyType.CONFUCIAN in router.engines
    assert PhilosophyType.LEGALISM in router.engines
    assert PhilosophyType.TAOISM in router.engines
    assert PhilosophyType.XUNZI in router.engines
    assert PhilosophyType.SUNZI in router.engines
    assert PhilosophyType.STOICISM in router.engines
    assert PhilosophyType.BEHAVIORAL in router.engines
    assert PhilosophyType.HUMAN_NATURE in router.engines


def test_ai_router_corrected_technical_directives() -> None:
    router = PhilosophyRouter()
    constraints = router.get_router_constraints()
    
    # 1. Deterministic AI Execution
    assert constraints["global_ai_temperature"] == 0.1
    assert constraints["fixed_reproducibility_seed"] == 42
    assert "Structured input/output schemas" in constraints["consistency_enforcement"]
    
    # 2. Canonical Source Registry
    registry = constraints["canonical_source_registry"]
    assert registry["knowledge_units"] == "knowledge/units/"
    assert registry["schemas"] == "schemas/"
    assert registry["docs_knowledge"] == "docs/knowledge/"
    assert registry["docs_departments"] == "docs/departments/"
    assert registry["governance"] == "governance/"
    
    # 3. Version Resolution Policy (Latest Approved + Active + Compatible Version)
    v_policy = constraints["version_resolution_policy"]
    assert v_policy["resolution_strategy"] == "LATEST_APPROVED_ACTIVE_COMPATIBLE"
    assert v_policy["enforce_pinning"] is True
    assert v_policy["record_provenance_checksum"] is True

    # 4. Fallback Handling for Unverified Query
    unverified_res = router.route({"scenario_type": "unsupported_unknown", "intent": ""})
    assert unverified_res["status"] == "error"
    assert unverified_res["error_code"] == "INSUFFICIENT_VERIFIED_KNOWLEDGE"


def test_philosophy_engines_metadata_standardization() -> None:
    router = PhilosophyRouter()
    for phil_type, engine_data in router.engines.items():
        assert "metadata" in engine_data, f"Missing metadata in {phil_type}"
        meta = engine_data["metadata"]
        assert "philosophy_id" in meta
        assert "philosophy_name" in meta
        assert "version" in meta
        assert "source_document" in meta
        assert "supported_domains" in meta
        assert "supported_personas" in meta
        assert "preferred_reasoning_modes" in meta
        assert "compatible_lenses" in meta
        assert "incompatible_lenses" in meta
        assert "confidence_modifier" in meta
        assert "governance_status" in meta
        assert "last_reviewed" in meta


def test_scenario_routing_customer_objection() -> None:
    router = PhilosophyRouter()
    result = router.route({
        "scenario_type": "objection",
        "intent": "Customer says price is too high",
        "keywords": ["price objection", "tu choi"]
    })
    assert result["primary_philosophy"] == PhilosophyType.RHETORIC.value
    assert result["secondary_philosophy"] == PhilosophyType.TAOISM.value
    assert result["lens_weights"][PhilosophyType.RHETORIC.value] == 0.70
    assert result["lens_weights"][PhilosophyType.TAOISM.value] == 0.30
    assert result["global_ai_temperature"] == 0.1
    assert "knowledge_units" in result["canonical_source_registry"]


def test_scenario_routing_leadership() -> None:
    router = PhilosophyRouter()
    result = router.route({
        "scenario_type": "leadership",
        "intent": "Executive team coaching and culture building",
        "keywords": ["duc tri", "quan tu"]
    })
    assert result["primary_philosophy"] == PhilosophyType.CONFUCIAN.value
    assert result["secondary_philosophy"] == PhilosophyType.XUNZI.value


def test_scenario_routing_corporate_governance() -> None:
    router = PhilosophyRouter()
    result = router.route({
        "scenario_type": "governance",
        "intent": "Auditing SOP compliance and title performance",
        "keywords": ["hinh danh", "phap gia"]
    })
    assert result["primary_philosophy"] == PhilosophyType.LEGALISM.value
    assert result["secondary_philosophy"] == PhilosophyType.CONFUCIAN.value


def test_scenario_routing_org_transformation() -> None:
    router = PhilosophyRouter()
    result = router.route({
        "scenario_type": "transformation",
        "intent": "Reorganizing organizational structure smoothly",
        "keywords": ["tiêu dao du", "vô vi"]
    })
    assert result["primary_philosophy"] == PhilosophyType.TAOISM.value
    assert result["secondary_philosophy"] == PhilosophyType.XUNZI.value


def test_scenario_routing_training_coaching() -> None:
    router = PhilosophyRouter()
    result = router.route({
        "scenario_type": "training",
        "intent": "Employee onboarding and mentorship coaching",
        "keywords": ["khuyen hoc", "tuan tu", "dao tao"]
    })
    assert result["primary_philosophy"] == PhilosophyType.XUNZI.value
    assert result["secondary_philosophy"] == PhilosophyType.CONFUCIAN.value
    assert result["primary_engine_data"]["engine_name"] == "Xunzi Engine"


def test_scenario_routing_org_conflict_trilens() -> None:
    router = PhilosophyRouter()
    result = router.route({
        "scenario_type": "conflict",
        "intent": "Resolving deep cross-departmental dispute",
        "keywords": ["org conflict", "dispute mediation"]
    })
    assert result["primary_philosophy"] == PhilosophyType.CONFUCIAN.value
    assert result["secondary_philosophy"] == PhilosophyType.LEGALISM.value
    assert result["tertiary_philosophy"] == PhilosophyType.TAOISM.value
    assert len(result["lenses"]) == 3
    assert result["lens_weights"][PhilosophyType.CONFUCIAN.value] == 0.60
    assert result["lens_weights"][PhilosophyType.LEGALISM.value] == 0.30
    assert result["lens_weights"][PhilosophyType.TAOISM.value] == 0.10


def test_program_8_program_9_router_outputs() -> None:
    router = PhilosophyRouter()
    result = router.route({
        "scenario_type": "training",
        "intent": "Behavior correction and mentorship",
        "keywords": ["khuyen hoc", "vĩ"]
    })
    # Check Program 8 Requirements
    assert "lenses" in result
    assert "lens_weights" in result
    assert "lens_confidence_scores" in result
    assert "conflict_resolution" in result
    assert "explanation" in result
    assert isinstance(result["explanation"], str)

    # Check Lens structure inside lenses list
    primary_lens = result["lenses"][0]
    assert primary_lens["priority"] == 1
    assert primary_lens["philosophy_id"] == "LENS-XUNZI"
    assert primary_lens["weight"] == 0.70
    assert "confidence_score" in primary_lens
    assert "provenance_checksum" in primary_lens
    assert primary_lens["pinned_version"] == "1.1.0"

    # Check Program 9 Requirements (Metadata Versioning & SemVer)
    meta = primary_lens["metadata"]
    assert meta["version"] == "1.1.0"
    assert meta["governance_status"] == "frozen"
