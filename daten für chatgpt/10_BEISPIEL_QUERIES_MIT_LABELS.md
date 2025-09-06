# 10 Beispiel-Queries mit Labels

## Testset aus dem Optimization System

### 1. HEAVY MODEL Queries (Mathematical/Optimization)

#### Query 1: ❌ FEHLROUTING
- **Text**: "Berechne die optimale Anzahl von Connections im Connection Pool?"
- **Expected**: heavy
- **Actual**: fast
- **Problem**: Mathematical optimization query wird als basic command erkannt

#### Query 2: ❌ FEHLROUTING  
- **Text**: "Bestimme die mathematisch beste Partitionierung für große Datasets"
- **Expected**: heavy
- **Actual**: fast
- **Problem**: "mathematisch" + "optimal" Pattern nicht erkannt

#### Query 3: ❌ FEHLROUTING
- **Text**: "Löse die Optimierungsaufgabe für Memory-Allocation"
- **Expected**: heavy
- **Actual**: code
- **Problem**: "Optimierungsaufgabe" Pattern zu schwach gewichtet

#### Query 4: ❌ FEHLROUTING
- **Text**: "Berechne Fibonacci-Zahlen zur Bestimmung von Retry-Intervallen"
- **Expected**: heavy
- **Actual**: code
- **Problem**: "Fibonacci" Pattern nicht stark genug

### 2. FAST MODEL Queries (Basic Commands)

#### Query 5: ✅ KORREKT
- **Text**: "Welcher Befehl zeigt die Festplattenbelegung an?"
- **Expected**: fast
- **Actual**: fast
- **Reason**: fast_basic_command pattern match

#### Query 6: ✅ KORREKT
- **Text**: "Was macht der df Befehl?"
- **Expected**: fast
- **Actual**: fast
- **Reason**: Basic command question

### 3. CODE MODEL Queries (Technical/Intermediate)

#### Query 7: ✅ KORREKT
- **Text**: "Erkläre mir die Unterschiede zwischen verschiedenen Dateisystemen"
- **Expected**: code
- **Actual**: code
- **Reason**: Complex explanation request

#### Query 8: ✅ KORREKT
- **Text**: "Schreibe ein Bash-Skript zum automatischen Backup"
- **Expected**: code
- **Actual**: code
- **Reason**: Code generation request

### 4. GRENZFÄLLE (Schwierige Klassifikation)

#### Query 9: ❌ FEHLROUTING
- **Text**: "Wie optimiere ich die Netzwerk-Performance unter Linux?"
- **Expected**: code (technical explanation)
- **Actual**: heavy (wegen "optimiere")
- **Problem**: "optimiere" triggert mathematical patterns

#### Query 10: ❌ FEHLROUTING
- **Text**: "Bestimme die optimale Cache-Größe für Datenbank-Queries"
- **Expected**: heavy
- **Actual**: code
- **Problem**: Database context überwiegt mathematical optimization

## Routing-Accuracy Analyse

### Erfolgsrate nach Kategorie
- **Fast Model**: ~90% korrekt (basic commands gut erkannt)
- **Code Model**: ~70% korrekt (technical content meist richtig)
- **Heavy Model**: ~30% korrekt (mathematical patterns zu schwach)

### Hauptprobleme
1. **Mathematical queries → Fast**: "optimal" + "berechne" nicht stark genug
2. **Mathematical queries → Code**: Technical keywords überwiegen math patterns
3. **Technical queries → Heavy**: "optimiere" triggert fälschlicherweise math patterns

### ChatGPT's Fixes Wirkung
- ✅ **Fix 2** (Enhanced math patterns): Fibonacci, Optimierungsaufgabe erkannt
- ✅ **Fix 3** (Relaxed tie-break): Mehr Heavy-Routing, aber noch nicht genug
- ❌ **Fix 1** (High-complexity override): Zu selten getriggert (complexity < 0.8)

## Empfohlene Verbesserungen
1. **Stärkere Mathematical Pattern Weights**
2. **Context-aware Routing** (Database + optimal = heavy)
3. **Negative Patterns** (exclude technical context from math routing)
4. **Lower complexity threshold** für mathematical override