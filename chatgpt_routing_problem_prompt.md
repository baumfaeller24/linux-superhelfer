# ChatGPT Prompt: Query Routing Problem in Linux Superhelfer System

## Problem Context

Ich arbeite an einem intelligenten Linux-Hilfssystem mit drei verschiedenen AI-Modellen:
- **Fast Model** (llama3.2:3b) - für einfache Fragen
- **Code Model** (qwen3-coder-30b) - für Code/Linux-spezifische Anfragen  
- **Heavy Model** (llama3.1:70b) - für komplexe mathematische/analytische Aufgaben

## Aktueller Status

Das System hat bereits eine Routing-Genauigkeit von 66.7% erreicht (Verbesserung von 47%), aber **zwei spezifische Probleme** bleiben ungelöst:

### Problem 1: ✅ GELÖST
**Query:** "Welcher Befehl zeigt die Festplattenbelegung an?"
- **War:** Code Model (wegen Keyword "befehl")
- **Ist jetzt:** Fast Model ✅
- **Lösung:** Spezielle Patterns für "Welcher Befehl..." Fragen

### Problem 2: ❌ NOCH NICHT GELÖST
**Query:** "Bestimme die mathematisch optimale Puffergröße für I/O-Operationen"
- **Soll:** Heavy Model (mathematische Optimierung)
- **Ist:** Code Model (Complexity: 0.500)
- **Problem:** Wird nicht als mathematische Query erkannt

## Meine aktuelle Implementierung

```python
def _should_use_code_model(self, query_lower, token_count, linux_kw, code_kw, complexity_kw, complexity_score):
    # 1. Basic command questions → Fast Model (funktioniert)
    basic_command_questions = [
        r'welcher\s+befehl\s+(zeigt|macht|gibt|listet)',
        # ... weitere Patterns
    ]
    for pattern in basic_command_questions:
        if re.search(pattern, query_lower):
            return False  # Fast Model
    
    # 2. Mathematical patterns → Heavy Model (funktioniert NICHT)
    mathematical_indicators = [
        r'mathematisch.{0,20}optimal',     # "mathematisch ... optimal"
        r'optimal.{0,20}puffer',           # "optimal ... buffer"
        r'bestimme.{0,20}optimal',         # "bestimme ... optimal"
        r'puffergröße.{0,20}operation',    # "puffergröße ... operation"
        # ... weitere Patterns
    ]
    for pattern in mathematical_indicators:
        if re.search(pattern, query_lower):
            return True  # Heavy Model (sollte funktionieren, tut es aber nicht)
    
    # 3. Linux/Code keywords → Code Model
    if linux_kw or code_kw:
        return True
    
    # 4. Complexity threshold
    if complexity_score >= 0.5:
        return True
    
    # ... weitere Logik
```

## Debug-Ergebnisse

Für "Bestimme die mathematisch optimale Puffergröße für I/O-Operationen":

```
Mathematical pattern matches:
✅ mathematisch.{0,20}optimal: mathematisch optimal
✅ optimal.{0,20}puffer: optimale puffer  
✅ bestimme.{0,20}optimal: bestimme die mathematisch optimal
✅ puffergröße.{0,20}operation: puffergröße für i/o-operation

Full analysis:
needs_code_model: True
complexity_score: 0.5
reasoning: Code model selected: Technical patterns detected
```

**Die mathematischen Patterns werden erkannt, aber die Query wird trotzdem als "Technical patterns detected" klassifiziert!**

## Weitere Kontext-Informationen

### Funktioniert korrekt:
- "Löse das Gleichungssystem: x+y=10, x-y=2" → Heavy Model ✅ (Complexity: 1.000)
- "ls -la zeigt mir alle Dateien" → Fast Model ✅ (Complexity: 0.000)
- "Welcher Befehl zeigt die Festplattenbelegung an?" → Fast Model ✅ (Complexity: 0.333)

### Funktioniert NICHT:
- "Bestimme die mathematisch optimale Puffergröße für I/O-Operationen" → Code Model ❌ (sollte Heavy Model sein)

## Meine Vermutungen

1. **Reihenfolge-Problem:** Die mathematischen Patterns werden von anderen Logik-Zweigen überschrieben
2. **Keyword-Konflikt:** "bestimme" ist sowohl in `complexity_indicators` als auch in mathematischen Patterns
3. **Technical Pattern Überschreibung:** Die Query wird durch `technical_patterns` am Ende gefangen

## Fragen an ChatGPT

1. **Warum wird die mathematische Query nicht korrekt geroutet, obwohl die Patterns matchen?**

2. **Wie sollte ich die Logik-Reihenfolge in `_should_use_code_model()` optimieren?**

3. **Welche spezifischen Änderungen würdest du vorschlagen, um mathematische Queries zuverlässig zum Heavy Model zu routen?**

4. **Gibt es bessere Patterns oder Ansätze für die Erkennung von mathematischen Optimierungsaufgaben?**

5. **Wie kann ich verhindern, dass `technical_patterns` mathematische Queries überschreibt?**

## Gewünschte Lösung

- **Ziel:** "Bestimme die mathematisch optimale Puffergröße für I/O-Operationen" → Heavy Model
- **Constraint:** Keine Regression bei den bereits funktionierenden Cases
- **Routing-Genauigkeit:** Von 66.7% auf 80%+ steigern

## Code-Struktur

Die relevante Funktion ist `_should_use_code_model()` in `modules/module_a_core/query_analyzer.py`. Sie gibt `True` zurück für Code/Heavy Model, `False` für Fast Model. Die finale Model-Auswahl erfolgt dann basierend auf `complexity_score >= 0.6` (Heavy vs. Code).

**Bitte gib mir konkrete, implementierbare Lösungsvorschläge mit Code-Beispielen!**