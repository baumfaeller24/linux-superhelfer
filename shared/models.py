"""
Shared data models and API contracts for Linux Superhelfer modules.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Query(BaseModel):
    """Standard query model used across modules."""
    text: str = Field(..., description="The query text")
    context: Optional[str] = Field(None, description="Optional context information")
    session_id: Optional[str] = Field(None, description="Session identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Query timestamp")


class Response(BaseModel):
    """Standard response model used across modules."""
    content: str = Field(..., description="Response content")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    source: str = Field(..., description="Source of the response")
    processing_time: float = Field(..., description="Processing time in seconds")


class Task(BaseModel):
    """Task model for proactive agents."""
    type: str = Field(..., description="Task type identifier")
    params: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    status: str = Field(default="pending", description="Task status")
    result: Optional[str] = Field(None, description="Task execution result")


class Command(BaseModel):
    """Command model for safe execution."""
    command: str = Field(..., description="Command to execute")
    safe: bool = Field(default=False, description="Whether command is marked as safe")
    preview: str = Field(..., description="Preview of command effects")
    executed: bool = Field(default=False, description="Whether command was executed")
    output: Optional[str] = Field(None, description="Command execution output")
    exit_code: Optional[int] = Field(None, description="Command exit code")


class HealthStatus(BaseModel):
    """Standard health check response."""
    status: str = Field(default="ok", description="Health status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    version: Optional[str] = Field(None, description="Module version")


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str = Field(..., description="Error message")
    code: int = Field(..., description="Error code")
    details: Optional[str] = Field(None, description="Additional error details")
    suggestion: Optional[str] = Field(None, description="Suggested resolution")


class DocumentChunk(BaseModel):
    """Document chunk for RAG system."""
    content: str = Field(..., description="Chunk content")
    source: str = Field(..., description="Source document")
    chunk_id: str = Field(..., description="Unique chunk identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SearchResult(BaseModel):
    """Search result from RAG system."""
    content: str = Field(..., description="Matching content")
    source: str = Field(..., description="Source document")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ModuleConfig(BaseModel):
    """Configuration for module endpoints."""
    name: str = Field(..., description="Module name")
    host: str = Field(default="localhost", description="Module host")
    port: int = Field(..., description="Module port")
    enabled: bool = Field(default=True, description="Whether module is enabled")


class SystemConfig(BaseModel):
    """System-wide configuration."""
    modules: Dict[str, ModuleConfig] = Field(..., description="Module configurations")
    features: Dict[str, Any] = Field(default_factory=dict, description="Feature flags")
    ollama: Dict[str, Any] = Field(default_factory=dict, description="Ollama configuration")