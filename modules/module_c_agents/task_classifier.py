"""
Task classifier for Module C: Proactive Agents.
Identifies task types based on keywords and patterns in user queries.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Supported task types for proactive agents."""
    LOG_ANALYZE = "log_analyze"
    BACKUP_CREATE = "backup_create"
    DISK_CHECK = "disk_check"
    MEMORY_CHECK = "memory_check"
    PROCESS_CHECK = "process_check"
    UNKNOWN = "unknown"


@dataclass
class TaskMatch:
    """Result of task classification."""
    task_type: TaskType
    confidence: float
    matched_keywords: List[str]
    extracted_params: Dict[str, str]


class TaskClassifier:
    """Classifies user queries into predefined task types."""
    
    def __init__(self):
        """Initialize task classifier with keyword patterns."""
        self.task_patterns = {
            TaskType.LOG_ANALYZE: {
                "keywords": [
                    "log", "logs", "journal", "journalctl", "syslog", "error", "errors",
                    "analyze", "check logs", "view logs", "system logs", "application logs",
                    "debug", "troubleshoot", "investigate", "audit"
                ],
                "patterns": [
                    r"check.*logs?",
                    r"analyze.*logs?",
                    r"view.*logs?",
                    r"show.*logs?",
                    r"journalctl",
                    r"syslog",
                    r"error.*logs?",
                    r"log.*analysis"
                ],
                "params": {
                    "service": r"service\s+(\w+)",
                    "since": r"since\s+([^\s]+)",
                    "until": r"until\s+([^\s]+)",
                    "priority": r"priority\s+(\w+)",
                    "lines": r"(\d+)\s+lines?"
                }
            },
            TaskType.BACKUP_CREATE: {
                "keywords": [
                    "backup", "backups", "rsync", "copy", "sync", "synchronize",
                    "archive", "create backup", "backup script", "backup files",
                    "backup directory", "backup system", "incremental", "differential"
                ],
                "patterns": [
                    r"create.*backup",
                    r"backup.*script",
                    r"backup.*files?",
                    r"backup.*directory",
                    r"rsync.*script",
                    r"sync.*files?",
                    r"archive.*data"
                ],
                "params": {
                    "source": r"(?:from|source)\s+([^\s]+)",
                    "destination": r"(?:to|dest|destination)\s+([^\s]+)",
                    "type": r"(incremental|differential|full)",
                    "exclude": r"exclude\s+([^\s]+)"
                }
            },
            TaskType.DISK_CHECK: {
                "keywords": [
                    "disk", "space", "storage", "filesystem", "df", "du",
                    "disk space", "disk usage", "free space", "storage usage",
                    "check disk", "disk full", "out of space"
                ],
                "patterns": [
                    r"check.*disk",
                    r"disk.*space",
                    r"disk.*usage",
                    r"free.*space",
                    r"storage.*usage",
                    r"df\s*-h?",
                    r"du\s*-h?"
                ],
                "params": {
                    "path": r"(?:path|directory)\s+([^\s]+)",
                    "format": r"(human|bytes|kb|mb|gb)"
                }
            },
            TaskType.MEMORY_CHECK: {
                "keywords": [
                    "memory", "ram", "swap", "free", "memory usage", "ram usage",
                    "check memory", "memory status", "available memory", "used memory"
                ],
                "patterns": [
                    r"check.*memory",
                    r"memory.*usage",
                    r"ram.*usage",
                    r"free.*memory",
                    r"available.*memory",
                    r"free\s*-h?"
                ],
                "params": {
                    "format": r"(human|bytes|kb|mb|gb)"
                }
            },
            TaskType.PROCESS_CHECK: {
                "keywords": [
                    "process", "processes", "ps", "top", "htop", "running",
                    "check processes", "list processes", "process status",
                    "running processes", "system processes", "cpu usage"
                ],
                "patterns": [
                    r"check.*process",
                    r"list.*process",
                    r"running.*process",
                    r"process.*status",
                    r"ps\s+aux",
                    r"top",
                    r"htop"
                ],
                "params": {
                    "user": r"user\s+(\w+)",
                    "name": r"(?:process|command)\s+(\w+)",
                    "sort": r"sort.*by\s+(\w+)"
                }
            }
        }
    
    def classify_task(self, query: str) -> TaskMatch:
        """
        Classify a user query into a task type.
        
        Args:
            query: User query string
            
        Returns:
            TaskMatch with classification results
        """
        query_lower = query.lower().strip()
        
        best_match = TaskMatch(
            task_type=TaskType.UNKNOWN,
            confidence=0.0,
            matched_keywords=[],
            extracted_params={}
        )
        
        for task_type, config in self.task_patterns.items():
            match_score = 0.0
            matched_keywords = []
            extracted_params = {}
            
            # Check keyword matches
            keyword_matches = 0
            for keyword in config["keywords"]:
                if keyword in query_lower:
                    keyword_matches += 1
                    matched_keywords.append(keyword)
            
            if keyword_matches > 0:
                match_score += (keyword_matches / len(config["keywords"])) * 0.6
            
            # Check pattern matches
            pattern_matches = 0
            for pattern in config["patterns"]:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    pattern_matches += 1
            
            if pattern_matches > 0:
                match_score += (pattern_matches / len(config["patterns"])) * 0.4
            
            # Extract parameters
            for param_name, param_pattern in config["params"].items():
                match = re.search(param_pattern, query, re.IGNORECASE)
                if match:
                    extracted_params[param_name] = match.group(1)
                    match_score += 0.1  # Bonus for parameter extraction
            
            # Update best match if this is better
            if match_score > best_match.confidence:
                best_match = TaskMatch(
                    task_type=task_type,
                    confidence=match_score,
                    matched_keywords=matched_keywords,
                    extracted_params=extracted_params
                )
        
        logger.debug(f"Classified query '{query}' as {best_match.task_type.value} (confidence: {best_match.confidence:.3f})")
        
        return best_match
    
    def get_task_suggestions(self, query: str, min_confidence: float = 0.1) -> List[TaskMatch]:
        """
        Get multiple task suggestions for a query.
        
        Args:
            query: User query string
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of TaskMatch objects sorted by confidence
        """
        suggestions = []
        query_lower = query.lower().strip()
        
        for task_type, config in self.task_patterns.items():
            match_score = 0.0
            matched_keywords = []
            extracted_params = {}
            
            # Check keyword matches
            keyword_matches = 0
            for keyword in config["keywords"]:
                if keyword in query_lower:
                    keyword_matches += 1
                    matched_keywords.append(keyword)
            
            if keyword_matches > 0:
                match_score += (keyword_matches / len(config["keywords"])) * 0.6
            
            # Check pattern matches
            pattern_matches = 0
            for pattern in config["patterns"]:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    pattern_matches += 1
            
            if pattern_matches > 0:
                match_score += (pattern_matches / len(config["patterns"])) * 0.4
            
            # Extract parameters
            for param_name, param_pattern in config["params"].items():
                match = re.search(param_pattern, query, re.IGNORECASE)
                if match:
                    extracted_params[param_name] = match.group(1)
                    match_score += 0.1
            
            # Add to suggestions if above threshold
            if match_score >= min_confidence:
                suggestions.append(TaskMatch(
                    task_type=task_type,
                    confidence=match_score,
                    matched_keywords=matched_keywords,
                    extracted_params=extracted_params
                ))
        
        # Sort by confidence (descending)
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        return suggestions
    
    def get_supported_tasks(self) -> List[TaskType]:
        """Get list of supported task types."""
        return [task_type for task_type in self.task_patterns.keys() if task_type != TaskType.UNKNOWN]
    
    def get_task_description(self, task_type: TaskType) -> str:
        """Get human-readable description of a task type."""
        descriptions = {
            TaskType.LOG_ANALYZE: "Analyze system logs and troubleshoot issues",
            TaskType.BACKUP_CREATE: "Create backup scripts and synchronization tasks",
            TaskType.DISK_CHECK: "Check disk space and storage usage",
            TaskType.MEMORY_CHECK: "Monitor memory and RAM usage",
            TaskType.PROCESS_CHECK: "List and monitor running processes",
            TaskType.UNKNOWN: "Unknown or unsupported task type"
        }
        return descriptions.get(task_type, "No description available")