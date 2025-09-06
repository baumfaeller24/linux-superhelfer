"""
Intelligent Model Router for Qwen3-Coder integration.
Routes queries to appropriate models based on complexity and content.
"""

import asyncio
import logging
import time
import re
import unicodedata
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .query_analyzer import QueryAnalyzer, QueryAnalysis
from .vram_monitor import VRAMMonitor
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Available model types."""
    FAST = "fast"
    CODE = "code" 
    HEAVY = "heavy"


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    name: str
    vram_mb: int
    timeout: int
    idle_unload_seconds: int
    description: str


@dataclass
class RoutingResult:
    """Result of model routing decision."""
    selected_model: ModelType
    model_name: str
    reasoning: str
    vram_check_passed: bool
    user_confirmed: bool
    analysis: QueryAnalysis


class ModelRouter:
    """Intelligent router for selecting appropriate AI models."""
    
    def __init__(self, ollama_host: str = "localhost", ollama_port: int = 11434):
        """
        Initialize the model router.
        
        Args:
            ollama_host: Ollama server host
            ollama_port: Ollama server port
        """
        self.query_analyzer = QueryAnalyzer()
        self.vram_monitor = VRAMMonitor(warning_threshold=0.8)
        
        # Model configurations
        self.models = {
            ModelType.FAST: ModelConfig(
                name="llama3.2:3b",
                vram_mb=2000,  # ~2GB
                timeout=30,
                idle_unload_seconds=0,  # Keep loaded
                description="Fast general-purpose model"
            ),
            ModelType.CODE: ModelConfig(
                name="qwen3-coder-30b-local", 
                vram_mb=18000,  # ~18GB (actual size from metadata)
                timeout=30,  # Reduced timeout per Grok's recommendation
                idle_unload_seconds=600,  # 10 minutes
                description="Specialized code and Linux model (Qwen3-Coder 30B)"
            ),
            ModelType.HEAVY: ModelConfig(
                name="llama3.1:70b",
                vram_mb=42000,  # ~42GB
                timeout=300,  # 5 minutes for complex math problems
                idle_unload_seconds=300,  # 5 minutes
                description="Heavy model for extreme complexity"
            )
        }
        
        # Ollama clients for each model
        self.ollama_clients = {}
        for model_type, config in self.models.items():
            self.ollama_clients[model_type] = OllamaClient(
                host=ollama_host,
                port=ollama_port,
                model=config.name
            )
        
        # Current active model
        self.current_model = ModelType.FAST
        self.last_activity = {}
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_idle_models())
    
    async def route_query(
        self, 
        query: str, 
        force_model: Optional[ModelType] = None,
        skip_vram_check: bool = False
    ) -> RoutingResult:
        """
        Route a query to the appropriate model.
        
        Args:
            query: The user query to process
            force_model: Force a specific model (optional)
            skip_vram_check: Skip VRAM checking (for testing)
            
        Returns:
            RoutingResult with routing decision and metadata
        """
        # Analyze the query
        analysis = self.query_analyzer.analyze_query(query)
        
        # Determine target model
        if force_model:
            target_model = force_model
            reasoning = f"Forced to {force_model.value} model"
        else:
            target_model = self._select_model_from_analysis(analysis)
            reasoning = f"Selected {target_model.value} model: {analysis.reasoning}"
        
        # Check VRAM if switching to a more demanding model
        vram_check_passed = True
        user_confirmed = True
        
        if not skip_vram_check and self._needs_vram_check(target_model):
            config = self.models[target_model]
            vram_check_passed = self.vram_monitor.check_before_model_switch(
                target_model=config.name,
                estimated_vram_mb=config.vram_mb,
                show_gui=True
            )
            user_confirmed = vram_check_passed
            
            if not vram_check_passed:
                # Fall back to current model or fast model
                target_model = self.current_model if self.current_model != target_model else ModelType.FAST
                reasoning += f" -> Fallback to {target_model.value} (VRAM check failed)"
        
        # Update current model and activity tracking
        self.current_model = target_model
        self.last_activity[target_model] = time.time()
        
        # Log the routing decision
        logger.info(f"Query routed to {target_model.value} model: {reasoning}")
        
        return RoutingResult(
            selected_model=target_model,
            model_name=self.models[target_model].name,
            reasoning=reasoning,
            vram_check_passed=vram_check_passed,
            user_confirmed=user_confirmed,
            analysis=analysis
        )
    
    def _select_model_from_analysis(self, analysis: QueryAnalysis) -> ModelType:
        """
        Intelligent hybrid routing using ChatGPT's logic with QueryAnalyzer results.
        Interprets QueryAnalyzer output more intelligently based on 96k test results.
        """
        import re
        import unicodedata
        
        # Get the original query for pattern matching
        query = getattr(analysis, 'original_query', '')
        if not query:
            # Fallback to basic logic if no query available
            return self._basic_routing_fallback(analysis)
        
        query_lower = query.lower()
        qn = self._normalize_text(query)
        
        # === PRIORITY 1: HEAVY MODEL PATTERNS (Mathematical/Optimization) ===
        # Mathematical queries MUST go to Heavy model - HIGHEST PRIORITY
        heavy_patterns = [
            # Pure Mathematical Patterns (HIGH PRIORITY)
            r'x\s*[\+\-\*\/=<>]',                             # "x + y", "x = 5"
            r'[\+\-\*\/=<>]\s*x',                             # "+ x", "= x"
            r'x\s+[\+\-]\s+y',                               # "x + y", "x - y"
            r'gleichung\w*',                                  # "gleichung", "gleichungssystem"
            r'(löse|solve).*[xy].*=',                        # "löse x = 5"
            r'berechne.*[xy].*[=<>]',                        # "berechne x = y"
            r'ganze\s+zahlen.*[xyz]',                        # "ganze zahlen x, y, z"
            r'werte\s+haben\s+[xyz]',                        # "welche werte haben x, y"
            r'bedingung\w*.*erfüll\w*',                      # "bedingungen erfüllen"
            r'mathe\w*.*problem',                            # "mathematisches problem"
            
            # System Optimization Patterns
            r'mathematisch.*optimal',                          # "mathematisch optimal"
            r'(bestimme|berechne|finde|löse).*optimal',       # "bestimme/berechne optimal"
            r'optimierungsaufgabe',                           # "optimierungsaufgabe"
            r'fibonacci.*zahlen',                             # "fibonacci zahlen"
            r'optimal.*anzahl.*worker',                       # "optimale anzahl worker"
            r'optimal.*größe.*puffer',                        # "optimale größe puffer"
            r'memory.*allocation.*optimal',                   # "memory allocation optimal"
            r'cpu.*intensive.*optimal',                       # "cpu intensive optimal"
            r'berechne.*fibonacci.*für',                      # "berechne fibonacci für"
            r'mathematisch.*bestimm',                         # "mathematisch bestimm"
        ]
        
        for pattern in heavy_patterns:
            if re.search(pattern, query_lower):
                return ModelType.HEAVY
        
        # === PRIORITY 2: FAST MODEL PATTERNS (Basic Commands) ===
        # These should ALWAYS go to Fast model regardless of other factors
        fast_patterns = [
            r'welcher\s+befehl\s+(zeigt|macht|gibt|listet)',  # "welcher befehl zeigt/macht"
            r'was\s+macht\s+(der|das)\s+\w+\s+befehl',        # "was macht der X befehl"
            r'wie\s+kann\s+ich\s+.*\s+(anzeigen|zeigen)\s*\??', # "wie kann ich X anzeigen?"
            r'was\s+ist\s+der\s+unterschied\s+zwischen\s+\w+\s+und\s+\w+', # "unterschied zwischen X und Y"
            r'^(ls|ll|pwd|cd|df|du|ps|top|htop|free|uname)\s*\??$', # basic commands alone
        ]
        
        for pattern in fast_patterns:
            if re.search(pattern, query_lower):
                return ModelType.FAST
        
        # === PRIORITY 3: INTERMEDIATE PATTERNS (Complex Explanations) ===
        # Complex explanation requests should go to Code model
        intermediate_patterns = [
            r'erkläre\s+mir\s+(die\s+)?unterschiede?\s+zwischen', # "erkläre mir unterschiede zwischen"
            r'was\s+sind\s+(die\s+)?best\s+practices?\s+für',     # "was sind best practices für"
            r'wie\s+funktioniert\s+.*\s+(system|prozess|mechanismus)', # "wie funktioniert X system"
            r'vor.*und.*nachteile\s+von',                         # "vor und nachteile von"
            r'unterschiede?\s+zwischen.*dateisystem',              # "unterschiede zwischen dateisystemen"
            r'security.*hardening',                               # "security hardening"
            r'performance.*optimierung',                          # "performance optimierung"
        ]
        
        for pattern in intermediate_patterns:
            if re.search(pattern, query_lower):
                return ModelType.CODE
        
        # === PRIORITY 4: USE CHATGPT'S ROUTE_MODEL IF AVAILABLE ===
        # If QueryAnalyzer has ChatGPT's route_model, use it with confidence
        if hasattr(analysis, 'route_model') and analysis.route_model:
            chatgpt_model = analysis.route_model.lower()
            if chatgpt_model == 'heavy':
                return ModelType.HEAVY
            elif chatgpt_model == 'code':
                return ModelType.CODE
            elif chatgpt_model == 'fast':
                return ModelType.FAST
        
        # === PRIORITY 5: INTELLIGENT COMPLEXITY INTERPRETATION ===
        # Interpret complexity score more intelligently based on content
        
        # High complexity + mathematical content = Heavy
        if analysis.complexity_score > 0.5:
            math_indicators = ['berechne', 'löse', 'optimal', 'mathematisch', 'fibonacci', 'gleichung']
            if any(indicator in query_lower for indicator in math_indicators):
                return ModelType.HEAVY
        
        # Medium complexity + technical content = Code  
        if analysis.complexity_score > 0.3:
            tech_indicators = ['erkläre', 'unterschied', 'funktioniert', 'erstelle', 'entwickle', 'implementiere']
            if any(indicator in query_lower for indicator in tech_indicators):
                return ModelType.CODE
        
        # === PRIORITY 6: KEYWORD-BASED ROUTING ===
        # Use detected keywords more intelligently
        
        # Linux/Code keywords but simple query = might be basic command
        if analysis.needs_code_model:
            # Check if it's really a basic command despite having keywords
            simple_command_indicators = [
                len(query.split()) <= 8,  # Short queries
                any(word in query_lower for word in ['welcher', 'was macht', 'wie zeige']),
                re.search(r'befehl.*\?$', query_lower),  # ends with "befehl?"
            ]
            
            if sum(simple_command_indicators) >= 2:
                return ModelType.FAST
            else:
                return ModelType.CODE
        
        # === PRIORITY 7: FALLBACK LOGIC ===
        # Final fallback based on complexity and length
        
        if analysis.complexity_score > 0.7:
            return ModelType.HEAVY
        elif analysis.complexity_score > 0.4 or len(query.split()) > 10:
            return ModelType.CODE
        else:
            return ModelType.FAST
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for pattern matching (ChatGPT's method)."""
        text = text.casefold()
        text = unicodedata.normalize("NFKD", text)
        return "".join(c for c in text if not unicodedata.combining(c))
    
    def _basic_routing_fallback(self, analysis: QueryAnalysis) -> ModelType:
        """Fallback to basic routing if no query text available."""
        if analysis.complexity_score > 0.6:
            return ModelType.HEAVY
        elif analysis.needs_code_model:
            return ModelType.CODE
        else:
            return ModelType.FAST
    
    def _needs_vram_check(self, target_model: ModelType) -> bool:
        """Determine if VRAM check is needed for model switch."""
        current_vram = self.models[self.current_model].vram_mb
        target_vram = self.models[target_model].vram_mb
        
        # Only check if switching to a more demanding model
        return target_vram > current_vram
    
    async def generate_response(
        self, 
        query: str, 
        context: Optional[str] = None,
        force_model: Optional[ModelType] = None
    ) -> Dict[str, Any]:
        """
        Generate response using routed model.
        
        Args:
            query: The user query
            context: Optional context to include
            force_model: Force a specific model
            
        Returns:
            Dictionary with response and metadata
        """
        # Route the query
        routing_result = await self.route_query(query, force_model)
        
        if not routing_result.user_confirmed:
            return {
                'response': "Anfrage abgebrochen: VRAM-Warnung vom Benutzer bestätigt.",
                'model_used': routing_result.model_name,
                'routing_info': routing_result,
                'success': False
            }
        
        # Get the appropriate Ollama client
        client = self.ollama_clients[routing_result.selected_model]
        
        # Generate response
        try:
            result = await client.generate_response(query, context)
            result['routing_info'] = routing_result
            result['success'] = True
            
            # Log successful generation
            logger.info(f"Response generated using {routing_result.selected_model.value} model")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate response with {routing_result.selected_model.value} model: {e}")
            
            # Try fallback to fast model if not already using it
            if routing_result.selected_model != ModelType.FAST:
                logger.info("Attempting fallback to fast model")
                try:
                    fallback_client = self.ollama_clients[ModelType.FAST]
                    result = await fallback_client.generate_response(query, context)
                    result['routing_info'] = routing_result
                    result['success'] = True
                    result['fallback_used'] = True
                    return result
                except Exception as fallback_error:
                    logger.error(f"Fallback to fast model also failed: {fallback_error}")
            
            # Return error response
            return {
                'response': f"Fehler bei der Antwortgenerierung: {str(e)}",
                'model_used': routing_result.model_name,
                'routing_info': routing_result,
                'success': False,
                'error': str(e)
            }
    
    async def _cleanup_idle_models(self):
        """Background task to unload idle models."""
        while True:
            try:
                current_time = time.time()
                
                for model_type, config in self.models.items():
                    if config.idle_unload_seconds <= 0:
                        continue  # Don't unload this model
                    
                    last_used = self.last_activity.get(model_type, 0)
                    idle_time = current_time - last_used
                    
                    if idle_time > config.idle_unload_seconds:
                        # TODO: Implement model unloading via Ollama API
                        # This would require Ollama API support for model management
                        logger.debug(f"Model {config.name} idle for {idle_time:.0f}s (threshold: {config.idle_unload_seconds}s)")
                
                # Check every minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in model cleanup task: {e}")
                await asyncio.sleep(60)
    
    def get_current_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        config = self.models[self.current_model]
        vram_info = self.vram_monitor.get_vram_info()
        
        return {
            "current_model": {
                "type": self.current_model.value,
                "name": config.name,
                "description": config.description,
                "vram_mb": config.vram_mb
            },
            "vram_status": {
                "total_mb": vram_info.total_mb if vram_info else None,
                "used_mb": vram_info.used_mb if vram_info else None,
                "usage_percent": vram_info.usage_percent if vram_info else None,
                "monitoring_available": vram_info is not None
            },
            "available_models": {
                model_type.value: {
                    "name": config.name,
                    "description": config.description,
                    "vram_mb": config.vram_mb
                }
                for model_type, config in self.models.items()
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all models and routing system."""
        health_status = {
            "router_status": "ok",
            "vram_monitoring": self.vram_monitor.pynvml_available,
            "models": {}
        }
        
        for model_type, client in self.ollama_clients.items():
            try:
                available = await client.is_available()
                health_status["models"][model_type.value] = {
                    "available": available,
                    "name": self.models[model_type].name
                }
            except Exception as e:
                health_status["models"][model_type.value] = {
                    "available": False,
                    "error": str(e),
                    "name": self.models[model_type].name
                }
        
        return health_status


# Convenience functions for external use
async def route_and_generate(query: str, context: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function for routing and generating response."""
    router = ModelRouter()
    return await router.generate_response(query, context)


if __name__ == "__main__":
    # Test the model router
    async def test_router():
        router = ModelRouter()
        
        test_queries = [
            "Hallo, wie geht es dir?",
            "Zeige mir alle laufenden Prozesse mit ps aux",
            "Schreibe eine Python-Funktion zum Kopieren von Dateien",
            "Erkläre mir detailliert, wie Docker Container funktionieren und wie ich sie deploye"
        ]
        
        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            
            routing_result = await router.route_query(query, skip_vram_check=True)
            print(f"Selected model: {routing_result.selected_model.value}")
            print(f"Reasoning: {routing_result.reasoning}")
            print(f"Complexity score: {routing_result.analysis.complexity_score:.2f}")
    
    # Run test
    asyncio.run(test_router())