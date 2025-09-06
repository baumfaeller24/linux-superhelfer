# Kiro-Prompt: Cleanup + Fixes für `overnight_optimization_runner.py` und `advanced_monitor.py`

## Anweisung

**Lösche alle bisherigen Kontext- und Codeschnipsel zu „Overnight Optimization/Monitor/Router KPIs“ aus deinem Speicher.** Verwende ausschließlich die beiden angehängten Dateien als Quelle:

* `overnight_optimization_runner.py`
* `advanced_monitor.py`

## Ziel

Stabile KPIs und saubere Dateien. Keine doppelten Writes, keine Race Conditions, korrekte Heavy-Recall/Cost-Scores im Monitor.

---

## Aufgaben – `overnight_optimization_runner.py`

1. **Pfad-Basis + Log-Verzeichnis**

* Setze `BASE = Path(__file__).resolve().parent` und `LOG_DIR = BASE / "optimization_logs"`, `LOG_DIR.mkdir(parents=True, exist_ok=True)`.
* Ersetze alle relativen `"optimization_logs/…"` durch `LOG_DIR / "…"`.

2. **Logging robust**

* Nutze `RotatingFileHandler(LOG_DIR / "overnight_optimization.log", maxBytes=5_000_000, backupCount=3)` + `StreamHandler`.
* Entferne alte `FileHandler`-Pfadangaben.

3. **Atomare JSON-Writes**

* Implementiere `_atomic_write_json(path: Path, payload: dict)` mit Tempfile + `os.replace()` + `fsync`.
* Verwende `_atomic_write_json()` in:

  * `save_progress_report()` für `progress_report_*.json` **und** `latest_progress.json`.
  * `save_cycle_results()` **oder** schreibe die Cycle-Datei genau einmal pro Zyklus atomar (siehe Punkt 4).

4. **Doppelte Writes entfernen**

* Sorge dafür, dass pro Zyklus **genau eine** Cycle-JSON erzeugt wird.
  Variante A: nur in `run_optimization_cycle()` nach Summary schreiben und **keinen** zweiten Write an anderer Stelle.
  Variante B: nur `save_cycle_results()` nutzen, aber atomar und mit `LOG_DIR`.

5. **Accuracy-History nicht doppelt pflegen**

* Entferne die erste `accuracy_history.append(...)` auf Basis von `cycle_accuracy`.
* Behalte nur **einen** Append auf Basis der finalen KPI-Berechnung.

6. **Hard-Negatives sammeln**

* Im Query-Loop: wenn `expected_model == 'heavy'` und `actual_model != 'heavy'`, dann `append` der Query nach `LOG_DIR / "hard_bank.txt"`.
* Zähler in Progress: Anzahl Zeilen aus `hard_bank.txt`.

7. **KPIs pro Zyklus berechnen und sofort persistieren**

* Funktion `_compute_kpis(results)` → `accuracy`, `cost_score`, `heavy_recall`.
* Nach jedem Zyklus:

  * Cycle-JSON atomar schreiben.
  * **Unmittelbar** `save_progress_report()` aufrufen (nicht nur alle 10 Zyklen).

8. **Progress-Report erweitern**

* Felder ergänzen:
  `recent_cost_score`, `recent_heavy_recall`, `hard_negatives`.
* `recent_*` über gleitendes Fenster der letzten 10 Einträge.
* `routing_distribution` prozentual aus `self.total_queries`.

9. **Optionale Parameter**

* `queries_per_cycle` und Sleep per Env (`QPC`, `OO_SLEEP_SECS`) übernehmbar, aber kein Muss.

---

## Aufgaben – `advanced_monitor.py`

1. **Konsistente Pfade + robustes Lesen**

* Setze `BASE/LOG_DIR` analog zum Runner.
* Implementiere `load_json_safe(path, retries=3, delay=0.2)` mit Retry bei `JSONDecodeError`.

2. **Anzeige der neuen KPIs**

* Zeige `recent_cost_score`, `recent_heavy_recall`, `hard_negatives`.
* Markiere „STALE“, wenn `latest_progress.json` älter als z. B. 3 min.

3. **Terminal-Robustheit**

* Unicode-Fallback für Pfeile/Balken.
* Balkenbreite dynamisch nach `shutil.get_terminal_size()`.

---

## Akzeptanzkriterien

* Nach **erstem** vollständigen Zyklus zeigen Monitor und `latest_progress.json`:

  * `total_cycles ≥ 1`, `total_queries > 0`.
  * Felder `recent_accuracy`, `recent_cost_score`, `recent_heavy_recall`, `hard_negatives` gefüllt.
* Keine doppelten Cycle-Dateien je Zyklus.
* Keine `JSONDecodeError` im Monitor bei laufender Aktualisierung.

---

## Kurzer Testplan

1. Setze `QPC=20`, `OO_SLEEP_SECS=5`.
2. Starte Runner. Warte 1–2 Zyklen.
3. Öffne Monitor. Prüfe, ob KPIs > 0 und „STALE“ verschwindet.
4. Erzeuge absichtlich einige Heavy-Fehlrouten im Testset. Prüfe Zuwachs in `hard_bank.txt` und Anzeige „Hard Negatives“.

