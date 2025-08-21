from schemas import *
from models.model_client import load_guidance, generate

_GUIDE = load_guidance()

def summarize_with_state(chunk_text: str, prev_state: State | None):
    prev = prev_state or State(summary="", entities=[], dates=[])
    prompt = (
        f"{_GUIDE}\n"
        "가능하면 아래 형식을 따르라. 필요하면 자유 설명을 덧붙여도 된다.\n"
        "{summary: '...', entities: ['...'], dates: ['YYYY-MM-DD']}\n\n"
        f"[이전요약]{prev.summary}\n[엔티티]{', '.join(prev.entities)}\n"
        f"[본문]{chunk_text}\n[요청] 3~5문장 요약 + 엔티티·날짜 후보."
    )
    raw = generate(prompt, temperature=0.2, max_tokens=600)
    # 관대한 파싱: JSON 비엄격 허용(여기선 단순 더미)
    summary = raw[:280]
    entities, dates = prev.entities, prev.dates
    new_state = State(summary=summary, entities=entities, dates=dates)
    out = {"summary": summary, "entities": entities, "dates": dates}
    return new_state, out
