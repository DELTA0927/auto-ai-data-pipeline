# 권장 지침만 주는 OSS LLM 어댑터
from pathlib import Path

def load_guidance(path="src/config/system_guidance.txt") -> str:
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else ""

def generate(prompt: str, temperature=0.2, max_tokens=512) -> str:
    # TODO: vLLM/llama.cpp/HF pipeline 연동
    # 현재 더미: 입력 앞부분 요약처럼 잘라 반환
    return prompt[:max_tokens]
