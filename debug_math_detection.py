#!/usr/bin/env python3

import re

def test_math_detection():
    query = "Löse: x + y = 5, x - y = 1"
    qn = query.lower()
    
    print(f"Original query: {query}")
    print(f"Normalized query: {qn}")
    
    # Test math indicators
    math_indicators = re.search(r"\b(bestimme|berechne|minimiere|maximiere|optimiere|finde|löse|mathematisch|optimal|fibonacci|gleichung|mathe|rechnen|werte\s+haben|ganze\s+zahlen)\b", qn)
    print(f"Math indicators found: {bool(math_indicators)}")
    if math_indicators:
        print(f"  Match: {math_indicators.group()}")
    
    # Test pure math
    pure_math = re.search(r"(x\s*[\+\-\*\/=<>]|[\+\-\*\/=<>]\s*x|x\s+[\+\-]\s+y|gleichung|mathe|rechnen|bedingung\w*|erfüll\w*|zahlen.*x.*y.*z|x.*y.*=.*\d+)", qn)
    print(f"Pure math found: {bool(pure_math)}")
    if pure_math:
        print(f"  Match: {pure_math.group()}")
    
    # Test complexity (mock)
    complexity_score = 0.4
    print(f"Complexity score: {complexity_score}")
    
    # Final decision
    should_be_heavy = pure_math or (math_indicators and complexity_score >= 0.4)
    print(f"Should route to heavy: {should_be_heavy}")

if __name__ == "__main__":
    test_math_detection()