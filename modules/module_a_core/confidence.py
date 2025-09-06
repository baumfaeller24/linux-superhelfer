"""
Confidence scoring for AI responses.
Implements heuristic-based confidence calculation for response quality assessment.
"""

import re
import logging
from typing import Dict, List


logger = logging.getLogger(__name__)


class ConfidenceCalculator:
    """Calculates confidence scores for AI responses using multiple heuristics."""
    
    def __init__(self):
        # Uncertainty indicators that lower confidence
        self.uncertainty_keywords = [
            'maybe', 'perhaps', 'possibly', 'might', 'could be', 'not sure',
            'i think', 'i believe', 'probably', 'likely', 'uncertain',
            'unclear', 'depends', 'varies', 'sometimes', 'may be'
        ]
        
        # Confidence indicators that raise confidence
        self.confidence_keywords = [
            'definitely', 'certainly', 'always', 'never', 'exactly',
            'precisely', 'specifically', 'clearly', 'obviously'
        ]
        
        # Minimum and maximum response lengths for optimal confidence
        self.min_optimal_length = 50
        self.max_optimal_length = 500
        
    def calculate_confidence(self, response: str, query: str = "", 
                           processing_time: float = 0.0, 
                           metadata: Dict = None) -> float:
        """
        Calculate confidence score based on multiple factors.
        
        Args:
            response: Generated response text
            query: Original query (for relevance checking)
            processing_time: Time taken to generate response
            metadata: Additional metadata from model
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not response or not response.strip():
            return 0.0
            
        scores = []
        
        # Length-based confidence
        length_score = self._calculate_length_score(response)
        scores.append(('length', length_score, 0.3))
        
        # Uncertainty keyword analysis
        uncertainty_score = self._calculate_uncertainty_score(response)
        scores.append(('uncertainty', uncertainty_score, 0.25))
        
        # Structure and completeness
        structure_score = self._calculate_structure_score(response)
        scores.append(('structure', structure_score, 0.2))
        
        # Specificity and detail level
        specificity_score = self._calculate_specificity_score(response)
        scores.append(('specificity', specificity_score, 0.15))
        
        # Processing time factor (faster might indicate cached/simple responses)
        time_score = self._calculate_time_score(processing_time)
        scores.append(('time', time_score, 0.1))
        
        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in scores)
        
        # Apply metadata adjustments if available
        if metadata:
            total_score = self._apply_metadata_adjustments(total_score, metadata)
        
        # Ensure score is within bounds
        confidence = max(0.0, min(1.0, total_score))
        
        logger.debug(f"Confidence calculation: {scores} -> {confidence:.3f}")
        
        return confidence
    
    def _calculate_length_score(self, response: str) -> float:
        """Score based on response length (too short or too long reduces confidence)."""
        length = len(response.strip())
        
        if length < 10:
            return 0.1  # Very short responses are likely incomplete
        elif length < self.min_optimal_length:
            return 0.4 + (length / self.min_optimal_length) * 0.4
        elif length <= self.max_optimal_length:
            return 0.8 + 0.2 * (1 - abs(length - 200) / 300)  # Peak around 200 chars
        else:
            # Gradually decrease for very long responses
            excess = length - self.max_optimal_length
            penalty = min(0.3, excess / 1000)
            return max(0.5, 0.8 - penalty)
    
    def _calculate_uncertainty_score(self, response: str) -> float:
        """Score based on uncertainty indicators in the response."""
        response_lower = response.lower()
        
        uncertainty_count = sum(1 for keyword in self.uncertainty_keywords 
                              if keyword in response_lower)
        confidence_count = sum(1 for keyword in self.confidence_keywords 
                             if keyword in response_lower)
        
        # Base score
        score = 0.7
        
        # Penalize uncertainty indicators
        uncertainty_penalty = min(0.4, uncertainty_count * 0.1)
        score -= uncertainty_penalty
        
        # Reward confidence indicators (but not too much)
        confidence_bonus = min(0.2, confidence_count * 0.05)
        score += confidence_bonus
        
        return max(0.0, min(1.0, score))
    
    def _calculate_structure_score(self, response: str) -> float:
        """Score based on response structure and completeness."""
        score = 0.5  # Base score
        
        # Check for proper sentence structure
        sentences = re.split(r'[.!?]+', response)
        valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        if len(valid_sentences) >= 2:
            score += 0.2
        
        # Check for code blocks or commands (good for Linux admin responses)
        if '`' in response or response.count('\n') > 2:
            score += 0.1
        
        # Check for lists or structured information
        if any(marker in response for marker in ['1.', '2.', '-', '*', ':']):
            score += 0.1
        
        # Penalize responses that seem cut off
        if response.endswith(('...', 'etc', 'and so on')):
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _calculate_specificity_score(self, response: str) -> float:
        """Score based on specificity and technical detail."""
        score = 0.5
        
        # Look for specific Linux commands, paths, or technical terms
        technical_patterns = [
            r'/[a-zA-Z0-9/_-]+',  # File paths
            r'sudo\s+\w+',        # Sudo commands
            r'\w+\s+-[a-zA-Z]+',  # Commands with flags
            r'systemctl\s+\w+',   # Systemctl commands
            r'chmod\s+\d+',       # Permission commands
        ]
        
        technical_matches = sum(1 for pattern in technical_patterns 
                              if re.search(pattern, response))
        
        # Reward technical specificity
        specificity_bonus = min(0.3, technical_matches * 0.1)
        score += specificity_bonus
        
        # Check for vague language
        vague_terms = ['something', 'things', 'stuff', 'various', 'some']
        vague_count = sum(1 for term in vague_terms if term in response.lower())
        vague_penalty = min(0.2, vague_count * 0.05)
        score -= vague_penalty
        
        return max(0.0, min(1.0, score))
    
    def _calculate_time_score(self, processing_time: float) -> float:
        """Score based on processing time (very fast or very slow might indicate issues)."""
        if processing_time <= 0:
            return 0.7  # No timing info available
        
        # Optimal range: 1-10 seconds
        if 1.0 <= processing_time <= 10.0:
            return 0.8
        elif processing_time < 1.0:
            # Very fast might indicate cached or simple response
            return 0.6
        elif processing_time <= 30.0:
            # Slower but acceptable
            return 0.7 - (processing_time - 10.0) / 100.0
        else:
            # Very slow processing
            return 0.4
    
    def _apply_metadata_adjustments(self, base_score: float, metadata: Dict) -> float:
        """Apply adjustments based on model metadata."""
        adjusted_score = base_score
        
        # Token count adjustments
        response_tokens = metadata.get('response_tokens', 0)
        if response_tokens > 0:
            if response_tokens < 10:
                adjusted_score *= 0.8  # Very short generation
            elif response_tokens > 800:
                adjusted_score *= 0.9  # Very long generation
        
        return adjusted_score
    
    def should_escalate(self, confidence: float, threshold: float = 0.5) -> bool:
        """Determine if response should be escalated to external services."""
        return confidence < threshold