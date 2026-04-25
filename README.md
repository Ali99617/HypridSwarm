<div align=\"center\">

# 🛡️ Hyprid AI CLI

**Autonomous, multi-agent AI assistant for offensive security on Kali Linux.**

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Kali%20Linux-success.svg)](https://www.kali.org/)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-Unlicensed-lightgrey.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/swarm-V5.1-magenta.svg)]()

<br>

![Hyprid AI CLI Screenshot](https://github.com/Ali99617/HypridSwarm/blob/8b4270b37aeaeab3e8abed47d250f5759d7c8172/%D9%84%D9%82%D8%B7%D8%A9%20%D8%B4%D8%A7%D8%B4%D8%A9%202026-04-25%20185247.png?raw=1)

<br>

</div>

> ⚠️ **Authorized use only.** Hyprid AI CLI is built for security researchers performing engagements they are explicitly authorized to perform (owned labs, red-team engagements, contracted pentests, in-scope bug-bounty programs). See [Legal & Ethical Use](#-legal--ethical-use).

---

## 📚 Table of Contents

1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [Architecture](#-architecture)
4. [Requirements](#-requirements)
5. [Installation](#-installation)
6. [Configuration](#-configuration)
7. [Quick Start](#-quick-start)
8. [Attack Modes](#-attack-modes)
9. [Agents Reference](#-agents-reference)
10. [Tools Reference](#-tools-reference)
11. [Workspaces & Reports](#-workspaces--reports)
12. [Troubleshooting / FAQ](#-troubleshooting--faq)
13. [Roadmap](#-roadmap)
14. [Contributing](#-contributing)
15. [License](#-license)
16. [Legal & Ethical Use](#-legal--ethical-use)

---

## 🔍 Overview

**Hyprid AI CLI** is a Python-based offensive-security assistant that ships with **two complementary entry points**:

| Entry point | What it is | When to use it |
|---|---|---|
| `hyprid.py` | Single-agent, single-command iterative CLI powered by **OpenRouter**. | Quick, conversational tasks; one command at a time with optional auto-pilot. |
| `hyprid_swarm.py` | **V5.1 multi-agent autonomous pentesting swarm** with 6 specialized AI agents, 5 attack modes, 4 model tiers, pre-flight tool scanner, CVE intelligence, exploit generation, and Markdown report compilation. | Full pentests, bug-bounty recon, multi-step engagements, persistent workspaces. |

Both tools are designed for **Kali Linux** but will run on most modern Linux distributions with the appropriate security tooling installed.

---

## ✨ Key Features

### Single-Agent CLI (`hyprid.py`)
- 🤖 OpenRouter-powered chat with streaming Markdown rendering (Rich).
- 🔁 Iterative one-command-at-a-time loop with optional **Auto-Pilot**.
- 🛑 `[TASK_COMPLETED]` sentinel to gracefully end autonomous runs.
- 🔄 Up to 15 autonomous iterations (configurable in code).

### Multi-Agent Swarm (`hyprid_swarm.py` V5.1)
- 🧠 **6 specialized agents**: Planner, Hacker, Analyst, Reporter, CVEIntel, ExploitGen.
- 🎯 **5 attack modes**: `recon`, `web`, `full`, `bugbounty`, `stealth`.
- 🏷️ **4 model tiers**: `free`, `free_ultra`, `mid`, `premium` — switch with one variable.
- 🛰️ **Pre-flight tool scanner** — detects installed Kali tools and informs the Planner.
- 🛡️ **Scope protection** — blocks out-of-scope domains in `bugbounty` mode.
- 🧬 **CVE intelligence** via NIST NVD API.
- 🐍 **Auto exploit generation** — saves Python PoC scripts to `exploits/`.
- 🌐 **Browser agent** (Playwright headless Chromium) for web-app interaction.
- 💾 **Workspace memory** — JSON-based persistent sessions.
- 📝 **Auto-generated Markdown pentest reports** with severity classification and verification status.
- ⚡ **Smart escalation** — auto-recovery on tool failures.
- 🔬 **\"No Exploit, No Report\"** verification policy.

---

## 🧱 Architecture

### High-level data flow (Swarm)

```
          ┌────────────────────┐
          │      User Goal     │
          └─────────┬──────────┘
                    ▼
   ┌────────────────────────────────────────┐  
   │   Pre-Flight Tool Scanner (preflight)  │  
   └─────────┬──────────────────────────────┘  
             ▼  
   ┌──────────────────┐    DIRECTIVE     ┌──────────────────┐  
   │  PLANNER (NVIDIA)│ ───────────────▶ │  HACKER (Groq)   │  
   └────────▲─────────┘                  └────────┬─────────┘  
            │                                     │ bash command  
            │ ANALYST REPORT                      ▼  
   ┌────────┴─────────┐                  ┌──────────────────┐  
   │ ANALYST(Minimax) │ ◀──── stdout/err │  Shell Executor  │  
   └────────▲─────────┘                  └──────────────────┘  
            │  
            │ if services discovered  
            ▼  
   ┌──────────────────┐    CVE data      ┌──────────────────┐  
   │  CVEIntel (NIM)  │ ───────────────▶ │ ExploitGen (NIM) │  
   └──────────────────┘                  └──────────────────┘  
                                                  │  
                                                  ▼  
                                         ┌──────────────────┐  
                                         │ Reporter (Groq)  │  
                                         │  → Markdown .md  │  
                                         └──────────────────┘
```

### Tier system

```
free         → llama-3.3-70b across all roles (NVIDIA + Groq)  
free_ultra   → Nemotron-120B (Planner) + Minimax-M2.7 (Analyst/ExploitGen) + Groq (Hacker/Reporter)  
mid          → Claude Sonnet + GPT-4.1 + Gemini 2.5 Pro  
premium      → Claude Opus across critical roles
```

Tiers are defined in `config.py` and switched by changing a single variable: `ACTIVE_TIER`.

---

## 🖥️ Requirements

- **OS**: Kali Linux (primary target). Other Debian/Ubuntu-based distros work; Arch/Fedora best-effort.
- **Python**: 3.9 or newer.
- **Network**: Outbound HTTPS to chosen model providers (NVIDIA NIM, Groq, Cerebras, OpenAI, Anthropic, Google, OpenRouter).
- **Disk**: ~500 MB for Python deps + Chromium (Playwright).
- **Privileges**: Some scans (raw sockets, low ports) require `sudo`.

### External tooling (recommended on Kali)

The pre-flight scanner detects these categories — install whatever is missing:

| Category | Examples |
|---|---|
| Reconnaissance | `nmap`, `masscan`, `rustscan`, `amass`, `subfinder`, `theharvester` |
| Web Scanning | `nuclei`, `gobuster`, `feroxbuster`, `ffuf`, `nikto`, `httpx`, `whatweb` |
| Vulnerability | `sqlmap`, `wpscan`, `dalfox`, `commix` |
| Exploitation | `metasploit`, `searchsploit`, `hydra`, `john`, `hashcat` |
| SSL/Crypto | `sslscan`, `sslyze`, `testssl` |
| OSINT | `sherlock`, `spiderfoot`, `recon-ng` |
| Wireless | `aircrack-ng`, `wifite`, `bettercap` |

---

## ⚙️ Installation

### 1. Clone

```bash
git clone https://github.com/Ali99617/HypridSwarm.git
cd HypridSwarm
```

### 2. Install Python dependencies

```bash\pip3 install -r requirements.txt --break-system-packages
```

`requirements.txt` ships with:

```
rich
requests
duckduckgo-search
playwright
```

### 3. Install Playwright Chromium (for the browser agent)

```bash
playwright install chromium
```

### 4. (Optional) Install the single-agent CLI globally on Kali

```bash
chmod +x setup.sh
./setup.sh
```

This installs `hyprid.py` to `/usr/local/bin/hyprid` so you can call it as `hyprid` from anywhere.

---

## 🔧 Configuration

### ⚠️ EXPOSED API KEYS — READ THIS FIRST

The current repository **hard-codes API keys** in:

- `config.py` → NVIDIA, Groq, Cerebras, OpenRouter
- `hyprid.py` → OpenRouter

**Before publishing or sharing this repo, you MUST:**

1. **Rotate every key listed in `config.py` and `hyprid.py**` through their respective provider dashboards.
2. **Migrate to environment variables** using the pattern below.
3. Add `.env` to your `.gitignore`.

#### Recommended `.env` migration pattern

Create a `.env` file at the repo root (gitignored):

```dotenv
NVIDIA_API_KEY=nvapi-...
GROQ_API_KEY=gsk_...
CEREBRAS_API_KEY=csk-...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
OPENROUTER_API_KEY=sk-or-...
```

Then in `config.py`, replace hard-coded values with environment lookups, e.g.:

```python
import os
KEYS = {
    \"nvidia\":     os.environ.get(\"NVIDIA_API_KEY\", \"\"),
    \"groq\":       os.environ.get(\"GROQ_API_KEY\", \"\"),
    \"cerebras\":   os.environ.get(\"CEREBRAS_API_KEY\", \"\"),
    \"openai\":     os.environ.get(\"OPENAI_API_KEY\", \"\"),
    \"anthropic\":  os.environ.get(\"ANTHROPIC_API_KEY\", \"\"),
    \"google\":     os.environ.get(\"GOOGLE_API_KEY\", \"\"),
    \"openrouter\": os.environ.get(\"OPENROUTER_API_KEY\", \"\"),
}
```

And in `hyprid.py`:

```python
OPENROUTER_API_KEY = os.environ.get(\"OPENROUTER_API_KEY\", \"\")
```

Optionally use `[python-dotenv](https://pypi.org/project/python-dotenv/)` to auto-load `.env`:

```bash
pip3 install python-dotenv
```

```python
from dotenv import load_dotenv
load_dotenv()
```

### Switching model tiers (Swarm)

Open `config.py` and change one line:

```python
ACTIVE_TIER = \"free_ultra\"   # options: \"free\", \"free_ultra\", \"mid\", \"premium\"
```


| Tier         | Approx. cost | Best for                                       |
| ------------ | ------------ | ---------------------------------------------- |
| `free`       | $0           | Daily use, rate-limited free APIs              |
| `free_ultra` | $0           | Best free models (Nemotron-120B, Minimax-M2.7) |
| `mid`        | ~$20–50/mo   | Claude Sonnet + GPT-4.1 + Gemini 2.5 Pro       |
| `premium`    | ~$100–200/mo | Claude Opus across critical roles              |


---

## 🚀 Quick Start

### Single-agent CLI

```bash
# Interactive
python3 hyprid.py

# One-shot with arguments
python3 hyprid.py \"scan all open ports on scanme.nmap.org\"

# Auto-pilot (no per-command confirmation)
python3 hyprid.py --auto \"enumerate subdomains of example.com\"
```

If installed via `setup.sh`, replace `python3 hyprid.py` with `hyprid`.

### Multi-agent Swarm

```bash
# Interactive menu (recommended first run)
python3 hyprid_swarm.py

# Direct mission
python3 hyprid_swarm.py \"full pentest of testlab.local\"

# With workspace + mode + scope (bug bounty)
python3 hyprid_swarm.py \\
    --workspace acme_engagement \\
    --mode bugbounty \\
    --scope acme.com \\
    --max-loops 25 \\
    \"find OWASP Top 10 vulnerabilities\"
```

The interactive menu offers:

```
[1] New Mission
[2] Resume Workspace
[3] View Workspaces
[4] View Reports
[5] Pre-Flight Check
[6] Agent Status
[7] Settings
[0] Exit
```

---

## 🎯 Attack Modes

Defined in `agents/modes.py`. Pass via `--mode` or pick from the interactive menu.


| Mode        | Purpose                 | Strategy summary                                                                               |
| ----------- | ----------------------- | ---------------------------------------------------------------------------------------------- |
| `recon`     | Reconnaissance only     | DNS/subdomain enum, full port scan, web tech detection, SSL check, OSINT. **No exploitation.** |
| `web`       | Web application attack  | Tech detect → Nuclei → directory brute → SQLi → XSS → misconfigs → WordPress.                  |
| `full`      | Complete pentest        | Recon → scanning → vulnerability assessment → exploitation → post-exploitation. Default.       |
| `bugbounty` | Safe bug-bounty hunting | Scope-locked, non-destructive, focuses on IDOR/SSRF/XSS/SQLi/auth-bypass/info-disclosure.      |
| `stealth`   | Low-and-slow evasion    | Slow nmap timing (`-T1`/`-T2`), passive recon, decoys, WAF avoidance.                          |


`bugbounty` mode requires a `--scope` argument and enforces it at the shell-execution layer.

---

## 🤖 Agents Reference

All 6 agents are defined in `agents/prompts.py` and routed through `agents/query.py`. Per-tier model assignment lives in `config.py`.


| Agent          | Role                                                                     | Default model (free_ultra)                 | Provider   |
| -------------- | ------------------------------------------------------------------------ | ------------------------------------------ | ---------- |
| **Planner**    | Strategic Commander — issues directives, never writes commands.          | `nvidia/nemotron-3-super-120b-a12b`        | NVIDIA NIM |
| **Hacker**     | Command Executor — converts directives into a single bash command.       | `llama-3.3-70b-versatile`                  | Groq       |
| **Analyst**    | Output Analyzer — classifies findings by severity & verification status. | `minimaxai/minimax-m2.7`                   | NVIDIA NIM |
| **Reporter**   | Report Compiler — produces the final Markdown pentest report.            | `llama-3.3-70b-versatile`                  | Groq       |
| **CVEIntel**   | Vulnerability Intel — maps discovered services to known CVEs.            | `nvidia/llama-3.3-nemotron-super-49b-v1.5` | NVIDIA NIM |
| **ExploitGen** | Exploit Developer — writes Python PoC scripts for confirmed CVEs.        | `minimaxai/minimax-m2.7`                   | NVIDIA NIM |


### Verification & severity vocabulary

Analyst tags findings with:

- **Verification**: `[VERIFIED]`, `[UNVERIFIED]`, `[FALSE POSITIVE]`
- **Severity**: `[CRITICAL]`, `[HIGH]`, `[MEDIUM]`, `[LOW]`, `[INFO]`

Per the **No Exploit, No Report** policy, only `[VERIFIED]` findings appear in the main report table.

---

## 🧰 Tools Reference

Helper scripts under `tools/` that the swarm can invoke as bash commands.

### `tools/preflight.py`

Scans the host for installed security tools and groups them by category. Output is fed into the Planner's system prompt so it only proposes commands for available tooling.

### `tools/websearch.py`

DuckDuckGo-based web search. Used by the Smart Escalation system when a tool fails repeatedly, and by the Planner for general lookups.

```bash
python3 tools/websearch.py \"how to install nuclei kali linux\"
```

### `tools/cve_lookup.py`

Queries the NIST NVD API for CVEs matching a service/version string. Returns CVE ID, description, CVSS score, severity, and references.

```bash
python3 tools/cve_lookup.py \"Apache 2.4.49\"
```

### `tools/browser_agent.py`

Playwright headless Chromium agent. Navigates URLs, performs click/fill/type/wait/screenshot/evaluate actions, captures console logs and cookies. Returns a JSON result.

```bash
python3 tools/browser_agent.py \"https://target.example.com\" screenshot.png
```

---

## 💾 Workspaces & Reports

### Workspaces (`workspaces/*.json`)

Persistent JSON snapshots of the Planner's full conversation memory. Created when you opt-in to \"Save to workspace\" during a New Mission, and reloaded via \"Resume Workspace\". Managed by `memory/workspace.py`.

### Reports (`Swarm_Report_*.md`)

Auto-generated at the end of each mission. Filename format:

```
Swarm_Report_<workspace_name>_<YYYYMMDD_HHMMSS>.md
```

Sections include: Executive Summary, Target Information, Methodology, Verified Findings (table with severity + CVSS), Potential Vulnerabilities (Unverified), Open Ports & Services, Recommendations, Conclusion.

### Exploits (`exploits/exploit_<timestamp>.py`)

Python PoC scripts emitted by the ExploitGen agent. Self-contained, with usage comments. **Use only against authorized targets.**

---

## 🛟 Troubleshooting / FAQ

**Q: I get `OPENROUTER_API_KEY is not set`.**  
A: Export it: `export OPENROUTER_API_KEY=\"sk-or-...\"` or use the `.env` migration in [Configuration](#-configuration).

**Q: `pip3 install` fails on Kali with \"externally managed environment\".**  
A: Use `--break-system-packages` (already included in `setup.sh`) or work inside a `venv`.

**Q: `playwright install chromium` fails behind a corporate proxy.**  
A: Set `HTTPS_PROXY` and `HTTP_PROXY` env vars before running the install.

**Q: The swarm keeps proposing tools I don't have.**  
A: Run option `[5] Pre-Flight Check` and install missing tools, or let the Planner auto-install via `apt-get`.

**Q: A scan in `bugbounty` mode is being blocked as \"out of scope\".**  
A: That's by design. Only domains containing your `--scope` value (or vice-versa) are allowed. Adjust `--scope` if legitimate.

**Q: Auto-Pilot stops after 15 iterations.**  
A: Increase via `--max-loops N` for the swarm, or edit `max_loops = 15` in `hyprid.py`.

**Q: I want different models for different agents.**  
A: Edit the relevant tier in `config.py` (`TIERS[\"free_ultra\"][\"Planner\"][\"model\"] = \"...\"`).

---

## 🗺️ Roadmap

- [ ] Migrate API key management to environment variables / `.env` (currently doc-only).
- [ ] Add `python-dotenv` to `requirements.txt`.
- [ ] Optional Docker image preloaded with common Kali tools.
- [ ] Plug-in style mode loader (`agents/modes/<mode>.py`).
- [ ] HTML report renderer in addition to Markdown.
- [ ] Slack / Discord webhook for finding notifications.
- [ ] Built-in scope file support (multi-domain bug-bounty scopes).
- [ ] Test suite + CI.

---

## 🤝 Contributing

See `[CONTRIBUTING.md](./CONTRIBUTING.md)` for the contribution workflow, coding conventions, and how to propose new agents, modes, or tools.

---

## 📜 License

**No license has been declared for this project.** All rights are reserved by the author by default. See `[LICENSE](./LICENSE)` for details. If you wish to use, modify, or redistribute Hyprid AI CLI, please contact the maintainer first.

---

## ⚖️ Legal & Ethical Use

> **Hyprid AI CLI is a dual-use security research tool. Misuse can be a serious crime.**

- ✅ **Authorized use only.** Run Hyprid AI CLI **only** against systems you **own** or have **explicit written permission** to test (signed engagement letter, bug-bounty program scope, lab environment).
- ❌ Do **not** use it against third-party systems, public websites, or infrastructure you do not control.
- ❌ Do **not** use it for unauthorized access, data theft, denial of service, or any other illegal activity.
- 🛡️ The maintainers and contributors of this project accept **no liability** for damage, legal consequences, or losses caused by misuse.
- 📜 You are solely responsible for complying with all applicable laws in your jurisdiction (including but not limited to the **CFAA**, **Computer Misuse Act**, **GDPR**, and equivalent national legislation).
- 🔬 The \"uncensored\" framing in some agent system prompts means **no built-in refusals for offensive-security tasks**. It does **not** override your legal and ethical obligations.

By using this software you confirm that you have read, understood, and accept these terms.

---

<div align=\"center\">



**Stay legal. Stay curious. Hack responsibly.** 🛡️

</div>
