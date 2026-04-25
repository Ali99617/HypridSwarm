#!/usr/bin/env python3
"""
Hyprid Swarm V5.1 - Autonomous Multi-Agent Pentesting System
Powered by NVIDIA NIM, Groq, and Cerebras

Features:
  - 6 AI Agents (Planner, Hacker, Analyst, Reporter, CVEIntel, ExploitGen)
  - 5 Attack Modes (recon, web, full, bugbounty, stealth)
  - Pre-Flight Tool Scanner
  - CVE Intelligence & Exploit Generation
  - Smart Escalation (auto-recovery on failures)
  - Scope Protection (bug bounty safety)
  - Workspace Memory (persistent sessions)
  - Auto-generated Pentest Reports
  - Browser Agent (Playwright headless Chrome)
  - Verification Policy (No Exploit, No Report)
  - Parallel Scan Strategy
"""
import sys
import subprocess
import json
import os
import re
import time
import glob
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich.rule import Rule

# --- Module Imports ---
from config import AGENT_CONFIG, ACTIVE_TIER
from agents.prompts import (
    PROMPT_PLANNER, PROMPT_HACKER, PROMPT_ANALYST,
    PROMPT_REPORTER, PROMPT_CVE_INTEL, PROMPT_EXPLOIT_GEN
)
from agents.query import query_agent, extract_command
from agents.modes import ATTACK_MODES, get_mode_prompt, list_modes
from memory.workspace import load_workspace, save_workspace
from tools.preflight import scan_installed_tools, get_tool_summary_for_planner, print_tool_table

console = Console()

VERSION = "5.1"
BANNER = f"""[bold cyan]
  _   _                 _     _   ____                             
 | | | |_   _ _ __  _ __(_) __| | / ___|_      ____ _ _ __ _ __ ___  
 | |_| | | | | '_ \\| '__| |/ _` | \\___ \\ \\ /\\ / / _` | '__| '_ ` _ \\ 
 |  _  | |_| | |_) | |  | | (_| |  ___) \\ V  V / (_| | |  | | | | | |
 |_| |_|\\__, | .__/|_|  |_|\\__,_| |____/ \\_/\\_/ \\__,_|_|  |_| |_| |_|
        |___/|_|                                         [bold magenta]V{VERSION}[/bold magenta]
[/bold cyan]"""

WORKSPACE_DIR = "workspaces"
EXPLOITS_DIR = "exploits"


# ─────────────────────────────────────────────
# Terminal Execution Engine
# ─────────────────────────────────────────────
def execute_command(command, scope=None):
    """Execute a shell command with live streaming output. Optionally enforce scope."""
    # Scope Protection
    if scope:
        blocked = check_scope(command, scope)
        if blocked:
            console.print(f"[bold red][SCOPE BLOCK] Command targets out-of-scope domain: {blocked}[/bold red]")
            return f"BLOCKED: Command targets out-of-scope domain '{blocked}'. Only {scope} is in scope.", "", 1
    
    try:
        console.print(Panel(command, title="[yellow]Terminal (Auto-Execution)[/yellow]", border_style="yellow"))
        console.print("[dim italic]Running... (Live Output)[/dim italic]\n")
        
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        output_lines = []
        
        for line in iter(process.stdout.readline, ''):
            sys.stdout.write(line)
            sys.stdout.flush()
            output_lines.append(line)
            
        process.wait()
        full_output = "".join(output_lines)
        return full_output, "", process.returncode
    except Exception as e:
        return "", str(e), 1


def check_scope(command, scope):
    """Check if a command targets something outside the defined scope."""
    # Extract hostnames/IPs from the command
    # Simple heuristic: look for domain-like patterns
    domain_pattern = r'(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'
    found_domains = re.findall(domain_pattern, command)
    
    # Filter out common non-target domains
    ignore = {"github.com", "google.com", "pypi.org", "apt.kali.org", "kali.org",
              "nmap.org", "exploit-db.com", "nvd.nist.gov", "cve.org"}
    
    for domain in found_domains:
        if domain not in ignore and scope not in domain and domain not in scope:
            return domain
    return None


# ─────────────────────────────────────────────
# Reporter Engine
# ─────────────────────────────────────────────
def generate_report(planner_memory, workspace_name=None):
    """Trigger Reporter to compile a Markdown pentest report."""
    console.print("\n[bold yellow][REPORTER] Compiling the final penetration test report...[/bold yellow]")
    
    transcript = json.dumps(planner_memory[-20:], indent=2, ensure_ascii=False)
    
    reporter_memory = [
        {"role": "system", "content": PROMPT_REPORTER},
        {"role": "user", "content": f"Operation transcript:\n{transcript}\n\nGenerate the official Markdown Pentest Report."}
    ]
    
    report_output = query_agent("Reporter", reporter_memory, console, "cyan")
    if report_output:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        prefix = f"{workspace_name}_" if workspace_name else ""
        report_filename = f"Swarm_Report_{prefix}{timestamp}.md"
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(report_output)
        console.print(Panel(f"[bold green][SUCCESS] Report saved: {report_filename}[/bold green]", border_style="green"))
        return report_filename
    return None


# ─────────────────────────────────────────────
# Exploit Generator
# ─────────────────────────────────────────────
def generate_exploit(cve_info, console):
    """Generate a Python exploit script based on CVE data."""
    console.print("\n[bold red][EXPLOIT GEN] Generating exploit code...[/bold red]")
    
    exploit_memory = [
        {"role": "system", "content": PROMPT_EXPLOIT_GEN},
        {"role": "user", "content": f"Generate a Python exploit for:\n{cve_info}\n\nWrite the complete script."}
    ]
    
    exploit_output = query_agent("ExploitGen", exploit_memory, console, "red")
    if exploit_output:
        # Extract Python code block
        pattern = r"```python\n([\s\S]*?)```"
        matches = re.findall(pattern, exploit_output)
        if matches:
            if not os.path.exists(EXPLOITS_DIR):
                os.makedirs(EXPLOITS_DIR)
            timestamp = int(time.time())
            filename = os.path.join(EXPLOITS_DIR, f"exploit_{timestamp}.py")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(matches[0])
            console.print(f"[bold green][SAVED] Exploit script: {filename}[/bold green]")
            return filename
    return None


# ─────────────────────────────────────────────
# Interactive Dashboard
# ─────────────────────────────────────────────
def show_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    console.print(BANNER)
    tier_colors = {"free": "green", "free_ultra": "bold green", "mid": "yellow", "premium": "red"}
    tier_labels = {"free": "FREE (NVIDIA/Groq)", "free_ultra": "FREE ULTRA (Nemotron-120B/49B)", "mid": "MID (Claude/GPT/Gemini)", "premium": "PREMIUM (Claude Opus)"}
    tc = tier_colors.get(ACTIVE_TIER, "white")
    tl = tier_labels.get(ACTIVE_TIER, ACTIVE_TIER)
    console.print(Rule(f"[bold dim]Autonomous Multi-Agent Pentesting[/bold dim] | [{tc}]Tier: {tl}[/{tc}]", style="cyan"))
    console.print()


def show_agent_status():
    """Display agent configuration table."""
    table = Table(title="[bold]Agent Configuration[/bold]", border_style="cyan", show_lines=True)
    table.add_column("Agent", style="bold white", justify="center")
    table.add_column("Role", style="dim")
    table.add_column("Model", style="green")
    table.add_column("Provider", style="yellow", justify="center")
    
    roles = {
        "Planner": "Strategic Commander",
        "Hacker": "Command Executor",
        "Analyst": "Output Analyzer",
        "Reporter": "Report Compiler",
        "CVEIntel": "Vulnerability Intel",
        "ExploitGen": "Exploit Developer"
    }
    colors = {"Planner": "blue", "Hacker": "red", "Analyst": "magenta",
              "Reporter": "cyan", "CVEIntel": "yellow", "ExploitGen": "red"}
    
    for name, cfg in AGENT_CONFIG.items():
        table.add_row(
            f"[{colors.get(name, 'white')}]{name}[/{colors.get(name, 'white')}]",
            roles.get(name, ""),
            cfg["model"],
            cfg["provider"]
        )
    console.print(table)
    console.print()


def list_workspaces():
    if not os.path.exists(WORKSPACE_DIR):
        return []
    files = glob.glob(os.path.join(WORKSPACE_DIR, "*.json"))
    workspaces = []
    for f in files:
        name = os.path.splitext(os.path.basename(f))[0]
        mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(f)))
        try:
            with open(f, "r", encoding="utf-8") as wf:
                msg_count = len(json.load(wf))
        except:
            msg_count = 0
        workspaces.append({"name": name, "messages": msg_count, "modified": mtime, "size": os.path.getsize(f)})
    return workspaces


def list_reports():
    files = glob.glob("Swarm_Report_*.md")
    reports = []
    for f in files:
        mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(f)))
        reports.append({"file": f, "modified": mtime, "size": os.path.getsize(f)})
    return sorted(reports, key=lambda x: x["modified"], reverse=True)


def show_main_menu():
    options = [
        ("[1]", "New Mission",           "Start a new autonomous pentesting session"),
        ("[2]", "Resume Workspace",      "Continue a previous session from memory"),
        ("[3]", "View Workspaces",       "Manage saved target workspaces"),
        ("[4]", "View Reports",          "Browse generated pentest reports"),
        ("[5]", "Pre-Flight Check",      "Scan system for installed security tools"),
        ("[6]", "Agent Status",          "Show agent/model configuration"),
        ("[7]", "Settings",              "Change iterations and other options"),
        ("[0]", "Exit",                  "Quit Hyprid Swarm"),
    ]
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold cyan", width=5)
    table.add_column(style="bold white", width=25)
    table.add_column(style="dim")
    for key, name, desc in options:
        table.add_row(key, name, desc)
    
    console.print("[bold white]  MAIN MENU[/bold white]\n")
    console.print(table)
    console.print()
    return Prompt.ask("[bold cyan]Select[/bold cyan]", choices=["0","1","2","3","4","5","6","7"], default="1")


def select_attack_mode():
    """Let user choose an attack mode."""
    console.print(Rule("[bold]Select Attack Mode[/bold]", style="green"))
    
    table = Table(show_header=True, border_style="green", show_lines=True)
    table.add_column("#", style="bold cyan", width=4, justify="center")
    table.add_column("Mode", style="bold white", width=12)
    table.add_column("Strategy", style="dim")
    
    modes = list_modes()
    for i, (key, name, desc) in enumerate(modes, 1):
        table.add_row(str(i), f"{name}", desc)
    
    console.print(table)
    console.print()
    
    choice = IntPrompt.ask("[cyan]Select mode[/cyan]", default=3)  # default: full
    if 1 <= choice <= len(modes):
        return modes[choice - 1][0]  # return the key (recon, web, etc.)
    return "full"


# ─────────────────────────────────────────────
# Swarm Execution Loop (CORE ENGINE)
# ─────────────────────────────────────────────
def run_swarm(user_input, workspace_name=None, max_loops=15, mode="full", scope=None):
    """Core swarm execution loop with all V5 features."""
    
    # Pre-Flight Check
    console.print(Rule("[bold]Pre-Flight System Check[/bold]", style="cyan"))
    results, installed, missing = scan_installed_tools()
    print_tool_table(console, results)
    tool_summary = get_tool_summary_for_planner(installed)
    
    # Load workspace
    planner_memory = []
    if workspace_name:
        planner_memory = load_workspace(workspace_name, console)
    
    # Build enhanced system prompt
    mode_inject = get_mode_prompt(mode)
    mode_name = ATTACK_MODES.get(mode, {}).get("name", mode)
    
    scope_inject = ""
    if scope:
        scope_inject = f"\nSCOPE RESTRICTION: You are ONLY allowed to target: {scope}. NEVER test anything outside this scope."
        console.print(f"[bold yellow][SCOPE] Locked to: {scope}[/bold yellow]")
    
    enhanced_planner_prompt = (
        PROMPT_PLANNER + "\n\n"
        + tool_summary + "\n\n"
        + mode_inject
        + scope_inject
    )
    
    console.print(Rule(f"[bold red]SWARM DEPLOYED - Mode: {mode_name}[/bold red]", style="red"))
    console.print("[bold red][!] Autonomous execution initiated...[/bold red]\n")

    # Initialize Planner Memory
    if not planner_memory:
        planner_memory = [
            {"role": "system", "content": enhanced_planner_prompt},
            {"role": "user", "content": f"INITIAL GOAL: {user_input}\nPlease break this down and issue your first DIRECTIVE."}
        ]
    elif user_input:
        planner_memory.append({"role": "user", "content": f"NEW OBJECTIVE: {user_input}\nPlease proceed."})
    
    loop_count = 0
    consecutive_failures = 0
    last_failed_tool = None
    
    # Verification stats (No Exploit, No Report)
    verified_count = 0
    unverified_count = 0
    false_positive_count = 0

    while True:
        loop_count += 1
        if loop_count > max_loops:
            console.print("[bold red][!] Maximum swarm iterations reached. Halting.[/bold red]")
            break

        console.print()
        console.print(f"[dim]================ SWARM ITERATION {loop_count}/{max_loops} ================[/dim]")
        
        # Stage 1: PLANNER
        planner_output = query_agent("Planner", planner_memory, console, "blue")
        if not planner_output: break
        
        planner_memory.append({"role": "assistant", "content": planner_output})
        
        if "[TASK_COMPLETED]" in planner_output or "TASK_COMPLETED" in planner_output:
            console.print("\n[bold green][SUCCESS] Mission objective completed![/bold green]")
            break
            
        directive = planner_output
        
        # Stage 2: HACKER
        hacker_memory = [
            {"role": "system", "content": PROMPT_HACKER},
            {"role": "user", "content": f"Directive from Planner:\n\n{directive}\n\nProvide the exact bash command."}
        ]
        
        hacker_output = query_agent("Hacker", hacker_memory, console, "red")
        if not hacker_output: break
        
        cmd = extract_command(hacker_output)
        if not cmd:
            console.print("[yellow][!] Hacker failed to provide a command block.[/yellow]")
            planner_memory.append({"role": "user", "content": "The Hacker failed to provide a command. Please re-formulate."})
            continue
            
        # Stage 3: EXECUTE (with scope protection)
        stdout, stderr, retcode = execute_command(cmd, scope=scope)
        stdout_trunc = stdout[:3000]
        stderr_trunc = stderr[:3000]
        
        if stdout_trunc: console.print(f"[dim green]STDOUT: {len(stdout)} bytes[/dim green]")
        if stderr_trunc: console.print(f"[dim red]STDERR: {len(stderr)} bytes[/dim red]")
        
        # SMART ESCALATION: Track failures
        current_tool = cmd.split()[0] if cmd else ""
        if retcode != 0 and "not found" in stdout.lower() + stderr.lower():
            if current_tool == last_failed_tool:
                consecutive_failures += 1
            else:
                consecutive_failures = 1
                last_failed_tool = current_tool
            
            if consecutive_failures == 2:
                console.print("[bold yellow][SMART ESCALATION] 2nd failure detected. Triggering web search...[/bold yellow]")
                planner_memory.append({"role": "user", "content": f"The tool '{current_tool}' has failed twice. Please instruct the Hacker to search the internet for alternatives or installation help using: python3 tools/websearch.py \"how to install {current_tool} kali linux\""})
                continue
            elif consecutive_failures >= 3:
                console.print("[bold red][SMART ESCALATION] 3rd failure. Switching to alternative tool...[/bold red]")
                planner_memory.append({"role": "user", "content": f"The tool '{current_tool}' has failed 3 times. ABANDON this tool and use a DIFFERENT alternative to achieve the same objective."})
                consecutive_failures = 0
                continue
        else:
            consecutive_failures = 0
        
        # Stage 4: ANALYST (with severity scoring)
        analyst_memory = [
            {"role": "system", "content": PROMPT_ANALYST},
            {"role": "user", "content": f"Command: {cmd}\nReturn Code: {retcode}\n\nSTDOUT:\n{stdout_trunc}\n\nSTDERR:\n{stderr_trunc}\n\nAnalyze and classify severity."}
        ]
        
        analyst_output = query_agent("Analyst", analyst_memory, console, "magenta")
        if not analyst_output: break

        # Color-code severity findings in output
        for sev, color in [("[CRITICAL]", "bold red"), ("[HIGH]", "red"), ("[MEDIUM]", "yellow"), ("[LOW]", "dim"), ("[INFO]", "dim cyan")]:
            if sev in analyst_output:
                console.print(f"[{color}]  >> Severity detected: {sev}[/{color}]")
        
        # Track verification stats
        if "[VERIFIED]" in analyst_output:
            verified_count += analyst_output.count("[VERIFIED]")
            console.print(f"[bold green]  ✓ VERIFIED findings: +{analyst_output.count('[VERIFIED]')}[/bold green]")
        if "[UNVERIFIED]" in analyst_output:
            unverified_count += analyst_output.count("[UNVERIFIED]")
        if "[FALSE POSITIVE]" in analyst_output:
            false_positive_count += analyst_output.count("[FALSE POSITIVE]")
            console.print(f"[dim]  ✗ False positives filtered: +{analyst_output.count('[FALSE POSITIVE]')}[/dim]")
        
        # Stage 5: CVE INTELLIGENCE (triggered when services are discovered)
        if any(kw in analyst_output.lower() for kw in ["version", "apache", "nginx", "openssh", "mysql", "ftp", "smtp", "iis"]):
            console.print("[bold yellow][CVE INTEL] Service versions detected. Analyzing threat intelligence...[/bold yellow]")
            
            cve_memory = [
                {"role": "system", "content": PROMPT_CVE_INTEL},
                {"role": "user", "content": f"Analyst report with discovered services:\n\n{analyst_output}\n\nIdentify services with known CVEs and recommend lookups."}
            ]
            
            cve_output = query_agent("CVEIntel", cve_memory, console, "yellow")
            if cve_output:
                analyst_output += f"\n\n--- CVE INTELLIGENCE ---\n{cve_output}"

        # Feed everything back to Planner
        planner_memory.append({"role": "user", "content": f"Analyst's report:\n\n{analyst_output}\n\nWhat is your next DIRECTIVE? Or is the task complete?"})

    # POST-LOOP: STATS & REPORT & SAVE
    if loop_count > 0:
        # Show verification summary
        console.print()
        console.print(Rule("[bold]Mission Summary[/bold]", style="cyan"))
        stats_table = Table(border_style="cyan", show_lines=True)
        stats_table.add_column("Metric", style="bold white")
        stats_table.add_column("Value", justify="center")
        stats_table.add_row("Total Iterations", str(loop_count))
        stats_table.add_row("[green]Verified Findings[/green]", f"[bold green]{verified_count}[/bold green]")
        stats_table.add_row("[yellow]Unverified Findings[/yellow]", f"[yellow]{unverified_count}[/yellow]")
        stats_table.add_row("[dim]False Positives Filtered[/dim]", f"[dim]{false_positive_count}[/dim]")
        console.print(stats_table)
        
        generate_report(planner_memory, workspace_name)

    if workspace_name:
        save_workspace(workspace_name, planner_memory, console)
    
    console.print()
    Prompt.ask("[dim]Press Enter to return to menu...[/dim]")


# ─────────────────────────────────────────────
# Menu Handlers
# ─────────────────────────────────────────────
def handle_new_mission(max_loops):
    console.print(Rule("[bold green]New Mission[/bold green]", style="green"))
    
    mission = Prompt.ask("[bold cyan]Enter mission objective[/bold cyan]")
    mode = select_attack_mode()
    
    scope = None
    if mode == "bugbounty":
        scope = Prompt.ask("[bold yellow]Define scope (target domain only)[/bold yellow]")
    
    use_workspace = Confirm.ask("[cyan]Save to workspace?[/cyan]", default=True)
    workspace_name = None
    if use_workspace:
        workspace_name = Prompt.ask("[cyan]Workspace name[/cyan]")
    
    run_swarm(mission, workspace_name, max_loops, mode, scope)


def handle_resume_workspace(max_loops):
    workspaces = list_workspaces()
    if not workspaces:
        console.print("[yellow]No saved workspaces found.[/yellow]")
        Prompt.ask("[dim]Press Enter...[/dim]")
        return
    
    console.print(Rule("[bold green]Resume Workspace[/bold green]", style="green"))
    
    table = Table(border_style="green", show_lines=True)
    table.add_column("#", style="bold cyan", width=4, justify="center")
    table.add_column("Workspace", style="bold white")
    table.add_column("Messages", style="yellow", justify="center")
    table.add_column("Last Modified", style="dim")
    
    for i, ws in enumerate(workspaces, 1):
        table.add_row(str(i), ws["name"], str(ws["messages"]), ws["modified"])
    console.print(table)
    console.print()
    
    choice = IntPrompt.ask("[cyan]Select workspace[/cyan]", default=1)
    if choice < 1 or choice > len(workspaces):
        return
    
    selected = workspaces[choice - 1]
    new_objective = Prompt.ask("[cyan]New objective (empty = continue)[/cyan]", default="")
    mode = select_attack_mode()
    
    run_swarm(new_objective, selected["name"], max_loops, mode)


def handle_view_workspaces():
    workspaces = list_workspaces()
    if not workspaces:
        console.print("[yellow]No workspaces.[/yellow]")
        Prompt.ask("[dim]Press Enter...[/dim]")
        return
    
    table = Table(border_style="cyan", show_lines=True)
    table.add_column("#", style="bold cyan", width=4, justify="center")
    table.add_column("Workspace", style="bold white")
    table.add_column("Messages", style="yellow", justify="center")
    table.add_column("Modified", style="dim")
    table.add_column("Size", style="dim", justify="right")
    
    for i, ws in enumerate(workspaces, 1):
        table.add_row(str(i), ws["name"], str(ws["messages"]), ws["modified"], f"{ws['size']/1024:.1f}KB")
    console.print(table)
    
    if Confirm.ask("[red]Delete a workspace?[/red]", default=False):
        num = IntPrompt.ask("[red]Number to delete[/red]")
        if 1 <= num <= len(workspaces):
            os.remove(os.path.join(WORKSPACE_DIR, f"{workspaces[num-1]['name']}.json"))
            console.print(f"[green]Deleted: {workspaces[num-1]['name']}[/green]")
    Prompt.ask("[dim]Press Enter...[/dim]")


def handle_view_reports():
    reports = list_reports()
    if not reports:
        console.print("[yellow]No reports found.[/yellow]")
        Prompt.ask("[dim]Press Enter...[/dim]")
        return
    
    table = Table(border_style="cyan", show_lines=True)
    table.add_column("#", style="bold cyan", width=4, justify="center")
    table.add_column("Report", style="bold white")
    table.add_column("Date", style="dim")
    table.add_column("Size", style="dim", justify="right")
    
    for i, r in enumerate(reports, 1):
        table.add_row(str(i), r["file"], r["modified"], f"{r['size']/1024:.1f}KB")
    console.print(table)
    
    if Confirm.ask("[cyan]Open a report?[/cyan]", default=False):
        num = IntPrompt.ask("[cyan]Report #[/cyan]")
        if 1 <= num <= len(reports):
            with open(reports[num-1]["file"], "r", encoding="utf-8") as f:
                console.print(Panel(f.read(), title=reports[num-1]["file"], border_style="green"))
    Prompt.ask("[dim]Press Enter...[/dim]")


def handle_preflight():
    console.print(Rule("[bold]Pre-Flight System Check[/bold]", style="cyan"))
    results, installed, missing = scan_installed_tools()
    print_tool_table(console, results)
    Prompt.ask("[dim]Press Enter...[/dim]")


def handle_settings(current):
    console.print(Rule("[bold]Settings[/bold]", style="cyan"))
    console.print(f"  Current max iterations: {current}")
    new = IntPrompt.ask("[cyan]Set max iterations[/cyan]", default=current)
    console.print(f"[green]Updated to: {new}[/green]")
    Prompt.ask("[dim]Press Enter...[/dim]")
    return new


# ─────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────
def main():
    max_loops = 15
    
    # Direct CLI mode (backward compatible)
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        mission = " ".join(sys.argv[1:])
        show_banner()
        run_swarm(mission, max_loops=max_loops)
        return
    
    if "--workspace" in sys.argv or "-w" in sys.argv:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--workspace', '-w', default=None)
        parser.add_argument('--max-loops', '-m', type=int, default=15)
        parser.add_argument('--mode', default="full", choices=list(ATTACK_MODES.keys()))
        parser.add_argument('--scope', default=None)
        parser.add_argument('query', nargs='*')
        args = parser.parse_args()
        show_banner()
        run_swarm(" ".join(args.query), args.workspace, args.max_loops, args.mode, args.scope)
        return
    
    # Interactive Menu Mode
    while True:
        show_banner()
        show_agent_status()
        choice = show_main_menu()
        
        if choice == "0":
            console.print("[bold cyan]Goodbye, operator.[/bold cyan]")
            break
        elif choice == "1":
            handle_new_mission(max_loops)
        elif choice == "2":
            handle_resume_workspace(max_loops)
        elif choice == "3":
            handle_view_workspaces()
        elif choice == "4":
            handle_view_reports()
        elif choice == "5":
            handle_preflight()
        elif choice == "6":
            show_banner()
            show_agent_status()
            Prompt.ask("[dim]Press Enter...[/dim]")
        elif choice == "7":
            max_loops = handle_settings(max_loops)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Swarm aborted.[/bold red]")
        sys.exit(0)
