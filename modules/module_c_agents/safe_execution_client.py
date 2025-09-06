"""
Safe Execution Client for Module C: Proactive Agents
Integrates with Module D for secure command execution.
"""

import logging
import httpx
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of safe command execution."""
    success: bool
    command: str
    executed: bool
    preview: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None
    exit_code: Optional[int] = None
    execution_time: Optional[float] = None
    safety_warnings: List[str] = None
    files_affected: Optional[int] = None


class SafeExecutionClient:
    """
    Client for Module D: Safe Execution & Control
    
    Provides secure command execution with dry-run capabilities
    and comprehensive safety checks.
    """
    
    def __init__(self, module_d_url: str = "http://localhost:8004"):
        """
        Initialize safe execution client.
        
        Args:
            module_d_url: Base URL for Module D API
        """
        self.module_d_url = module_d_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    async def check_health(self) -> bool:
        """
        Check if Module D is available.
        
        Returns:
            True if Module D is healthy, False otherwise
        """
        try:
            response = await self.client.get(f"{self.module_d_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Module D health check failed: {e}")
            return False
    
    async def preview_command(self, command: str, working_directory: Optional[str] = None) -> ExecutionResult:
        """
        Preview command execution without actually running it.
        
        Args:
            command: Command to preview
            working_directory: Optional working directory
            
        Returns:
            ExecutionResult with preview information
        """
        try:
            payload = {
                "command": command,
                "dry_run": True,
                "force": False
            }
            
            if working_directory:
                payload["working_directory"] = working_directory
            
            response = await self.client.post(
                f"{self.module_d_url}/safe_execute",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                return ExecutionResult(
                    success=data.get("success", False),
                    command=data.get("command", command),
                    executed=data.get("executed", False),
                    preview=data.get("preview"),
                    output=data.get("output"),
                    error=data.get("error"),
                    exit_code=data.get("exit_code"),
                    execution_time=data.get("execution_time"),
                    safety_warnings=data.get("safety_warnings", []),
                    files_affected=data.get("files_affected")
                )
            else:
                error_msg = f"Preview failed with status {response.status_code}"
                logger.error(error_msg)
                return ExecutionResult(
                    success=False,
                    command=command,
                    executed=False,
                    error=error_msg
                )
                
        except Exception as e:
            error_msg = f"Preview request failed: {str(e)}"
            logger.error(error_msg)
            return ExecutionResult(
                success=False,
                command=command,
                executed=False,
                error=error_msg
            )
    
    async def execute_command(self, 
                            command: str, 
                            working_directory: Optional[str] = None,
                            force: bool = False) -> ExecutionResult:
        """
        Execute command safely with confirmation.
        
        Args:
            command: Command to execute
            working_directory: Optional working directory
            force: Force execution without additional confirmation
            
        Returns:
            ExecutionResult with execution details
        """
        try:
            payload = {
                "command": command,
                "dry_run": False,
                "force": force
            }
            
            if working_directory:
                payload["working_directory"] = working_directory
            
            response = await self.client.post(
                f"{self.module_d_url}/safe_execute",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                return ExecutionResult(
                    success=data.get("success", False),
                    command=data.get("command", command),
                    executed=data.get("executed", False),
                    preview=data.get("preview"),
                    output=data.get("output"),
                    error=data.get("error"),
                    exit_code=data.get("exit_code"),
                    execution_time=data.get("execution_time"),
                    safety_warnings=data.get("safety_warnings", []),
                    files_affected=data.get("files_affected")
                )
            else:
                error_msg = f"Execution failed with status {response.status_code}"
                logger.error(error_msg)
                return ExecutionResult(
                    success=False,
                    command=command,
                    executed=False,
                    error=error_msg
                )
                
        except Exception as e:
            error_msg = f"Execution request failed: {str(e)}"
            logger.error(error_msg)
            return ExecutionResult(
                success=False,
                command=command,
                executed=False,
                error=error_msg
            )
    
    async def execute_commands_batch(self, 
                                   commands: List[str],
                                   working_directory: Optional[str] = None,
                                   stop_on_error: bool = True) -> List[ExecutionResult]:
        """
        Execute multiple commands in sequence.
        
        Args:
            commands: List of commands to execute
            working_directory: Optional working directory
            stop_on_error: Stop execution if a command fails
            
        Returns:
            List of ExecutionResult objects
        """
        results = []
        
        for command in commands:
            logger.info(f"Executing command: {command}")
            
            # First preview the command
            preview_result = await self.preview_command(command, working_directory)
            
            if not preview_result.success:
                logger.warning(f"Command preview failed: {command}")
                results.append(preview_result)
                if stop_on_error:
                    break
                continue
            
            # Log safety warnings
            if preview_result.safety_warnings:
                logger.warning(f"Safety warnings for '{command}': {preview_result.safety_warnings}")
            
            # Execute the command
            exec_result = await self.execute_command(command, working_directory, force=True)
            results.append(exec_result)
            
            if not exec_result.success and stop_on_error:
                logger.error(f"Command execution failed, stopping batch: {command}")
                break
        
        return results
    
    async def get_execution_logs(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent execution logs from Module D.
        
        Args:
            limit: Maximum number of log entries to retrieve
            
        Returns:
            Dictionary with log data
        """
        try:
            response = await self.client.get(
                f"{self.module_d_url}/logs/history",
                params={"limit": limit}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get logs: {response.status_code}")
                return {"success": False, "error": "Failed to retrieve logs"}
                
        except Exception as e:
            logger.error(f"Log request failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_security_events(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent security events from Module D.
        
        Args:
            limit: Maximum number of events to retrieve
            
        Returns:
            Dictionary with security event data
        """
        try:
            response = await self.client.get(
                f"{self.module_d_url}/logs/security",
                params={"limit": limit}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get security events: {response.status_code}")
                return {"success": False, "error": "Failed to retrieve security events"}
                
        except Exception as e:
            logger.error(f"Security events request failed: {str(e)}")
            return {"success": False, "error": str(e)}


# Global client instance
safe_execution_client = SafeExecutionClient()


async def preview_command(command: str, working_directory: Optional[str] = None) -> ExecutionResult:
    """Convenience function for command preview."""
    return await safe_execution_client.preview_command(command, working_directory)


async def execute_command(command: str, 
                         working_directory: Optional[str] = None,
                         force: bool = False) -> ExecutionResult:
    """Convenience function for command execution."""
    return await safe_execution_client.execute_command(command, working_directory, force)


async def execute_commands_batch(commands: List[str],
                               working_directory: Optional[str] = None,
                               stop_on_error: bool = True) -> List[ExecutionResult]:
    """Convenience function for batch command execution."""
    return await safe_execution_client.execute_commands_batch(commands, working_directory, stop_on_error)