#!/usr/bin/env python3
"""
Autonomous Linux Superhelfer Optimization System
Runs continuous tests and optimizations while user is away.
"""

import asyncio
import json
import time
import logging
import random
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import signal
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autonomous_optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutonomousOptimizer:
    """Autonomous system for continuous Linux expertise optimization."""
    
    def __init__(self):
        self.running = True
        self.start_time = datetime.now()
        self.test_results = []
        self.optimization_metrics = {
            'total_tests': 0,
            'successful_routes': 0,
            'failed_routes': 0,
            'avg_response_time': 0,
            'avg_confidence': 0,
            'model_usage': {'fast': 0, 'code': 0, 'heavy': 0}
        }
        
        # Linux test queries for different complexity levels
        self.linux_test_queries = {
            'basic': [
                "Wie kann ich alle laufenden Prozesse anzeigen?",
                "Was ist der Unterschied zwischen ls und ll?",
                "Wie erstelle ich ein neues Verzeichnis?",
                "Welcher Befehl zeigt die Festplattenbelegung an?",
                "Wie kann ich eine Datei kopieren?",
                "Was macht der grep Befehl?",
                "Wie ändere ich Dateiberechtigungen mit chmod?",
                "Welcher Befehl zeigt Systeminformationen an?"
            ],
            'intermediate': [
                "Schreibe ein Bash-Skript zum automatischen Backup von /home",
                "Wie konfiguriere ich einen Cron-Job für tägliche Backups?",
                "Erkläre die Unterschiede zwischen systemctl und service",
                "Wie überwache ich die CPU- und RAM-Auslastung in Echtzeit?",
                "Erstelle ein Skript zur Logrotation für Apache-Logs",
                "Wie richte ich SSH-Keys für passwortlose Anmeldung ein?",
                "Welche Schritte sind nötig für ein Kernel-Update?",
                "Wie debugge ich Netzwerkprobleme mit netstat und ss?"
            ],
            'advanced': [
                "Entwickle ein komplexes Monitoring-System mit Bash und Python",
                "Erstelle ein Load-Balancing-Setup mit nginx und mehreren Backends",
                "Implementiere ein automatisches Failover-System für Datenbanken",
                "Schreibe ein Skript zur Performance-Analyse von I/O-Operationen",
                "Konfiguriere ein High-Availability-Cluster mit Pacemaker",
                "Entwickle ein Custom-Kernel-Modul für Hardware-Monitoring",
                "Implementiere Zero-Downtime-Deployment mit Docker und Kubernetes",
                "Erstelle ein Security-Audit-System für Linux-Server"
            ],
            'mathematical': [
                "Berechne die optimale Anzahl von Worker-Prozessen basierend auf CPU-Kernen",
                "Löse das Gleichungssystem für Load-Balancing-Gewichtung: x+y+z=100, 2x+y=80, x+3z=90",
                "Bestimme die mathematisch optimale Puffergröße für I/O-Operationen",
                "Berechne Fibonacci-Zahlen zur Bestimmung von Retry-Intervallen",
                "Finde die Primfaktoren einer Process-ID zur Hash-Verteilung"
            ]
        }
        
        # Expected routing for each category
        self.expected_routing = {
            'basic': 'fast',
            'intermediate': 'code', 
            'advanced': 'code',
            'mathematical': 'heavy'
        }
        
        # Signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def run_optimization_cycle(self):
        """Main optimization loop."""
        logger.info("🚀 Starting Autonomous Linux Optimization System")
        logger.info(f"Start time: {self.start_time}")
        
        cycle = 0
        while self.running:
            cycle += 1
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 OPTIMIZATION CYCLE {cycle}")
            logger.info(f"{'='*60}")
            
            try:
                # Run test suite
                await self._run_test_suite()
                
                # Analyze results
                await self._analyze_performance()
                
                # Generate optimization recommendations
                await self._generate_optimizations()
                
                # Save progress
                self._save_progress()
                
                # Wait before next cycle (5 minutes)
                if self.running:
                    logger.info("⏳ Waiting 5 minutes before next cycle...")
                    await asyncio.sleep(300)
                    
            except Exception as e:
                logger.error(f"Error in optimization cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
        
        logger.info("🏁 Optimization system stopped gracefully")
        self._generate_final_report()
    
    async def _run_test_suite(self):
        """Run comprehensive test suite."""
        logger.info("🧪 Running Linux expertise test suite...")
        
        # Test each category
        for category, queries in self.linux_test_queries.items():
            logger.info(f"Testing {category} queries...")
            
            # Test 2-3 random queries from each category
            test_queries = random.sample(queries, min(3, len(queries)))
            
            for query in test_queries:
                await self._test_single_query(query, category)
                
                # Small delay between tests
                await asyncio.sleep(2)
    
    async def _test_single_query(self, query: str, category: str):
        """Test a single query and record results."""
        try:
            start_time = time.time()
            
            # Send query to system
            response = requests.post(
                'http://localhost:8001/infer',
                json={'query': query},
                timeout=120
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Record test result
                result = {
                    'timestamp': datetime.now().isoformat(),
                    'query': query[:100] + '...' if len(query) > 100 else query,
                    'category': category,
                    'expected_model': self.expected_routing[category],
                    'actual_model': data.get('routing_info', {}).get('selected_model', 'unknown'),
                    'complexity_score': data.get('routing_info', {}).get('complexity_score', 0),
                    'confidence': data.get('confidence', 0),
                    'response_time': response_time,
                    'success': True,
                    'model_used': data.get('model_used', 'unknown')
                }
                
                # Check if routing was correct
                routing_correct = result['actual_model'] == result['expected_model']
                result['routing_correct'] = routing_correct
                
                self.test_results.append(result)
                self._update_metrics(result)
                
                # Log result
                status = "✅" if routing_correct else "⚠️"
                logger.info(f"{status} {category}: {result['actual_model']} model, "
                          f"confidence: {result['confidence']:.3f}, "
                          f"time: {response_time:.2f}s")
                
            else:
                logger.error(f"❌ Query failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Test error: {e}")
    
    def _update_metrics(self, result: Dict[str, Any]):
        """Update optimization metrics."""
        self.optimization_metrics['total_tests'] += 1
        
        if result['routing_correct']:
            self.optimization_metrics['successful_routes'] += 1
        else:
            self.optimization_metrics['failed_routes'] += 1
        
        # Update averages
        total = self.optimization_metrics['total_tests']
        self.optimization_metrics['avg_response_time'] = (
            (self.optimization_metrics['avg_response_time'] * (total - 1) + result['response_time']) / total
        )
        self.optimization_metrics['avg_confidence'] = (
            (self.optimization_metrics['avg_confidence'] * (total - 1) + result['confidence']) / total
        )
        
        # Update model usage
        model = result['actual_model']
        if model in self.optimization_metrics['model_usage']:
            self.optimization_metrics['model_usage'][model] += 1
    
    async def _analyze_performance(self):
        """Analyze current performance metrics."""
        if not self.test_results:
            return
        
        logger.info("📊 Performance Analysis:")
        
        # Calculate routing accuracy
        total_tests = len(self.test_results)
        correct_routes = sum(1 for r in self.test_results if r['routing_correct'])
        accuracy = (correct_routes / total_tests) * 100 if total_tests > 0 else 0
        
        logger.info(f"   Routing Accuracy: {accuracy:.1f}% ({correct_routes}/{total_tests})")
        logger.info(f"   Avg Response Time: {self.optimization_metrics['avg_response_time']:.2f}s")
        logger.info(f"   Avg Confidence: {self.optimization_metrics['avg_confidence']:.3f}")
        
        # Model usage distribution
        usage = self.optimization_metrics['model_usage']
        total_usage = sum(usage.values())
        if total_usage > 0:
            logger.info("   Model Usage:")
            for model, count in usage.items():
                percentage = (count / total_usage) * 100
                logger.info(f"     {model}: {count} ({percentage:.1f}%)")
        
        # Identify problem areas
        await self._identify_issues()
    
    async def _identify_issues(self):
        """Identify performance issues and routing problems."""
        logger.info("🔍 Issue Analysis:")
        
        # Check for routing mismatches by category
        category_issues = {}
        for result in self.test_results:
            category = result['category']
            if not result['routing_correct']:
                if category not in category_issues:
                    category_issues[category] = []
                category_issues[category].append(result)
        
        if category_issues:
            logger.info("   Routing Issues Found:")
            for category, issues in category_issues.items():
                logger.info(f"     {category}: {len(issues)} misrouted queries")
                
                # Show examples
                for issue in issues[:2]:  # Show first 2 examples
                    logger.info(f"       Expected: {issue['expected_model']}, "
                              f"Got: {issue['actual_model']}, "
                              f"Complexity: {issue['complexity_score']:.3f}")
        
        # Check for slow responses
        slow_responses = [r for r in self.test_results if r['response_time'] > 30]
        if slow_responses:
            logger.info(f"   Slow Responses: {len(slow_responses)} queries > 30s")
        
        # Check for low confidence
        low_confidence = [r for r in self.test_results if r['confidence'] < 0.6]
        if low_confidence:
            logger.info(f"   Low Confidence: {len(low_confidence)} queries < 0.6")
    
    async def _generate_optimizations(self):
        """Generate optimization recommendations."""
        logger.info("🎯 Optimization Recommendations:")
        
        if not self.test_results:
            logger.info("   No data available for optimization")
            return
        
        # Analyze routing patterns
        routing_accuracy = sum(1 for r in self.test_results if r['routing_correct']) / len(self.test_results)
        
        if routing_accuracy < 0.8:
            logger.info("   ⚠️  Routing accuracy below 80% - consider threshold adjustments")
        
        # Check mathematical routing
        math_results = [r for r in self.test_results if r['category'] == 'mathematical']
        if math_results:
            math_accuracy = sum(1 for r in math_results if r['routing_correct']) / len(math_results)
            if math_accuracy < 0.9:
                logger.info("   🧮 Mathematical routing needs improvement")
        
        # Performance recommendations
        avg_time = self.optimization_metrics['avg_response_time']
        if avg_time > 20:
            logger.info("   ⏱️  Average response time high - consider model optimization")
        
        # Confidence analysis
        avg_confidence = self.optimization_metrics['avg_confidence']
        if avg_confidence < 0.7:
            logger.info("   🎯 Average confidence low - consider training data enhancement")
    
    def _save_progress(self):
        """Save current progress to file."""
        progress_data = {
            'start_time': self.start_time.isoformat(),
            'current_time': datetime.now().isoformat(),
            'metrics': self.optimization_metrics,
            'recent_results': self.test_results[-10:] if len(self.test_results) > 10 else self.test_results
        }
        
        with open('optimization_progress.json', 'w') as f:
            json.dump(progress_data, f, indent=2)
    
    def _generate_final_report(self):
        """Generate final optimization report."""
        logger.info("\n" + "="*60)
        logger.info("📋 FINAL OPTIMIZATION REPORT")
        logger.info("="*60)
        
        runtime = datetime.now() - self.start_time
        logger.info(f"Runtime: {runtime}")
        logger.info(f"Total Tests: {self.optimization_metrics['total_tests']}")
        
        if self.optimization_metrics['total_tests'] > 0:
            accuracy = (self.optimization_metrics['successful_routes'] / 
                       self.optimization_metrics['total_tests']) * 100
            logger.info(f"Routing Accuracy: {accuracy:.1f}%")
            logger.info(f"Average Response Time: {self.optimization_metrics['avg_response_time']:.2f}s")
            logger.info(f"Average Confidence: {self.optimization_metrics['avg_confidence']:.3f}")
        
        # Save final report
        report_data = {
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'runtime_seconds': runtime.total_seconds(),
            'final_metrics': self.optimization_metrics,
            'all_results': self.test_results
        }
        
        with open(f'optimization_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info("📁 Final report saved to optimization_report_*.json")

async def main():
    """Main entry point."""
    optimizer = AutonomousOptimizer()
    await optimizer.run_optimization_cycle()

if __name__ == "__main__":
    asyncio.run(main())