#!/usr/bin/env python3

import re

def test_heavy_patterns():
    query = "Mathematisches Problem: Es gibt drei ganze Zahlen x, y, z mit x+y+z=30"
    query_lower = query.lower()
    
    print(f"Testing query: {query}")
    print(f"Query lower: {query_lower}")
    
    # Test the patterns I added
    heavy_patterns = [
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
    ]
    
    for i, pattern in enumerate(heavy_patterns):
        match = re.search(pattern, query_lower)
        print(f"Pattern {i+1}: {pattern}")
        print(f"  Match: {bool(match)}")
        if match:
            print(f"  Found: '{match.group()}'")
        print()

if __name__ == "__main__":
    test_heavy_patterns()