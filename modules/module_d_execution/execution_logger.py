"""
Execution Logger for Module D: Safe Execution & Control
Provides audit trail functionality for all command executions.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from models import ExecutionLog

logger = logging.getLogger(__name__)


@dataclass
class LogEntry:
    """Single execution log entry"""
    timestamp: str
    command: str
    user: str
    working_directory: str
    dry_run: bool
    executed: bool
    success: bool
    exit_code: Optional[int]
    execution_time: float
    safety_warnings: List[str]
    files_affected: Optional[int]
    output_preview: Optional[str]
    error_message: Optional[str]


class ExecutionLogger:
    """
    Audit trail logger for command executions.
    
    Provides comprehensive logging of all command execution attempts
    with security audit trail capabilities.
    """
    
    def __init__(self, log_directory: str = "data/logs"):
        """
        Initialize execution logger.
        
        Args:
            log_directory: Directory to store log files
        """
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Setup log files
        self.audit_log_file = self.log_directory / "execution_audit.jsonl"
        self.security_log_file = self.log_directory / "security_events.jsonl"
        self.daily_log_file = self._get_daily_log_file()
        
        # Configure Python logging
        self._setup_file_logging()
    
    def _get_daily_log_file(self) -> Path:
        """Get daily log file path"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.log_directory / f"execution_{today}.jsonl"
    
    def _setup_file_logging(self):
        """Setup file-based logging configuration"""
        log_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create file handler for execution logs
        file_handler = logging.FileHandler(
            self.log_directory / "module_d_execution.log"
        )
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(logging.INFO)
        
        # Add handler to logger
        execution_logger = logging.getLogger("module_d_execution")
        execution_logger.addHandler(file_handler)
        execution_logger.setLevel(logging.INFO)
    
    def log_execution(self, 
                     command: str,
                     user: str = "system",
                     working_directory: str = "/",
                     dry_run: bool = True,
                     executed: bool = False,
                     success: bool = False,
                     exit_code: Optional[int] = None,
                     execution_time: float = 0.0,
                     safety_warnings: List[str] = None,
                     files_affected: Optional[int] = None,
                     output_preview: Optional[str] = None,
                     error_message: Optional[str] = None) -> str:
        """
        Log command execution with full audit trail.
        
        Args:
            command: Command that was executed
            user: User who executed the command
            working_directory: Directory where command was executed
            dry_run: Whether this was a dry run
            executed: Whether command was actually executed
            success: Whether execution was successful
            exit_code: Command exit code
            execution_time: Time taken for execution
            safety_warnings: Any safety warnings generated
            files_affected: Number of files affected
            output_preview: Preview of command output
            error_message: Error message if execution failed
            
        Returns:
            Log entry ID for reference
        """
        if safety_warnings is None:
            safety_warnings = []
        
        # Create log entry
        log_entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            command=command,
            user=user,
            working_directory=working_directory,
            dry_run=dry_run,
            executed=executed,
            success=success,
            exit_code=exit_code,
            execution_time=execution_time,
            safety_warnings=safety_warnings,
            files_affected=files_affected,
            output_preview=output_preview[:500] if output_preview else None,  # Truncate long output
            error_message=error_message
        )
        
        # Generate entry ID
        entry_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(command) % 10000:04d}"
        
        # Write to audit log
        self._write_audit_log(entry_id, log_entry)
        
        # Write to daily log
        self._write_daily_log(entry_id, log_entry)
        
        # Check for security events
        if safety_warnings or (executed and not success):
            self._log_security_event(entry_id, log_entry)
        
        # Log to Python logger
        log_level = logging.WARNING if safety_warnings else logging.INFO
        logger.log(log_level, 
                  f"Command execution logged: {command} (dry_run={dry_run}, "
                  f"executed={executed}, success={success})")
        
        return entry_id
    
    def _write_audit_log(self, entry_id: str, log_entry: LogEntry):
        """Write entry to main audit log"""
        try:
            audit_record = {
                "entry_id": entry_id,
                "log_type": "execution_audit",
                **asdict(log_entry)
            }
            
            with open(self.audit_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(audit_record) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def _write_daily_log(self, entry_id: str, log_entry: LogEntry):
        """Write entry to daily log file"""
        try:
            # Update daily log file if date changed
            self.daily_log_file = self._get_daily_log_file()
            
            daily_record = {
                "entry_id": entry_id,
                "log_type": "daily_execution",
                **asdict(log_entry)
            }
            
            with open(self.daily_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(daily_record) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to write daily log: {e}")
    
    def _log_security_event(self, entry_id: str, log_entry: LogEntry):
        """Log security-relevant events"""
        try:
            security_record = {
                "entry_id": entry_id,
                "log_type": "security_event",
                "event_type": "command_execution",
                "severity": "high" if log_entry.safety_warnings else "medium",
                "timestamp": log_entry.timestamp,
                "command": log_entry.command,
                "user": log_entry.user,
                "executed": log_entry.executed,
                "success": log_entry.success,
                "safety_warnings": log_entry.safety_warnings,
                "error_message": log_entry.error_message
            }
            
            with open(self.security_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(security_record) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to write security log: {e}")
    
    def get_execution_history(self, 
                            limit: int = 100,
                            user: Optional[str] = None,
                            command_pattern: Optional[str] = None) -> List[Dict]:
        """
        Retrieve execution history with optional filtering.
        
        Args:
            limit: Maximum number of entries to return
            user: Filter by user
            command_pattern: Filter by command pattern
            
        Returns:
            List of execution log entries
        """
        try:
            entries = []
            
            if self.audit_log_file.exists():
                with open(self.audit_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            
                            # Apply filters
                            if user and entry.get('user') != user:
                                continue
                            
                            if command_pattern and command_pattern not in entry.get('command', ''):
                                continue
                            
                            entries.append(entry)
                            
                            if len(entries) >= limit:
                                break
                                
                        except json.JSONDecodeError:
                            continue
            
            # Return most recent entries first
            return list(reversed(entries[-limit:]))
            
        except Exception as e:
            logger.error(f"Failed to retrieve execution history: {e}")
            return []
    
    def get_security_events(self, limit: int = 50) -> List[Dict]:
        """
        Retrieve recent security events.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of security event entries
        """
        try:
            events = []
            
            if self.security_log_file.exists():
                with open(self.security_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            events.append(event)
                            
                            if len(events) >= limit:
                                break
                                
                        except json.JSONDecodeError:
                            continue
            
            return list(reversed(events[-limit:]))
            
        except Exception as e:
            logger.error(f"Failed to retrieve security events: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get execution statistics.
        
        Returns:
            Dictionary with execution statistics
        """
        try:
            stats = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "dry_runs": 0,
                "security_events": 0,
                "most_common_commands": {},
                "recent_activity": []
            }
            
            if self.audit_log_file.exists():
                command_counts = {}
                
                with open(self.audit_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            
                            stats["total_executions"] += 1
                            
                            if entry.get("dry_run"):
                                stats["dry_runs"] += 1
                            
                            if entry.get("executed"):
                                if entry.get("success"):
                                    stats["successful_executions"] += 1
                                else:
                                    stats["failed_executions"] += 1
                            
                            if entry.get("safety_warnings"):
                                stats["security_events"] += 1
                            
                            # Count commands
                            cmd = entry.get("command", "").split()[0] if entry.get("command") else "unknown"
                            command_counts[cmd] = command_counts.get(cmd, 0) + 1
                            
                        except json.JSONDecodeError:
                            continue
                
                # Get most common commands
                stats["most_common_commands"] = dict(
                    sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                )
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to generate statistics: {e}")
            return {"error": str(e)}
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Clean up log files older than specified days.
        
        Args:
            days_to_keep: Number of days to keep logs
        """
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
            
            for log_file in self.log_directory.glob("execution_*.jsonl"):
                if log_file.stat().st_mtime < cutoff_date:
                    log_file.unlink()
                    logger.info(f"Cleaned up old log file: {log_file}")
                    
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {e}")


# Global logger instance
execution_logger = ExecutionLogger()


def log_command_execution(**kwargs) -> str:
    """Convenience function for logging command execution"""
    return execution_logger.log_execution(**kwargs)


def get_execution_stats() -> Dict[str, any]:
    """Convenience function for getting execution statistics"""
    return execution_logger.get_statistics()