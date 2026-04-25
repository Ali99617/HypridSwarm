# tools/preflight.py
# Pre-Flight System Check - Scans installed security tools on Kali Linux

import shutil

# Tools organized by category
TOOL_CATEGORIES = {
    "Reconnaissance": ["nmap", "masscan", "rustscan", "amass", "subfinder", "fierce", "dnsenum", "theharvester", "autorecon"],
    "Web Scanning": ["nikto", "nuclei", "gobuster", "feroxbuster", "dirsearch", "ffuf", "dirb", "httpx", "katana", "whatweb"],
    "Vulnerability": ["sqlmap", "wpscan", "dalfox", "commix", "tplmap", "nosqlmap", "xsstrike"],
    "Exploitation": ["metasploit", "msfconsole", "msfvenom", "searchsploit", "hydra", "john", "hashcat", "medusa"],
    "SSL/Crypto": ["sslscan", "sslyze", "testssl"],
    "OSINT": ["sherlock", "spiderfoot", "recon-ng", "maltego"],
    "Wireless": ["aircrack-ng", "wifite", "bettercap"],
    "Web Search": ["python3"],
}


def scan_installed_tools():
    """Scan the system for installed pentesting tools."""
    results = {}
    all_installed = []
    all_missing = []
    
    for category, tools in TOOL_CATEGORIES.items():
        installed = []
        missing = []
        for tool in tools:
            # Handle special cases
            check_name = tool
            if tool == "metasploit":
                check_name = "msfconsole"
            
            if shutil.which(check_name):
                installed.append(tool)
                all_installed.append(tool)
            else:
                missing.append(tool)
                all_missing.append(tool)
        
        results[category] = {"installed": installed, "missing": missing}
    
    return results, all_installed, all_missing


def get_tool_summary_for_planner(installed_tools):
    """Generate a concise tool summary string for the Planner's system prompt."""
    if not installed_tools:
        return "No known security tools detected. You may need to install tools before proceeding."
    
    return (
        f"AVAILABLE TOOLS ON THIS SYSTEM ({len(installed_tools)} detected): "
        + ", ".join(installed_tools)
        + "\nONLY use tools from this list. If a tool is not listed, instruct the Hacker to install it first."
    )


def print_tool_table(console, results):
    """Print a Rich table showing tool status."""
    from rich.table import Table
    
    table = Table(title="[bold]System Tool Scanner (Pre-Flight Check)[/bold]", border_style="cyan", show_lines=True)
    table.add_column("Category", style="bold white", width=18)
    table.add_column("Installed", style="green")
    table.add_column("Missing", style="dim red")
    
    total_installed = 0
    total_missing = 0
    
    for category, data in results.items():
        installed_str = ", ".join(data["installed"]) if data["installed"] else "-"
        missing_str = ", ".join(data["missing"]) if data["missing"] else "-"
        total_installed += len(data["installed"])
        total_missing += len(data["missing"])
        table.add_row(category, installed_str, missing_str)
    
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold green]{total_installed} tools[/bold green]",
        f"[bold red]{total_missing} missing[/bold red]"
    )
    
    console.print(table)
    console.print()
