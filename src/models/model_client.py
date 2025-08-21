# src/models/model_client.py
import os, requests

OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
GENERATE_URL = f"{OLLAMA_BASE}/api/generate"

def generate(prompt: str,
             model: str = DEFAULT_MODEL,
             max_tokens: int = 256,
             temperature: float = 0.2,
             system: str = "한국어로 답하라. 군더더기 없이 한 문장만 출력하라.",
             timeout: int = 120,
             **kwargs) -> str:
    body = {
        "model": model,
        "prompt": prompt,
        "system": system,   # ← 지시어
        "think": False,     # ← 생각 분리 끔 (response만 받기)
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature,
        }
    }
    # 필요 옵션 더 있다면 kwargs로 확장
    if "stop" in kwargs:  # 예: 반복되는 '번역결과'를 잘라내고 싶다면 stop=["번역결과"]
        body["options"]["stop"] = kwargs["stop"]

    r = requests.post(GENERATE_URL, json=body, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return (data.get("response") or "").strip()
