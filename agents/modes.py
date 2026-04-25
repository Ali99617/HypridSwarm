# agents/modes.py
# Attack Mode Definitions - Each mode injects specific strategy into the Planner

ATTACK_MODES = {
    "recon": {
        "name": "Reconnaissance Only",
        "description": "Passive/active recon: port scanning, DNS, subdomains, tech detection. No exploitation.",
        "inject": """MISSION MODE: RECONNAISSANCE ONLY
You are in RECON mode. Your strategy is:
1. Start with DNS enumeration and subdomain discovery (subfinder, amass, fierce).
2. Run full port scan with service detection (nmap -sV -sC).
3. Identify web technologies (whatweb, httpx).
4. Check SSL/TLS configuration (sslscan).
5. Harvest emails and metadata (theharvester).
6. DO NOT attempt any exploitation or brute-force attacks.
7. When all recon data is gathered, declare [TASK_COMPLETED]."""
    },
    
    "web": {
        "name": "Web Application Attack",
        "description": "Focus on web vulnerabilities: SQLi, XSS, SSRF, directory brute-force.",
        "inject": """MISSION MODE: WEB APPLICATION ATTACK
You are in WEB mode. Your strategy is:
1. Start with technology detection (whatweb, httpx).
2. Run Nuclei with web-specific templates if available.
3. Directory/file discovery (gobuster, feroxbuster, or ffuf).
4. SQL injection testing (sqlmap) on discovered parameters.
5. XSS scanning (dalfox) on input fields.
6. Check for common misconfigurations (nikto).
7. If WordPress detected, run wpscan.
8. Document all findings with severity levels."""
    },
    
    "full": {
        "name": "Full Penetration Test",
        "description": "Complete pentest: recon -> scanning -> exploitation -> reporting.",
        "inject": """MISSION MODE: FULL PENETRATION TEST
You are in FULL mode. Execute a complete penetration test:
1. Phase 1 - Recon: Port scan, service detection, subdomain enum.
2. Phase 2 - Scanning: Nuclei templates, nikto, SSL checks.
3. Phase 3 - Vulnerability Assessment: SQLi, XSS, known CVEs.
4. Phase 4 - Exploitation: Attempt to exploit found vulnerabilities.
5. Phase 5 - Post-Exploitation: If access gained, enumerate internal.
6. Be aggressive but smart. Use background jobs for slow scans.
7. Search the internet for exploits matching discovered services."""
    },
    
    "bugbounty": {
        "name": "Bug Bounty Mode",
        "description": "Safe, scope-respecting bug bounty hunting. No destructive actions.",
        "inject": """MISSION MODE: BUG BOUNTY HUNTING
You are in BUGBOUNTY mode. Rules:
1. NEVER perform destructive actions (no data deletion, no DoS).
2. NEVER test out-of-scope targets.
3. Focus on: IDOR, SSRF, XSS, SQLi, Authentication bypass, Info disclosure.
4. Start with subdomain enumeration and endpoint discovery.
5. Use Nuclei with safe templates (no intrusive ones).
6. Check for exposed APIs, .git directories, backup files.
7. Test each finding manually before reporting.
8. Classify each bug by severity (Critical/High/Medium/Low/Info)."""
    },
    
    "stealth": {
        "name": "Stealth Mode",
        "description": "Low and slow scanning to avoid detection by IDS/IPS/WAF.",
        "inject": """MISSION MODE: STEALTH PENETRATION
You are in STEALTH mode. You must evade detection:
1. Use slow scan rates (nmap -T1 or -T2, max 10 packets/sec).
2. Randomize scan order and use decoy addresses when possible.
3. Avoid tools that generate excessive traffic (no masscan, no dirb).
4. Use passive reconnaissance first (OSINT, DNS, certificate transparency).
5. When scanning web apps, use custom User-Agent strings.
6. Space out requests to avoid WAF rate limiting.
7. If a WAF is detected, attempt bypass techniques."""
    }
}


def get_mode_prompt(mode_name):
    """Get the injection prompt for a specific attack mode."""
    mode = ATTACK_MODES.get(mode_name)
    if mode:
        return mode["inject"]
    return ""


def list_modes():
    """Return a list of available modes for display."""
    return [(name, data["name"], data["description"]) for name, data in ATTACK_MODES.items()]
