from schemas import SubtopicResult

def reduce_subtopic(name: str, outs: list[dict], sources: list[str]) -> SubtopicResult:
    merged = " ".join(o["summary"] for o in outs)[:1500]
    return SubtopicResult(name=name, summary=merged, key_points=[], sources=sorted(set(sources)))

def reduce_final(topic: str, subs: list[SubtopicResult], generated_at: str) -> dict:
    return {
        "topic": topic,
        "generated_at": generated_at,
        "subtopics": [
            {"name": s.name, "summary": s.summary, "key_points": s.key_points, "sources": s.sources}
            for s in subs
        ]
    }
