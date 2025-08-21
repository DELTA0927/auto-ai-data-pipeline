from schemas import Plan, SubtopicPlan

DEFAULT_SUBTOPICS = ["개념","원인","주요 사례","현대 동향","전망"]

def plan_subtopics_and_queries(topic: str, subtopics=None) -> Plan:
    subs = subtopics or DEFAULT_SUBTOPICS
    plans = [SubtopicPlan(s, [f"{topic} {s}", f"{topic} {s} 정의", f"{topic} {s} 사례"]) for s in subs]
    return Plan(topic=topic, subtopics=plans)
