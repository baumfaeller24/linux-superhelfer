"""
Query Rewriter for RAG Knowledge Vault - Grok's Implementation.
Improves search queries through expansion, normalization, and context injection.
"""

import logging
import re
import time
from typing import List, Dict, Any, Optional, Set
import asyncio

logger = logging.getLogger(__name__)


class QueryRewriter:
    """Rewrites and enhances queries for better search results."""
    
    def __init__(self):
        """Initialize query rewriter with expansion dictionaries."""
        
        # Linux command synonyms and expansions
        self.linux_expansions = {
            "ls": ["list", "directory", "files", "listing"],
            "ps": ["process", "processes", "running", "tasks"],
            "df": ["disk", "space", "filesystem", "usage"],
            "du": ["disk", "usage", "directory", "size"],
            "chmod": ["permissions", "file", "access", "rights"],
            "chown": ["owner", "ownership", "file", "user"],
            "grep": ["search", "pattern", "text", "find"],
            "find": ["search", "locate", "files", "directories"],
            "tar": ["archive", "compress", "extract", "backup"],
            "ssh": ["remote", "connection", "secure", "login"],
            "systemctl": ["service", "daemon", "system", "control"],
            "docker": ["container", "containerization", "virtualization"],
            "git": ["version", "control", "repository", "source"]
        }
        
        # Technical concept expansions
        self.concept_expansions = {
            "performance": ["optimization", "speed", "efficiency", "tuning"],
            "security": ["hardening", "protection", "vulnerability", "access"],
            "network": ["networking", "connection", "protocol", "communication"],
            "memory": ["ram", "allocation", "usage", "management"],
            "cpu": ["processor", "computation", "load", "utilization"],
            "storage": ["disk", "filesystem", "data", "persistence"],
            "backup": ["restore", "recovery", "archive", "snapshot"],
            "monitoring": ["logging", "metrics", "observability", "tracking"]
        }
        
        # Mathematical/optimization terms
        self.math_expansions = {
            "optimal": ["best", "efficient", "maximum", "minimum", "optimized"],
            "algorithm": ["method", "approach", "technique", "procedure"],
            "calculate": ["compute", "determine", "evaluate", "measure"],
            "analyze": ["examine", "investigate", "study", "assess"],
            "optimize": ["improve", "enhance", "tune", "maximize"],
            "fibonacci": ["sequence", "series", "recursive", "mathematical"],
            "equation": ["formula", "calculation", "mathematical", "solve"]
        }
        
        # Common German-English mappings
        self.german_english = {
            "befehl": "command",
            "datei": "file",
            "ordner": "directory",
            "prozess": "process",
            "speicher": "memory",
            "festplatte": "disk",
            "netzwerk": "network",
            "sicherheit": "security",
            "leistung": "performance",
            "optimierung": "optimization",
            "berechnung": "calculation",
            "algorithmus": "algorithm"
        }
    
    async def rewrite_query(self, query: str, context: Optional[str] = None, expand_terms: bool = True) -> Dict[str, Any]:
        """
        Rewrite and enhance a query for better search results.
        
        Args:
            query: Original query
            context: Optional context to consider
            expand_terms: Whether to expand technical terms
            
        Returns:
            Dictionary with rewritten queries and metadata
        """
        try:
            start_time = time.time()
            
            # Normalize the query
            normalized_query = self._normalize_query(query)
            
            # Generate query variations
            variations = []
            
            # 1. Original normalized query
            variations.append({
                "query": normalized_query,
                "type": "normalized",
                "weight": 1.0
            })
            
            # 2. Expanded query (if enabled)
            if expand_terms:
                expanded_query = self._expand_terms(normalized_query)
                if expanded_query != normalized_query:
                    variations.append({
                        "query": expanded_query,
                        "type": "expanded",
                        "weight": 0.8
                    })
            
            # 3. Context-enhanced query
            if context:
                context_query = self._add_context(normalized_query, context)
                variations.append({
                    "query": context_query,
                    "type": "context_enhanced",
                    "weight": 0.9
                })
            
            # 4. Synonym variations
            synonym_queries = self._generate_synonyms(normalized_query)
            for syn_query in synonym_queries[:2]:  # Limit to 2 synonym variations
                variations.append({
                    "query": syn_query,
                    "type": "synonym",
                    "weight": 0.7
                })
            
            # 5. Mathematical query enhancement (if applicable)
            if self._is_mathematical_query(query):
                math_query = self._enhance_mathematical_query(normalized_query)
                if math_query != normalized_query:
                    variations.append({
                        "query": math_query,
                        "type": "mathematical",
                        "weight": 1.1  # Higher weight for math queries
                    })
            
            rewrite_time = time.time() - start_time
            
            result = {
                "original_query": query,
                "primary_query": variations[0]["query"] if variations else query,
                "variations": variations,
                "rewrite_time": rewrite_time,
                "metadata": {
                    "is_mathematical": self._is_mathematical_query(query),
                    "detected_commands": self._detect_linux_commands(query),
                    "complexity_indicators": self._detect_complexity_indicators(query)
                }
            }
            
            logger.debug(f"Query rewritten: '{query}' → {len(variations)} variations in {rewrite_time:.3f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Query rewriting failed for '{query}': {e}")
            return {
                "original_query": query,
                "primary_query": query,
                "variations": [{"query": query, "type": "original", "weight": 1.0}],
                "rewrite_time": 0,
                "error": str(e)
            }
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query text."""
        # Convert to lowercase
        normalized = query.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove common punctuation that doesn't add meaning
        normalized = re.sub(r'[?!.]+$', '', normalized)
        
        # Normalize German umlauts and special characters
        replacements = {
            'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e'
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        return normalized
    
    def _expand_terms(self, query: str) -> str:
        """Expand technical terms in the query."""
        expanded_terms = []
        words = query.split()
        
        for word in words:
            expanded_terms.append(word)
            
            # Check all expansion dictionaries
            for expansion_dict in [self.linux_expansions, self.concept_expansions, 
                                 self.math_expansions, self.german_english]:
                if word in expansion_dict:
                    # Add the first expansion term
                    expanded_terms.append(expansion_dict[word][0])
                    break
        
        return ' '.join(expanded_terms)
    
    def _add_context(self, query: str, context: str) -> str:
        """Add context to the query."""
        # Simple context addition - can be made more sophisticated
        context_normalized = self._normalize_query(context)
        
        # Extract key terms from context (avoid common words)
        context_words = context_normalized.split()
        key_context_words = [w for w in context_words 
                           if len(w) > 3 and w not in ['the', 'and', 'for', 'with', 'this', 'that']]
        
        # Add up to 3 key context words
        if key_context_words:
            context_addition = ' '.join(key_context_words[:3])
            return f"{query} {context_addition}"
        
        return query
    
    def _generate_synonyms(self, query: str) -> List[str]:
        """Generate synonym variations of the query."""
        synonyms = []
        
        # Simple synonym replacement
        synonym_map = {
            "show": "display",
            "list": "enumerate",
            "find": "locate",
            "create": "generate",
            "make": "build",
            "run": "execute",
            "start": "launch",
            "stop": "terminate",
            "check": "verify",
            "test": "validate"
        }
        
        words = query.split()
        for old_word, new_word in synonym_map.items():
            if old_word in words:
                synonym_query = query.replace(old_word, new_word)
                if synonym_query != query:
                    synonyms.append(synonym_query)
        
        return synonyms
    
    def _is_mathematical_query(self, query: str) -> bool:
        """Check if query is mathematical/optimization related."""
        math_indicators = [
            'optimal', 'optimize', 'calculate', 'compute', 'algorithm',
            'fibonacci', 'equation', 'mathematical', 'bestimme', 'berechne',
            'optimiere', 'löse', 'mathematisch', 'algorithmus'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in math_indicators)
    
    def _enhance_mathematical_query(self, query: str) -> str:
        """Enhance mathematical queries with relevant terms."""
        math_enhancements = [
            "algorithm", "optimization", "calculation", "mathematical",
            "efficient", "performance", "analysis"
        ]
        
        # Add mathematical context terms
        enhanced_terms = []
        if 'optimal' in query or 'optimize' in query:
            enhanced_terms.extend(['efficient', 'performance', 'best'])
        if 'calculate' in query or 'compute' in query:
            enhanced_terms.extend(['algorithm', 'mathematical', 'analysis'])
        if 'fibonacci' in query:
            enhanced_terms.extend(['sequence', 'recursive', 'mathematical'])
        
        if enhanced_terms:
            # Add up to 2 enhancement terms
            enhancement = ' '.join(enhanced_terms[:2])
            return f"{query} {enhancement}"
        
        return query
    
    def _detect_linux_commands(self, query: str) -> List[str]:
        """Detect Linux commands mentioned in the query."""
        commands = []
        query_lower = query.lower()
        
        for command in self.linux_expansions.keys():
            if command in query_lower:
                commands.append(command)
        
        return commands
    
    def _detect_complexity_indicators(self, query: str) -> List[str]:
        """Detect complexity indicators in the query."""
        complexity_patterns = [
            'step by step', 'detailed', 'explain', 'how to', 'tutorial',
            'guide', 'walkthrough', 'comprehensive', 'complete',
            'schritt für schritt', 'detailliert', 'erkläre', 'anleitung'
        ]
        
        indicators = []
        query_lower = query.lower()
        
        for pattern in complexity_patterns:
            if pattern in query_lower:
                indicators.append(pattern)
        
        return indicators
    
    async def rewrite_batch(self, queries: List[str], context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Rewrite multiple queries in batch.
        
        Args:
            queries: List of queries to rewrite
            context: Optional context for all queries
            
        Returns:
            List of rewrite results
        """
        try:
            results = []
            
            for query in queries:
                result = await self.rewrite_query(query, context)
                results.append(result)
                
                # Small delay to avoid overwhelming the system
                await asyncio.sleep(0.01)
            
            logger.info(f"Batch rewrite completed: {len(queries)} queries")
            return results
            
        except Exception as e:
            logger.error(f"Batch query rewriting failed: {e}")
            return [{"original_query": q, "primary_query": q, "error": str(e)} for q in queries]
    
    def get_expansion_stats(self) -> Dict[str, Any]:
        """Get statistics about available expansions."""
        return {
            "linux_commands": len(self.linux_expansions),
            "technical_concepts": len(self.concept_expansions),
            "mathematical_terms": len(self.math_expansions),
            "german_english_mappings": len(self.german_english),
            "total_expansions": (len(self.linux_expansions) + len(self.concept_expansions) + 
                               len(self.math_expansions) + len(self.german_english))
        }


# Convenience function for external use
async def rewrite_query(query: str, context: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function for rewriting a single query."""
    rewriter = QueryRewriter()
    return await rewriter.rewrite_query(query, context)


if __name__ == "__main__":
    # Test the query rewriter
    async def test_rewriter():
        rewriter = QueryRewriter()
        
        test_queries = [
            "Welcher Befehl zeigt die Festplattenbelegung an?",
            "Berechne die optimale Anzahl von Worker-Threads",
            "Wie kann ich die Performance optimieren?",
            "Erstelle ein Backup-Skript mit tar"
        ]
        
        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"Original: {query}")
            
            result = await rewriter.rewrite_query(query, expand_terms=True)
            
            print(f"Primary: {result['primary_query']}")
            print(f"Variations: {len(result['variations'])}")
            
            for var in result['variations']:
                print(f"  - {var['type']}: {var['query']} (weight: {var['weight']})")
            
            if result['metadata']['detected_commands']:
                print(f"Commands: {result['metadata']['detected_commands']}")
            
            print(f"Mathematical: {result['metadata']['is_mathematical']}")
    
    # Run test
    asyncio.run(test_rewriter())