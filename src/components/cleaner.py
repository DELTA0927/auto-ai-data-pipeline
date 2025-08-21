from schemas import SourceDoc, Chunk
from typing import List
import hashlib

def _split(text: str, size=1200, overlap=200) -> list[str]:
    sents = text.split(". ")
    chunks, cur = [], ""
    for s in sents:
        if len(cur)+len(s) < size:
            cur += s + ". "
        else:
            chunks.append(cur.strip())
            cur = cur[-overlap:] + s + ". "
    if cur.strip(): chunks.append(cur.strip())
    return chunks

def clean_and_chunk(docs: List[SourceDoc]) -> List[Chunk]:
    out = []
    for d in docs:
        for t in _split(d.text):
            out.append(Chunk(text=t, source_url=d.url))
    return out

def dedupe_chunks(chunks: List[Chunk]) -> List[Chunk]:
    seen, out = set(), []
    for c in chunks:
        h = hashlib.md5(c.text.lower().encode()).hexdigest()
        if h in seen: continue
        seen.add(h); out.append(c)
    return out
