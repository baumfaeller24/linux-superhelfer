# Query Rewrite & Router Regeln

## Router-Regeln (ModelRouter + QueryAnalyzer)

### Prioritäten-Hierarchie

#### PRIORITY 1: FAST MODEL (Basic Commands)
```python
fast_patterns = [
    r'welcher\s+befehl\s+(zeigt|macht|gibt|listet)',  # "welcher befehl zeigt/macht"
    r'was\s+macht\s+(der|das)\s+\w+\s+befehl',        # "was macht der X befehl"
    r'wie\s+kann\s+ich\s+.*\s+(anzeigen|zeigen)\s*\??', # "wie kann ich X anzeigen?"
    r'^(ls|ll|pwd|cd|df|du|ps|top|htop|free|uname)\s*\??$', # basic commands alone
]
```

#### PRIORITY 2: HEAVY MODEL (Mathematical/Optimization)
```python
heavy_patterns = [
    r'mathematisch.*optimal',                          # "mathematisch optimal"
    r'(bestimme|berechne|finde|löse).*optimal',       # "bestimme/berechne optimal"
    r'optimierungsaufgabe',                           # "optimierungsaufgabe"
    r'fibonacci.*zahlen',                             # "fibonacci zahlen"
    r'gleichungssystem',                              # "gleichungssystem"
    r'optimal.*anzahl.*worker',                       # "optimale anzahl worker"
    r'optimal.*größe.*puffer',                        # "optimale größe puffer"
]
```

#### PRIORITY 3: CODE MODEL (Complex Explanations)
```python
intermediate_patterns = [
    r'erkläre\s+mir\s+(die\s+)?unterschiede?\s+zwischen', # "erkläre mir unterschiede zwischen"
    r'was\s+sind\s+(die\s+)?best\s+practices?\s+für',     # "was sind best practices für"
    r'wie\s+funktioniert\s+.*\s+(system|prozess|mechanismus)', # "wie funktioniert X system"
    r'vor.*und.*nachteile\s+von',                         # "vor und nachteile von"
]
```

### QueryAnalyzer Patterns (ChatGPT's Enhanced)

#### Mathematical Patterns (_MATH_PATS)
```python
_MATH_PATS = [
    re.compile(r"\bmathematisch\w*\b.{0,40}\boptimal\w*\b"),
    re.compile(r"\b(bestimme|berechne|minimiere|maximiere|optimiere|finde|löse)\b[^\.]{0,80}\b(optimal\w*|minimum|maxim\w*|argmin|argmax)\b"),
    re.compile(r"\boptimierungsaufgabe\b"),  # ChatGPT's Fix 2
    re.compile(r"\boptimale?\s+(anzahl|größe|batch[-\s]?größe|timeouts?|cache[-\s]?größe|connections?)\b"),
    re.compile(r"\b(worker[-\s]?threads?|connection\s+pool|batch[-\s]?size)\b.*\b(optimal\w*|anzahl|größe)\b"),
    re.compile(r"\bfibonacci\b"),
]
```

#### Fast Command Patterns (_FAST_PATS)
```python
_FAST_PATS = [
    re.compile(r'welcher\s+befehl\s+(zeigt|macht|gibt|listet)')
]
```

### Routing-Entscheidungslogik

#### ChatGPT's Enhanced Decision Tree
```python
# 1. High-Complexity-Override (ChatGPT's Fix 1)
if complexity_score >= 0.80 and re.search(r"\b(bestimme|berechne|minimiere|maximiere|optimiere|finde|löse)\b", qn):
    return MODEL_HEAVY

# 2. Fast Model Check
for pattern in _FAST_PATS:
    if pattern.search(qn):
        return MODEL_FAST

# 3. Mathematical Scoring
heavy_score = sum(1 for p in _MATH_PATS if p.search(q) or p.search(qn))
if complexity_score >= 0.8:
    heavy_score += 1

# 4. Technical Scoring  
tech_score = sum(1 for p in _TECH_PATS if p.search(q) or p.search(qn))
if linux_kw or code_kw:
    tech_score += 1

# 5. Decision (ChatGPT's Fix 3: Relaxed tie-break)
if heavy_score >= max(1.5, tech_score + 0.5):  # Was: max(2.0, tech_score + 1.0)
    return MODEL_HEAVY
```

### Cost Matrix (ChatGPT's Fix 5)
```python
COST = {
    ('heavy','code'): 2.0, ('heavy','fast'): 3.0,
    ('code','fast'): 1.0,  ('code','heavy'): 0.5,
    ('fast','code'): 0.5,  ('fast','heavy'): 1.0
}
# Score = 100*(1 - wrong_cost/len(results))
```

## Query Rewriting: NICHT IMPLEMENTIERT

### Fehlende Features
- ❌ Query Expansion
- ❌ Synonym Replacement  
- ❌ Context Injection
- ❌ Multi-language Normalization
- ❌ Spelling Correction

### Aktueller Workaround
```python
# Nur in search_with_context()
enhanced_query = f"{query} {context}".strip()
```

## Hard Negatives Integration (ChatGPT's Fix 4)
```python
# Oversampling von Hard Negatives
hard_negatives = self.pull_hard_negatives(max(20, self.queries_per_cycle // 3))
regular_queries = self.generate_random_queries(self.queries_per_cycle)
test_queries = hard_negatives + regular_queries
```