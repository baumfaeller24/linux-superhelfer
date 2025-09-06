"""
Unit tests for Module D: Safe Execution & Control
"""

import pytest
from modules.module_d_execution.command_parser import (
    CommandParser, ParsedCommand, CommandRisk, create_command_parser
)
from modules.module_d_execution.safety_checker import (
    SafetyChecker, SafetyRule, create_safety_checker
)


class TestCommandParser:
    """Test cases for CommandParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = create_command_parser()
    
    def test_parse_simple_safe_command(self):
        """Test parsing of simple safe command."""
        result = self.parser.parse_command("ls -la /home")
        
        assert result.executable == "ls"
        assert result.arguments == ["-la", "/home"]
        assert result.flags == ["-la"]
        assert result.paths == ["/home"]
        assert result.risk_level == CommandRisk.SAFE
        assert not result.is_destructive
        assert not result.requires_sudo
    
    def test_parse_destructive_command(self):
        """Test parsing of destructive command."""
        result = self.parser.parse_command("rm -rf /tmp/test")
        
        assert result.executable == "rm"
        assert result.risk_level in [CommandRisk.HIGH, CommandRisk.CRITICAL]
        assert result.is_destructive
        assert "Destructive command: rm" in result.risk_reasons
        assert "High-risk flag: -rf" in result.risk_reasons
    
    def test_parse_sudo_command(self):
        """Test parsing of command with sudo."""
        result = self.parser.parse_command("sudo systemctl restart nginx")
        
        assert result.executable == "sudo"
        assert result.requires_sudo
        assert result.affects_system
        assert "Requires elevated privileges" in result.risk_reasons
    
    def test_parse_system_command(self):
        """Test parsing of system command."""
        result = self.parser.parse_command("systemctl status apache2")
        
        assert result.executable == "systemctl"
        assert result.affects_system
        assert result.risk_level >= CommandRisk.MEDIUM
    
    def test_parse_critical_path_command(self):
        """Test parsing of command affecting critical paths."""
        result = self.parser.parse_command("chmod 777 /etc/passwd")
        
        assert "/etc/passwd" in result.paths
        assert result.risk_level >= CommandRisk.HIGH
        assert "Critical path: /etc/passwd" in result.risk_reasons
    
    def test_parse_empty_command(self):
        """Test parsing of empty command."""
        with pytest.raises(ValueError, match="Empty command provided"):
            self.parser.parse_command("")
    
    def test_parse_invalid_syntax(self):
        """Test parsing of command with invalid syntax."""
        with pytest.raises(ValueError, match="Invalid command syntax"):
            self.parser.parse_command("ls 'unclosed quote")
    
    def test_extract_flags(self):
        """Test flag extraction from arguments."""
        flags = self.parser._extract_flags(["-la", "/home", "--verbose", "file.txt"])
        assert flags == ["-la", "--verbose"]
    
    def test_extract_paths(self):
        """Test path extraction from arguments."""
        paths = self.parser._extract_paths(["-la", "/home", "file.txt", "~/documents"])
        assert "/home" in paths
        assert "~/documents" in paths
        assert "file.txt" not in paths  # Simple filename, not a path
    
    def test_risk_assessment_safe(self):
        """Test risk assessment for safe command."""
        risk, reasons = self.parser._assess_risk("ls", ["-la"], ["-la"], ["/home"], False)
        assert risk == CommandRisk.SAFE
    
    def test_risk_assessment_critical(self):
        """Test risk assessment for critical command."""
        risk, reasons = self.parser._assess_risk(
            "rm", ["-rf", "/"], ["-rf"], ["/"], True
        )
        assert risk == CommandRisk.CRITICAL
        assert len(reasons) >= 3  # Multiple risk factors
    
    def test_validate_command_safety_safe(self):
        """Test safety validation for safe command."""
        parsed = self.parser.parse_command("df -h")
        validation = self.parser.validate_command_safety(parsed)
        
        assert validation['safe_to_execute']
        assert not validation['requires_confirmation']
        assert not validation['requires_dry_run']
    
    def test_validate_command_safety_destructive(self):
        """Test safety validation for destructive command."""
        parsed = self.parser.parse_command("rm -rf /tmp/test")
        validation = self.parser.validate_command_safety(parsed)
        
        assert validation['requires_confirmation']
        assert validation['requires_dry_run']
        assert len(validation['warnings']) > 0


class TestSafetyChecker:
    """Test cases for SafetyChecker class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.checker = create_safety_checker()
    
    def test_check_safe_command(self):
        """Test safety check for safe command."""
        result = self.checker.check_command_safety("ls -la /home")
        
        assert result['is_safe']
        assert result['recommendation'] == 'safe'
        assert len(result['violations']) == 0
    
    def test_check_blacklisted_command(self):
        """Test safety check for blacklisted command."""
        result = self.checker.check_command_safety("rm -rf /")
        
        assert not result['is_safe']
        assert result['recommendation'] == 'blocked'
        assert len(result['violations']) > 0
    
    def test_check_whitelisted_command(self):
        """Test safety check for whitelisted command."""
        result = self.checker.check_command_safety("df -h")
        
        assert result['is_safe']
        assert result['recommendation'] == 'safe'
        assert len(result['matched_rules']) > 0
    
    def test_check_unknown_command(self):
        """Test safety check for unknown command."""
        result = self.checker.check_command_safety("unknown_command --flag")
        
        assert result['recommendation'] == 'review'
        assert 'Command not in whitelist' in str(result['warnings'])
    
    def test_validate_command_structure_valid(self):
        """Test command structure validation for valid command."""
        validation = self.checker.validate_command_structure("ls -la /home")
        
        assert validation['is_valid']
        assert len(validation['syntax_errors']) == 0
    
    def test_validate_command_structure_empty(self):
        """Test command structure validation for empty command."""
        validation = self.checker.validate_command_structure("")
        
        assert not validation['is_valid']
        assert 'Empty command' in validation['syntax_errors']
    
    def test_validate_command_structure_dangerous_operators(self):
        """Test command structure validation for dangerous operators."""
        validation = self.checker.validate_command_structure("ls && rm -rf /")
        
        assert validation['is_valid']  # Structurally valid but dangerous
        assert len(validation['structure_warnings']) > 0
        assert any('&&' in warning for warning in validation['structure_warnings'])
    
    def test_get_safety_recommendations_backup(self):
        """Test safety recommendations for commands needing backup."""
        recommendations = self.checker.get_safety_recommendations("rm important_file.txt")
        
        assert any('backup' in rec.lower() for rec in recommendations)
    
    def test_get_safety_recommendations_dry_run(self):
        """Test safety recommendations for commands needing dry run."""
        recommendations = self.checker.get_safety_recommendations("rm -rf /tmp/cache")
        
        assert any('dry-run' in rec.lower() for rec in recommendations)
    
    def test_get_safety_recommendations_sudo(self):
        """Test safety recommendations for commands needing sudo."""
        recommendations = self.checker.get_safety_recommendations("cp file.txt /etc/")
        
        assert any('sudo' in rec.lower() for rec in recommendations)
    
    def test_add_custom_rule(self):
        """Test adding custom safety rule."""
        initial_count = len(self.checker.safety_rules)
        
        self.checker.add_custom_rule(
            pattern=r'custom_command.*',
            rule_type='blacklist',
            description='Custom test rule',
            severity='medium'
        )
        
        assert len(self.checker.safety_rules) == initial_count + 1
        
        # Test the custom rule
        result = self.checker.check_command_safety("custom_command --test")
        assert len(result['violations']) > 0


class TestIntegration:
    """Integration tests for Module D components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = create_command_parser()
        self.checker = create_safety_checker()
    
    def test_full_command_analysis_safe(self):
        """Test full command analysis workflow for safe command."""
        command = "df -h /home"
        
        # Parse command
        parsed = self.parser.parse_command(command)
        assert parsed.risk_level == CommandRisk.SAFE
        
        # Check safety
        safety = self.checker.check_command_safety(command)
        assert safety['is_safe']
        
        # Validate structure
        structure = self.checker.validate_command_structure(command)
        assert structure['is_valid']
        
        # Get recommendations
        recommendations = self.checker.get_safety_recommendations(command)
        # Safe commands may have no specific recommendations
    
    def test_full_command_analysis_dangerous(self):
        """Test full command analysis workflow for dangerous command."""
        command = "sudo rm -rf /tmp/important_data"
        
        # Parse command
        parsed = self.parser.parse_command(command)
        assert parsed.risk_level >= CommandRisk.HIGH
        assert parsed.is_destructive
        assert parsed.requires_sudo
        
        # Check safety
        safety = self.checker.check_command_safety(command)
        # May or may not be blocked depending on specific patterns
        
        # Validate structure
        structure = self.checker.validate_command_structure(command)
        assert structure['is_valid']
        
        # Get recommendations
        recommendations = self.checker.get_safety_recommendations(command)
        assert len(recommendations) > 0
        assert any('backup' in rec.lower() for rec in recommendations)
    
    def test_command_validation_workflow(self):
        """Test complete command validation workflow."""
        commands = [
            "ls -la",  # Safe
            "df -h",   # Safe
            "rm -rf /tmp/test",  # Risky
            "sudo systemctl restart nginx",  # System command
            "chmod 777 /etc/passwd"  # Critical
        ]
        
        for command in commands:
            # Should not raise exceptions
            parsed = self.parser.parse_command(command)
            safety = self.checker.check_command_safety(command)
            validation = self.parser.validate_command_safety(parsed)
            
            # All should return valid structures
            assert isinstance(parsed, ParsedCommand)
            assert isinstance(safety, dict)
            assert isinstance(validation, dict)
            
            # Risk assessment should be consistent
            if parsed.risk_level == CommandRisk.SAFE:
                assert validation['safe_to_execute'] or not validation['requires_confirmation']