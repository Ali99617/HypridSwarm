#!/usr/bin/env python3
import sys
import json
try:
    from duckduckgo_search import DDGS
except ImportError:
    print("Error: duckduckgo-search package is not installed. Please run: pip3 install duckduckgo-search")
    sys.exit(1)

def search_web(query, max_results=3):
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=max_results)]
            return results
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 websearch.py 'your search query'")
        sys.exit(1)
        
    query = sys.argv[1]
    
    # We set default to 5 to give Analyst enough context
    max_res = 5 
    if len(sys.argv) == 3:
        try:
             max_res = int(sys.argv[2])
        except ValueError:
             pass
             
    results = search_web(query, max_res)
    print(json.dumps(results, indent=2, ensure_ascii=False))
