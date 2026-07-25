# NhanThuat Agent Routing

These instructions apply to work inside this repository.

## Governing Authority

Read `PROJECT_CONSTITUTION.md` and all files under `governance/` before making
governance, architecture, schema, taxonomy, ontology, Epic status, approval, or
Frozen-state changes.

Only the Product Owner may approve or freeze an Epic. Agents may implement,
validate, test, document, review, and prepare evidence, but must not self-approve
or self-freeze project content.

Frozen content must not be modified directly. Do not modify EPIC 0 or EPIC 1
Frozen deliverables except through the formal change-control process.

Do not implement EPIC 2 as part of routing setup.

## Main Agent

Use the repository-scoped main agent configuration:

- model: `gpt-5.5`
- reasoning effort: `high`

The main agent handles approved implementation, YAML/JSON authoring, validators,
tests, documentation updates, routine fixes, validation, and Git operations.

Routine implementation stays with the main agent.

## Knowledge Architecture Reviewer

Use `.codex/agents/knowledge-architecture-reviewer.toml` for the reviewer
configuration:

- model: `gpt-5.6`
- reasoning effort: `xhigh`

Delegate to `knowledge-architecture-reviewer` for Epic analysis, architecture
decisions, taxonomy or ontology changes, schema changes, breaking changes,
governance changes, and review before Frozen.

The reviewer must not approve or freeze an Epic.

Do not claim that the model was switched unless the reviewer subagent was
actually invoked.
