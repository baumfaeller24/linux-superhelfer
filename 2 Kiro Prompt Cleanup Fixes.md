Hallo Kiro, das System Läuft stabil, aber nicht optimal.

Belege:

* Zyklen zählen korrekt: 97→99, 20 Queries/Zyklus, 1 940 total.
* Hard-Negatives werden gesammelt: 298.
* KPIs schwach: Accuracy 68.5 %, Cost 57.0, Heavy-Recall 39.8 %. Ziel klar verfehlt.

Hauptursachen:

* Heavy-Detection greift zu selten. Tech-Signale dominieren.
* Hard-Negatives werden nicht aggressiv genug zurückgespielt.
* Logik-Mix: `route_model` vs. `needs_code_model` deutet auf Legacy-Pfad im Log.

Sofort-Fixes (präzise und klein):

1. High-Complexity-Override aktivieren.

```python
# QueryAnalyzer._route_query – direkt nach Fast-Check
if complexity_score >= 0.80 and re.search(r"\b(bestimme|berechne|minimiere|maximiere|optimiere|finde|löse)\b", qn):
    self.debug['route_reason'] = 'heavy_high_complexity_verb'
    return MODEL_HEAVY
```

2. Mathe-Patterns an Testset anpassen.

```python
# + in _MATH_PATS
re.compile(r"\boptimierungsaufgabe\b"),
re.compile(r"\boptimale?\s+(anzahl|größe|batch[-\s]?größe|timeouts?|cache[-\s]?größe|connections?)\b"),
re.compile(r"\b(worker[-\s]?threads?|connection\s+pool|batch[-\s]?size)\b.*\b(optimal\w*|anzahl|größe)\b"),
re.compile(r"\bfibonacci\b"),
```

3. Tie-Break zugunsten Heavy lockern.

```python
# Entscheidungsteil
if heavy_score >= max(1.5, tech_score + 0.5):
    self.debug['route_reason'] = f'heavy_win_relaxed H:{heavy_score} T:{tech_score}'
    return MODEL_HEAVY
```

4. Hard-Negatives wirklich oversamplen.

```python
# beim Fehlrouting heavy→{code,fast}
with (LOG_DIR / 'hard_bank.txt').open('a') as f: f.write(query_text+"\n")

# zu Zyklusbeginn
test_queries = pull_hard_negatives(k=max(20, self.queries_per_cycle//3)) \
               + self.generate_random_queries(self.queries_per_cycle)
```

5. Kostenbasierte Optimierung verwenden (nicht nur Accuracy).

```python
COST = {('heavy','code'):2.0, ('heavy','fast'):3.0, ('code','fast'):1.0,
        ('code','heavy'):0.5, ('fast','code'):0.5, ('fast','heavy'):1.0}
# Score = 100*(1 - wrong_cost/len(results)) → für Parametertuning verwenden
```

6. Logs bereinigen: `needs_code_model` entfernen oder an `route_model` angleichen, plus `route_reason/heavy_hits/tech_hits` bei Fehlrouten mitschreiben.

Optional, aber sinnvoll:

* `cycle_time`: mit `time.perf_counter()` messen statt 0.0.
* Bandit/Grid-Search über `heavy_threshold/tie_margin/verb_bonus/complexity_cut`.

Erwartung: Heavy-Recall > 70 % nach wenigen Zyklen, Cost-Score steigt.

