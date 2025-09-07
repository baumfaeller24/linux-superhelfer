#!/usr/bin/env python3
"""
HARDCORE Linux Wizard Training System
====================================

Extreme Training für absolute Linux-Zauberer mit:
- Stress-Testing unter Last
- Adaptive Schwierigkeitsgrade
- Failure-Recovery Training
- Performance unter Druck
- Multi-Threading Chaos-Engineering
- Memory/CPU Pressure Simulation
- Real-World Crisis Scenarios
"""

import asyncio, json, time, logging, os, random, signal, gc, argparse, threading
from datetime import datetime, timedelta
from pathlib import Path
from logging.handlers import RotatingFileHandler
import subprocess
import concurrent.futures
from typing import Dict, List, Any
import hashlib

try:
    import psutil
    import numpy as np
except ImportError:
    psutil = None
    np = None

HARDCORE_CFG = {
    "max_cycles": 2000,              # Doppelt so viele Zyklen
    "cycle_interval_sec": 15,        # Schnellere Zyklen = mehr Stress
    "parallel_modules": 8,           # Mehr parallele Module
    "module_timeout_sec": 10,        # Weniger Zeit pro Modul = Druck
    "stop_at_hour": 7,
    "max_hours": 12,                 # Längeres Training
    "max_errors": 100,               # Mehr Fehlertoleranz
    "log_max_mb": 100,
    "log_backups": 10,
    "seed": 1337,
    
    # HARDCORE Features
    "stress_mode": True,             # Aktiviert Stress-Testing
    "chaos_engineering": True,       # Chaos Engineering
    "adaptive_difficulty": True,     # Schwierigkeit steigt automatisch
    "memory_pressure": True,         # Simuliert Memory-Druck
    "cpu_pressure": True,            # Simuliert CPU-Last
    "failure_injection": True,       # Injiziert zufällige Failures
    "crisis_scenarios": True,        # Real-World Crisis Training
    "performance_benchmarks": True,  # Performance-Messungen
    "hardcore_multiplier": 2.5,      # Multiplikator für Schwierigkeit
}

class HardcoreLinuxWizardTrainer:
    def __init__(self, cfg: dict):
        self.cfg = {**HARDCORE_CFG, **cfg}
        self.training_log_dir = Path("hardcore_wizard_logs")
        self.training_log_dir.mkdir(exist_ok=True)
        
        # Hardcore-spezifische Verzeichnisse
        self.stress_log_dir = self.training_log_dir / "stress_tests"
        self.crisis_log_dir = self.training_log_dir / "crisis_scenarios"
        self.benchmark_log_dir = self.training_log_dir / "benchmarks"
        
        for d in [self.stress_log_dir, self.crisis_log_dir, self.benchmark_log_dir]:
            d.mkdir(exist_ok=True)
        
        self.state_file = self.training_log_dir / "hardcore_state.json"
        self.heartbeat = self.training_log_dir / "hardcore_heartbeat.txt"
        
        # Enhanced Logging
        log_file = self.training_log_dir / f"hardcore_wizard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        handler = RotatingFileHandler(
            log_file, 
            maxBytes=self.cfg["log_max_mb"]*1024*1024, 
            backupCount=self.cfg["log_backups"]
        )
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[handler, logging.StreamHandler()]
        )
        self.logger = logging.getLogger("hardcore_wizard")
        
        random.seed(self.cfg["seed"])
        self._stop = asyncio.Event()
        self._errors = 0
        self._stress_level = 1.0
        self._crisis_active = False
        
        # Performance Tracking
        self.performance_metrics = {
            "cycle_times": [],
            "memory_usage": [],
            "cpu_usage": [],
            "error_rates": [],
            "stress_levels": []
        }
        
        # Hardcore Training Modules
        self.training_modules = {
            "extreme_command_mastery": self.train_extreme_command_mastery,
            "crisis_sysadmin": self.train_crisis_sysadmin,
            "performance_under_pressure": self.train_performance_under_pressure,
            "security_war_games": self.train_security_war_games,
            "chaos_troubleshooting": self.train_chaos_troubleshooting,
            "extreme_shell_scripting": self.train_extreme_shell_scripting,
            "network_warfare": self.train_network_warfare,
            "container_chaos": self.train_container_chaos,
            "kernel_hacking": self.train_kernel_hacking,
            "distributed_systems": self.train_distributed_systems
        }
        
        # Crisis Scenarios
        self.crisis_scenarios = [
            "server_meltdown",
            "network_partition",
            "disk_failure_cascade",
            "memory_leak_explosion",
            "security_breach_response",
            "database_corruption",
            "load_balancer_failure",
            "dns_poisoning_attack"
        ]
        
        self.linux_knowledge_base = self.load_hardcore_knowledge_base()
        self.training_stats = self._load_state() or {
            "cycles_completed": 0,
            "knowledge_gained": 0,
            "patterns_learned": 0,
            "expertise_level": "Hardcore Beginner",
            "stress_tests_passed": 0,
            "crisis_scenarios_survived": 0,
            "performance_score": 0,
            "hardcore_points": 0,
            "started_at": datetime.now().isoformat(),
            "version": "hardcore_v2.0"
        }

    def load_hardcore_knowledge_base(self):
        """Lädt die Hardcore Linux-Wissensbasis"""
        return {
            "extreme_commands": {
                "system_forensics": ["strace", "ltrace", "gdb", "objdump", "readelf", "hexdump"],
                "performance_analysis": ["perf", "valgrind", "systemtap", "ftrace", "bpftrace"],
                "network_hacking": ["nmap", "masscan", "zmap", "hping3", "scapy", "tcpreplay"],
                "kernel_debugging": ["crash", "kgdb", "kdb", "sysrq", "kdump", "kexec"],
                "container_internals": ["runc", "containerd", "cgroups", "namespaces", "seccomp"],
                "security_tools": ["metasploit", "burpsuite", "wireshark", "aircrack", "hashcat"]
            },
            "crisis_patterns": {
                "system_failure": [
                    "Kernel panic recovery",
                    "Filesystem corruption repair",
                    "Memory exhaustion handling",
                    "CPU overload mitigation"
                ],
                "security_incidents": [
                    "Rootkit detection and removal",
                    "DDoS attack mitigation",
                    "Data breach containment",
                    "Privilege escalation prevention"
                ],
                "performance_disasters": [
                    "Database deadlock resolution",
                    "Memory leak hunting",
                    "CPU thrashing elimination",
                    "I/O bottleneck removal"
                ]
            },
            "hardcore_techniques": {
                "kernel_hacking": [
                    "Custom kernel module development",
                    "System call interception",
                    "Memory management optimization",
                    "Interrupt handler modification"
                ],
                "advanced_networking": [
                    "Custom protocol implementation",
                    "Network stack optimization",
                    "Traffic shaping algorithms",
                    "Load balancing strategies"
                ],
                "extreme_automation": [
                    "Self-healing systems",
                    "Predictive failure detection",
                    "Autonomous scaling",
                    "Chaos engineering frameworks"
                ]
            }
        }

    def install_signal_handlers(self):
        def _sigterm(_sig, _frm): 
            self.logger.warning("🔥 SIGTERM received during hardcore training!")
            self._stop.set()
        def _sigint(_sig, _frm): 
            self.logger.warning("🔥 SIGINT received - Emergency shutdown!")
            self._stop.set()
        signal.signal(signal.SIGTERM, _sigterm)
        signal.signal(signal.SIGINT, _sigint)

    def _load_state(self):
        if self.state_file.exists():
            try: 
                return json.loads(self.state_file.read_text())
            except Exception as e:
                self.logger.error(f"Failed to load state: {e}")
                return None
        return None

    def _save_state(self):
        tmp = self.training_stats.copy()
        tmp["saved_at"] = datetime.now().isoformat()
        tmp["stress_level"] = self._stress_level
        tmp["performance_metrics"] = self.performance_metrics
        self.state_file.write_text(json.dumps(tmp, indent=2))

    def _heartbeat(self, cycle: int):
        heartbeat_data = {
            "ts": datetime.now().isoformat(),
            "cycle": cycle,
            "stress_level": self._stress_level,
            "crisis_active": self._crisis_active,
            "expertise_level": self.training_stats["expertise_level"],
            "hardcore_points": self.training_stats["hardcore_points"]
        }
        
        if psutil:
            process = psutil.Process()
            heartbeat_data.update({
                "mem_mb": process.memory_info().rss // (1024*1024),
                "cpu_percent": process.cpu_percent(),
                "threads": process.num_threads()
            })
        
        self.heartbeat.write_text(json.dumps(heartbeat_data, indent=2))

    def adaptive_difficulty_adjustment(self):
        """Passt die Schwierigkeit basierend auf Performance an"""
        if not self.cfg["adaptive_difficulty"]:
            return
        
        cycles = self.training_stats["cycles_completed"]
        error_rate = self._errors / max(cycles, 1)
        
        # Erhöhe Stress bei guter Performance
        if error_rate < 0.1 and cycles > 10:
            self._stress_level = min(5.0, self._stress_level * 1.1)
            self.logger.info(f"🔥 Difficulty increased! Stress level: {self._stress_level:.2f}")
        
        # Reduziere Stress bei zu vielen Fehlern
        elif error_rate > 0.3:
            self._stress_level = max(0.5, self._stress_level * 0.9)
            self.logger.warning(f"⚡ Difficulty reduced. Stress level: {self._stress_level:.2f}")

    def inject_chaos(self):
        """Chaos Engineering - Injiziert zufällige Probleme"""
        if not self.cfg["chaos_engineering"]:
            return
        
        if random.random() < 0.1 * self._stress_level:  # 10% Chance * Stress Level
            chaos_type = random.choice([
                "memory_spike",
                "cpu_burn",
                "disk_fill",
                "network_delay",
                "process_kill"
            ])
            
            self.logger.warning(f"🌪️  CHAOS INJECTION: {chaos_type}")
            
            if chaos_type == "memory_spike":
                # Simuliere Memory-Spike
                asyncio.create_task(self._simulate_memory_spike())
            elif chaos_type == "cpu_burn":
                # Simuliere CPU-Last
                asyncio.create_task(self._simulate_cpu_burn())

    async def _simulate_memory_spike(self):
        """Simuliert einen Memory-Spike"""
        try:
            # Allokiere temporär viel Memory
            memory_hog = bytearray(50 * 1024 * 1024)  # 50MB
            await asyncio.sleep(5)
            del memory_hog
            gc.collect()
        except:
            pass

    async def _simulate_cpu_burn(self):
        """Simuliert CPU-Last"""
        def cpu_burn():
            end_time = time.time() + 3  # 3 Sekunden
            while time.time() < end_time:
                _ = sum(i*i for i in range(1000))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(cpu_burn) for _ in range(2)]
            await asyncio.gather(*[asyncio.wrap_future(f) for f in futures])

    def trigger_crisis_scenario(self):
        """Triggert ein Crisis-Szenario"""
        if not self.cfg["crisis_scenarios"] or self._crisis_active:
            return
        
        if random.random() < 0.05 * self._stress_level:  # 5% Chance * Stress Level
            scenario = random.choice(self.crisis_scenarios)
            self._crisis_active = True
            self.logger.critical(f"🚨 CRISIS SCENARIO ACTIVATED: {scenario}")
            
            # Starte Crisis-Handling in separatem Task
            asyncio.create_task(self._handle_crisis_scenario(scenario))

    async def _handle_crisis_scenario(self, scenario: str):
        """Behandelt ein Crisis-Szenario"""
        start_time = time.time()
        
        try:
            if scenario == "server_meltdown":
                await self._simulate_server_meltdown()
            elif scenario == "network_partition":
                await self._simulate_network_partition()
            elif scenario == "memory_leak_explosion":
                await self._simulate_memory_leak()
            # ... weitere Szenarien
            
            # Crisis erfolgreich überstanden
            duration = time.time() - start_time
            self.training_stats["crisis_scenarios_survived"] += 1
            self.training_stats["hardcore_points"] += int(100 * self._stress_level)
            
            self.logger.info(f"✅ Crisis scenario '{scenario}' survived in {duration:.1f}s!")
            
        except Exception as e:
            self.logger.error(f"❌ Crisis scenario '{scenario}' failed: {e}")
        finally:
            self._crisis_active = False

    async def _simulate_server_meltdown(self):
        """Simuliert einen Server-Meltdown"""
        # Simuliere verschiedene Probleme gleichzeitig
        tasks = [
            self._simulate_memory_spike(),
            self._simulate_cpu_burn(),
            asyncio.sleep(2)  # Simuliere Disk I/O Probleme
        ]
        await asyncio.gather(*tasks)

    async def _simulate_network_partition(self):
        """Simuliert eine Netzwerk-Partition"""
        # Simuliere Netzwerk-Delays und Timeouts
        await asyncio.sleep(3)

    async def _simulate_memory_leak(self):
        """Simuliert einen Memory Leak"""
        memory_chunks = []
        try:
            for i in range(10):
                chunk = bytearray(10 * 1024 * 1024)  # 10MB chunks
                memory_chunks.append(chunk)
                await asyncio.sleep(0.5)
        finally:
            del memory_chunks
            gc.collect()

    # Hardcore Training Modules
    async def train_extreme_command_mastery(self, cycle):
        """Extreme Command Mastery unter Stress"""
        stress_factor = self._stress_level
        
        # Simuliere komplexe Command-Chains unter Zeitdruck
        scenarios = [
            f"Find and analyze {int(1000 * stress_factor)} log files simultaneously",
            f"Process {int(500 * stress_factor)} concurrent network connections",
            f"Monitor {int(100 * stress_factor)} system processes in real-time"
        ]
        
        for scenario in scenarios:
            # Simuliere intensive Verarbeitung
            await asyncio.sleep(0.1 * stress_factor)
            
            if random.random() < 0.1:  # 10% Failure Rate
                raise Exception(f"Command mastery failed under stress: {scenario}")
        
        points = int(50 * stress_factor)
        self.training_stats["patterns_learned"] += points
        self.training_stats["hardcore_points"] += points
        
        return f"Extreme Command Mastery: {len(scenarios)} scenarios @ {stress_factor:.1f}x stress"

    async def train_crisis_sysadmin(self, cycle):
        """Crisis SysAdmin Training"""
        crisis_situations = [
            "Mass service failure recovery",
            "Database corruption under load",
            "Security breach containment",
            "Resource exhaustion mitigation"
        ]
        
        for situation in crisis_situations:
            await asyncio.sleep(0.2 * self._stress_level)
            
            # Höhere Failure-Rate bei Crisis-Training
            if random.random() < 0.15:
                raise Exception(f"Crisis management failed: {situation}")
        
        points = int(75 * self._stress_level)
        self.training_stats["hardcore_points"] += points
        return f"Crisis SysAdmin: {len(crisis_situations)} crises handled"

    async def train_performance_under_pressure(self, cycle):
        """Performance Optimization unter extremem Druck"""
        # Simuliere Performance-Tuning unter Last
        optimization_tasks = [
            "Real-time kernel tuning",
            "Live memory optimization",
            "Hot-swap performance fixes",
            "Zero-downtime scaling"
        ]
        
        # Parallele Ausführung für mehr Stress
        tasks = []
        for task in optimization_tasks:
            tasks.append(self._simulate_performance_task(task))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in results if not isinstance(r, Exception))
        points = int(successful * 60 * self._stress_level)
        self.training_stats["performance_score"] += points
        self.training_stats["hardcore_points"] += points
        
        return f"Performance Under Pressure: {successful}/{len(optimization_tasks)} tasks completed"

    async def _simulate_performance_task(self, task_name):
        """Simuliert eine Performance-Optimierung"""
        # Simuliere CPU-intensive Arbeit
        await asyncio.sleep(0.3 * self._stress_level)
        
        if random.random() < 0.12:  # 12% Failure Rate
            raise Exception(f"Performance task failed: {task_name}")
        
        return f"Completed: {task_name}"

    async def train_security_war_games(self, cycle):
        """Security War Games Training"""
        return await self._generic_hardcore_training("Security War Games", 0.25, 0.08)

    async def train_chaos_troubleshooting(self, cycle):
        """Chaos Troubleshooting Training"""
        return await self._generic_hardcore_training("Chaos Troubleshooting", 0.3, 0.15)

    async def train_extreme_shell_scripting(self, cycle):
        """Extreme Shell Scripting unter Zeitdruck"""
        return await self._generic_hardcore_training("Extreme Shell Scripting", 0.2, 0.1)

    async def train_network_warfare(self, cycle):
        """Network Warfare Training"""
        return await self._generic_hardcore_training("Network Warfare", 0.35, 0.12)

    async def train_container_chaos(self, cycle):
        """Container Chaos Engineering"""
        return await self._generic_hardcore_training("Container Chaos", 0.28, 0.14)

    async def train_kernel_hacking(self, cycle):
        """Kernel Hacking Training"""
        return await self._generic_hardcore_training("Kernel Hacking", 0.4, 0.2)

    async def train_distributed_systems(self, cycle):
        """Distributed Systems unter Chaos"""
        return await self._generic_hardcore_training("Distributed Systems", 0.45, 0.18)

    async def _generic_hardcore_training(self, module_name, base_time, failure_rate):
        """Generisches Hardcore-Training-Modul"""
        await asyncio.sleep(base_time * self._stress_level)
        
        if random.random() < failure_rate * self._stress_level:
            raise Exception(f"{module_name} failed under hardcore conditions")
        
        points = int(40 * self._stress_level)
        self.training_stats["hardcore_points"] += points
        return f"{module_name}: Hardcore level {self._stress_level:.1f}x"

    def update_expertise_level(self):
        """Aktualisiert Expertise Level für Hardcore Training"""
        cycles = self.training_stats["cycles_completed"]
        points = self.training_stats["hardcore_points"]
        
        if cycles < 20:
            level = "Hardcore Beginner"
        elif cycles < 100:
            level = "Stress Warrior"
        elif cycles < 300:
            level = "Crisis Master"
        elif cycles < 600:
            level = "Chaos Engineer"
        elif cycles < 1000:
            level = "Linux Samurai"
        elif points > 50000:
            level = "Ultimate Linux Wizard"
        else:
            level = "Linux God Emperor"
        
        self.training_stats["expertise_level"] = level
        return level

    def resource_guard(self):
        """Enhanced Resource Guard mit Hardcore-Features"""
        if psutil:
            process = psutil.Process()
            memory_info = process.memory_info()
            rss_mb = memory_info.rss / (1024*1024)
            
            # Tracking für Performance-Metriken
            self.performance_metrics["memory_usage"].append(rss_mb)
            self.performance_metrics["cpu_usage"].append(process.cpu_percent())
            self.performance_metrics["stress_levels"].append(self._stress_level)
            
            # Aggressive Memory Management bei Hardcore Training
            total_memory_mb = psutil.virtual_memory().total / (1024*1024)
            memory_threshold = 0.85 if self._stress_level > 2.0 else 0.80
            
            if rss_mb > (memory_threshold * total_memory_mb):
                self.logger.warning(f"🔥 HIGH MEMORY USAGE: {rss_mb:.0f}MB ({rss_mb/total_memory_mb*100:.1f}%)")
                gc.collect()
                time.sleep(1)
                
                # Bei extremer Memory-Usage: Stress reduzieren
                if rss_mb > (0.90 * total_memory_mb):
                    self._stress_level = max(0.5, self._stress_level * 0.8)
                    self.logger.warning(f"Emergency stress reduction: {self._stress_level:.2f}")
        else:
            gc.collect()

    async def run_training_cycle(self, cycle: int):
        """Hardcore Training Cycle mit allen Features"""
        cycle_start = time.time()
        self.logger.info(f"🔥 HARDCORE Cycle {cycle} | Stress: {self._stress_level:.2f}x")
        
        # Pre-cycle chaos injection
        self.inject_chaos()
        self.trigger_crisis_scenario()
        
        # Adaptive difficulty
        self.adaptive_difficulty_adjustment()
        
        # Parallel execution mit höherem Stress
        sem = asyncio.Semaphore(self.cfg["parallel_modules"])
        results, tasks = [], []
        
        async def _wrapped_hardcore(name, func):
            async with sem:
                try:
                    start_time = time.time()
                    result = await asyncio.wait_for(
                        func(cycle), 
                        timeout=self.cfg["module_timeout_sec"] / self._stress_level
                    )
                    duration = time.time() - start_time
                    results.append((name, "ok", result, duration))
                    
                except asyncio.TimeoutError:
                    results.append((name, "timeout", "Module timed out under stress", 0))
                    self._errors += 1
                    
                except Exception as e:
                    results.append((name, "error", str(e), 0))
                    self._errors += 1
                    self.logger.error(f"💥 {name} FAILED: {e}")

        # Starte alle Module parallel
        for name, func in self.training_modules.items():
            tasks.append(asyncio.create_task(_wrapped_hardcore(name, func)))
        
        await asyncio.gather(*tasks)
        
        # Update statistics
        self.training_stats["cycles_completed"] = cycle
        successful = sum(1 for _, status, _, _ in results if status == "ok")
        self.training_stats["knowledge_gained"] += successful
        
        # Stress Tests
        if self.cfg["stress_mode"]:
            stress_passed = successful >= len(self.training_modules) * 0.7  # 70% success rate
            if stress_passed:
                self.training_stats["stress_tests_passed"] += 1
        
        # Performance tracking
        cycle_time = time.time() - cycle_start
        self.performance_metrics["cycle_times"].append(cycle_time)
        self.performance_metrics["error_rates"].append(self._errors / cycle)
        
        # Update expertise
        level = self.update_expertise_level()
        
        # Enhanced summary
        summary = {
            "cycle": cycle,
            "timestamp": datetime.now().isoformat(),
            "stress_level": self._stress_level,
            "crisis_active": self._crisis_active,
            "cycle_time": cycle_time,
            "results": results,
            "expertise_level": level,
            "performance_metrics": {
                "successful_modules": successful,
                "total_modules": len(self.training_modules),
                "success_rate": successful / len(self.training_modules),
                "average_duration": sum(d for _, _, _, d in results) / len(results) if results else 0
            },
            "stats": self.training_stats.copy()
        }
        
        # Save detailed cycle data
        cycle_file = self.training_log_dir / f"hardcore_cycle_{cycle:06d}.json"
        cycle_file.write_text(json.dumps(summary, indent=2))
        
        self._save_state()
        self._heartbeat(cycle)
        
        # Enhanced logging
        error_count = sum(1 for _, status, _, _ in results if status != "ok")
        self.logger.info(
            f"🔥 Cycle {cycle} COMPLETE | "
            f"Level: {level} | "
            f"Success: {successful}/{len(self.training_modules)} | "
            f"Errors: {error_count} | "
            f"Stress: {self._stress_level:.2f}x | "
            f"Time: {cycle_time:.2f}s | "
            f"Points: {self.training_stats['hardcore_points']}"
        )
        
        return summary

    async def run_overnight_training(self):
        """Hardcore Overnight Training Main Loop"""
        self.install_signal_handlers()
        start_time = datetime.now()
        
        self.logger.info("🔥🧙‍♂️ HARDCORE LINUX WIZARD TRAINING INITIATED!")
        self.logger.info(f"Configuration: {json.dumps(self.cfg, indent=2)}")
        
        max_cycles = self.cfg["max_cycles"]
        interval = self.cfg["cycle_interval_sec"]
        
        try:
            for cycle in range(self.training_stats["cycles_completed"] + 1, max_cycles + 1):
                if self._stop.is_set():
                    self.logger.info("🛑 Training stopped by signal")
                    break
                
                # Time limits
                elapsed = datetime.now() - start_time
                if elapsed > timedelta(hours=self.cfg["max_hours"]):
                    self.logger.info(f"⏰ Max training time reached: {elapsed}")
                    break
                
                # Error limits
                if self._errors >= self.cfg["max_errors"]:
                    self.logger.error(f"💥 Max errors reached: {self._errors}")
                    break
                
                # Daytime stop
                current_hour = datetime.now().hour
                if (self.cfg["stop_at_hour"] is not None and 
                    current_hour >= self.cfg["stop_at_hour"] and 
                    current_hour < 22):
                    self.logger.info(f"🌅 Daytime reached, stopping at {current_hour}:00")
                    break
                
                # Execute hardcore training cycle
                await self.run_training_cycle(cycle)
                
                # Resource management
                self.resource_guard()
                
                # Dynamic interval with jitter
                sleep_time = interval / self._stress_level  # Faster cycles at higher stress
                jitter = random.uniform(-0.2 * sleep_time, 0.2 * sleep_time)
                actual_sleep = max(1.0, sleep_time + jitter)
                
                await asyncio.sleep(actual_sleep)
        
        except Exception as e:
            self.logger.critical(f"💀 CRITICAL ERROR in hardcore training: {e}")
            raise
        
        finally:
            # Final statistics
            duration = datetime.now() - start_time
            self.logger.info("🎉 HARDCORE TRAINING COMPLETED!")
            self.logger.info(f"Duration: {duration}")
            self.logger.info(f"Cycles: {self.training_stats['cycles_completed']}")
            self.logger.info(f"Final Level: {self.training_stats['expertise_level']}")
            self.logger.info(f"Hardcore Points: {self.training_stats['hardcore_points']}")
            self.logger.info(f"Stress Tests Passed: {self.training_stats['stress_tests_passed']}")
            self.logger.info(f"Crisis Scenarios Survived: {self.training_stats['crisis_scenarios_survived']}")
            self.logger.info(f"Total Errors: {self._errors}")
            
            # Save final state
            self._save_state()

def parse_args():
    ap = argparse.ArgumentParser(description="Hardcore Linux Wizard Training")
    ap.add_argument("--config", type=str, help="Path to config.json")
    ap.add_argument("--max-cycles", type=int, help="Maximum training cycles")
    ap.add_argument("--interval", type=int, help="Cycle interval in seconds")
    ap.add_argument("--stress-level", type=float, help="Initial stress level (0.5-5.0)")
    ap.add_argument("--hardcore", action="store_true", help="Enable all hardcore features")
    ap.add_argument("--chaos", action="store_true", help="Enable chaos engineering")
    ap.add_argument("--crisis", action="store_true", help="Enable crisis scenarios")
    
    args = ap.parse_args()
    cfg = {}
    
    if args.config and Path(args.config).exists():
        cfg.update(json.loads(Path(args.config).read_text()))
    
    if args.max_cycles:
        cfg["max_cycles"] = args.max_cycles
    if args.interval:
        cfg["cycle_interval_sec"] = args.interval
    if args.stress_level:
        cfg["initial_stress_level"] = args.stress_level
    if args.hardcore:
        cfg.update({
            "stress_mode": True,
            "chaos_engineering": True,
            "adaptive_difficulty": True,
            "crisis_scenarios": True,
            "hardcore_multiplier": 3.0
        })
    if args.chaos:
        cfg["chaos_engineering"] = True
    if args.crisis:
        cfg["crisis_scenarios"] = True
    
    return cfg

if __name__ == "__main__":
    cfg = parse_args()
    trainer = HardcoreLinuxWizardTrainer(cfg)
    asyncio.run(trainer.run_overnight_training())