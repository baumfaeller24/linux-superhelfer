"""
Confidence Evaluator for Module E: Hybrid Intelligence Gateway
Evaluates confidence scores and triggers escalation to external APIs.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ConfidenceThresholds:
    """Configuration for confidence thresholds."""
    escalation_threshold: float = 0.5
    high_confidence: float = 0.8
    medium_confidence: float = 0.6
    low_confidence: float = 0.3


@dataclass
class EscalationDecision:
    """Decision result for escalation."""
    should_escalate: bool
    reason: str
    confidence_score: float
    threshold_used: float
    escalation_priority: str  # 'low', 'medium', 'high'


class ConfidenceEvaluator:
    """
    Evaluates confidence scores from Module A and decides on escalation.
    
    Provides intelligent escalation logic based on confidence scores,
    query complexity, and system context.
    """
    
    def __init__(self, thresholds: Optional[ConfidenceThresholds] = None):
        """
        Initialize confidence evaluator.
        
        Args:
            thresholds: Custom confidence thresholds
        """
        self.thresholds = thresholds or ConfidenceThresholds()
        
        # Escalation statistics
        self.escalation_stats = {
            "total_evaluations": 0,
            "escalations_triggered": 0,
            "escalation_success_rate": 0.0,
            "last_escalation": None
        }
    
    def evaluate_confidence(self, 
                          confidence_score: float,
                          query: str,
                          context: Optional[str] = None,
                          response: Optional[str] = None) -> EscalationDecision:
        """
        Evaluate confidence score and decide on escalation.
        
        Args:
            confidence_score: Confidence score from Module A (0.0-1.0)
            query: Original user query
            context: Optional context information
            response: Optional response from Module A
            
        Returns:
            EscalationDecision with escalation recommendation
        """
        self.escalation_stats["total_evaluations"] += 1
        
        # Basic threshold check
        if confidence_score >= self.thresholds.escalation_threshold:
            return EscalationDecision(
                should_escalate=False,
                reason=f"Confidence score {confidence_score:.3f} above threshold {self.thresholds.escalation_threshold}",
                confidence_score=confidence_score,
                threshold_used=self.thresholds.escalation_threshold,
                escalation_priority="none"
            )
        
        # Analyze query complexity for escalation priority
        escalation_priority = self._analyze_query_complexity(query, context)
        
        # Check for specific escalation triggers
        escalation_triggers = self._check_escalation_triggers(query, response, confidence_score)
        
        # Determine escalation reason
        reasons = [f"Low confidence score: {confidence_score:.3f} < {self.thresholds.escalation_threshold}"]
        reasons.extend(escalation_triggers)
        
        escalation_reason = "; ".join(reasons)
        
        # Update statistics
        self.escalation_stats["escalations_triggered"] += 1
        self.escalation_stats["last_escalation"] = datetime.now().isoformat()
        
        logger.info(f"Escalation triggered: {escalation_reason}")
        
        return EscalationDecision(
            should_escalate=True,
            reason=escalation_reason,
            confidence_score=confidence_score,
            threshold_used=self.thresholds.escalation_threshold,
            escalation_priority=escalation_priority
        )
    
    def _analyze_query_complexity(self, query: str, context: Optional[str] = None) -> str:
        """
        Analyze query complexity to determine escalation priority.
        
        Args:
            query: User query
            context: Optional context
            
        Returns:
            Priority level: 'low', 'medium', 'high'
        """
        query_lower = query.lower()
        
        # High priority indicators
        high_priority_keywords = [
            'critical', 'urgent', 'emergency', 'production', 'outage',
            'security', 'breach', 'attack', 'vulnerability', 'exploit',
            'data loss', 'corruption', 'failure', 'crash', 'down'
        ]
        
        # Medium priority indicators  
        medium_priority_keywords = [
            'performance', 'slow', 'optimization', 'tuning', 'monitoring',
            'backup', 'restore', 'migration', 'upgrade', 'configuration',
            'troubleshoot', 'debug', 'error', 'warning', 'issue'
        ]
        
        # Low priority indicators
        low_priority_keywords = [
            'how to', 'tutorial', 'guide', 'example', 'documentation',
            'best practice', 'recommendation', 'suggestion', 'tip',
            'learn', 'understand', 'explain', 'what is', 'difference'
        ]
        
        # Check for high priority
        if any(keyword in query_lower for keyword in high_priority_keywords):
            return "high"
        
        # Check for medium priority
        if any(keyword in query_lower for keyword in medium_priority_keywords):
            return "medium"
        
        # Check for low priority
        if any(keyword in query_lower for keyword in low_priority_keywords):
            return "low"
        
        # Complex technical queries (multiple technical terms)
        technical_terms = [
            'systemctl', 'journalctl', 'iptables', 'nginx', 'apache', 'mysql',
            'postgresql', 'docker', 'kubernetes', 'ansible', 'terraform',
            'ssh', 'ssl', 'tls', 'certificate', 'firewall', 'selinux'
        ]
        
        technical_count = sum(1 for term in technical_terms if term in query_lower)
        
        if technical_count >= 3:
            return "medium"
        elif technical_count >= 1:
            return "low"
        
        # Default to medium for unclear queries
        return "medium"
    
    def _check_escalation_triggers(self, 
                                 query: str, 
                                 response: Optional[str], 
                                 confidence_score: float) -> List[str]:
        """
        Check for specific conditions that should trigger escalation.
        
        Args:
            query: User query
            response: Response from Module A
            confidence_score: Confidence score
            
        Returns:
            List of escalation trigger reasons
        """
        triggers = []
        
        # Very low confidence
        if confidence_score < self.thresholds.low_confidence:
            triggers.append(f"Very low confidence: {confidence_score:.3f}")
        
        # Response quality indicators
        if response:
            response_lower = response.lower()
            
            # Uncertainty indicators in response
            uncertainty_phrases = [
                "i'm not sure", "i don't know", "unclear", "uncertain",
                "might be", "possibly", "maybe", "not certain"
            ]
            
            if any(phrase in response_lower for phrase in uncertainty_phrases):
                triggers.append("Response contains uncertainty indicators")
            
            # Very short response (likely incomplete)
            if len(response.strip()) < 50:
                triggers.append("Response too short (likely incomplete)")
            
            # Generic/template response indicators
            generic_phrases = [
                "please provide more information", "need more details",
                "could you clarify", "more specific", "additional context"
            ]
            
            if any(phrase in response_lower for phrase in generic_phrases):
                triggers.append("Response appears generic/incomplete")
        
        # Query complexity vs confidence mismatch
        query_length = len(query.split())
        if query_length > 20 and confidence_score < self.thresholds.medium_confidence:
            triggers.append("Complex query with low confidence")
        
        # Technical query without technical response
        if response and self._is_technical_query(query) and not self._is_technical_response(response):
            triggers.append("Technical query without technical response")
        
        return triggers
    
    def _is_technical_query(self, query: str) -> bool:
        """Check if query contains technical Linux terms."""
        technical_indicators = [
            'command', 'script', 'config', 'log', 'service', 'process',
            'file', 'directory', 'permission', 'user', 'group', 'network',
            'port', 'protocol', 'server', 'daemon', 'kernel', 'module'
        ]
        
        query_lower = query.lower()
        return sum(1 for term in technical_indicators if term in query_lower) >= 2
    
    def _is_technical_response(self, response: str) -> bool:
        """Check if response contains technical content."""
        technical_indicators = [
            'sudo', 'systemctl', 'journalctl', 'grep', 'awk', 'sed',
            '/etc/', '/var/', '/usr/', 'chmod', 'chown', 'ps aux',
            'df -h', 'free -h', 'netstat', 'ss', 'iptables'
        ]
        
        response_lower = response.lower()
        return sum(1 for term in technical_indicators if term in response_lower) >= 1
    
    def update_escalation_success(self, success: bool):
        """
        Update escalation success statistics.
        
        Args:
            success: Whether the escalation was successful
        """
        if self.escalation_stats["escalations_triggered"] > 0:
            # Simple running average for now
            current_rate = self.escalation_stats["escalation_success_rate"]
            total_escalations = self.escalation_stats["escalations_triggered"]
            
            if success:
                new_rate = (current_rate * (total_escalations - 1) + 1.0) / total_escalations
            else:
                new_rate = (current_rate * (total_escalations - 1)) / total_escalations
            
            self.escalation_stats["escalation_success_rate"] = new_rate
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get escalation statistics.
        
        Returns:
            Dictionary with escalation statistics
        """
        stats = dict(self.escalation_stats)
        
        # Calculate escalation rate
        if stats["total_evaluations"] > 0:
            stats["escalation_rate"] = stats["escalations_triggered"] / stats["total_evaluations"]
        else:
            stats["escalation_rate"] = 0.0
        
        # Add threshold information
        stats["thresholds"] = {
            "escalation_threshold": self.thresholds.escalation_threshold,
            "high_confidence": self.thresholds.high_confidence,
            "medium_confidence": self.thresholds.medium_confidence,
            "low_confidence": self.thresholds.low_confidence
        }
        
        return stats
    
    def adjust_thresholds(self, 
                         escalation_threshold: Optional[float] = None,
                         high_confidence: Optional[float] = None,
                         medium_confidence: Optional[float] = None,
                         low_confidence: Optional[float] = None):
        """
        Adjust confidence thresholds dynamically.
        
        Args:
            escalation_threshold: New escalation threshold
            high_confidence: New high confidence threshold
            medium_confidence: New medium confidence threshold
            low_confidence: New low confidence threshold
        """
        if escalation_threshold is not None:
            self.thresholds.escalation_threshold = max(0.0, min(1.0, escalation_threshold))
        
        if high_confidence is not None:
            self.thresholds.high_confidence = max(0.0, min(1.0, high_confidence))
        
        if medium_confidence is not None:
            self.thresholds.medium_confidence = max(0.0, min(1.0, medium_confidence))
        
        if low_confidence is not None:
            self.thresholds.low_confidence = max(0.0, min(1.0, low_confidence))
        
        logger.info(f"Updated confidence thresholds: {self.thresholds}")


# Global evaluator instance
confidence_evaluator = ConfidenceEvaluator()


def evaluate_confidence(confidence_score: float, 
                       query: str,
                       context: Optional[str] = None,
                       response: Optional[str] = None) -> EscalationDecision:
    """Convenience function for confidence evaluation."""
    return confidence_evaluator.evaluate_confidence(confidence_score, query, context, response)