from components.planner import plan_subtopics_and_queries
from components.crawler import crawl_by_plan
from components.cleaner import clean_and_chunk, dedupe_chunks
from components.router import route_chunks
from components.summarizer import summarize_with_state
from components.reducer import reduce_subtopic, reduce_final
from components.exporter import export_json
from schemas import SubtopicResult
from datetime import datetime

def run_topic_pipeline(topic: str, subtopics=None) -> dict:
    plan = plan_subtopics_and_queries(topic, subtopics)
    docs = crawl_by_plan(plan)
    chunks = dedupe_chunks(clean_and_chunk(docs))
    routed = route_chunks(chunks, plan)

    results: list[SubtopicResult] = []
    for name in sorted({c.subtopic for c in routed}):
        cs = [c for c in routed if c.subtopic == name]
        state = None
        outs = []
        for c in cs:
            state, o = summarize_with_state(c.text, prev_state=state)
            outs.append(o)
        results.append(reduce_subtopic(name, outs, [c.source_url for c in cs]))

    final = reduce_final(topic, results, generated_at=datetime.now().isoformat())
    export_json(final, f"data/output/{topic}_summary.json")
    return final
