#!/usr/bin/env python3
"""
Advanced Overnight Optimizer with ChatGPT's enhanced features:
- Adversarial sampling & hard negatives
- Cost-aware metrics
- Parameter tuning with bandits
- Curriculum sampling
- Confusion matrix analysis
"""

import asyncio
import json
import logging
import os
import random
import sys
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import tempfile
import threading
from collections import defaultdict, Counter

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.module_a_core.query_analyzer import QueryAnalyzer, MODEL_HEAVY, MODEL_CODE, MODEL_FAST

# Configure logging with rotation
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

# ChatGPT's Cost Matrix
COST_MATRIX = {
    ('heavy', 'code'): 2.0,
    ('heavy', 'fast'): 3.0,
    ('code', 'fast'): 1.0,
    ('code', 'heavy'): 0.5,
    ('fast', 'code'): 0.5,
    ('fast', 'heavy'): 1.0,
}

# Parameter space for tuning
PARAM_SPACE = [
    {'heavy_threshold': 1.5, 'tie_margin': 0.5, 'verb_bonus': 0.3, 'complexity_cut': 0.75},
    {'heavy_threshold': 2.0, 'tie_margin': 1.0, 'verb_bonus': 0.5, 'complexity_cut': 0.80},
    {'heavy_threshold': 2.5, 'tie_margin': 1.5, 'verb_bonus': 0.7, 'complexity_cut': 0.85},
    {'heavy_threshold': 1.8, 'tie_margin': 0.8, 'verb_bonus': 0.4, 'complexity_cut': 0.78},
    {'heavy_threshold': 2.2, 'tie_margin': 1.2, 'verb_bonus': 0.6, 'complexity_cut': 0.82},
]

class AdvancedOvernightOptimizer:
    """Advanced optimizer with ChatGPT's enhancements."""
    
    def __init__(self):
        self.setup_logging()
        self.analyzer = QueryAnalyzer()
        self.start_time = time.time()
        self.cycle_count = 0
        self.total_queries = 0
        
        # Enhanced tracking
        self.confusion_matrix = defaultdict(int)
        self.hard_negatives = []
        self.parameter_bandits = self._init_bandits()
        self.current_params = PARAM_SPACE[0].copy()
        self.best_params = None
        self.best_cost_score = 0.0
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Ensure directories
        os.makedirs('optimization_logs', exist_ok=True)
        os.makedirs('conf', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
        
        # Load existing hard negatives
        self.load_hard_negatives()
        
        # Load best params if available
        self.load_best_params()
        
        logger.info("🚀 Advanced Overnight Optimizer initialized")
        
    def setup_logging(self):
        """Setup rotating file handler."""
        log_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Rotating file handler
        file_handler = RotatingFileHandler(
            'optimization_logs/advanced_overnight.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(log_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        
        # Configure logger
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    def _init_bandits(self) -> Dict[int, Dict[str, float]]:
        """Initialize bandit arms for parameter tuning."""
        return {
            i: {'count': 0, 'total_reward': 0.0, 'avg_reward': 0.0}
            for i in range(len(PARAM_SPACE))
        }
    
    def bandit_pick(self, epsilon: float = 0.1) -> int:
        """ε-greedy bandit selection."""
        if random.random() < epsilon or all(arm['count'] == 0 for arm in self.parameter_bandits.values()):
            return random.randint(0, len(PARAM_SPACE) - 1)
        
        # Pick best arm
        best_arm = max(self.parameter_bandits.items(), key=lambda x: x[1]['avg_reward'])
        return best_arm[0]
    
    def bandit_update(self, arm_idx: int, reward: float):
        """Update bandit arm with reward."""
        arm = self.parameter_bandits[arm_idx]
        arm['count'] += 1
        arm['total_reward'] += reward
        arm['avg_reward'] = arm['total_reward'] / arm['count']
    
    def set_router_params(self, **kwargs):
        """Set router parameters (placeholder for actual implementation)."""
        self.current_params.update(kwargs)
        logger.info(f"🔧 Updated router params: {kwargs}")
    
    def mutate_query(self, query: str) -> str:
        """ChatGPT's adversarial mutations."""
        mutations = [
            # Original
            query,
            
            # Paraphrases
            query.replace("Bestimme", "Ermittle"),
            query.replace("zeigt", "anzeigt"),
            query.replace("Befehl", "Kommando"),
            
            # Typos
            query.replace("optimale", "optimahle"),
            query.replace("Puffergröße", "Puffergroesse"),
            
            # Unicode variants
            query.replace("I/O", "I∕O"),
            query.replace("I/O", "IO"),
            query.replace("ö", "oe"),
            
            # Politeness
            f"Kannst du mir bitte helfen: {query.lower()}",
            f"{query} Vielen Dank!",
            f"Bitte {query.lower()}",
            
            # Case variations
            query.upper(),
            query.lower(),
            query.title(),
            
            # Punctuation
            query.rstrip('?') + '.',
            query + '??',
            query.replace('?', ''),
        ]
        
        return random.choice(mutations)
    
    def load_hard_negatives(self):
        """Load hard negatives from file."""
        try:
            with open('optimization_logs/hard_bank.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.hard_negatives.append(json.loads(line.strip()))
            logger.info(f"📚 Loaded {len(self.hard_negatives)} hard negatives")
        except FileNotFoundError:
            logger.info("📚 No existing hard negatives found")
    
    def save_hard_negatives(self):
        """Save hard negatives to file."""
        with open('optimization_logs/hard_bank.txt', 'w', encoding='utf-8') as f:
            for neg in self.hard_negatives:
                f.write(json.dumps(neg, ensure_ascii=False) + '\n')
    
    def pull_hard_negatives(self, k: int = 30) -> List[Dict[str, Any]]:
        """Pull k hard negatives for oversampling."""
        if len(self.hard_negatives) <= k:
            return self.hard_negatives.copy()
        
        # Weight by recency and error frequency
        weighted_negatives = []
        for neg in self.hard_negatives:
            weight = neg.get('error_count', 1) * (1.0 / max(1, time.time() - neg.get('timestamp', 0)))
            weighted_negatives.append((neg, weight))
        
        # Sample based on weights
        weighted_negatives.sort(key=lambda x: x[1], reverse=True)
        return [neg for neg, _ in weighted_negatives[:k]]
    
    def sampling_mix(self, recent_accuracy: float) -> Dict[str, float]:
        """ChatGPT's curriculum sampling strategy."""
        if recent_accuracy < 75:
            return {'basic_commands': 0.5, 'mathematical': 0.2, 'code_tasks': 0.2, 'intermediate': 0.1}
        elif recent_accuracy < 85:
            return {'basic_commands': 0.3, 'mathematical': 0.25, 'code_tasks': 0.25, 'intermediate': 0.2}
        else:
            return {'basic_commands': 0.2, 'mathematical': 0.3, 'code_tasks': 0.2, 'intermediate': 0.3}
    
    def cost_score(self, results: List[Dict[str, Any]]) -> float:
        """Calculate cost-aware score."""
        if not results:
            return 0.0
        
        total_cost = 0.0
        max_possible_cost = 0.0
        
        for result in results:
            expected = result['expected']
            actual = result['actual']
            
            if expected == actual:
                cost = 0.0  # No cost for correct routing
            else:
                cost = COST_MATRIX.get((expected, actual), 1.0)
            
            total_cost += cost
            max_possible_cost += max(COST_MATRIX.values())
        
        # Convert to score (higher is better)
        cost_efficiency = 1.0 - (total_cost / max_possible_cost)
        return cost_efficiency * 100
    
    def generate_test_queries(self, count: int = 100, recent_accuracy: float = 80.0) -> List[Dict[str, Any]]:
        """Generate test queries with curriculum sampling and hard negatives."""
        
        # Base query sets
        base_queries = {
            'basic_commands': [
                "Welcher Befehl zeigt die Festplattenbelegung an?",
                "Wie kann ich alle laufenden Prozesse anzeigen?",
                "Welches Kommando listet alle Dateien auf?",
                "Was macht der df Befehl?",
                "Wie zeige ich die CPU-Auslastung an?",
            ],
            'mathematical': [
                "Bestimme die mathematisch optimale Puffergröße für I/O-Operationen",
                "Löse das Gleichungssystem: x+y=10, x-y=2",
                "Berechne Fibonacci-Zahlen zur Bestimmung von Retry-Intervallen",
                "Finde die optimale Anzahl von Worker-Threads für CPU-intensive Tasks",
                "Bestimme die mathematisch optimale Cache-Größe für Datenbank-Queries",
            ],
            'code_tasks': [
                "Schreibe ein Bash-Skript zum automatischen Backup",
                "Erstelle eine Python-Funktion für Datei-Synchronisation",
                "Entwickle ein Shell-Skript für Log-Rotation",
                "Programmiere einen Service-Monitor in Python",
                "Schreibe ein Bash-Skript für System-Updates",
            ],
            'intermediate': [
                "Erkläre mir die Unterschiede zwischen verschiedenen Dateisystemen",
                "Wie funktioniert die Speicherverwaltung in Linux?",
                "Was sind die Vor- und Nachteile von Docker vs. LXC?",
                "Analysiere die Performance-Probleme bei hoher CPU-Last",
                "Vergleiche verschiedene Load-Balancing-Strategien",
            ]
        }
        
        # Get sampling mix based on recent accuracy
        mix = self.sampling_mix(recent_accuracy)
        
        queries = []
        
        # Add hard negatives (oversampled)
        hard_negatives = self.pull_hard_negatives(min(30, count // 4))
        for neg in hard_negatives:
            # Create mutations of hard negatives
            for _ in range(3):  # 3 mutations per hard negative
                mutated = self.mutate_query(neg['query'])
                queries.append({
                    'text': mutated,
                    'category': neg['category'],
                    'expected_model': neg['expected'],
                    'timestamp': time.time(),
                    'source': 'hard_negative_mutation'
                })
        
        # Fill remaining with curriculum sampling
        remaining = count - len(queries)
        
        for category, ratio in mix.items():
            category_count = int(remaining * ratio)
            category_queries = base_queries.get(category, [])
            
            for _ in range(category_count):
                if category_queries:
                    base_query = random.choice(category_queries)
                    mutated_query = self.mutate_query(base_query)
                    
                    queries.append({
                        'text': mutated_query,
                        'category': category,
                        'expected_model': self._get_expected_model(category),
                        'timestamp': time.time(),
                        'source': 'curriculum_sampling'
                    })
        
        return queries[:count]
    
    def _get_expected_model(self, category: str) -> str:
        """Get expected model for category."""
        mapping = {
            'basic_commands': MODEL_FAST,
            'mathematical': MODEL_HEAVY,
            'code_tasks': MODEL_CODE,
            'intermediate': MODEL_CODE  # Marked as "don't-care" in cost calculation
        }
        return mapping.get(category, MODEL_CODE)
    
    def analyze_queries_parallel(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze queries in parallel using ThreadPool."""
        def analyze_single(query_data):
            query_text = query_data['text']
            analysis = self.analyzer.analyze_query(query_text)
            
            return {
                'query': query_text,
                'category': query_data['category'],
                'expected': query_data['expected_model'],
                'actual': getattr(analysis, 'route_model', MODEL_CODE),
                'complexity': analysis.complexity_score,
                'reasoning': analysis.reasoning,
                'debug_info': getattr(analysis, 'debug_info', {}),
                'timestamp': query_data['timestamp'],
                'source': query_data.get('source', 'unknown')
            }
        
        max_workers = min(os.cpu_count() or 4, len(queries))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(analyze_single, queries))
        
        return results
    
    def update_confusion_matrix(self, results: List[Dict[str, Any]]):
        """Update confusion matrix and collect hard negatives."""
        new_hard_negatives = []
        
        for result in results:
            expected = result['expected']
            actual = result['actual']
            
            # Update confusion matrix
            with self.lock:
                self.confusion_matrix[(expected, actual)] += 1
            
            # Collect hard negatives (misclassified cases)
            if expected != actual:
                # Check if this is a costly error
                cost = COST_MATRIX.get((expected, actual), 1.0)
                if cost >= 1.5:  # High-cost errors
                    hard_negative = {
                        'query': result['query'],
                        'category': result['category'],
                        'expected': expected,
                        'actual': actual,
                        'cost': cost,
                        'timestamp': time.time(),
                        'error_count': 1,
                        'debug_info': result.get('debug_info', {})
                    }
                    
                    # Check if already exists and increment count
                    existing = None
                    for neg in self.hard_negatives:
                        if neg['query'] == result['query']:
                            existing = neg
                            break
                    
                    if existing:
                        existing['error_count'] += 1
                        existing['timestamp'] = time.time()
                    else:
                        new_hard_negatives.append(hard_negative)
        
        # Add new hard negatives
        self.hard_negatives.extend(new_hard_negatives)
        
        # Limit hard negatives to prevent memory issues
        if len(self.hard_negatives) > 1000:
            # Keep most recent and most frequent
            self.hard_negatives.sort(key=lambda x: (x['error_count'], x['timestamp']), reverse=True)
            self.hard_negatives = self.hard_negatives[:1000]
        
        if new_hard_negatives:
            logger.info(f"🔍 Added {len(new_hard_negatives)} new hard negatives")
    
    def calculate_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive metrics."""
        if not results:
            return {}
        
        # Basic accuracy
        correct = sum(1 for r in results if r['expected'] == r['actual'])
        accuracy = (correct / len(results)) * 100
        
        # Cost score
        cost_score = self.cost_score(results)
        
        # Per-class metrics
        class_metrics = {}
        for model in [MODEL_FAST, MODEL_CODE, MODEL_HEAVY]:
            expected_count = sum(1 for r in results if r['expected'] == model)
            actual_count = sum(1 for r in results if r['actual'] == model)
            correct_count = sum(1 for r in results if r['expected'] == model and r['actual'] == model)
            
            precision = (correct_count / max(actual_count, 1)) * 100
            recall = (correct_count / max(expected_count, 1)) * 100
            
            class_metrics[model] = {
                'precision': precision,
                'recall': recall,
                'expected_count': expected_count,
                'actual_count': actual_count,
                'correct_count': correct_count
            }
        
        # Heavy recall (critical metric)
        heavy_recall = class_metrics[MODEL_HEAVY]['recall']
        
        # Top misrouted queries
        misrouted = [r for r in results if r['expected'] != r['actual']]
        misrouted.sort(key=lambda x: COST_MATRIX.get((x['expected'], x['actual']), 1.0), reverse=True)
        top_misrouted = misrouted[:10]
        
        return {
            'accuracy': accuracy,
            'cost_score': cost_score,
            'heavy_recall': heavy_recall,
            'class_metrics': class_metrics,
            'top_misrouted': top_misrouted,
            'confusion_matrix': dict(self.confusion_matrix)
        }
    
    def save_progress_atomic(self, data: Dict[str, Any]):
        """Atomic JSON write using temp file."""
        progress_file = 'optimization_logs/latest_progress.json'
        
        # Write to temp file first
        with tempfile.NamedTemporaryFile(mode='w', delete=False, 
                                       dir='optimization_logs', 
                                       suffix='.tmp') as tmp_file:
            json.dump(data, tmp_file, indent=2, default=str)
            tmp_name = tmp_file.name
        
        # Atomic replace
        os.replace(tmp_name, progress_file)
    
    def load_best_params(self):
        """Load best parameters from previous runs."""
        try:
            with open('conf/best_params.json', 'r') as f:
                self.best_params = json.load(f)
                self.current_params.update(self.best_params['params'])
                self.best_cost_score = self.best_params.get('cost_score', 0.0)
                logger.info(f"📚 Loaded best params: cost_score={self.best_cost_score:.1f}")
        except FileNotFoundError:
            logger.info("📚 No previous best params found")
    
    def save_best_params(self, cost_score: float):
        """Save best parameters if improved."""
        if cost_score > self.best_cost_score:
            self.best_cost_score = cost_score
            self.best_params = {
                'params': self.current_params.copy(),
                'cost_score': cost_score,
                'timestamp': time.time(),
                'cycle': self.cycle_count
            }
            
            with open('conf/best_params.json', 'w') as f:
                json.dump(self.best_params, f, indent=2, default=str)
            
            logger.info(f"💾 New best params saved: cost_score={cost_score:.1f}")
    
    async def run_optimization_cycle(self, recent_accuracy: float = 80.0) -> Dict[str, Any]:
        """Run enhanced optimization cycle."""
        cycle_start = time.time()
        self.cycle_count += 1
        
        logger.info(f"🚀 Starting enhanced cycle {self.cycle_count}")
        
        # Parameter tuning with bandits
        if self.cycle_count > 1:  # Skip first cycle
            arm_idx = self.bandit_pick()
            new_params = PARAM_SPACE[arm_idx]
            self.set_router_params(**new_params)
            logger.info(f"🎰 Selected parameter set {arm_idx}: {new_params}")
        
        # Generate test queries with curriculum sampling
        queries_per_cycle = int(os.environ.get('QPC', '100'))
        test_queries = self.generate_test_queries(queries_per_cycle, recent_accuracy)
        
        # Analyze queries in parallel
        results = self.analyze_queries_parallel(test_queries)
        
        # Update confusion matrix and hard negatives
        self.update_confusion_matrix(results)
        
        # Calculate comprehensive metrics
        metrics = self.calculate_metrics(results)
        
        # Update bandit if not first cycle
        if self.cycle_count > 1:
            reward = metrics['cost_score']
            self.bandit_update(arm_idx, reward)
            
            # Save best params if improved
            self.save_best_params(metrics['cost_score'])
        
        cycle_time = time.time() - cycle_start
        self.total_queries += len(results)
        
        # Prepare cycle summary
        cycle_summary = {
            'cycle': self.cycle_count,
            'timestamp': cycle_start,
            'metrics': metrics,
            'cycle_time': cycle_time,
            'query_count': len(results),
            'total_queries': self.total_queries,
            'current_params': self.current_params.copy(),
            'bandit_stats': self.parameter_bandits.copy(),
            'hard_negatives_count': len(self.hard_negatives)
        }
        
        # Save progress atomically
        self.save_progress_atomic(cycle_summary)
        
        # Save hard negatives
        self.save_hard_negatives()
        
        logger.info(f"✅ Cycle {self.cycle_count}: Accuracy={metrics['accuracy']:.1f}%, "
                   f"Cost-Score={metrics['cost_score']:.1f}, "
                   f"Heavy-Recall={metrics['heavy_recall']:.1f}%")
        
        return cycle_summary
    
    async def run_overnight_optimization(self, target_hours: float = 8.0):
        """Run advanced overnight optimization."""
        logger.info(f"🌙 Starting advanced overnight optimization for {target_hours} hours")
        
        end_time = time.time() + (target_hours * 3600)
        sleep_secs = int(os.environ.get('OO_SLEEP_SECS', '30'))
        
        recent_accuracy = 80.0  # Initial baseline
        
        try:
            while time.time() < end_time:
                # Run cycle
                cycle_summary = await self.run_optimization_cycle(recent_accuracy)
                
                # Update recent accuracy for curriculum sampling
                recent_accuracy = cycle_summary['metrics']['accuracy']
                
                # Sleep between cycles
                await asyncio.sleep(sleep_secs)
                
        except KeyboardInterrupt:
            logger.info("⏹️  Optimization stopped by user")
        except Exception as e:
            logger.error(f"❌ Optimization error: {e}")
        finally:
            # Generate final report
            await self.generate_final_report()
    
    async def generate_final_report(self):
        """Generate comprehensive final report."""
        runtime = time.time() - self.start_time
        
        # Calculate final metrics
        final_metrics = {
            'runtime_hours': runtime / 3600,
            'total_cycles': self.cycle_count,
            'total_queries': self.total_queries,
            'best_params': self.best_params,
            'best_cost_score': self.best_cost_score,
            'final_confusion_matrix': dict(self.confusion_matrix),
            'hard_negatives_collected': len(self.hard_negatives),
            'bandit_final_stats': self.parameter_bandits.copy()
        }
        
        # Save final report with JSON-safe serialization
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Convert any tuple keys to strings for JSON compatibility
        def make_json_safe(obj):
            if isinstance(obj, dict):
                return {str(k): make_json_safe(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [make_json_safe(item) for item in obj]
            else:
                return obj
        
        json_safe_metrics = make_json_safe(final_metrics)
        
        with open(f'reports/overnight_summary_{timestamp}.json', 'w') as f:
            json.dump(json_safe_metrics, f, indent=2, default=str)
        
        logger.info("🏁 Advanced overnight optimization completed!")
        logger.info(f"📊 Best cost score: {self.best_cost_score:.1f}")
        logger.info(f"🎯 Hard negatives collected: {len(self.hard_negatives)}")


async def main():
    """Main function."""
    optimizer = AdvancedOvernightOptimizer()
    
    target_hours = 8.0
    if len(sys.argv) > 1:
        try:
            target_hours = float(sys.argv[1])
        except ValueError:
            logger.warning(f"Invalid hours: {sys.argv[1]}, using 8.0")
    
    await optimizer.run_overnight_optimization(target_hours)


if __name__ == "__main__":
    asyncio.run(main())