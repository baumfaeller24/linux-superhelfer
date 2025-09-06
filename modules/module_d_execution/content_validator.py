"""
Content Validator for Module D
Validates web content and commands for security
"""

import re
import hashlib
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class ContentValidator:
    """Validates content and URLs for security compliance"""
    
    def __init__(self):
        self.allowed_domains = [
            "wiki.archlinux.org",
            "help.ubuntu.com", 
            "stackoverflow.com",
            "man7.org",
            "kernel.org",
            "docs.python.org"
        ]
        
        self.blocked_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'eval\s*\(',
            r'document\.write',
            r'innerHTML\s*=',
            r'<iframe[^>]*src=',
            r'\.exe$',
            r'\.bat$',
            r'\.sh$'
        ]
        
        self.dangerous_commands = [
            'rm -rf /',
            'dd if=',
            'mkfs',
            'fdisk',
            'parted',
            'shutdown',
            'reboot',
            'halt',
            'init 0',
            'init 6',
            ':(){ :|:& };:',  # Fork bomb
            'chmod 777 /',
            'chown -R'
        ]
    
    def validate_url(self, url: str) -> Dict[str, any]:
        """Validate URL for security"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check protocol
            if parsed.scheme not in ['http', 'https']:
                return {
                    "valid": False,
                    "reason": f"Unsupported protocol: {parsed.scheme}",
                    "risk_level": "high"
                }
            
            # Check domain whitelist
            domain_allowed = any(allowed in domain for allowed in self.allowed_domains)
            if not domain_allowed:
                return {
                    "valid": False,
                    "reason": f"Domain not whitelisted: {domain}",
                    "risk_level": "medium"
                }
            
            # Check for suspicious patterns in URL
            suspicious_found = []
            for pattern in self.blocked_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    suspicious_found.append(pattern)
            
            if suspicious_found:
                return {
                    "valid": False,
                    "reason": f"Suspicious patterns found: {suspicious_found}",
                    "risk_level": "high"
                }
            
            return {
                "valid": True,
                "reason": "URL passed validation",
                "risk_level": "low"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "reason": f"URL parsing failed: {e}",
                "risk_level": "high"
            }
    
    def validate_content(self, content: str, max_size: int = 1024*1024) -> Dict[str, any]:
        """Validate content for security issues"""
        
        # Check size
        if len(content) > max_size:
            return {
                "valid": False,
                "reason": f"Content too large: {len(content)} > {max_size}",
                "risk_level": "medium"
            }
        
        # Check for malicious patterns
        suspicious_patterns = []
        for pattern in self.blocked_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            if matches:
                suspicious_patterns.append(pattern)
        
        if suspicious_patterns:
            return {
                "valid": False,
                "reason": f"Malicious patterns detected: {suspicious_patterns}",
                "risk_level": "high"
            }
        
        # Check for dangerous commands in content
        dangerous_found = []
        content_lower = content.lower()
        for cmd in self.dangerous_commands:
            if cmd.lower() in content_lower:
                dangerous_found.append(cmd)
        
        if dangerous_found:
            return {
                "valid": False,
                "reason": f"Dangerous commands found: {dangerous_found}",
                "risk_level": "high"
            }
        
        return {
            "valid": True,
            "reason": "Content passed validation",
            "risk_level": "low"
        }
    
    def sanitize_content(self, content: str) -> str:
        """Sanitize content by removing dangerous elements"""
        
        # Remove script tags
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove event handlers
        content = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
        
        # Remove javascript: links
        content = re.sub(r'javascript:[^"\'>\s]*', '#', content, flags=re.IGNORECASE)
        
        # Remove style tags
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove comments
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        return content.strip()
    
    def validate_command_for_web_content(self, command: str) -> Dict[str, any]:
        """Special validation for commands that might process web content"""
        
        # Check if command involves downloading or processing web content
        web_commands = ['curl', 'wget', 'lynx', 'w3m', 'links']
        
        command_lower = command.lower()
        involves_web = any(cmd in command_lower for cmd in web_commands)
        
        if not involves_web:
            return {"valid": True, "reason": "No web content processing"}
        
        # Additional checks for web commands
        dangerous_flags = [
            '-o /etc/',      # Writing to system directories
            '-O /etc/',
            '| sh',          # Piping to shell
            '| bash',
            '&& rm',         # Chaining with dangerous commands
            '; rm',
            '--post-data',   # POST requests (potential for abuse)
            '--post-file'
        ]
        
        for flag in dangerous_flags:
            if flag in command_lower:
                return {
                    "valid": False,
                    "reason": f"Dangerous web command pattern: {flag}",
                    "risk_level": "high"
                }
        
        return {
            "valid": True,
            "reason": "Web command passed validation",
            "risk_level": "low"
        }
    
    def create_content_hash(self, content: str) -> str:
        """Create hash for content tracking"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def validate_file_upload(self, filename: str, content: str) -> Dict[str, any]:
        """Validate file uploads"""
        
        # Check filename
        if '..' in filename or filename.startswith('/'):
            return {
                "valid": False,
                "reason": "Invalid filename path",
                "risk_level": "high"
            }
        
        # Check file extension
        allowed_extensions = ['.txt', '.md', '.log', '.conf', '.cfg', '.ini']
        file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        
        if file_ext not in allowed_extensions:
            return {
                "valid": False,
                "reason": f"File extension not allowed: {file_ext}",
                "risk_level": "medium"
            }
        
        # Validate content
        content_validation = self.validate_content(content)
        if not content_validation["valid"]:
            return content_validation
        
        return {
            "valid": True,
            "reason": "File upload passed validation",
            "risk_level": "low"
        }