# Security Policy

Hyprid AI CLI is an **offensive-security tool**. Because of its nature, security hygiene around the project itself is critical. This document covers:

1. How to report a vulnerability in Hyprid AI CLI
2. Mandatory key-rotation guidance for users of this repository
3. Operational security recommendations

---

## 📣 Reporting a Vulnerability

If you discover a security vulnerability in **Hyprid AI CLI itself** (not in a target you are testing), please report it privately:

- **Do not** open a public GitHub issue.
- Contact the maintainer through a private channel (GitHub private vulnerability reporting if enabled, or a dedicated security email if listed in the repository profile).
- Include:
  - A description of the vulnerability
  - Affected file(s) and line numbers
  - Steps to reproduce
  - Potential impact
  - Suggested mitigation, if any

We aim to acknowledge reports within **5 business days** and to provide a remediation plan within **30 days** for confirmed issues. Coordinated disclosure is appreciated.

---

## 🔑 Mandatory Key Rotation (READ THIS)

> The current state of this repository contains **hard-coded API keys** in `config.py` and `hyprid.py`.

If you have **cloned, forked, or pulled** this repository at any point while these keys were present, you must assume the keys are **compromised** and act accordingly:

### Immediate actions

1. **Revoke / rotate** every key listed below through its provider dashboard:
   - **NVIDIA NIM** → [https://build.nvidia.com/](https://build.nvidia.com/)
   - **Groq** → [https://console.groq.com/keys](https://console.groq.com/keys)
   - **Cerebras** → [https://cloud.cerebras.ai/](https://cloud.cerebras.ai/)
   - **OpenRouter** → [https://openrouter.ai/keys](https://openrouter.ai/keys)
   - **OpenAI** (if you added one) → [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - **Anthropic** (if you added one) → [https://console.anthropic.com/](https://console.anthropic.com/)
   - **Google AI** (if you added one) → [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. **Audit your billing** for any unexpected usage on each provider during the exposure window.

### Migrate to environment variables

After rotation, do **not** paste the new keys back into `config.py`. Use environment variables instead:

```bash
export NVIDIA_API_KEY="nvapi-..."
export GROQ_API_KEY="gsk_..."
export CEREBRAS_API_KEY="csk-..."
export OPENROUTER_API_KEY="sk-or-..."
```

Or use a gitignored .env file with [python-dotenv](https://pypi.org/project/python-dotenv/). The full migration pattern is documented in README.md → Configuration.

Add the following to .gitignore:
- .env
- .env.*
- *.key
- secrets/
- workspaces/
- exploits/
- Swarm_Report_*.md

This prevents accidental commits of secrets, sensitive engagement data, generated reports, and PoC exploit scripts.

---

## 🛡️ Operational Security Recommendations

### For users running Hyprid AI CLI
- Run inside an isolated VM or container when conducting authorized engagements. Hyprid AI CLI executes shell commands proposed by an LLM — sandbox accordingly.
- Never feed real production credentials into chats with the agents.
- Review every command in non-auto mode for first-time use of a new model tier or attack mode.
- Keep --max-loops reasonable to avoid runaway autonomous behavior.
- Use --scope in bugbounty mode for every engagement — scope protection is enforced at the shell-execution layer.
- Do not commit the workspaces/ folder, exploits/ folder, or any Swarm_Report_*.md file — these contain target data.

### For maintainers and contributors
- Never commit real API keys, tokens, customer hostnames, or scan output to the repository.
- Treat any branch that touches config.py with extra review.
- When in doubt about whether something is sensitive, assume it is.

---

## 🚫 Out of Scope for This Policy
- Vulnerabilities in third-party tools invoked by Hyprid AI CLI (nmap, nuclei, sqlmap, etc.) — report those upstream.
- Vulnerabilities in AI provider APIs (NVIDIA NIM, Groq, OpenAI, Anthropic, etc.) — report to the provider.
- Misuse of the tool against unauthorized targets — that is a legal matter, not a security vulnerability in the tool.

---

## 📜 Disclaimer
By using Hyprid AI CLI you acknowledge that you have read and accept the Legal & Ethical Use section of README.md. The maintainers accept no liability for damage, legal consequences, or losses caused by misuse, exposed keys, or unauthorized testing.

Thank you for helping keep Hyprid AI CLI and its users safe. 🛡️
