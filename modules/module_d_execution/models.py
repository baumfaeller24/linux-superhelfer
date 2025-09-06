"""
Data models for Module D: Safe Execution & Control
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    command: str = Field(..., description="Command to execute")
    dry_run: bool = Field(True, description="Whether to perform dry run only")
    force: bool = Field(False, description="Force execution without confirmation")
    working_directory: Optional[str] = Field(None, description="Working directory for command")


class CommandResponse(BaseModel):
    success: bool
    command: str
    dry_run: bool
    executed: bool
    preview: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None
    exit_code: Optional[int] = None
    execution_time: Optional[float] = None
    safety_warnings: List[str] = []
    files_affected: Optional[int] = None


class ExecutionLog(BaseModel):
    timestamp: datetime
    command: str
    user: str
    success: bool
    exit_code: int
    execution_time: float