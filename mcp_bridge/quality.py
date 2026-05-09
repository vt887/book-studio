from typing import Any

from mcp_bridge import db


_CONTRADICTIONS = {
    frozenset({"supports", "contrasts"}),
    frozenset({"extends", "contrasts"}),
    frozenset({"depends_on", "contrasts"}),
}


def _completeness_for_concept(concept: dict[str, Any]) -> float:
    required = [
        bool(concept.get("concept_id")),
        bool(concept.get("name")),
        "definition" in concept,
        "summary" in concept,
        isinstance(concept.get("importance_score", 0.5), (float, int)),
        isinstance(concept.get("source_chunks", []), list),
        isinstance(concept.get("embedding", []), list),
        isinstance(concept.get("tags", []), list),
        isinstance(concept.get("applicable_roles", []), list),
    ]
    return sum(1 for x in required if x) / len(required)


async def score_concept_quality(pg_pool, concept: dict[str, Any]) -> dict[str, float]:
    source_chunks = [str(x) for x in concept.get("source_chunks", [])]
    grounding_score = 1.0
    if source_chunks:
        valid = await db.valid_chunk_count(pg_pool, source_chunks)
        grounding_score = valid / len(source_chunks)

    completeness_score = _completeness_for_concept(concept)

    # Deterministic placeholder until contradiction-check rules are added.
    consistency_score = 1.0

    quality_score = (grounding_score + completeness_score + consistency_score) / 3.0

    return {
        "grounding_score": float(grounding_score),
        "completeness_score": float(completeness_score),
        "consistency_score": float(consistency_score),
        "quality_score": float(quality_score),
    }


def relation_consistency_score(relations_by_target: dict[str, set[str]]) -> float:
    if not relations_by_target:
        return 1.0

    contradictions = 0
    total_targets = 0

    for _, rel_types in relations_by_target.items():
        if not rel_types:
            continue
        total_targets += 1
        for pair in _CONTRADICTIONS:
            if pair.issubset(rel_types):
                contradictions += 1
                break

    if total_targets == 0:
        return 1.0

    return max(0.0, 1.0 - (contradictions / total_targets))
