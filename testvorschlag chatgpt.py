#!/usr/bin/env python3
import asyncio, json, time, logging, os, random, signal, gc, argparse
from datetime import datetime, timedelta
from pathlib import Path
from logging.handlers import RotatingFileHandler

try:
    import psutil  # optional
except Exception:
    psutil = None

DEFAULT_CFG = {
    "max_cycles": 1000,
    "cycle_interval_sec": 30,
    "parallel_modules": 4,
    "module_timeout_sec": 25,
    "stop_at_hour": 7,           # lokale Uhr
    "max_hours": 10,             # harte Obergrenze
    "max_errors": 50,
    "log_max_mb": 50,
    "log_backups": 5,
    "seed": 1337,
}

class LinuxWizardTrainer:
    def __init__(self, cfg: dict):
        self.cfg = {**DEFAULT_CFG, **cfg}
        self.training_log_dir = Path("wizard_training_logs"); self.training_log_dir.mkdir(exist_ok=True)
        self.state_file = self.training_log_dir / "state.json"
        self.heartbeat = self.training_log_dir / "heartbeat.txt"

        log_file = self.training_log_dir / f"wizard_{datetime.now().strftime('%Y%m%d')}.log"
        handler = RotatingFileHandler(log_file, maxBytes=self.cfg["log_max_mb"]*1024*1024, backupCount=self.cfg["log_backups"])
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', handlers=[handler, logging.StreamHandler()])
        self.logger = logging.getLogger("wizard")

        random.seed(self.cfg["seed"])
        self._stop = asyncio.Event()
        self._errors = 0

        # deine Module wie gehabt
        self.training_modules = {
            "command_mastery": self.train_command_mastery,
            "sysadmin_expertise": self.train_sysadmin_expertise,
            "performance_tuning": self.train_performance_tuning,
            "security_hardening": self.train_security_hardening,
            "troubleshooting": self.train_troubleshooting,
            "shell_scripting": self.train_shell_scripting,
            "network_mastery": self.train_network_mastery,
            "container_virtualization": self.train_container_virtualization,
        }
        self.linux_knowledge_base = self.load_linux_knowledge_base()
        self.training_stats = self._load_state() or {
            "cycles_completed": 0, "knowledge_gained": 0, "patterns_learned": 0, "expertise_level": "Beginner",
            "started_at": datetime.now().isoformat(), "version": "v1.1"
        }

    # ==== signals / state ====
    def install_signal_handlers(self):
        def _sigterm(_sig, _frm): self.logger.info("SIGTERM received"); self._stop.set()
        def _sigint(_sig, _frm): self.logger.info("SIGINT received"); self._stop.set()
        signal.signal(signal.SIGTERM, _sigterm); signal.signal(signal.SIGINT, _sigint)

    def _load_state(self):
        if self.state_file.exists():
            try: return json.loads(self.state_file.read_text())
            except Exception: return None
        return None

    def _save_state(self):
        tmp = self.training_stats.copy()
        tmp["saved_at"] = datetime.now().isoformat()
        self.state_file.write_text(json.dumps(tmp, indent=2))

    def _heartbeat(self, cycle:int):
        self.heartbeat.write_text(json.dumps({
            "ts": datetime.now().isoformat(),
            "cycle": cycle,
            "mem_mb": psutil.Process().memory_info().rss//(1024*1024) if psutil else None
        }))

    # ==== deine ursprünglichen Wissensfunktionen bleiben unverändert ====
    def load_linux_knowledge_base(self):  # unverändert gekürzt
        return {"commands": {}, "scenarios": {}, "best_practices": {}}

    async def train_command_mastery(self, cycle): await asyncio.sleep(0.2); self.training_stats["patterns_learned"]+=5; return "Command Mastery ok"
    async def train_sysadmin_expertise(self, cycle): await asyncio.sleep(0.2); return "SysAdmin ok"
    async def train_performance_tuning(self, cycle): await asyncio.sleep(0.2); return "Perf ok"
    async def train_security_hardening(self, cycle): await asyncio.sleep(0.2); return "Security ok"
    async def train_troubleshooting(self, cycle): await asyncio.sleep(0.2); return "Troubleshooting ok"
    async def train_shell_scripting(self, cycle): await asyncio.sleep(0.2); return "Scripting ok"
    async def train_network_mastery(self, cycle): await asyncio.sleep(0.2); return "Network ok"
    async def train_container_virtualization(self, cycle): await asyncio.sleep(0.2); return "Containers ok"

    def update_expertise_level(self):
        c = self.training_stats["cycles_completed"]
        lvl = "Beginner" if c<10 else "Intermediate" if c<50 else "Advanced" if c<100 else "Expert" if c<200 else "Linux Wizard Master"
        self.training_stats["expertise_level"]=lvl; return lvl

    # ==== Ressourcen-Garde ====
    def resource_guard(self):
        if psutil:
            p = psutil.Process()
            rss = p.memory_info().rss/(1024*1024)
            if rss> (0.80* (psutil.virtual_memory().total/(1024*1024))):  # >80% phys RAM
                self.logger.warning(f"High RSS {rss:.0f} MB, triggering GC+sleep")
                gc.collect(); time.sleep(2)
        else:
            gc.collect()

    # ==== Training-Cycle ====
    async def run_training_cycle(self, cycle:int):
        self.logger.info(f"Cycle {cycle} start")
        sem = asyncio.Semaphore(self.cfg["parallel_modules"])
        results, tasks = [], []

        async def _wrapped(name, func):
            async with sem:
                try:
                    r = await asyncio.wait_for(func(cycle), timeout=self.cfg["module_timeout_sec"])
                    results.append((name, "ok", r))
                except Exception as e:
                    results.append((name, "err", str(e))); self.logger.error(f"{name} failed: {e}")
                    self._errors += 1

        for name, func in self.training_modules.items():
            tasks.append(asyncio.create_task(_wrapped(name, func)))
        await asyncio.gather(*tasks)

        self.training_stats["cycles_completed"] = cycle
        self.training_stats["knowledge_gained"] += sum(1 for _,s,_ in results if s=="ok")
        lvl = self.update_expertise_level()

        # persist
        summary = {
            "cycle": cycle, "ts": datetime.now().isoformat(),
            "results": results, "expertise_level": lvl,
            "stats": self.training_stats.copy()
        }
        (self.training_log_dir / f"cycle_{cycle:05d}.json").write_text(json.dumps(summary, indent=2))
        self._save_state()
        self._heartbeat(cycle)
        self.logger.info(f"Cycle {cycle} done | level={lvl} | ok={sum(1 for _,s,_ in results if s=='ok')} err={sum(1 for _,s,_ in results if s=='err')}")
        return summary

    # ==== Main loop ====
    async def run_overnight_training(self):
        self.install_signal_handlers()
        start = datetime.now()
        self.logger.info("🧙 Start Overnight Training")
        max_cycles = self.cfg["max_cycles"]
        interval = self.cfg["cycle_interval_sec"]

        for cycle in range(self.training_stats["cycles_completed"]+1, max_cycles+1):
            if self._stop.is_set(): break
            if (datetime.now()-start) > timedelta(hours=self.cfg["max_hours"]):
                self.logger.info("Max hours reached"); break
            if self._errors >= self.cfg["max_errors"]:
                self.logger.error("Max errors reached"); break
            # Tageszeit-Stopp
            if self.cfg["stop_at_hour"] is not None and datetime.now().hour >= self.cfg["stop_at_hour"] and datetime.now().hour < 22:
                self.logger.info("Daytime window reached; stopping"); break

            await self.run_training_cycle(cycle)
            self.resource_guard()

            # Backoff + Jitter
            sleep_s = interval + random.uniform(-0.15*interval, 0.15*interval)
            await asyncio.sleep(max(1.0, sleep_s))

        dur = (datetime.now()-start).total_seconds()/3600
        self.logger.info(f"✅ Completed. cycles={self.training_stats['cycles_completed']} level={self.training_stats['expertise_level']} hours={dur:.2f}")

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=str, help="Pfad zu config.json")
    ap.add_argument("--max-cycles", type=int)
    ap.add_argument("--interval", type=int)
    ap.add_argument("--stop-at-hour", type=int)
    ap.add_argument("--max-hours", type=float)
    args = ap.parse_args()
    cfg = {}
    if args.config and Path(args.config).exists():
        cfg.update(json.loads(Path(args.config).read_text()))
    if args.max_cycles: cfg["max_cycles"]=args.max_cycles
    if args.interval: cfg["cycle_interval_sec"]=args.interval
    if args.stop_at_hour is not None: cfg["stop_at_hour"]=args.stop_at_hour
    if args.max_hours: cfg["max_hours"]=args.max_hours
    return cfg

if __name__ == "__main__":
    cfg = parse_args()
    trainer = LinuxWizardTrainer(cfg)
    asyncio.run(trainer.run_overnight_training())

