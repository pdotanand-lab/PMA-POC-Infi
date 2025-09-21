from typing import List
import itertools
from collections import Counter
import re

def simple_keywords(text: str, top_k: int = 15) -> List[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_\-]+", text.lower())
    stop = set("""a an the and or but if then else for of to in on at by with from is are was were be been being
    i you he she it we they this that those these there here when where how what which who whom why
    do does did done doing have has had having not no yes ok okay so just very really into out up down
    about across after before during between among over under again more most some any few many much 
    can could should would shall will may might must
    meeting client call project review brainstorm quarterly
    """.split())
    words = [w for w in words if w not in stop and len(w) > 2]
    freq = Counter(words)
    return [w for w, _ in freq.most_common(top_k)]

def build_topic_graph(topics: List[str], segments: List[str]):
    # Build co-occurrence edges between topics if they appear in same segment text
    nodes = [{"id": t, "type": "topic"} for t in topics]
    edges = []
    for a, b in itertools.combinations(topics, 2):
        weight = 0
        for seg in segments:
            s = seg.lower()
            if a.lower() in s and b.lower() in s:
                weight += 1
        if weight > 0:
            edges.append({"source": a, "target": b, "weight": weight})
    return {"nodes": nodes, "links": edges}
