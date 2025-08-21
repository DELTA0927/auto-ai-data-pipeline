from schemas import Plan, Chunk
import re

def route_chunks(chunks: list[Chunk], plan: Plan) -> list[Chunk]:
    kws = {sp.name: [sp.name] for sp in plan.subtopics}
    for c in chunks:
        best, score = plan.subtopics[0].name, -1
        for name, keys in kws.items():
            s = sum(1 for k in keys if re.search(k, c.text, re.I))
            if s > score: best, score = name, s
        c.subtopic = best
    return chunks
