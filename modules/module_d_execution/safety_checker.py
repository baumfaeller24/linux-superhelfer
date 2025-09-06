"""
Safety Checker for Module D: Safe Execution & Control

This module provides command validation logic with blacklist/whitelist
functionality for secure command execution.
"""

import re
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class SafetyRule:
    """Safety rule for command validation"""
    pattern: str
    rule_type: str  # 'blacklist' or 'whitelist'
    description: str
    severity: str  # 'low', 'medium', 'high', 'critical'


class SafetyChecker:
    """
    Command validation with blacklist/whitelist functionality.
    
    Provides comprehensive safety checking for Linux commands
    before execution with configurable rules.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize safety checker with default rules.
        
        Args:
            config_path: Optional path to custom safety configuration
        """
        self.blacklist_patterns = self._load_default_blacklist()
        self.whitelist_patterns = self._load_default_whitelist()
        self.safety_rules = self._load_default_rules()
        
        if config_path:
            self._load_custom_config(config_path)
    
    def _load_default_blacklist(self) -> Set[str]:
        """Load default blacklisted command patterns."""
        return {
            # Destructive file operations
            r'rm\s+.*-rf\s+/',
            r'rm\s+.*-rf\s+\*',
            r'dd\s+.*of=/dev/',
            r'mkfs\.*',
            r'fdisk\s+/dev/',
            r'parted\s+/dev/',
            
            # System shutdown/reboot
            r'shutdown\s+.*now',
            r'reboot\s+.*-f',
            r'halt\s+.*-f',
            r'poweroff\s+.*-f',
            
            # Process killing
            r'kill\s+.*-9\s+1',  # Don't kill init
            r'killall\s+.*-9',
            r'pkill\s+.*-9',
            
            # Network/firewall changes
            r'iptables\s+.*-F',
            r'ufw\s+.*--force',
            
            # Dangerous file operations
            r'chmod\s+.*777\s+/',
            r'chown\s+.*root\s+/',
            r'find\s+.*-delete',
            
            # Package management (potentially dangerous)
            r'apt\s+.*remove\s+.*--purge',
            r'yum\s+.*remove',
            r'dnf\s+.*remove',
            
            # Disk operations
            r'wipefs\s+/dev/',
            r'shred\s+/dev/',
        }
    
    def _load_default_whitelist(self) -> Set[str]:
        """Load default whitelisted command patterns."""
        return {
            # Safe information commands
            r'ls\s+.*',
            r'cat\s+.*',
            r'less\s+.*',
            r'more\s+.*',
            r'head\s+.*',
            r'tail\s+.*',
            r'grep\s+.*',
            r'find\s+.*-type\s+f',
            r'find\s+.*-name\s+.*',
            
            # System information
            r'df\s+.*',
            r'du\s+.*',
            r'free\s+.*',
            r'ps\s+.*',
            r'top\s*',
            r'htop\s*',
            r'uptime\s*',
            r'whoami\s*',
            r'id\s*',
            r'uname\s+.*',
            
            # Network information
            r'ping\s+.*-c\s+\d+',
            r'netstat\s+.*',
            r'ss\s+.*',
            r'ip\s+.*show',
            r'ip\s+.*addr',
            
            # Log viewing
            r'journalctl\s+.*',
            r'dmesg\s*',
            r'tail\s+.*\.log',
            
            # Safe file operations
            r'cp\s+.*',
            r'mv\s+.*',
            r'mkdir\s+.*',
            r'touch\s+.*',
            
            # Archive operations
            r'tar\s+.*-[tz].*',
            r'gzip\s+.*',
            r'gunzip\s+.*',
            r'zip\s+.*',
            r'unzip\s+.*',
        }
    
    def _load_default_rules(self) -> List[SafetyRule]:
        """Load default safety rules."""
        return [
            SafetyRule(
                pattern=r'rm\s+.*-rf\s+/',
                rule_type='blacklist',
                description='Recursive force removal from root paths',
                severity='critical'
            ),
            SafetyRule(
                pattern=r'sudo\s+.*',
                rule_type='whitelist',
                description='Commands requiring elevated privileges',
                severity='high'
            ),
            SafetyRule(
                pattern=r'.*\*.*',
                rule_type='blacklist',
                description='Commands with wildcards require caution',
                severity='medium'
            ),
            SafetyRule(
                pattern=r'ls\s+.*',
                rule_type='whitelist',
                description='Safe directory listing command',
                severity='low'
            ),
        ]
    
    def _load_custom_config(self, config_path: str):
        """Load custom safety configuration from file."""
        try:
            # TODO: Implement custom config loading
            logger.info(f"Loading custom safety config from {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load custom config: {e}")
    
    def check_command_safety(self, command: str) -> Dict[str, any]:
        """
        Check command against safety rules.
        
        Args:
            command: Command string to validate
            
        Returns:
            Dictionary with safety check results
        """
        result = {
            'is_safe': True,
            'violations': [],
            'warnings': [],
            'matched_rules': [],
            'recommendation': 'safe'
        }
        
        # Check against blacklist patterns
        for pattern in self.blacklist_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                result['is_safe'] = False
                result['violations'].append({
                    'pattern': pattern,
                    'type': 'blacklist',
                    'severity': 'high'
                })
        
        # Check against whitelist patterns
        whitelist_match = False
        for pattern in self.whitelist_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                whitelist_match = True
                result['matched_rules'].append({
                    'pattern': pattern,
                    'type': 'whitelist',
                    'severity': 'low'
                })
                break
        
        # Check detailed safety rules
        for rule in self.safety_rules:
            if re.search(rule.pattern, command, re.IGNORECASE):
                rule_match = {
                    'pattern': rule.pattern,
                    'type': rule.rule_type,
                    'description': rule.description,
                    'severity': rule.severity
                }
                
                if rule.rule_type == 'blacklist':
                    result['violations'].append(rule_match)
                    if rule.severity in ['high', 'critical']:
                        result['is_safe'] = False
                else:  # whitelist
                    result['matched_rules'].append(rule_match)
        
        # Determine recommendation
        if not result['is_safe']:
            result['recommendation'] = 'blocked'
        elif result['violations']:
            result['recommendation'] = 'caution'
        elif whitelist_match:
            result['recommendation'] = 'safe'
        else:
            result['recommendation'] = 'review'
            result['warnings'].append('Command not in whitelist - manual review recommended')
        
        logger.debug(f"Safety check for '{command}': {result['recommendation']}")
        return result
    
    def validate_command_structure(self, command: str) -> Dict[str, any]:
        """
        Validate command structure and syntax.
        
        Args:
            command: Command to validate
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'is_valid': True,
            'syntax_errors': [],
            'structure_warnings': []
        }
        
        # Basic syntax validation
        if not command.strip():
            validation['is_valid'] = False
            validation['syntax_errors'].append('Empty command')
            return validation
        
        # Check for dangerous character combinations
        dangerous_chars = ['&&', '||', ';', '|', '>', '>>', '<']
        for char_combo in dangerous_chars:
            if char_combo in command:
                validation['structure_warnings'].append(
                    f'Command contains potentially dangerous operator: {char_combo}'
                )
        
        # Check for command injection patterns
        injection_patterns = [
            r'`.*`',  # Command substitution
            r'\$\(.*\)',  # Command substitution
            r'.*\|\s*sh',  # Piping to shell
            r'.*\|\s*bash',  # Piping to bash
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, command):
                validation['structure_warnings'].append(
                    f'Potential command injection pattern detected: {pattern}'
                )
        
        return validation
    
    def get_safety_recommendations(self, command: str) -> List[str]:
        """
        Get safety recommendations for command execution.
        
        Args:
            command: Command to analyze
            
        Returns:
            List of safety recommendations
        """
        recommendations = []
        
        # Check if command needs dry run
        if any(pattern in command.lower() for pattern in ['rm', 'delete', 'remove']):
            recommendations.append('Consider running with --dry-run flag first')
        
        # Check if backup is recommended
        if any(pattern in command.lower() for pattern in ['rm', 'mv', 'cp']):
            recommendations.append('Consider backing up affected files before execution')
        
        # Check if elevated privileges are needed
        if not command.startswith('sudo') and any(
            pattern in command for pattern in ['/etc/', '/usr/', '/var/']
        ):
            recommendations.append('This command may require elevated privileges (sudo)')
        
        # Check for system impact
        if any(pattern in command.lower() for pattern in ['systemctl', 'service', 'mount']):
            recommendations.append('This command affects system services - verify impact')
        
        return recommendations
    
    def add_custom_rule(self, pattern: str, rule_type: str, 
                       description: str, severity: str):
        """
        Add custom safety rule.
        
        Args:
            pattern: Regex pattern to match
            rule_type: 'blacklist' or 'whitelist'
            description: Rule description
            severity: Rule severity level
        """
        rule = SafetyRule(pattern, rule_type, description, severity)
        self.safety_rules.append(rule)
        logger.info(f"Added custom safety rule: {description}")


def create_safety_checker(config_path: Optional[str] = None) -> SafetyChecker:
    """Factory function to create SafetyChecker instance."""
    return SafetyChecker(config_path)