"""
Command Parser for Module D: Safe Execution & Control
Analyzes command structure and safety.
"""

import shlex
from typing import Dict, List, Any


class CommandParser:
    """Analyzes command structure and safety."""
    
    DANGEROUS_COMMANDS = {
        'rm': 'File deletion command',
        'rmdir': 'Directory removal command', 
        'dd': 'Low-level disk operations',
        'mkfs': 'Filesystem creation',
        'fdisk': 'Disk partitioning',
        'parted': 'Disk partitioning',
        'mount': 'Filesystem mounting',
        'umount': 'Filesystem unmounting',
        'chmod': 'Permission changes',
        'chown': 'Ownership changes',
        'sudo': 'Elevated privileges',
        'su': 'User switching',
        'passwd': 'Password changes',
        'userdel': 'User deletion',
        'groupdel': 'Group deletion'
    }
    
    DESTRUCTIVE_FLAGS = [
        '-rf', '-r', '-f', '--force', '--recursive',
        '--delete', '--remove', '--purge'
    ]
    
    def parse_command(self, command: str) -> Dict[str, Any]:
        """Parse command and analyze safety."""
        try:
            # Split command safely
            parts = shlex.split(command)
            if not parts:
                return {"valid": False, "error": "Empty command"}
            
            base_command = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            
            # Check for dangerous commands
            warnings = []
            danger_level = "safe"
            
            if base_command in self.DANGEROUS_COMMANDS:
                warnings.append(f"Potentially dangerous: {self.DANGEROUS_COMMANDS[base_command]}")
                danger_level = "dangerous"
            
            # Check for destructive flags
            for arg in args:
                if arg in self.DESTRUCTIVE_FLAGS:
                    warnings.append(f"Destructive flag detected: {arg}")
                    danger_level = "destructive"
            
            # Check for system paths
            system_paths = ['/bin', '/sbin', '/usr', '/etc', '/boot', '/sys', '/proc']
            for arg in args:
                if any(arg.startswith(path) for path in system_paths):
                    warnings.append(f"System path detected: {arg}")
                    if danger_level == "safe":
                        danger_level = "risky"
            
            return {
                "valid": True,
                "base_command": base_command,
                "args": args,
                "warnings": warnings,
                "danger_level": danger_level,
                "requires_confirmation": danger_level in ["dangerous", "destructive"]
            }
            
        except Exception as e:
            return {"valid": False, "error": f"Command parsing failed: {str(e)}"}