"""
Safe Executor for Module D: Safe Execution & Control
Main execution logic with safety checks.
"""

import asyncio
import os
import time
from typing import Optional
from pathlib import Path

from command_parser import CommandParser
from models import CommandRequest, CommandResponse
from content_validator import ContentValidator
from execution_logger import execution_logger


class SafeExecutor:
    """Main class for safe command execution."""
    
    def __init__(self):
        self.parser = CommandParser()
        self.content_validator = ContentValidator()
    
    async def execute_command(self, request: CommandRequest) -> CommandResponse:
        """Execute command safely with optional dry-run."""
        start_time = time.time()
        
        # Parse command
        parsed = self.parser.parse_command(request.command)
        if not parsed["valid"]:
            return CommandResponse(
                success=False,
                command=request.command,
                dry_run=request.dry_run,
                executed=False,
                error=parsed["error"]
            )
        
        # Create preview
        preview_effects = []
        base_command = parsed["base_command"]
        args = parsed["args"]
        
        # Simple command simulation
        if base_command in ["ls", "cat", "grep", "find", "ps", "top", "df", "free", "whoami", "pwd"]:
            preview_effects = ["Read-only operation - no system changes"]
        elif base_command == "rm":
            preview_effects = [f"Will delete: {' '.join([arg for arg in args if not arg.startswith('-')])}"]
        elif base_command in ["cp", "mv"]:
            if len(args) >= 2:
                preview_effects = [f"Will {base_command}: {args[-2]} -> {args[-1]}"]
        elif base_command == "mkdir":
            dirs = [arg for arg in args if not arg.startswith("-")]
            preview_effects = [f"Will create directories: {', '.join(dirs)}"]
        else:
            preview_effects = [f"Will execute: {base_command} with args: {' '.join(args)}"]
        
        response = CommandResponse(
            success=True,
            command=request.command,
            dry_run=request.dry_run,
            executed=False,
            preview="\n".join(preview_effects),
            safety_warnings=parsed.get("warnings", []),
            files_affected=len([arg for arg in args if not arg.startswith("-")])
        )
        
        # If dry run only, return preview
        if request.dry_run:
            response.execution_time = time.time() - start_time
            
            # Log dry run
            execution_logger.log_execution(
                command=request.command,
                user="system",  # TODO: Get actual user
                working_directory=request.working_directory or os.getcwd(),
                dry_run=True,
                executed=False,
                success=True,
                execution_time=response.execution_time,
                safety_warnings=parsed.get("warnings", []),
                files_affected=response.files_affected,
                output_preview=response.preview
            )
            
            return response
        
        # Check if confirmation required
        if parsed["requires_confirmation"] and not request.force:
            response.error = "Command requires confirmation. Use force=true to execute."
            return response
        
        # Execute command
        try:
            working_dir = request.working_directory or os.getcwd()
            
            process = await asyncio.create_subprocess_shell(
                request.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir
            )
            
            stdout, stderr = await process.communicate()
            
            execution_time = time.time() - start_time
            
            response.executed = True
            response.exit_code = process.returncode
            response.execution_time = execution_time
            response.success = process.returncode == 0
            
            if stdout:
                response.output = stdout.decode('utf-8', errors='replace')
            if stderr:
                response.error = stderr.decode('utf-8', errors='replace')
            
        except Exception as e:
            response.success = False
            response.error = f"Execution failed: {str(e)}"
            response.execution_time = time.time() - start_time
        
        # Log actual execution
        execution_logger.log_execution(
            command=request.command,
            user="system",  # TODO: Get actual user
            working_directory=working_dir,
            dry_run=False,
            executed=True,
            success=response.success,
            exit_code=response.exit_code,
            execution_time=response.execution_time,
            safety_warnings=parsed.get("warnings", []),
            files_affected=response.files_affected,
            output_preview=response.output[:500] if response.output else None,
            error_message=response.error
        )
        
        return response