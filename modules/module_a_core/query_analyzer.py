"""
Query Analyzer for intelligent model routing.
Detects Linux/code-related queries and determines complexity.
"""

import re
import logging
import unicodedata
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ChatGPT's Model Constants
MODEL_HEAVY = 'heavy'
MODEL_CODE = 'code'
MODEL_FAST = 'fast'

def _normalize(s: str) -> str:
    """ChatGPT's Unicode normalization function."""
    s = s.casefold()
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))

# ChatGPT's Pattern Definitions
_MATH_VERBS = r"(bestimme|berechne|minimiere|maximiere|optimiere|finde|löse)"

_MATH_PATS = [
    # Pure Mathematical Patterns (PRIORITY)
    re.compile(r"\b(gleichung\w*|equation\w*)\b"),  # "gleichung", "gleichungssystem"
    re.compile(r"\b(x\s*\+\s*y|x\s*\-\s*y|x\s*\*\s*y|x\s*\/\s*y)\b"),  # mathematical expressions
    re.compile(r"\b(x\d*|y\d*|z\d*)\s*[=<>]\s*\d+\b"),  # variables with numbers
    re.compile(r"\b\d+\s*[=<>]\s*\d+\b"),  # number equations
    re.compile(r"\b(ganze\s+zahlen|integer\w*|natürliche\s+zahlen)\b"),  # number types
    re.compile(r"\b(bedingung\w*|condition\w*|erfüll\w*)\b"),  # conditions
    re.compile(r"\b(mathe|mathematik|mathematics|rechnen|calculation)\b"),  # math keywords
    re.compile(r"\b(werte\s+haben|values\s+are|lösung\w*|solution\w*)\b"),  # solution keywords
    
    # System Optimization Patterns
    re.compile(rf"\bmathematisch\w*\b.{{0,40}}\boptimal\w*\b"),
    re.compile(rf"\b{_MATH_VERBS}\b[^\.]{{0,80}}\b(optimal\w*|minimum|maxim\w*|argmin|argmax)\b"),
    re.compile(rf"\b(puffer(?:grö|gro)ss?e|block(?:grö|gro)ss?e)\b.{{0,40}}\b(operation\w*|i/?o)\b"),
    re.compile(rf"\b{_MATH_VERBS}\b.{{0,40}}\b(gleichung\w*|system)\b"),  # "löse gleichungssystem"
    re.compile(r"\boptimierungsaufgabe\b"),
    re.compile(r"\bfibonacci\b"),
    
    # Performance Optimization
    re.compile(r"\boptimale?\s+(anzahl|größe|batch[-\s]?größe|timeouts?|cache[-\s]?größe|connections?)\b"),
    re.compile(r"\b(worker[-\s]?threads?|connection\s+pool|batch[-\s]?size)\b.*\b(optimal\w*|anzahl|größe)\b"),
    re.compile(r"\b(berechne|bestimme).*\b(anzahl|größe|wert\w*)\b.*\b(connection\w*|pool|thread\w*|cache|puffer|buffer)\b"),
]

_TECH_PATS = [
    re.compile(r"\b(i/?o|io)[\s/\-–—]*operation\w*"),
    re.compile(r"\b(buffer|puffer|blocksize|durchsatz|throughput|syscall\w*)\b"),
]

_FAST_PATS = [
    re.compile(r'welcher\s+befehl\s+(zeigt|macht|gibt|listet)')
]

@dataclass
class QueryAnalysis:
    """Result of query analysis."""
    needs_code_model: bool
    complexity_score: float
    detected_keywords: List[str]
    token_count: int
    reasoning: str
    route_model: str = MODEL_CODE  # ChatGPT's addition
    debug_info: Dict = None  # ChatGPT's debug info
    original_query: str = ""  # Store original query for hybrid routing


class QueryAnalyzer:
    """Analyzes queries to determine appropriate model routing."""
    
    def __init__(self):
        """Initialize the query analyzer with keyword sets."""
        self.debug = {}  # ChatGPT's debug tracking
        self.linux_keywords = [
            # Basic commands
            "befehl", "command", "kommando", "cmd",
            "bash", "shell", "terminal", "konsole",
            
            # System administration
            "systemctl", "service", "daemon", "process",
            "grep", "awk", "sed", "find", "locate",
            "chmod", "chown", "chgrp", "permissions",
            "mount", "umount", "filesystem", "disk",
            "df", "du", "fdisk", "lsblk",
            
            # Process management
            "ps", "top", "htop", "kill", "killall",
            "jobs", "nohup", "screen", "tmux",
            
            # Network
            "ssh", "scp", "rsync", "wget", "curl",
            "netstat", "ss", "iptables", "firewall",
            "ping", "traceroute", "nslookup",
            
            # File operations
            "tar", "zip", "unzip", "gzip", "compress",
            "cp", "mv", "rm", "mkdir", "rmdir",
            "ln", "symlink", "hardlink",
            
            # System monitoring
            "cron", "crontab", "systemd", "init",
            "log", "journal", "dmesg", "syslog",
            "docker", "container", "kubernetes",
            
            # Package management
            "apt", "yum", "dnf", "pacman", "snap",
            "pip", "npm", "gem", "cargo",
            
            # Text processing
            "vim", "nano", "emacs", "editor",
            "cat", "less", "more", "head", "tail"
        ]
        
        self.code_keywords = [
            # Programming general
            "programmiere", "code", "coding", "entwickle",
            "function", "funktion", "method", "methode",
            "class", "klasse", "object", "objekt",
            "variable", "konstante", "array", "list",
            
            # Debugging
            "debug", "debuggen", "fehler", "error",
            "exception", "traceback", "stack trace",
            "breakpoint", "logging", "print",
            
            # Languages
            "python", "javascript", "java", "c++",
            "rust", "go", "php", "ruby", "perl",
            "html", "css", "sql", "json", "xml",
            
            # Development tools
            "git", "github", "repository", "repo",
            "commit", "push", "pull", "merge",
            "branch", "checkout", "clone",
            
            # Build systems
            "compile", "build", "make", "cmake",
            "test", "testing", "unittest", "pytest",
            "deploy", "deployment", "ci/cd",
            
            # Syntax elements
            "syntax", "import", "include", "require",
            "if", "else", "for", "while", "loop",
            "try", "catch", "finally", "return"
        ]
        
        self.complexity_indicators = [
            # Multi-step processes
            "schritt für schritt", "step by step", "anleitung",
            "tutorial", "guide", "walkthrough",
            
            # Analysis requests
            "analysiere", "analyze", "untersuche", "examine",
            "erkläre detailliert", "explain in detail",
            "vergleiche", "compare", "bewerte", "evaluate",
            
            # Problem solving
            "löse", "solve", "behebe", "fix", "repair",
            "optimiere", "optimize", "verbessere", "improve",
            "troubleshoot", "diagnose", "investigate",
            
            # Mathematical operations
            "berechne", "calculate", "rechne", "compute",
            "mathematik", "mathematics", "formel", "formula",
            "algorithmus", "algorithm", "komplexität"
        ]
    
    def _route_query_chatgpt(self, query: str, token_count: int, linux_kw: bool, code_kw: bool, complexity_score: float) -> str:
        """
        OPTIMIZED routing function with enhanced mathematical detection.
        Returns MODEL_HEAVY, MODEL_CODE, or MODEL_FAST.
        """
        q = query
        qn = _normalize(query)
        
        # Reset debug info
        self.debug = {}
        
        # 0) FAST MODEL - Basic commands (HIGHEST PRIORITY)
        for p in _FAST_PATS:
            if p.search(qn):
                self.debug['route_reason'] = 'fast_basic_command'
                return MODEL_FAST
        
        # Enhanced basic command detection
        basic_command_patterns = [
            r'welcher\s+befehl\s+(zeigt|macht|gibt|listet)',
            r'was\s+macht\s+(der|das)\s+\w+\s+befehl',
            r'welches\s+kommando\s+(zeigt|macht)',
            r'wie\s+(liste|zeige)\s+ich.*\b(dateien|ordner|prozesse)\b',
            r'^(ls|ll|pwd|cd|df|du|ps|top|htop|free|uname)(\s|$)',
            r'^(cat|less|more|head|tail|grep|find|which)(\s|$)',
        ]
        
        for pattern in basic_command_patterns:
            if re.search(pattern, qn):
                self.debug['route_reason'] = 'fast_basic_linux_command'
                return MODEL_FAST
        
        # Don't route mathematical queries to FAST just because they're short
        has_math_content = re.search(r"\b(berechne|fibonacci|gleichung|löse|mathematisch|optimal|x\s*[=+\-]|zahlen|integral|eigenwerte|matrix|polynom|faktorisiere|zeige|mod|fläche|derangements|dreieck|projektplanung|cpm|kreisgeometrie|kombinatorik|dezimalzahlen|quersumme|fourier|analyse|poisson|summationsformel|schwartz|theta|lineare|algebra|charakterisiere|diagonaliserbar|spektralsatz|transportproblem|kostenmatrix|nordwestecke|modi|codierungstheorie|generator|paritaetsmatrix)\b|[∫∑π≡∞²³⁴]", qn)
        
        if token_count < 5 and not (linux_kw or code_kw or has_math_content):
            self.debug['route_reason'] = 'fast_short'
            return MODEL_FAST
        
        # 1) PROGRAMMING DETECTION - Check for programming context BEFORE math
        programming_indicators = re.search(r"\b(implementiere|schreibe|erstelle|programmiere|python|javascript|java|c\+\+|rust|go|php|ruby|function|funktion|class|klasse|script|code|coding|entwickle)\b", qn)
        
        # Mathematical programming tasks should go to CODE model
        if programming_indicators:
            # Check if it's mathematical programming (CODE model)
            math_programming = re.search(r"\b(fibonacci|primzahl|algorithmus|parser|berechnung|mathematisch).*\b(funktion|function|script|implementiere|programmiere|code)\b", qn) or \
                              re.search(r"\b(implementiere|programmiere|schreibe).*\b(fibonacci|primzahl|algorithmus|parser|berechnung|mathematisch)\b", qn)
            
            # Check if it's pure mathematical theory (should go to HEAVY despite "zeige" or "gib")
            pure_math_theory = re.search(r"\b(fourier.*analyse|codierungstheorie|zahlentheorie|topologie|geometrie|maßtheorie|spektralgraphen|variationsrechnung).*\b(zeige|gib|beweise)\b", qn)
            
            if math_programming and not pure_math_theory:
                self.debug['route_reason'] = 'code_mathematical_programming'
                return MODEL_CODE
            
            # Don't route pure mathematical theory to CODE just because of "zeige" or "gib"
            if pure_math_theory:
                pass  # Continue to mathematical detection
            else:
                # General programming tasks
                self.debug['route_reason'] = 'code_programming_task'
                return MODEL_CODE
        
        # 2) PURE MATHEMATICAL PROBLEMS - Only for non-programming math
        math_indicators = re.search(r"\b(bestimme|berechne|minimiere|maximiere|optimiere|finde|löse|mathematisch|optimal|fibonacci|gleichung|mathe|rechnen|werte\s+haben|ganze\s+zahlen|zeige|integral|eigenwerte|matrix|derangements|fourierreihe|polynom|faktorisiere|binom|mod|fläche|dreiecks?|einheitskreis|anzahl.*derangements|beweise|satz|lemma|theorem|spektral|martingal|laplace|topologie|geometrie|kombinatorik|zahlentheorie|variationsrechnung|maßtheorie|funktionalgleichung|informationstheorie|codierungstheorie|graphentheorie|konvexe|dualität|isoperimetrisch|carathéodory|erdős|ramsey|hamming|young|tableaux|kongruenz|tsp|bayes|portfolio|nash|brachistochrone|zykloide|projektplanung|cpm|kreisgeometrie|dezimalzahlen|quersumme|fourier|analyse|poisson|summationsformel|schwartz|theta|lineare|algebra|charakterisiere|diagonaliserbar|spektralsatz|transportproblem|kostenmatrix|nordwestecke|modi|generator|paritaetsmatrix)\b", qn)
        pure_math = re.search(r"(x\s*[\+\-\*\/=<>]|[\+\-\*\/=<>]\s*x|x\s+[\+\-]\s+y|gleichung|mathe|rechnen|bedingung\w*|erfüll\w*|zahlen.*x.*y.*z|x.*y.*=.*\d+|∫|∑|π|≡|∞|²|³|⁴|x\^?\d+|sin\(|cos\(|ln\(|martingal|fourier|derangements|fläche.*dreieck|gleichseitig|zeige.*dass|beweise.*satz|summe.*über|integral.*von|wahrscheinlichkeit.*posterior|eigenwerte.*matrix|spektral.*graph|laplace.*matrix|nash.*gleichgewicht|ramsey.*zahl|hamming.*code|young.*tableaux|kongruenz.*mod|tsp.*minimum|bayes.*update|portfolio.*varianz|isoperimetrische.*ungleichung|projektplanung.*cpm|kreisgeometrie.*kreis|kombinatorik.*dezimalzahlen|fourier.*analyse|poisson.*summationsformel|lineare.*algebra|charakterisiere.*diagonaliserbar|transportproblem.*kostenmatrix|codierungstheorie.*hamming)", qn)
        
        # System optimization with mathematical context (HEAVY model)
        system_math_optimization = re.search(r"\b(puffergröße|blockgröße|cache|buffer|thread|worker|connection|pool|batch).*\b(optimal|mathematisch|berechne|bestimme)\b", qn) or \
                                  re.search(r"\b(optimal|mathematisch|berechne|bestimme).*\b(puffergröße|blockgröße|cache|buffer|thread|worker|connection|pool|batch)\b", qn)
        
        # Check for non-mathematical optimization (should go to CODE)
        non_math_optimization = re.search(r"\b(optimiere|optimize).*\b(performance|datenbankperformance|database|web|api|code|system)\b", qn) and not system_math_optimization
        
        # Route to HEAVY model for pure mathematical problems or system optimization
        if (pure_math or system_math_optimization or (math_indicators and complexity_score >= 0.4 and not programming_indicators)) and not non_math_optimization:
            self.debug['route_reason'] = 'heavy_math_detection_enhanced'
            self.debug['math_indicators'] = bool(math_indicators)
            self.debug['pure_math'] = bool(pure_math)
            self.debug['system_optimization'] = bool(system_math_optimization)
            return MODEL_HEAVY
        
        # 1) Scores berechnen
        heavy_score = 0.0
        tech_score = 0.0
        
        hits_h = []
        for p in _MATH_PATS:
            if p.search(q) or p.search(qn):
                heavy_score += 1
                hits_h.append(p.pattern)
        
        if re.search(rf"\b{_MATH_VERBS}\b.{{0,60}}\b(optimal\w*|minimum|maxim\w*|argmin|argmax)\b", qn):
            heavy_score += 0.5
        
        if complexity_score >= 0.8:
            heavy_score += 1
        
        hits_t = []
        for p in _TECH_PATS:
            if p.search(q) or p.search(qn):
                tech_score += 1
                hits_t.append(p.pattern)
        
        if linux_kw or code_kw:
            tech_score += 1
        
        self.debug['heavy_hits'] = hits_h
        self.debug['tech_hits'] = hits_t
        self.debug['scores'] = {'heavy': heavy_score, 'tech': tech_score, 'complexity': complexity_score}
        
        # 2) Balanced routing decision
        if heavy_score >= 1.5 and heavy_score >= tech_score + 0.5:
            self.debug['route_reason'] = f'heavy_win_balanced H:{heavy_score} T:{tech_score}'
            return MODEL_HEAVY
        
        if tech_score > 0:
            self.debug['route_reason'] = f'code_tech T:{tech_score}'
            return MODEL_CODE
        
        if complexity_score >= 0.5:
            self.debug['route_reason'] = 'code_complexity_fallback'
            return MODEL_CODE
        
        self.debug['route_reason'] = 'fast_default'
        return MODEL_FAST
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """
        Analyze a query to determine routing requirements.
        
        Args:
            query: The user query to analyze
            
        Returns:
            QueryAnalysis with routing decision and metadata
        """
        query_lower = query.lower()
        
        # Count tokens (simple word-based approximation)
        token_count = len(query.split())
        
        # Detect keywords
        detected_linux = [kw for kw in self.linux_keywords if kw in query_lower]
        detected_code = [kw for kw in self.code_keywords if kw in query_lower]
        detected_complexity = [kw for kw in self.complexity_indicators if kw in query_lower]
        
        all_detected = detected_linux + detected_code + detected_complexity
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(
            query, token_count, detected_linux, detected_code, detected_complexity
        )
        
        # CHATGPT'S IMPROVED ROUTING: Use the new 3-class router
        route_model = self._route_query_chatgpt(
            query, token_count, bool(detected_linux), bool(detected_code), complexity_score
        )
        
        # Convert to legacy needs_code_model for compatibility
        needs_code_model = route_model != MODEL_FAST
        
        # Generate reasoning with ChatGPT's debug info
        reasoning = self._generate_reasoning_chatgpt(
            route_model, token_count, detected_linux, 
            detected_code, detected_complexity, complexity_score
        )
        
        # ChatGPT's Fix 6: Logs bereinigen - add debug info for misroutes
        debug_str = ""
        if hasattr(self, 'debug') and self.debug:
            if 'route_reason' in self.debug:
                debug_str = f", reason={self.debug['route_reason']}"
            if 'heavy_hits' in self.debug and self.debug['heavy_hits']:
                debug_str += f", heavy_hits={len(self.debug['heavy_hits'])}"
            if 'tech_hits' in self.debug and self.debug['tech_hits']:
                debug_str += f", tech_hits={len(self.debug['tech_hits'])}"
        
        logger.info(f"Query analysis: route_model={route_model}, "
                   f"complexity={complexity_score:.2f}, tokens={token_count}{debug_str}")
        
        return QueryAnalysis(
            needs_code_model=needs_code_model,
            complexity_score=complexity_score,
            detected_keywords=all_detected,
            token_count=token_count,
            reasoning=reasoning,
            route_model=route_model,
            debug_info=self.debug.copy(),
            original_query=query  # Store original query for hybrid routing
        )
    
    def _calculate_complexity_score(
        self, 
        query: str, 
        token_count: int,
        linux_kw: List[str], 
        code_kw: List[str], 
        complexity_kw: List[str]
    ) -> float:
        """Calculate complexity score from 0.0 to 1.0."""
        score = 0.0
        
        # Token count contribution (0-0.3)
        if token_count > 100:
            score += 0.3
        elif token_count > 50:
            score += 0.2
        elif token_count > 20:
            score += 0.1
        
        # Keyword density contribution (0-0.4)
        total_keywords = len(linux_kw) + len(code_kw)
        keyword_density = total_keywords / max(token_count, 1)
        score += min(keyword_density * 2, 0.4)
        
        # Complexity indicators (0-0.3)
        if complexity_kw:
            score += min(len(complexity_kw) * 0.1, 0.3)
        
        # Mathematical complexity assessment
        math_complexity = self._assess_mathematical_complexity(query)
        score += math_complexity
        
        # Special patterns that indicate complexity
        complex_patterns = [
            r'wie\s+kann\s+ich.*und.*auch',  # "wie kann ich X und auch Y"
            r'erstelle.*mit.*für',           # "erstelle X mit Y für Z"
            r'schritt.*schritt',             # step by step requests
            r'erkläre.*warum.*und.*wie',     # explain why and how
            r'unterschied.*zwischen.*und'    # difference between X and Y
        ]
        
        for pattern in complex_patterns:
            if re.search(pattern, query.lower()):
                score += 0.1
        
        return min(score, 1.0)
    
    def _assess_mathematical_complexity(self, query: str) -> float:
        """
        Assess mathematical complexity of a query.
        Returns score from 0.0 to 0.5 for mathematical content.
        """
        score = 0.0
        query_lower = query.lower()
        
        # Enhanced mathematical symbols and notation (Grok's recommendations + Advanced patterns)
        math_symbols = [
            r'x\^?2|y\^?2|z\^?2',           # squared variables
            r'x²|y²|z²',                     # unicode squared symbols
            r'∈|∀|∃|∑|∏|∫',                 # mathematical set/logic symbols
            r'[xyz]\s*[+\-=]\s*[xyz]',      # variable equations
            r'[xyz]\s*[<>]\s*[xyz]',        # variable inequalities
            r'\+.*\+.*=',                    # multiple addition equations
            r'=.*\+.*\+',                    # equations with multiple terms
            r'bedingungen?\s+erfüllen',      # "conditions fulfill"
            r'gleichung(en|ssystem)?',       # equation/equation system
            r'system\s+von\s+gleichungen',   # system of equations
            # Grok's additional mathematical patterns
            r'löse.*gleichung',              # "solve equation"
            r'berechne.*fibonacci',          # "calculate fibonacci"
            r'bestimme.*optimal',            # "determine optimal"
            r'mathematisch.*optimal',        # "mathematically optimal"
            r'algorithmus.*komplexität',     # "algorithm complexity"
            r'matrix.*multiplikation',       # "matrix multiplication"
            r'differential.*gleichung',      # "differential equation"
            r'integral.*berechnung',         # "integral calculation"
            r'wahrscheinlichkeit.*verteilung', # "probability distribution"
            r'statistik.*analyse',           # "statistical analysis"
            r'puffer.*größe',                # "buffer size"
            r'optimal.*größe',               # "optimal size"
            r'mathematisch.*puffer',         # "mathematical buffer"
            
            # Advanced mathematical patterns for complex problems
            r'zeige.*dass.*summe',           # "zeige dass summe"
            r'beweise.*satz',                # "beweise satz"
            r'eigenwerte.*matrix',           # "eigenwerte matrix"
            r'laplace.*matrix',              # "laplace matrix"
            r'spektral.*graph',              # "spektral graph"
            r'martingal.*ist',               # "martingal ist"
            r'fourier.*reihe',               # "fourier reihe"
            r'ito.*lemma',                   # "ito lemma"
            r'brownsche.*bewegung',          # "brownsche bewegung"
            r'wahrscheinlichkeits.*theorie', # "wahrscheinlichkeits theorie"
            r'zahlentheorie.*anzahl',        # "zahlentheorie anzahl"
            r'kombinatorik.*anzahl',         # "kombinatorik anzahl"
            r'topologie.*zeige',             # "topologie zeige"
            r'geometrie.*beweise',           # "geometrie beweise"
            r'optimierung.*loese',           # "optimierung loese"
            r'variationsrechnung.*loese',    # "variationsrechnung loese"
            r'tsp.*minimum',                 # "tsp minimum"
            r'bayes.*update',                # "bayes update"
            r'portfolio.*varianz',           # "portfolio varianz"
            r'nash.*gleichgewicht',          # "nash gleichgewicht"
            r'ramsey.*zahl',                 # "ramsey zahl"
            r'hamming.*code',                # "hamming code"
            r'young.*tableaux',              # "young tableaux"
            r'derangements.*von',            # "derangements von"
            r'kongruenz.*mod',               # "kongruenz mod"
            r'binom.*gleich',                # "binom gleich"
            r'isoperimetrische.*ungleichung', # "isoperimetrische ungleichung"
        ]
        
        math_symbol_count = 0
        for pattern in math_symbols:
            if re.search(pattern, query_lower):
                math_symbol_count += 1
        
        # Enhanced mathematical complexity scoring (Grok's recommendations)
        if math_symbol_count >= 3:
            score += 0.5  # Very high mathematical complexity (increased)
        elif math_symbol_count >= 2:
            score += 0.4  # High mathematical complexity (increased)
        elif math_symbol_count >= 1:
            score += 0.3  # Medium mathematical complexity (increased)
        
        # Enhanced mathematical keywords (Grok's expanded list + Advanced terms)
        math_keywords = [
            'löse', 'solve', 'berechne', 'calculate', 'finde', 'find',
            'bestimme', 'determine', 'werte', 'values', 'zahlen', 'numbers',
            'ganze zahlen', 'integers', 'tripel', 'triple', 'paar', 'pair',
            # Grok's additional mathematical keywords
            'fibonacci', 'primzahl', 'prime', 'faktor', 'factor',
            'matrix', 'vektor', 'vector', 'integral', 'differential',
            'wahrscheinlichkeit', 'probability', 'statistik', 'statistics',
            'algorithmus', 'algorithm', 'komplexität', 'complexity',
            'optimierung', 'optimization', 'minimum', 'maximum',
            
            # Advanced mathematical terms for complex problems
            'zeige', 'beweise', 'beweis', 'satz', 'theorem', 'lemma',
            'eigenwerte', 'eigenvalues', 'spektral', 'spectral',
            'martingal', 'martingale', 'fourier', 'laplace',
            'topologie', 'topology', 'geometrie', 'geometry',
            'kombinatorik', 'combinatorics', 'zahlentheorie', 'number theory',
            'variationsrechnung', 'calculus of variations',
            'maßtheorie', 'measure theory', 'funktionalgleichung',
            'informationstheorie', 'information theory',
            'codierungstheorie', 'coding theory', 'graphentheorie', 'graph theory',
            'konvexe', 'convex', 'dualität', 'duality',
            'isoperimetrisch', 'isoperimetric', 'carathéodory',
            'erdős', 'ramsey', 'hamming', 'young', 'tableaux',
            'derangements', 'kongruenz', 'congruence', 'binom', 'binomial',
            'tsp', 'bayes', 'portfolio', 'nash', 'gleichgewicht',
            'brachistochrone', 'zykloide', 'cycloid'
        ]
        
        math_keyword_count = sum(1 for kw in math_keywords if kw in query_lower)
        if math_keyword_count >= 2:
            score += 0.1
        
        # Numbered conditions (indicates systematic problem)
        numbered_conditions = len(re.findall(r'\d+\.\s+[xyz]', query_lower))
        if numbered_conditions >= 2:
            score += 0.2  # Multiple numbered mathematical conditions
        
        return min(score, 0.5)  # Cap at 0.5 to leave room for other complexity factors
    
    def _should_use_code_model(
        self,
        query_lower: str,
        token_count: int,
        linux_kw: List[str],
        code_kw: List[str], 
        complexity_kw: List[str],
        complexity_score: float
    ) -> bool:
        """Determine if the code model should be used."""
        
        # GROK'S SOLUTION: Enhanced basic query filter for Problem 1
        # Check for basic "Welcher Befehl..." questions FIRST (highest priority)
        basic_command_questions = [
            r'welcher\s+befehl\s+(zeigt|macht|gibt|listet)',  # "welcher befehl zeigt/macht/gibt/listet"
            r'was\s+(ist|macht)\s+(der|das)\s+befehl',        # "was ist/macht der/das befehl"
            r'wie\s+(kann|zeige)\s+ich.*\s+(dateien|ordner|prozesse)', # basic file/process questions
            r'welches\s+kommando\s+(zeigt|macht)',            # "welches kommando zeigt/macht"
        ]
        
        # Force Fast Model for basic command questions (Grok's Problem 1 solution)
        for pattern in basic_command_questions:
            if re.search(pattern, query_lower):
                return False  # Force Fast Model for basic "Welcher Befehl..." questions
        
        # GROK'S SOLUTION: Enhanced mathematical detection for Problem 2
        # Check for mathematical patterns that should use Heavy Model
        mathematical_indicators = [
            r'mathematisch.{0,20}optimal',     # "mathematisch ... optimal" (up to 20 chars between)
            r'optimal.{0,20}puffer',           # "optimal ... buffer"
            r'bestimme.{0,20}optimal',         # "bestimme ... optimal"
            r'berechne.{0,20}optimal',         # "berechne ... optimal"
            r'fibonacci.{0,10}zahlen',         # "fibonacci zahlen"
            r'gleichungssystem',               # "gleichungssystem"
            r'i/o.{0,10}operation',            # "I/O operations"
            r'puffergröße.{0,20}operation',    # "puffergröße ... operation"
            r'mathematisch.{0,20}puffer',      # "mathematisch ... puffer"
            r'bestimme.{0,20}mathematisch',    # "bestimme ... mathematisch"
            r'optimal.{0,10}größe',            # "optimal größe"
            r'puffergröße.{0,10}i/o',          # "puffergröße i/o"
        ]
        
        # Force Heavy Model for mathematical queries (Grok's Problem 2 solution)
        for pattern in mathematical_indicators:
            if re.search(pattern, query_lower):
                return True  # Force Code/Heavy Model for mathematical queries
        
        # Always use code model for Linux/code keywords (but after basic command check)
        if linux_kw or code_kw:
            return True
        
        # GROK'S SOLUTION: Enhanced mathematical threshold for Problem 2
        # Lower threshold for mathematical queries to 0.5 (was 0.4)
        if complexity_score >= 0.5:  # Grok's adjusted threshold
            return True
        
        # Use code model for medium complexity queries (original logic)
        if complexity_score > 0.4:
            # But not for very basic Linux commands and simple questions
            basic_linux_commands = [
                r'^(ls|ll|pwd|cd|df|du|ps|top|htop|free|uname)(\s|$)',
                r'^(cat|less|more|head|tail|grep|find|which|whereis)(\s|$)',
                r'^(chmod|chown|mkdir|rmdir|rm|cp|mv|ln)(\s|$)',
                r'^(systemctl|service|crontab|mount|umount)(\s|$)',
            ]
            
            # Check if it's a basic command that should use Fast Model
            for pattern in basic_linux_commands:
                if re.search(pattern, query_lower):
                    return False  # Force Fast Model for basic commands
            
            return True
        
        # Use code model for long queries (likely complex)
        if token_count > 100:
            return True
        
        # Use code model for specific complexity indicators (but check for mathematical patterns first)
        if complexity_kw:
            # Check if it's a mathematical query that should use Heavy Model
            for math_pattern in mathematical_indicators:
                if re.search(math_pattern, query_lower):
                    return True  # Mathematical queries should use Heavy Model
            return True
        
        # Check for mathematical content (equations, variables, etc.)
        math_patterns = [
            r'[xyz]\s*[+\-=<>]\s*[xyz]',     # variable operations
            r'x\d|y\d|z\d',                  # variables with numbers
            r'∈|∀|∃|∑|∏|∫',                 # mathematical symbols
            r'bedingungen?\s+erfüllen',       # mathematical conditions
            r'gleichung|equation',            # equations
            r'löse|solve|berechne|calculate', # mathematical operations
            r'ganze\s+zahlen|integers',       # number theory
            r'\d+\.\s+[xyz]',                # numbered mathematical conditions
        ]
        
        for pattern in math_patterns:
            if re.search(pattern, query_lower):
                return True
        
        # Check for implicit technical content (but exclude mathematical queries)
        technical_patterns = [
            r'wie\s+funktioniert',           # "wie funktioniert"
            r'was\s+ist\s+der\s+unterschied', # "was ist der unterschied"
            r'erkläre\s+mir',                # "erkläre mir"
            r'zeige\s+mir\s+wie',            # "zeige mir wie"
            r'schreibe\s+ein',               # "schreibe ein"
            r'erstelle\s+ein',               # "erstelle ein"
        ]
        
        # Check if it's a mathematical query first (should not be caught by technical patterns)
        for math_pattern in mathematical_indicators:
            if re.search(math_pattern, query_lower):
                return True  # Mathematical queries should use Heavy Model
        
        for pattern in technical_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def _generate_reasoning(
        self,
        needs_code_model: bool,
        token_count: int,
        linux_kw: List[str],
        code_kw: List[str],
        complexity_kw: List[str],
        complexity_score: float
    ) -> str:
        """Generate human-readable reasoning for the decision."""
        reasons = []
        
        if linux_kw:
            reasons.append(f"Linux keywords detected: {', '.join(linux_kw[:3])}")
        
        if code_kw:
            reasons.append(f"Code keywords detected: {', '.join(code_kw[:3])}")
        
        if complexity_kw:
            reasons.append(f"Complexity indicators: {', '.join(complexity_kw[:2])}")
        
        if token_count > 100:
            reasons.append(f"Long query ({token_count} tokens)")
        
        if complexity_score > 0.6:
            reasons.append(f"High complexity score ({complexity_score:.2f})")
        
        if not reasons and needs_code_model:
            reasons.append("Technical patterns detected")
        
        if not reasons:
            reasons.append("Simple general query")
        
        model_choice = "Code model" if needs_code_model else "Fast model"
        return f"{model_choice} selected: {'; '.join(reasons)}"
    
    def _generate_reasoning_chatgpt(
        self,
        route_model: str,
        token_count: int,
        linux_kw: List[str],
        code_kw: List[str],
        complexity_kw: List[str],
        complexity_score: float
    ) -> str:
        """Generate reasoning using ChatGPT's debug information."""
        
        # Use ChatGPT's debug info if available
        if hasattr(self, 'debug') and 'route_reason' in self.debug:
            base_reason = self.debug['route_reason']
            
            # Add additional context
            context_parts = []
            if linux_kw:
                context_parts.append(f"Linux keywords: {', '.join(linux_kw[:3])}")
            if code_kw:
                context_parts.append(f"Code keywords: {', '.join(code_kw[:3])}")
            if complexity_kw:
                context_parts.append(f"Complexity indicators: {', '.join(complexity_kw[:2])}")
            
            # Add debug scores if available
            if 'scores' in self.debug:
                scores = self.debug['scores']
                context_parts.append(f"Scores - Heavy: {scores.get('heavy', 0)}, Tech: {scores.get('tech', 0)}")
            
            context_str = "; ".join(context_parts) if context_parts else ""
            
            return f"{route_model.title()} model selected: {base_reason}" + (f" ({context_str})" if context_str else "")
        
        # Fallback to original reasoning
        return self._generate_reasoning(
            route_model != MODEL_FAST, token_count, linux_kw, code_kw, complexity_kw, complexity_score
        )


# Convenience function for quick analysis
def analyze_query(query: str) -> QueryAnalysis:
    """Quick analysis function for external use."""
    analyzer = QueryAnalyzer()
    return analyzer.analyze_query(query)


if __name__ == "__main__":
    # Test the analyzer
    test_queries = [
        "Hallo, wie geht es dir?",
        "Zeige mir alle laufenden Prozesse mit ps",
        "Wie kann ich eine Python-Funktion schreiben, die Dateien kopiert?",
        "Erkläre mir Schritt für Schritt, wie ich einen Docker Container erstelle und deploye",
        "Was ist der Unterschied zwischen chmod 755 und chmod 644?"
    ]
    
    analyzer = QueryAnalyzer()
    for query in test_queries:
        result = analyzer.analyze_query(query)
        print(f"\nQuery: {query}")
        print(f"Code model needed: {result.needs_code_model}")
        print(f"Complexity: {result.complexity_score:.2f}")
        print(f"Reasoning: {result.reasoning}")