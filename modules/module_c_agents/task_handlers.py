"""
Task handlers for Module C: Proactive Agents.
Implements specific task execution logic for different task types.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from .task_classifier import TaskType
from .safe_execution_client import SafeExecutionClient, ExecutionResult

logger = logging.getLogger(__name__)


@dataclass
class TaskResult:
    """Result of task execution."""
    success: bool
    result: Dict[str, Any]
    sources: List[str]
    commands_generated: List[str]
    execution_time: float
    error: Optional[str] = None


class BaseTaskHandler(ABC):
    """Base class for task handlers."""
    
    def __init__(self, task_type: TaskType):
        self.task_type = task_type
        self.safe_executor = SafeExecutionClient()
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> TaskResult:
        """Execute the task with given parameters and context."""
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize task parameters."""
        pass
    
    @abstractmethod
    def get_confirmation_message(self, parameters: Dict[str, Any]) -> str:
        """Get human-readable confirmation message for the task."""
        pass
    
    def requires_confirmation(self, parameters: Dict[str, Any]) -> bool:
        """Check if task requires human confirmation."""
        return True  # Default: all tasks require confirmation
    
    async def execute_commands_safely(self, commands: List[str], working_directory: Optional[str] = None) -> List[ExecutionResult]:
        """
        Execute commands safely using Module D integration.
        
        Args:
            commands: List of commands to execute
            working_directory: Optional working directory
            
        Returns:
            List of execution results
        """
        results = []
        
        # Check if Module D is available
        if not await self.safe_executor.check_health():
            logger.warning("Module D not available, commands will not be executed")
            return results
        
        for command in commands:
            try:
                # First preview the command
                preview_result = await self.safe_executor.preview_command(command, working_directory)
                
                if preview_result.success:
                    logger.info(f"Command preview: {command} -> {preview_result.preview}")
                    
                    # For now, we only do dry-run previews
                    # Actual execution would require explicit user confirmation
                    results.append(preview_result)
                else:
                    logger.error(f"Command preview failed: {command} -> {preview_result.error}")
                    results.append(preview_result)
                    
            except Exception as e:
                logger.error(f"Failed to preview command '{command}': {e}")
                error_result = ExecutionResult(
                    success=False,
                    command=command,
                    executed=False,
                    error=str(e)
                )
                results.append(error_result)
        
        return results


class LogAnalyzeHandler(BaseTaskHandler):
    """Handler for log analysis tasks."""
    
    def __init__(self):
        super().__init__(TaskType.LOG_ANALYZE)
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate log analysis parameters."""
        validated = {
            "service": parameters.get("service", ""),
            "since": parameters.get("since", "1 hour ago"),
            "until": parameters.get("until", "now"),
            "priority": parameters.get("priority", "info"),
            "lines": int(parameters.get("lines", 50)),
            "follow": parameters.get("follow", False),
            "grep_pattern": parameters.get("grep_pattern", ""),
            "output_format": parameters.get("output_format", "short")
        }
        
        # Validate priority levels
        valid_priorities = ["emerg", "alert", "crit", "err", "warning", "notice", "info", "debug"]
        if validated["priority"] not in valid_priorities:
            validated["priority"] = "info"
        
        # Limit lines to reasonable range
        validated["lines"] = max(1, min(validated["lines"], 1000))
        
        return validated
    
    def get_confirmation_message(self, parameters: Dict[str, Any]) -> str:
        """Get confirmation message for log analysis."""
        service = parameters.get("service", "system")
        lines = parameters.get("lines", 50)
        since = parameters.get("since", "1 hour ago")
        
        if service:
            return f"Analyze logs for service '{service}' (last {lines} lines since {since})"
        else:
            return f"Analyze system logs (last {lines} lines since {since})"
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> TaskResult:
        """Execute log analysis task."""
        import time
        start_time = time.time()
        
        try:
            validated_params = self.validate_parameters(parameters)
            
            # Build journalctl command
            commands = []
            base_cmd = "journalctl"
            
            # Add service filter
            if validated_params["service"]:
                base_cmd += f" -u {validated_params['service']}"
            
            # Add time filters
            if validated_params["since"]:
                base_cmd += f" --since '{validated_params['since']}'"
            
            if validated_params["until"] and validated_params["until"] != "now":
                base_cmd += f" --until '{validated_params['until']}'"
            
            # Add priority filter
            if validated_params["priority"]:
                base_cmd += f" -p {validated_params['priority']}"
            
            # Add line limit
            base_cmd += f" -n {validated_params['lines']}"
            
            # Add output format
            base_cmd += f" -o {validated_params['output_format']}"
            
            # Add follow if requested
            if validated_params["follow"]:
                base_cmd += " -f"
            
            commands.append(base_cmd)
            
            # Add grep filter if specified
            if validated_params["grep_pattern"]:
                grep_cmd = f"{base_cmd} | grep -i '{validated_params['grep_pattern']}'"
                commands.append(grep_cmd)
            
            # Generate analysis suggestions
            analysis_suggestions = []
            
            if validated_params["service"]:
                analysis_suggestions.extend([
                    f"systemctl status {validated_params['service']}",
                    f"systemctl is-enabled {validated_params['service']}",
                    f"systemctl show {validated_params['service']}"
                ])
            
            analysis_suggestions.extend([
                "dmesg | tail -20",
                "tail -f /var/log/syslog",
                "journalctl --disk-usage",
                "journalctl --vacuum-time=7d"
            ])
            
            execution_time = time.time() - start_time
            
            result = {
                "task_type": "log_analyze",
                "commands": commands,
                "analysis_suggestions": analysis_suggestions,
                "parameters_used": validated_params,
                "description": f"Log analysis for {validated_params['service'] or 'system'} logs",
                "next_steps": [
                    "Run the generated journalctl command to view logs",
                    "Look for ERROR, WARN, or FAIL patterns in the output",
                    "Check service status if analyzing specific service logs",
                    "Consider log rotation and disk usage if logs are large"
                ]
            }
            
            # Execute commands safely via Module D
            execution_results = await self.execute_commands_safely(commands[:2])  # Limit to first 2 commands
            
            # Add execution results to the result
            result["execution_results"] = []
            for exec_result in execution_results:
                result["execution_results"].append({
                    "command": exec_result.command,
                    "success": exec_result.success,
                    "preview": exec_result.preview,
                    "safety_warnings": exec_result.safety_warnings or [],
                    "error": exec_result.error
                })
            
            return TaskResult(
                success=True,
                result=result,
                sources=["journalctl", "systemd"],
                commands_generated=commands + analysis_suggestions,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Log analysis task failed: {e}")
            
            return TaskResult(
                success=False,
                result={"error": str(e)},
                sources=[],
                commands_generated=[],
                execution_time=execution_time,
                error=str(e)
            )


class BackupCreateHandler(BaseTaskHandler):
    """Handler for backup creation tasks."""
    
    def __init__(self):
        super().__init__(TaskType.BACKUP_CREATE)
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate backup creation parameters."""
        validated = {
            "source": parameters.get("source", "/home"),
            "destination": parameters.get("destination", "/backup"),
            "type": parameters.get("type", "incremental"),
            "exclude": parameters.get("exclude", ""),
            "compress": parameters.get("compress", True),
            "preserve_permissions": parameters.get("preserve_permissions", True),
            "dry_run": parameters.get("dry_run", True),
            "delete_excluded": parameters.get("delete_excluded", False),
            "bandwidth_limit": parameters.get("bandwidth_limit", "")
        }
        
        # Validate backup type
        valid_types = ["full", "incremental", "differential", "sync"]
        if validated["type"] not in valid_types:
            validated["type"] = "incremental"
        
        # Ensure paths don't end with slash (rsync behavior)
        validated["source"] = validated["source"].rstrip("/")
        validated["destination"] = validated["destination"].rstrip("/")
        
        return validated
    
    def get_confirmation_message(self, parameters: Dict[str, Any]) -> str:
        """Get confirmation message for backup creation."""
        source = parameters.get("source", "/home")
        destination = parameters.get("destination", "/backup")
        backup_type = parameters.get("type", "incremental")
        
        return f"Create {backup_type} backup from '{source}' to '{destination}'"
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> TaskResult:
        """Execute backup creation task."""
        import time
        start_time = time.time()
        
        try:
            validated_params = self.validate_parameters(parameters)
            
            # Build rsync command
            rsync_cmd = "rsync"
            
            # Add basic options
            rsync_options = ["-av"]  # archive, verbose
            
            if validated_params["compress"]:
                rsync_options.append("-z")  # compress
            
            if validated_params["preserve_permissions"]:
                rsync_options.append("-p")  # preserve permissions
            
            if validated_params["dry_run"]:
                rsync_options.append("-n")  # dry run
            
            if validated_params["delete_excluded"]:
                rsync_options.append("--delete")  # delete excluded files
            
            # Add progress and stats
            rsync_options.extend(["--progress", "--stats"])
            
            # Add exclude patterns
            exclude_patterns = []
            if validated_params["exclude"]:
                for pattern in validated_params["exclude"].split(","):
                    pattern = pattern.strip()
                    if pattern:
                        exclude_patterns.append(f"--exclude='{pattern}'")
            
            # Add common exclusions
            common_exclusions = [
                "--exclude='*.tmp'",
                "--exclude='*.log'",
                "--exclude='.cache'",
                "--exclude='.thumbnails'",
                "--exclude='Trash'"
            ]
            exclude_patterns.extend(common_exclusions)
            
            # Add bandwidth limit if specified
            if validated_params["bandwidth_limit"]:
                rsync_options.append(f"--bwlimit={validated_params['bandwidth_limit']}")
            
            # Build full command
            full_cmd = f"{rsync_cmd} {' '.join(rsync_options)} {' '.join(exclude_patterns)} {validated_params['source']}/ {validated_params['destination']}/"
            
            # Generate backup script
            script_lines = [
                "#!/bin/bash",
                "# Generated backup script",
                f"# Backup type: {validated_params['type']}",
                f"# Source: {validated_params['source']}",
                f"# Destination: {validated_params['destination']}",
                "",
                "# Check if source exists",
                f"if [ ! -d \"{validated_params['source']}\" ]; then",
                f"    echo \"Error: Source directory {validated_params['source']} does not exist\"",
                "    exit 1",
                "fi",
                "",
                "# Create destination if it doesn't exist",
                f"mkdir -p \"{validated_params['destination']}\"",
                "",
                "# Run backup",
                f"echo \"Starting {validated_params['type']} backup...\"",
                full_cmd,
                "",
                "# Check result",
                "if [ $? -eq 0 ]; then",
                "    echo \"Backup completed successfully\"",
                "else",
                "    echo \"Backup failed with error code $?\"",
                "    exit 1",
                "fi"
            ]
            
            script_content = "\n".join(script_lines)
            
            # Generate verification commands
            verification_commands = [
                f"du -sh {validated_params['source']}",
                f"du -sh {validated_params['destination']}",
                f"find {validated_params['destination']} -type f | wc -l",
                f"rsync -av --dry-run {validated_params['source']}/ {validated_params['destination']}/ | grep '^[^/]' | wc -l"
            ]
            
            execution_time = time.time() - start_time
            
            result = {
                "task_type": "backup_create",
                "rsync_command": full_cmd,
                "backup_script": script_content,
                "verification_commands": verification_commands,
                "parameters_used": validated_params,
                "description": f"{validated_params['type'].title()} backup from {validated_params['source']} to {validated_params['destination']}",
                "next_steps": [
                    "Review the generated rsync command",
                    "Test with --dry-run first to see what would be copied",
                    "Ensure destination has sufficient disk space",
                    "Consider scheduling the backup with cron",
                    "Verify backup integrity after completion"
                ],
                "estimated_size_check": f"du -sh {validated_params['source']}",
                "space_check": f"df -h {validated_params['destination']}"
            }
            
            return TaskResult(
                success=True,
                result=result,
                sources=["rsync", "filesystem"],
                commands_generated=[full_cmd] + verification_commands,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Backup creation task failed: {e}")
            
            return TaskResult(
                success=False,
                result={"error": str(e)},
                sources=[],
                commands_generated=[],
                execution_time=execution_time,
                error=str(e)
            )


class DiskCheckHandler(BaseTaskHandler):
    """Handler for disk space checking tasks."""
    
    def __init__(self):
        super().__init__(TaskType.DISK_CHECK)
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate disk check parameters."""
        validated = {
            "path": parameters.get("path", "/"),
            "format": parameters.get("format", "human"),
            "include_inodes": parameters.get("include_inodes", False),
            "show_all": parameters.get("show_all", False),
            "threshold_warning": int(parameters.get("threshold_warning", 80)),
            "threshold_critical": int(parameters.get("threshold_critical", 90))
        }
        
        # Validate format
        valid_formats = ["human", "bytes", "kb", "mb", "gb"]
        if validated["format"] not in valid_formats:
            validated["format"] = "human"
        
        # Validate thresholds
        validated["threshold_warning"] = max(1, min(validated["threshold_warning"], 99))
        validated["threshold_critical"] = max(validated["threshold_warning"], min(validated["threshold_critical"], 99))
        
        return validated
    
    def get_confirmation_message(self, parameters: Dict[str, Any]) -> str:
        """Get confirmation message for disk check."""
        path = parameters.get("path", "/")
        return f"Check disk space usage for path '{path}'"
    
    def requires_confirmation(self, parameters: Dict[str, Any]) -> bool:
        """Disk check is safe and doesn't require confirmation."""
        return False
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> TaskResult:
        """Execute disk check task."""
        import time
        start_time = time.time()
        
        try:
            validated_params = self.validate_parameters(parameters)
            
            # Build df command
            df_cmd = "df"
            
            if validated_params["format"] == "human":
                df_cmd += " -h"
            elif validated_params["format"] == "kb":
                df_cmd += " -k"
            elif validated_params["format"] == "mb":
                df_cmd += " -m"
            elif validated_params["format"] == "gb":
                df_cmd += " --block-size=1G"
            
            if validated_params["include_inodes"]:
                df_cmd += " -i"
            
            if validated_params["show_all"]:
                df_cmd += " -a"
            
            # Add path if specified
            if validated_params["path"] != "/":
                df_cmd += f" {validated_params['path']}"
            
            # Generate additional commands
            additional_commands = [
                f"du -sh {validated_params['path']}/*" if validated_params["path"] != "/" else "du -sh /*",
                f"find {validated_params['path']} -type f -size +100M" if validated_params["path"] != "/" else "find / -type f -size +100M 2>/dev/null | head -10",
                "lsblk -f",
                "mount | grep -E '^/dev'",
                "df -i"  # Show inode usage
            ]
            
            # Generate cleanup suggestions
            cleanup_suggestions = [
                "# Clean package cache",
                "sudo apt autoremove && sudo apt autoclean",
                "",
                "# Clean journal logs (keep last 7 days)",
                "sudo journalctl --vacuum-time=7d",
                "",
                "# Find large files",
                "find /var/log -type f -size +50M",
                "find /tmp -type f -size +10M -mtime +7",
                "",
                "# Check disk usage by directory",
                "du -sh /var/* | sort -hr | head -10",
                "du -sh /home/* | sort -hr | head -10"
            ]
            
            execution_time = time.time() - start_time
            
            result = {
                "task_type": "disk_check",
                "primary_command": df_cmd,
                "additional_commands": additional_commands,
                "cleanup_suggestions": cleanup_suggestions,
                "parameters_used": validated_params,
                "description": f"Disk space check for {validated_params['path']}",
                "thresholds": {
                    "warning": f"{validated_params['threshold_warning']}%",
                    "critical": f"{validated_params['threshold_critical']}%"
                },
                "next_steps": [
                    "Run the df command to check current disk usage",
                    "Identify directories using the most space with du commands",
                    "Look for large files that can be cleaned up",
                    "Consider log rotation if /var/log is large",
                    "Check for old temporary files in /tmp"
                ]
            }
            
            return TaskResult(
                success=True,
                result=result,
                sources=["df", "du", "filesystem"],
                commands_generated=[df_cmd] + additional_commands,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Disk check task failed: {e}")
            
            return TaskResult(
                success=False,
                result={"error": str(e)},
                sources=[],
                commands_generated=[],
                execution_time=execution_time,
                error=str(e)
            )


class MemoryCheckHandler(BaseTaskHandler):
    """Handler for memory usage checking tasks."""
    
    def __init__(self):
        super().__init__(TaskType.MEMORY_CHECK)
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate memory check parameters."""
        validated = {
            "format": parameters.get("format", "human"),
            "show_swap": parameters.get("show_swap", True),
            "show_buffers": parameters.get("show_buffers", True),
            "continuous": parameters.get("continuous", False),
            "interval": int(parameters.get("interval", 1))
        }
        
        # Validate format
        valid_formats = ["human", "bytes", "kb", "mb", "gb"]
        if validated["format"] not in valid_formats:
            validated["format"] = "human"
        
        # Validate interval
        validated["interval"] = max(1, min(validated["interval"], 60))
        
        return validated
    
    def get_confirmation_message(self, parameters: Dict[str, Any]) -> str:
        """Get confirmation message for memory check."""
        return "Check system memory and swap usage"
    
    def requires_confirmation(self, parameters: Dict[str, Any]) -> bool:
        """Memory check is safe and doesn't require confirmation."""
        return False
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> TaskResult:
        """Execute memory check task."""
        import time
        start_time = time.time()
        
        try:
            validated_params = self.validate_parameters(parameters)
            
            # Build free command
            free_cmd = "free"
            
            if validated_params["format"] == "human":
                free_cmd += " -h"
            elif validated_params["format"] == "kb":
                free_cmd += " -k"
            elif validated_params["format"] == "mb":
                free_cmd += " -m"
            elif validated_params["format"] == "gb":
                free_cmd += " -g"
            
            if validated_params["continuous"]:
                free_cmd += f" -s {validated_params['interval']}"
            
            # Generate additional commands
            additional_commands = [
                "cat /proc/meminfo",
                "ps aux --sort=-%mem | head -10",
                "top -b -n1 -o %MEM | head -20",
                "vmstat 1 5",
                "cat /proc/swaps"
            ]
            
            # Generate memory optimization suggestions
            optimization_suggestions = [
                "# Check memory-intensive processes",
                "ps aux --sort=-%mem | head -10",
                "",
                "# Clear system caches (if safe)",
                "sudo sync && sudo sysctl vm.drop_caches=1",
                "",
                "# Check swap usage",
                "swapon --show",
                "cat /proc/swaps",
                "",
                "# Monitor memory usage over time",
                "watch -n 2 'free -h'",
                "",
                "# Check for memory leaks",
                "valgrind --tool=memcheck --leak-check=yes your_program"
            ]
            
            execution_time = time.time() - start_time
            
            result = {
                "task_type": "memory_check",
                "primary_command": free_cmd,
                "additional_commands": additional_commands,
                "optimization_suggestions": optimization_suggestions,
                "parameters_used": validated_params,
                "description": "System memory and swap usage check",
                "next_steps": [
                    "Run the free command to check current memory usage",
                    "Identify memory-intensive processes with ps/top commands",
                    "Monitor swap usage and consider adding more if needed",
                    "Check for memory leaks in running applications",
                    "Consider clearing system caches if memory is low"
                ]
            }
            
            return TaskResult(
                success=True,
                result=result,
                sources=["free", "proc", "vmstat"],
                commands_generated=[free_cmd] + additional_commands,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Memory check task failed: {e}")
            
            return TaskResult(
                success=False,
                result={"error": str(e)},
                sources=[],
                commands_generated=[],
                execution_time=execution_time,
                error=str(e)
            )


class ProcessCheckHandler(BaseTaskHandler):
    """Handler for process monitoring tasks."""
    
    def __init__(self):
        super().__init__(TaskType.PROCESS_CHECK)
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate process check parameters."""
        validated = {
            "user": parameters.get("user", ""),
            "name": parameters.get("name", ""),
            "sort": parameters.get("sort", "cpu"),
            "limit": int(parameters.get("limit", 20)),
            "show_threads": parameters.get("show_threads", False),
            "tree_view": parameters.get("tree_view", False)
        }
        
        # Validate sort options
        valid_sorts = ["cpu", "mem", "pid", "time", "command"]
        if validated["sort"] not in valid_sorts:
            validated["sort"] = "cpu"
        
        # Validate limit
        validated["limit"] = max(1, min(validated["limit"], 100))
        
        return validated
    
    def get_confirmation_message(self, parameters: Dict[str, Any]) -> str:
        """Get confirmation message for process check."""
        user = parameters.get("user", "")
        name = parameters.get("name", "")
        
        if user and name:
            return f"List processes for user '{user}' matching '{name}'"
        elif user:
            return f"List processes for user '{user}'"
        elif name:
            return f"List processes matching '{name}'"
        else:
            return "List running system processes"
    
    def requires_confirmation(self, parameters: Dict[str, Any]) -> bool:
        """Process check is safe and doesn't require confirmation."""
        return False
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> TaskResult:
        """Execute process check task."""
        import time
        start_time = time.time()
        
        try:
            validated_params = self.validate_parameters(parameters)
            
            # Build ps command
            ps_cmd = "ps aux"
            
            # Add sorting
            if validated_params["sort"] == "cpu":
                ps_cmd += " --sort=-%cpu"
            elif validated_params["sort"] == "mem":
                ps_cmd += " --sort=-%mem"
            elif validated_params["sort"] == "pid":
                ps_cmd += " --sort=pid"
            elif validated_params["sort"] == "time":
                ps_cmd += " --sort=-time"
            
            # Add user filter
            if validated_params["user"]:
                ps_cmd = f"ps -u {validated_params['user']} -o pid,ppid,user,%cpu,%mem,vsz,rss,tty,stat,start,time,command"
                if validated_params["sort"] == "cpu":
                    ps_cmd += " --sort=-%cpu"
                elif validated_params["sort"] == "mem":
                    ps_cmd += " --sort=-%mem"
            
            # Add limit
            ps_cmd += f" | head -{validated_params['limit'] + 1}"  # +1 for header
            
            # Add name filter if specified
            if validated_params["name"]:
                ps_cmd += f" | grep -i {validated_params['name']}"
            
            # Generate additional commands
            additional_commands = []
            
            if validated_params["tree_view"]:
                additional_commands.append("pstree -p")
                additional_commands.append("ps auxf")
            
            if validated_params["show_threads"]:
                additional_commands.append("ps -eLf")
            
            additional_commands.extend([
                "top -b -n1 | head -20",
                "htop --help 2>/dev/null && echo 'Use: htop' || echo 'htop not installed'",
                "systemctl list-units --type=service --state=running",
                "lsof -i -P -n | head -20"
            ])
            
            # Generate process management suggestions
            management_suggestions = [
                "# Kill process by PID",
                "kill PID",
                "kill -9 PID  # Force kill",
                "",
                "# Kill processes by name",
                "pkill process_name",
                "killall process_name",
                "",
                "# Monitor processes in real-time",
                "top",
                "htop",
                "watch -n 1 'ps aux --sort=-%cpu | head -20'",
                "",
                "# Check process details",
                "cat /proc/PID/status",
                "lsof -p PID",
                "",
                "# Service management",
                "systemctl status service_name",
                "systemctl stop service_name",
                "systemctl restart service_name"
            ]
            
            execution_time = time.time() - start_time
            
            result = {
                "task_type": "process_check",
                "primary_command": ps_cmd,
                "additional_commands": additional_commands,
                "management_suggestions": management_suggestions,
                "parameters_used": validated_params,
                "description": f"Process listing sorted by {validated_params['sort']}",
                "next_steps": [
                    "Run the ps command to see current processes",
                    "Identify resource-intensive processes",
                    "Use kill/pkill to terminate unwanted processes",
                    "Monitor processes with top/htop for real-time view",
                    "Check service status with systemctl for system services"
                ]
            }
            
            return TaskResult(
                success=True,
                result=result,
                sources=["ps", "proc", "systemctl"],
                commands_generated=[ps_cmd] + additional_commands,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Process check task failed: {e}")
            
            return TaskResult(
                success=False,
                result={"error": str(e)},
                sources=[],
                commands_generated=[],
                execution_time=execution_time,
                error=str(e)
            )


class MemoryCheckHandler(BaseTaskHandler):
    """Handler for memory usage checking tasks."""
    
    def __init__(self):
        super().__init__(TaskType.MEMORY_CHECK)
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate memory check parameters."""
        validated = {
            "format": parameters.get("format", "human"),
            "show_swap": parameters.get("show_swap", True),
            "show_buffers": parameters.get("show_buffers", True),
            "continuous": parameters.get("continuous", False),
            "interval": int(parameters.get("interval", 1)),
            "count": int(parameters.get("count", 1))
        }
        
        # Validate format
        valid_formats = ["human", "bytes", "kb", "mb", "gb"]
        if validated["format"] not in valid_formats:
            validated["format"] = "human"
        
        # Validate interval and count
        validated["interval"] = max(1, min(validated["interval"], 60))
        validated["count"] = max(1, min(validated["count"], 100))
        
        return validated
    
    def get_confirmation_message(self, parameters: Dict[str, Any]) -> str:
        """Get confirmation message for memory check."""
        return "Check system memory and swap usage"
    
    def requires_confirmation(self, parameters: Dict[str, Any]) -> bool:
        """Memory check is safe and doesn't require confirmation."""
        return False
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> TaskResult:
        """Execute memory check task."""
        import time
        start_time = time.time()
        
        try:
            validated_params = self.validate_parameters(parameters)
            
            # Build free command
            free_cmd = "free"
            
            if validated_params["format"] == "human":
                free_cmd += " -h"
            elif validated_params["format"] == "kb":
                free_cmd += " -k"
            elif validated_params["format"] == "mb":
                free_cmd += " -m"
            elif validated_params["format"] == "gb":
                free_cmd += " -g"
            
            # Add additional options
            if validated_params["show_buffers"]:
                free_cmd += " -w"  # Wide format showing buffers/cache separately
            
            if validated_params["continuous"]:
                free_cmd += f" -s {validated_params['interval']}"
                if validated_params["count"] > 1:
                    free_cmd += f" -c {validated_params['count']}"
            
            # Generate additional memory analysis commands
            additional_commands = [
                "cat /proc/meminfo",
                "ps aux --sort=-%mem | head -10",  # Top memory consumers
                "top -b -n1 -o %MEM | head -20",  # Memory usage snapshot
                "vmstat 1 5",  # Virtual memory statistics
                "cat /proc/swaps",  # Swap information
                "swapon --show"  # Show swap devices
            ]
            
            # Generate memory optimization suggestions
            optimization_suggestions = [
                "# Check for memory leaks",
                "ps aux --sort=-%mem | head -10",
                "",
                "# Clear page cache (if safe)",
                "sync && echo 1 > /proc/sys/vm/drop_caches",
                "",
                "# Check swap usage",
                "swapon --show",
                "cat /proc/swaps",
                "",
                "# Monitor memory over time",
                "watch -n 2 'free -h'",
                "",
                "# Find large processes",
                "ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head -20"
            ]
            
            execution_time = time.time() - start_time
            
            result = {
                "task_type": "memory_check",
                "primary_command": free_cmd,
                "additional_commands": additional_commands,
                "optimization_suggestions": optimization_suggestions,
                "parameters_used": validated_params,
                "description": f"Memory usage check in {validated_params['format']} format",
                "next_steps": [
                    "Run the free command to check current memory usage",
                    "Identify processes using the most memory with ps commands",
                    "Check swap usage if memory is low",
                    "Monitor memory usage over time if issues persist",
                    "Consider adding more RAM if consistently high usage"
                ]
            }
            
            return TaskResult(
                success=True,
                result=result,
                sources=["free", "proc", "ps"],
                commands_generated=[free_cmd] + additional_commands,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Memory check task failed: {e}")
            
            return TaskResult(
                success=False,
                result={"error": str(e)},
                sources=[],
                commands_generated=[],
                execution_time=execution_time,
                error=str(e)
            )


class ProcessCheckHandler(BaseTaskHandler):
    """Handler for process monitoring tasks."""
    
    def __init__(self):
        super().__init__(TaskType.PROCESS_CHECK)
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate process check parameters."""
        validated = {
            "user": parameters.get("user", ""),
            "name": parameters.get("name", ""),
            "sort": parameters.get("sort", "cpu"),
            "limit": int(parameters.get("limit", 20)),
            "show_threads": parameters.get("show_threads", False),
            "tree_view": parameters.get("tree_view", False)
        }
        
        # Validate sort options
        valid_sorts = ["cpu", "mem", "pid", "time", "name"]
        if validated["sort"] not in valid_sorts:
            validated["sort"] = "cpu"
        
        # Validate limit
        validated["limit"] = max(1, min(validated["limit"], 100))
        
        return validated
    
    def get_confirmation_message(self, parameters: Dict[str, Any]) -> str:
        """Get confirmation message for process check."""
        return "List and monitor running processes"
    
    def requires_confirmation(self, parameters: Dict[str, Any]) -> bool:
        """Process check is safe and doesn't require confirmation."""
        return False
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> TaskResult:
        """Execute process check task."""
        import time
        start_time = time.time()
        
        try:
            validated_params = self.validate_parameters(parameters)
            
            # Build ps command
            ps_cmd = "ps aux"
            
            # Add sorting
            if validated_params["sort"] == "cpu":
                ps_cmd += " --sort=-%cpu"
            elif validated_params["sort"] == "mem":
                ps_cmd += " --sort=-%mem"
            elif validated_params["sort"] == "time":
                ps_cmd += " --sort=-time"
            
            # Add user filter
            if validated_params["user"]:
                ps_cmd += f" -u {validated_params['user']}"
            
            # Add limit
            ps_cmd += f" | head -{validated_params['limit'] + 1}"  # +1 for header
            
            # Generate additional process commands
            additional_commands = [
                "top -b -n1 | head -20",  # Process snapshot
                "htop -C",  # Enhanced process viewer (if available)
                "pstree -p",  # Process tree with PIDs
                "systemctl list-units --type=service --state=running",  # Running services
                "jobs -l",  # Background jobs
                "lsof -i",  # Network connections
            ]
            
            # Add name-specific commands if specified
            if validated_params["name"]:
                additional_commands.extend([
                    f"pgrep -l {validated_params['name']}",
                    f"ps aux | grep {validated_params['name']}",
                    f"systemctl status {validated_params['name']} 2>/dev/null || echo 'Not a service'"
                ])
            
            # Generate process management suggestions
            management_suggestions = [
                "# Kill process by PID",
                "kill -TERM <PID>",
                "kill -9 <PID>  # Force kill",
                "",
                "# Kill processes by name",
                "pkill process_name",
                "killall process_name",
                "",
                "# Process priority management",
                "nice -n 10 command  # Lower priority",
                "renice -n 5 -p <PID>  # Change priority",
                "",
                "# Background process management",
                "nohup command &  # Run in background",
                "disown %1  # Detach from shell",
                "",
                "# Monitor specific process",
                f"watch -n 2 'ps aux | grep {validated_params['name']}'" if validated_params['name'] else "watch -n 2 'ps aux | head -10'"
            ]
            
            execution_time = time.time() - start_time
            
            result = {
                "task_type": "process_check",
                "primary_command": ps_cmd,
                "additional_commands": additional_commands,
                "management_suggestions": management_suggestions,
                "parameters_used": validated_params,
                "description": f"Process monitoring sorted by {validated_params['sort']}",
                "next_steps": [
                    "Run the ps command to see current processes",
                    "Identify high CPU/memory usage processes",
                    "Check if any processes are consuming excessive resources",
                    "Use kill commands to terminate problematic processes if needed",
                    "Monitor process trends over time"
                ]
            }
            
            return TaskResult(
                success=True,
                result=result,
                sources=["ps", "top", "proc"],
                commands_generated=[ps_cmd] + additional_commands,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Process check task failed: {e}")
            
            return TaskResult(
                success=False,
                result={"error": str(e)},
                sources=[],
                commands_generated=[],
                execution_time=execution_time,
                error=str(e)
            )


class MemoryCheckHandler(BaseTaskHandler):
    """Handler for memory usage checking tasks."""
    
    def __init__(self):
        super().__init__(TaskType.MEMORY_CHECK)
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate memory check parameters."""
        validated = {
            "format": parameters.get("format", "human"),
            "show_swap": parameters.get("show_swap", True),
            "show_buffers": parameters.get("show_buffers", True),
            "continuous": parameters.get("continuous", False),
            "interval": int(parameters.get("interval", 1)),
            "count": int(parameters.get("count", 1))
        }
        
        # Validate format
        valid_formats = ["human", "bytes", "kb", "mb", "gb"]
        if validated["format"] not in valid_formats:
            validated["format"] = "human"
        
        # Validate interval and count
        validated["interval"] = max(1, min(validated["interval"], 60))
        validated["count"] = max(1, min(validated["count"], 100))
        
        return validated
    
    def get_confirmation_message(self, parameters: Dict[str, Any]) -> str:
        """Get confirmation message for memory check."""
        return "Check system memory and swap usage"
    
    def requires_confirmation(self, parameters: Dict[str, Any]) -> bool:
        """Memory check is safe and doesn't require confirmation."""
        return False
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> TaskResult:
        """Execute memory check task."""
        import time
        start_time = time.time()
        
        try:
            validated_params = self.validate_parameters(parameters)
            
            # Build free command
            free_cmd = "free"
            
            if validated_params["format"] == "human":
                free_cmd += " -h"
            elif validated_params["format"] == "kb":
                free_cmd += " -k"
            elif validated_params["format"] == "mb":
                free_cmd += " -m"
            elif validated_params["format"] == "gb":
                free_cmd += " -g"
            
            # Add additional options
            if validated_params["show_buffers"]:
                free_cmd += " -w"  # Wide format showing buffers/cache separately
            
            if validated_params["continuous"]:
                free_cmd += f" -s {validated_params['interval']}"
                if validated_params["count"] > 1:
                    free_cmd += f" -c {validated_params['count']}"
            
            # Generate additional memory analysis commands
            additional_commands = [
                "cat /proc/meminfo",
                "ps aux --sort=-%mem | head -10",  # Top memory consumers
                "top -b -n1 -o %MEM | head -20",  # Memory usage snapshot
                "vmstat 1 5",  # Virtual memory statistics
                "cat /proc/swaps",  # Swap information
                "swapon --show"  # Show swap devices
            ]
            
            # Generate memory optimization suggestions
            optimization_suggestions = [
                "# Check for memory leaks",
                "ps aux --sort=-%mem | head -10",
                "",
                "# Clear page cache (if safe)",
                "# echo 1 > /proc/sys/vm/drop_caches",
                "",
                "# Check swap usage",
                "swapon --show",
                "",
                "# Monitor memory over time",
                "vmstat 1 10",
                "",
                "# Find large processes",
                "ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head -20"
            ]
            
            execution_time = time.time() - start_time
            
            result = {
                "task_type": "memory_check",
                "primary_command": free_cmd,
                "additional_commands": additional_commands,
                "optimization_suggestions": optimization_suggestions,
                "parameters_used": validated_params,
                "description": f"Memory usage check in {validated_params['format']} format",
                "next_steps": [
                    "Run the free command to check current memory usage",
                    "Identify processes using the most memory with ps commands",
                    "Monitor memory usage over time with vmstat",
                    "Check swap usage and consider adding more if needed",
                    "Look for memory leaks in high-usage processes"
                ]
            }
            
            return TaskResult(
                success=True,
                result=result,
                sources=["free", "proc", "vmstat"],
                commands_generated=[free_cmd] + additional_commands,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Memory check task failed: {e}")
            
            return TaskResult(
                success=False,
                result={"error": str(e)},
                sources=[],
                commands_generated=[],
                execution_time=execution_time,
                error=str(e)
            )


class ProcessCheckHandler(BaseTaskHandler):
    """Handler for process monitoring tasks."""
    
    def __init__(self):
        super().__init__(TaskType.PROCESS_CHECK)
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate process check parameters."""
        validated = {
            "user": parameters.get("user", ""),
            "name": parameters.get("name", ""),
            "sort": parameters.get("sort", "cpu"),
            "limit": int(parameters.get("limit", 20)),
            "show_threads": parameters.get("show_threads", False),
            "tree_view": parameters.get("tree_view", False)
        }
        
        # Validate sort options
        valid_sorts = ["cpu", "mem", "pid", "time", "name"]
        if validated["sort"] not in valid_sorts:
            validated["sort"] = "cpu"
        
        # Validate limit
        validated["limit"] = max(1, min(validated["limit"], 100))
        
        return validated
    
    def get_confirmation_message(self, parameters: Dict[str, Any]) -> str:
        """Get confirmation message for process check."""
        return "List and monitor running processes"
    
    def requires_confirmation(self, parameters: Dict[str, Any]) -> bool:
        """Process check is safe and doesn't require confirmation."""
        return False
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> TaskResult:
        """Execute process check task."""
        import time
        start_time = time.time()
        
        try:
            validated_params = self.validate_parameters(parameters)
            
            # Build ps command
            ps_cmd = "ps aux"
            
            # Add sorting
            if validated_params["sort"] == "cpu":
                ps_cmd += " --sort=-%cpu"
            elif validated_params["sort"] == "mem":
                ps_cmd += " --sort=-%mem"
            elif validated_params["sort"] == "time":
                ps_cmd += " --sort=-time"
            
            # Add user filter
            if validated_params["user"]:
                ps_cmd += f" -u {validated_params['user']}"
            
            # Add limit
            ps_cmd += f" | head -{validated_params['limit'] + 1}"  # +1 for header
            
            # Generate additional process commands
            additional_commands = [
                "top -b -n1 | head -20",  # Process snapshot
                "htop -C",  # Enhanced process viewer (if available)
                "pstree -p",  # Process tree with PIDs
                "systemctl list-units --type=service --state=running",  # Running services
                "lsof -i",  # Network connections
                "netstat -tulpn"  # Network listening processes
            ]
            
            # Add name-specific commands if specified
            if validated_params["name"]:
                additional_commands.extend([
                    f"pgrep -f {validated_params['name']}",
                    f"ps aux | grep {validated_params['name']}",
                    f"systemctl status {validated_params['name']} 2>/dev/null || echo 'Not a service'"
                ])
            
            # Generate process management suggestions
            management_suggestions = [
                "# Kill process by PID",
                "kill -TERM <PID>  # Graceful termination",
                "kill -KILL <PID>  # Force kill",
                "",
                "# Process priority management",
                "nice -n 10 <command>  # Start with lower priority",
                "renice -n 5 -p <PID>  # Change priority of running process",
                "",
                "# Monitor specific process",
                "watch -n 1 'ps aux | grep <process_name>'",
                "",
                "# Resource limits",
                "ulimit -a  # Show current limits",
                "prlimit --pid <PID>  # Show process limits"
            ]
            
            execution_time = time.time() - start_time
            
            result = {
                "task_type": "process_check",
                "primary_command": ps_cmd,
                "additional_commands": additional_commands,
                "management_suggestions": management_suggestions,
                "parameters_used": validated_params,
                "description": f"Process listing sorted by {validated_params['sort']}",
                "next_steps": [
                    "Run the ps command to see current processes",
                    "Identify high CPU/memory usage processes",
                    "Check if any processes need attention or restart",
                    "Monitor system services with systemctl",
                    "Use top/htop for real-time monitoring"
                ]
            }
            
            return TaskResult(
                success=True,
                result=result,
                sources=["ps", "top", "systemctl"],
                commands_generated=[ps_cmd] + additional_commands,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Process check task failed: {e}")
            
            return TaskResult(
                success=False,
                result={"error": str(e)},
                sources=[],
                commands_generated=[],
                execution_time=execution_time,
                error=str(e)
            )


class TaskHandlerRegistry:
    """Registry for task handlers."""
    
    def __init__(self):
        self.handlers: Dict[TaskType, BaseTaskHandler] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default task handlers."""
        self.register_handler(LogAnalyzeHandler())
        self.register_handler(BackupCreateHandler())
        self.register_handler(DiskCheckHandler())
        self.register_handler(MemoryCheckHandler())
        self.register_handler(ProcessCheckHandler())
        self.register_handler(MemoryCheckHandler())
        self.register_handler(ProcessCheckHandler())
        self.register_handler(MemoryCheckHandler())  # Added missing handler
        self.register_handler(ProcessCheckHandler())  # Added missing handler
    
    def register_handler(self, handler: BaseTaskHandler):
        """Register a task handler."""
        self.handlers[handler.task_type] = handler
        logger.info(f"Registered handler for task type: {handler.task_type.value}")
    
    def get_handler(self, task_type: TaskType) -> Optional[BaseTaskHandler]:
        """Get handler for task type."""
        return self.handlers.get(task_type)
    
    def get_supported_tasks(self) -> List[TaskType]:
        """Get list of supported task types."""
        return list(self.handlers.keys())
    
    def is_supported(self, task_type: TaskType) -> bool:
        """Check if task type is supported."""
        return task_type in self.handlers