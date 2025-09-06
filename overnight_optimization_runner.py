#!/usr/bin/env python3
"""
Overnight Optimization Runner for Linux Superhelfer System.
Runs continuous optimization cycles with ChatGPT's improved routing.
"""

import asyncio
import json
import logging
import os
import random
import sys
import time
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.module_a_core.query_analyzer import QueryAnalyzer
from modules.module_a_core.session_manager import get_session_manager

# ChatGPT's Cleanup Fix 1: Robust paths and logging
BASE = Path(__file__).resolve().parent
LOG_DIR = BASE / "optimization_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def _atomic_write_json(path: Path, payload: dict):
    """Atomic JSON writing to prevent corruption."""
    with tempfile.NamedTemporaryFile('w', dir=str(path.parent), delete=False) as tmp:
        json.dump(payload, tmp, indent=2, default=str)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_name = tmp.name
    os.replace(tmp_name, path)

# ChatGPT's Cleanup Fix 2: Robust logging with rotation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(LOG_DIR / "overnight_optimization.log", maxBytes=5_000_000, backupCount=3),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OvernightOptimizer:
    """Runs continuous optimization cycles overnight."""
    
    def __init__(self):
        self.analyzer = QueryAnalyzer()
        self.session_manager = get_session_manager()
        self.start_time = time.time()
        self.cycle_count = 0
        self.total_queries = 0
        self.routing_stats = {
            'fast': 0,
            'code': 0, 
            'heavy': 0
        }
        self.accuracy_history = []
        
        # ChatGPT's Cleanup Fix: KPI tracking
        self.cost_history = []
        self.heavy_recall_history = []
        
        # ChatGPT's Fix 5: Kostenbasierte Optimierung verwenden
        self.COST = {
            ('heavy','code'): 2.0, ('heavy','fast'): 3.0,
            ('code','fast'): 1.0,  ('code','heavy'): 0.5,
            ('fast','code'): 0.5,  ('fast','heavy'): 1.0
        }
        
        # Environment variables for tuning
        self.queries_per_cycle = int(os.getenv('QPC', '20'))
        self.sleep_seconds = int(os.getenv('OO_SLEEP_SECS', '5'))
        
        # Test query sets for different categories
        self.test_queries = {
            'basic_commands': [
                "Welcher Befehl zeigt die Festplattenbelegung an?",
                "Wie kann ich alle laufenden Prozesse anzeigen?",
                "Welches Kommando listet alle Dateien auf?",
                "Was macht der df Befehl?",
                "Wie zeige ich die CPU-Auslastung an?",
                "Welcher Befehl zeigt den verfügbaren Speicher?",
                "Wie kann ich die Netzwerkverbindungen anzeigen?",
                "Was ist der Unterschied zwischen ls und ll?",
                "Welcher Befehl zeigt die Systemzeit an?",
                "Wie kann ich die Festplattenbelegung prüfen?"
            ],
            'mathematical': [
                "Bestimme die mathematisch optimale Puffergröße für I/O-Operationen",
                "Löse das Gleichungssystem: x+y=10, x-y=2",
                "Berechne Fibonacci-Zahlen zur Bestimmung von Retry-Intervallen",
                "Finde die optimale Anzahl von Worker-Threads für CPU-intensive Tasks",
                "Bestimme die mathematisch optimale Cache-Größe für Datenbank-Queries",
                "Berechne die optimale Timeout-Werte für HTTP-Requests",
                "Löse die Optimierungsaufgabe für Memory-Allocation",
                "Bestimme die mathematisch beste Partitionierung für große Datasets",
                "Berechne die optimale Anzahl von Connections im Connection Pool",
                "Finde die mathematisch optimale Batch-Größe für Datenverarbeitung"
            ],
            'code_tasks': [
                "Schreibe ein Bash-Skript zum automatischen Backup",
                "Erstelle eine Python-Funktion für Datei-Synchronisation",
                "Entwickle ein Shell-Skript für Log-Rotation",
                "Programmiere einen Service-Monitor in Python",
                "Schreibe ein Bash-Skript für System-Updates",
                "Erstelle ein Python-Tool für Netzwerk-Monitoring",
                "Entwickle ein Shell-Skript für Datenbank-Backup",
                "Programmiere einen Cron-Job für automatische Wartung",
                "Schreibe ein Python-Skript für Performance-Monitoring",
                "Erstelle ein Bash-Tool für User-Management"
            ],
            'intermediate': [
                "Erkläre mir die Unterschiede zwischen verschiedenen Dateisystemen",
                "Wie funktioniert die Speicherverwaltung in Linux?",
                "Was sind die Vor- und Nachteile von Docker vs. LXC?",
                "Analysiere die Performance-Probleme bei hoher CPU-Last",
                "Vergleiche verschiedene Load-Balancing-Strategien",
                "Erkläre die Funktionsweise von systemd Services",
                "Wie optimiere ich die Netzwerk-Performance unter Linux?",
                "Was sind Best Practices für Linux-Security-Hardening?",
                "Analysiere die Ursachen für Memory-Leaks in Anwendungen",
                "Erkläre die Unterschiede zwischen verschiedenen Schedulern"
            ]
        }
        
    def generate_random_queries(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate random test queries from different categories."""
        queries = []
        
        for _ in range(count):
            category = random.choice(list(self.test_queries.keys()))
            query_text = random.choice(self.test_queries[category])
            
            # Add some variations
            variations = [
                query_text,
                query_text + "?",
                query_text.replace("?", " bitte?"),
                "Kannst du mir helfen: " + query_text.lower(),
                query_text + " Danke im Voraus!"
            ]
            
            final_query = random.choice(variations)
            
            queries.append({
                'text': final_query,
                'category': category,
                'expected_model': self._get_expected_model(category),
                'timestamp': time.time()
            })
        
        return queries
    
    def _get_expected_model(self, category: str) -> str:
        """Get expected model for category."""
        mapping = {
            'basic_commands': 'fast',
            'mathematical': 'heavy', 
            'code_tasks': 'code',
            'intermediate': 'code'
        }
        return mapping.get(category, 'code')
    
    def run_optimization_cycle(self) -> Dict[str, Any]:
        """Run a single optimization cycle."""
        cycle_start = time.perf_counter()
        self.cycle_count += 1
        
        logger.info(f"🚀 Starting optimization cycle {self.cycle_count}")
        
        # EMERGENCY FIX: STOP Hard Negatives Oversampling (causing negative feedback loop)
        # hard_negatives = self.pull_hard_negatives(max(20, self.queries_per_cycle // 3))
        test_queries = self.generate_random_queries(self.queries_per_cycle)
        # test_queries = hard_negatives + regular_queries
        
        results = []
        correct_routes = 0
        
        for query_data in test_queries:
            query_text = query_data['text']
            expected_model = query_data['expected_model']
            
            # Analyze query
            analysis = self.analyzer.analyze_query(query_text)
            actual_model = getattr(analysis, 'route_model', 'code')
            
            # Track routing stats
            self.routing_stats[actual_model] += 1
            self.total_queries += 1
            
            # Check accuracy
            is_correct = actual_model == expected_model
            if is_correct:
                correct_routes += 1
            
            # ChatGPT's Cleanup Fix 6: Collect hard negatives
            if expected_model == 'heavy' and actual_model != 'heavy':
                self._collect_hard_negative(query_text, expected_model, actual_model)
            
            result = {
                'query': query_text,
                'category': query_data['category'],
                'expected': expected_model,
                'actual': actual_model,
                'correct': is_correct,
                'complexity': analysis.complexity_score,
                'reasoning': analysis.reasoning,
                'debug_info': getattr(analysis, 'debug_info', {}),
                'timestamp': query_data['timestamp']
            }
            results.append(result)
        
        # ChatGPT's Optional: cycle_time mit perf_counter messen
        cycle_time = time.perf_counter() - cycle_start
        
        # ChatGPT's Cleanup Fix 7: Compute KPIs immediately after results
        acc, cost_score, heavy_rec = self._compute_kpis(results)
        
        cycle_summary = {
            'cycle': self.cycle_count,
            'accuracy': acc,
            'cost_score': cost_score,
            'heavy_recall': heavy_rec,
            'correct_routes': correct_routes,
            'total_queries': len(test_queries),
            'cycle_time': cycle_time,
            'routing_distribution': {
                'fast': sum(1 for r in results if r['actual'] == 'fast'),
                'code': sum(1 for r in results if r['actual'] == 'code'),
                'heavy': sum(1 for r in results if r['actual'] == 'heavy')
            },
            'category_accuracy': self._calculate_category_accuracy(results),
            'results': results
        }
        
        # ChatGPT's Cleanup Fix 5: Single accuracy history entry
        self.accuracy_history.append({
            'cycle': self.cycle_count,
            'accuracy': acc,
            'timestamp': cycle_start,
            'query_count': len(test_queries)
        })
        
        if heavy_rec is not None:
            self.heavy_recall_history.append({
                'cycle': self.cycle_count,
                'heavy_recall': heavy_rec,
                'timestamp': cycle_start
            })
        
        self.cost_history.append({
            'cycle': self.cycle_count,
            'cost_score': cost_score,
            'timestamp': cycle_start
        })
        
        # ChatGPT's Cleanup Fix 4: Single atomic write per cycle
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        _atomic_write_json(LOG_DIR / f"cycle_{self.cycle_count}_{ts}.json", cycle_summary)
        
        # ChatGPT's Cleanup Fix 7: Immediate progress save after every cycle
        self.save_progress_report()
        
        logger.info(f"✅ Cycle {self.cycle_count} completed: {acc:.1f}% accuracy "
                   f"({correct_routes}/{len(test_queries)}) in {cycle_time:.1f}s")
        
        return cycle_summary
    
    def _compute_kpis(self, results: List[Dict]) -> tuple:
        """ChatGPT's Fix 3: Compute KPIs (accuracy, cost_score, heavy_recall)."""
        n = len(results) or 1
        acc = 100.0 * sum(r['correct'] for r in results) / n
        
        wrong_cost = sum(self.COST.get((r['expected'], r['actual']), 1.0)
                        for r in results if not r['correct'])
        cost_score = 100.0 * (1.0 - wrong_cost / n)
        
        heavy_exp = [r for r in results if r['expected'] == 'heavy']
        heavy_rec = None if not heavy_exp else 100.0 * sum(
            1 for r in heavy_exp if r['actual'] == 'heavy'
        ) / len(heavy_exp)
        
        return acc, cost_score, heavy_rec
    
    def _collect_hard_negative(self, query: str, expected: str, actual: str):
        """ChatGPT's Cleanup Fix 6: Collect hard negatives."""
        hard_bank_file = LOG_DIR / "hard_bank.txt"
        timestamp = datetime.now().isoformat()
        entry = f"{timestamp}\t{expected}\t{actual}\t{query}\n"
        
        with open(hard_bank_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        # ChatGPT's Fix 4: Also write just the query for oversampling
        with open(hard_bank_file, 'a', encoding='utf-8') as f:
            f.write(query + "\n")
    
    def pull_hard_negatives(self, k: int) -> List[Dict[str, Any]]:
        """ChatGPT's Fix 4: Pull hard negatives for oversampling."""
        hard_bank_file = LOG_DIR / "hard_bank.txt"
        
        try:
            with open(hard_bank_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            
            if not lines:
                return []
            
            # Take last k lines (most recent hard negatives)
            recent_lines = lines[-k:] if len(lines) >= k else lines
            
            hard_queries = []
            for line in recent_lines:
                # Skip lines with tabs (metadata entries)
                if '\t' in line:
                    continue
                
                # This is a pure query line
                query_text = line
                
                # Determine expected model based on query content
                expected_model = self._get_expected_model_for_query(query_text)
                
                hard_queries.append({
                    'text': query_text,
                    'category': 'hard_negative',
                    'expected_model': expected_model,
                    'timestamp': time.time()
                })
            
            return hard_queries
            
        except FileNotFoundError:
            return []
    
    def _get_expected_model_for_query(self, query: str) -> str:
        """Determine expected model for a query."""
        query_lower = query.lower()
        
        # Mathematical patterns -> heavy
        math_patterns = [
            'bestimme', 'berechne', 'optimiere', 'fibonacci', 'gleichung',
            'mathematisch', 'optimal', 'minimum', 'maximum'
        ]
        
        if any(pattern in query_lower for pattern in math_patterns):
            return 'heavy'
        
        # Basic command patterns -> fast
        fast_patterns = [
            'welcher befehl', 'was macht', 'zeigt', 'listet'
        ]
        
        if any(pattern in query_lower for pattern in fast_patterns):
            return 'fast'
        
        # Default to code
        return 'code'
    
    def _hard_negative_count(self) -> int:
        """Count hard negatives from hard_bank.txt."""
        fn = LOG_DIR / "hard_bank.txt"
        try:
            return sum(1 for line in fn.open() if line.strip())
        except FileNotFoundError:
            return 0
    
    def _calculate_category_accuracy(self, results: List[Dict]) -> Dict[str, float]:
        """Calculate accuracy per category."""
        category_stats = {}
        
        for result in results:
            category = result['category']
            if category not in category_stats:
                category_stats[category] = {'correct': 0, 'total': 0}
            
            category_stats[category]['total'] += 1
            if result['correct']:
                category_stats[category]['correct'] += 1
        
        return {
            category: (stats['correct'] / stats['total']) * 100
            for category, stats in category_stats.items()
        }
    

    
    def generate_progress_report(self) -> Dict[str, Any]:
        """ChatGPT's Cleanup Fix 8: Enhanced progress report with all KPIs."""
        now = time.time()
        runtime = now - self.start_time
        
        # Recent accuracy (last 10 cycles)
        recent = self.accuracy_history[-10:] or [{'accuracy': 0}]
        r_acc = sum(x['accuracy'] for x in recent) / len(recent)
        o_acc = sum(x['accuracy'] for x in self.accuracy_history) / max(1, len(self.accuracy_history))
        
        # Recent cost score (last 10 cycles)
        recent_cost = self.cost_history[-10:] or [{'cost_score': 0}]
        r_cost = sum(x['cost_score'] for x in recent_cost) / len(recent_cost)
        
        # Recent heavy recall (last 10 cycles)
        recent_hr = [x['heavy_recall'] for x in self.heavy_recall_history[-10:] 
                    if x.get('heavy_recall') is not None]
        r_hr = sum(recent_hr) / len(recent_hr) if recent_hr else None
        
        return {
            'timestamp': now,
            'runtime_hours': runtime / 3600,
            'total_cycles': self.cycle_count,
            'total_queries': self.total_queries,
            'overall_accuracy': o_acc,
            'recent_accuracy': r_acc,
            'recent_cost_score': r_cost,
            'recent_heavy_recall': r_hr,
            'routing_distribution': {
                m: (c / max(self.total_queries, 1)) * 100 
                for m, c in self.routing_stats.items()
            },
            'accuracy_trend': self.accuracy_history[-20:],
            'queries_per_hour': self.total_queries / max(runtime / 3600, 0.1),
            'cycles_per_hour': self.cycle_count / max(runtime / 3600, 0.1),
            'hard_negatives': self._hard_negative_count()
        }
    
    def save_progress_report(self):
        """ChatGPT's Fix 5: Save progress atomically."""
        report = self.generate_progress_report()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save timestamped report
        _atomic_write_json(LOG_DIR / f"progress_report_{ts}.json", report)
        
        # Save latest report atomically
        _atomic_write_json(LOG_DIR / "latest_progress.json", report)
        
        logger.info(f"📊 Progress: acc {report['recent_accuracy']:.1f}%, "
                   f"cost {report['recent_cost_score']:.1f}, "
                   f"heavyR {report['recent_heavy_recall'] if report['recent_heavy_recall'] is not None else 'n/a'}")
    
    async def run_overnight_optimization(self, target_hours: float = 8.0):
        """Run optimization for specified hours."""
        logger.info(f"🌙 Starting overnight optimization for {target_hours} hours")
        logger.info(f"📊 Current routing accuracy baseline: 80.0%")
        
        end_time = time.time() + (target_hours * 3600)
        
        try:
            while time.time() < end_time:
                # Run optimization cycle
                cycle_summary = self.run_optimization_cycle()
                
                # Log progress every 5 cycles
                if self.cycle_count % 5 == 0:
                    report = self.generate_progress_report()
                    logger.info(f"🔄 Progress: Cycle {self.cycle_count}, "
                               f"Accuracy: {report['recent_accuracy']:.1f}%, "
                               f"Runtime: {report['runtime_hours']:.1f}h")
                
                # Sleep between cycles
                await asyncio.sleep(self.sleep_seconds)
                
        except KeyboardInterrupt:
            logger.info("⏹️  Optimization stopped by user")
        except Exception as e:
            logger.error(f"❌ Optimization error: {e}")
        finally:
            # Final report
            final_report = self.generate_progress_report()
            self.save_progress_report()
            
            logger.info(f"🏁 Overnight optimization completed!")
            logger.info(f"📊 Final Results:")
            logger.info(f"   - Total Cycles: {final_report['total_cycles']}")
            logger.info(f"   - Total Queries: {final_report['total_queries']}")
            logger.info(f"   - Overall Accuracy: {final_report['overall_accuracy']:.1f}%")
            logger.info(f"   - Recent Accuracy: {final_report['recent_accuracy']:.1f}%")
            logger.info(f"   - Runtime: {final_report['runtime_hours']:.1f} hours")
            logger.info(f"   - Queries/Hour: {final_report['queries_per_hour']:.0f}")


async def main():
    """Main function to start overnight optimization."""
    optimizer = OvernightOptimizer()
    
    # Default to 8 hours, but can be adjusted
    target_hours = 8.0
    
    if len(sys.argv) > 1:
        try:
            target_hours = float(sys.argv[1])
        except ValueError:
            logger.warning(f"Invalid hours argument: {sys.argv[1]}, using default 8.0")
    
    await optimizer.run_overnight_optimization(target_hours)


if __name__ == "__main__":
    asyncio.run(main())