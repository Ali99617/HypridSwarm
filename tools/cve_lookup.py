#!/usr/bin/env python3
# tools/cve_lookup.py
# CVE Intelligence - Search for known vulnerabilities using NIST NVD API
# Usage: python3 tools/cve_lookup.py "Apache 2.4.49"

import sys
import json
import requests

NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def search_cves(keyword, max_results=5):
    """Search NIST NVD for CVEs matching a keyword."""
    try:
        params = {
            "keywordSearch": keyword,
            "resultsPerPage": max_results
        }
        response = requests.get(NVD_API, params=params, timeout=15)
        
        if response.status_code != 200:
            return [{"error": f"NVD API returned status {response.status_code}"}]
        
        data = response.json()
        results = []
        
        for vuln in data.get("vulnerabilities", []):
            cve = vuln.get("cve", {})
            cve_id = cve.get("id", "Unknown")
            
            # Get description
            descriptions = cve.get("descriptions", [])
            desc = ""
            for d in descriptions:
                if d.get("lang") == "en":
                    desc = d.get("value", "")
                    break
            
            # Get CVSS score
            cvss_score = "N/A"
            cvss_severity = "Unknown"
            metrics = cve.get("metrics", {})
            
            # Try CVSS 3.1 first, then 3.0, then 2.0
            for version in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
                if version in metrics and metrics[version]:
                    cvss_data = metrics[version][0].get("cvssData", {})
                    cvss_score = cvss_data.get("baseScore", "N/A")
                    cvss_severity = cvss_data.get("baseSeverity", "Unknown")
                    break
            
            # Get references
            refs = cve.get("references", [])
            ref_urls = [r.get("url", "") for r in refs[:3]]
            
            results.append({
                "cve_id": cve_id,
                "description": desc[:300],
                "cvss_score": cvss_score,
                "severity": cvss_severity,
                "references": ref_urls
            })
        
        if not results:
            return [{"info": f"No CVEs found for: {keyword}"}]
        
        return results
        
    except requests.exceptions.Timeout:
        return [{"error": "NVD API request timed out"}]
    except Exception as e:
        return [{"error": str(e)}]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/cve_lookup.py 'service version'")
        sys.exit(1)
    
    keyword = sys.argv[1]
    max_res = 5
    if len(sys.argv) == 3:
        try:
            max_res = int(sys.argv[2])
        except ValueError:
            pass
    
    results = search_cves(keyword, max_res)
    print(json.dumps(results, indent=2, ensure_ascii=False))
