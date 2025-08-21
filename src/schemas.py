from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

@dataclass
class SourceDoc:
    url: str
    title: Optional[str]
    text: str
    fetched_at: str

@dataclass
class SubtopicPlan:
    name: str
    queries: List[str]

@dataclass
class Plan:
    topic: str
    subtopics: List[SubtopicPlan]

@dataclass
class Chunk:
    text: str
    source_url: str
    subtopic: str = ""

@dataclass
class SubtopicResult:
    name: str
    summary: str
    key_points: List[str]
    sources: List[str]

def to_dict(obj): return asdict(obj)
