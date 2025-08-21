# robots 준수 크롤링·본문추출
import requests, time, urllib.robotparser as robotparser, re
from bs4 import BeautifulSoup
from datetime import datetime
from schemas import Plan, SourceDoc
from typing import List

UA = "Mozilla/5.0"
DELAY = 1.0

def _allowed(url: str) -> bool:
    from urllib.parse import urlparse
    p = urlparse(url); rp = robotparser.RobotFileParser()
    try:
        rp.set_url(f"{p.scheme}://{p.netloc}/robots.txt"); rp.read()
        return rp.can_fetch(UA, url)
    except: return True

def _fetch(url: str) -> str | None:
    if not _allowed(url): return None
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=10)
        r.raise_for_status(); return r.text
    except: return None

def _extract(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    texts = []
    for tag in soup.find_all(["article","main","p","div"]):
        t = tag.get_text(" ", strip=True)
        if len(t) > 80: texts.append(t)
    txt = " ".join(texts)
    return re.sub(r"\s+", " ", txt).strip()

def _serp(query: str) -> list[str]:
    # TODO: 실제 검색 연결. 초기엔 수동 URL 주입 사용.
    return []

def crawl_by_plan(plan: Plan) -> List[SourceDoc]:
    urls = set()
    for sp in plan.subtopics:
        for q in sp.queries:
            urls.update(_serp(q))
    docs: List[SourceDoc] = []
    for u in list(urls)[:60]:
        html = _fetch(u); 
        if not html: continue
        text = _extract(html)
        if len(text) < 200: continue
        docs.append(SourceDoc(u, None, text, datetime.utcnow().isoformat()))
        time.sleep(DELAY)
    return docs
