# config.py
# Hyprid Swarm V5 - Multi-Provider Agent Configuration
# ═══════════════════════════════════════════════════════
# Switch between FREE, FREE_ULTRA, MID, and PREMIUM tiers by changing ACTIVE_TIER below.
# Add your API keys in the KEYS section, then set ACTIVE_TIER to use them.

# ─────────────────────────────────────────────
# API KEYS (add yours here)
# ─────────────────────────────────────────────
KEYS = {
    # Free tier (already working)
    "nvidia": "", # Get from: https://build.nvidia.com
    "groq": "",   # Get from: https://console.groq.com
    "cerebras": "", # Get from: https://cloud.cerebras.ai

    # Paid tier (paste your keys here when you get them)
    "openai": "",       # Get from: https://platform.openai.com/api-keys
    "anthropic": "",    # Get from: https://console.anthropic.com/
    "google": "",       # Get from: https://aistudio.google.com/apikey
    "openrouter": "",   # Get from: https://openrouter.ai/keys
}

# ─────────────────────────────────────────────
# ACTIVE TIER: Change this to switch all models
# Options: "free", "free_ultra", "mid", "premium"
# ─────────────────────────────────────────────
ACTIVE_TIER = "free_ultra"

# ─────────────────────────────────────────────
# TIER CONFIGURATIONS
# ─────────────────────────────────────────────

TIERS = {
    # ══════════════════════════════════════════
    # FREE TIER ($0/month) - Original safe config
    # ══════════════════════════════════════════
    "free": {
        "Planner": {
            "url": "https://integrate.api.nvidia.com/v1/chat/completions",
            "key": KEYS["nvidia"],
            "model": "meta/llama-3.3-70b-instruct",
            "provider": "NVIDIA NIM"
        },
        "Hacker": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "key": KEYS["groq"],
            "model": "llama-3.3-70b-versatile",
            "provider": "Groq"
        },
        "Analyst": {
            "url": "https://integrate.api.nvidia.com/v1/chat/completions",
            "key": KEYS["nvidia"],
            "model": "meta/llama-3.3-70b-instruct",
            "provider": "NVIDIA NIM"
        },
        "Reporter": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "key": KEYS["groq"],
            "model": "llama-3.3-70b-versatile",
            "provider": "Groq"
        },
        "CVEIntel": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "key": KEYS["groq"],
            "model": "llama-3.3-70b-versatile",
            "provider": "Groq"
        },
        "ExploitGen": {
            "url": "https://integrate.api.nvidia.com/v1/chat/completions",
            "key": KEYS["nvidia"],
            "model": "meta/llama-3.3-70b-instruct",
            "provider": "NVIDIA NIM"
        },
    },

    # ══════════════════════════════════════════
    # FREE ULTRA ($0/month) - Best free models!
    # Uses Nemotron-120B + MiniMax M2.7 + Nemotron-49B + Groq
    # Optimal hybrid: each agent gets the best model for its role
    # ══════════════════════════════════════════
    "free_ultra": {
        "Planner": {
            "url": "https://integrate.api.nvidia.com/v1/chat/completions",
            "key": KEYS["nvidia"],
            "model": "nvidia/nemotron-3-super-120b-a12b",  # 120B, 1M context - strategic planning
            "provider": "NVIDIA NIM"
        },
        "Hacker": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "key": KEYS["groq"],
            "model": "llama-3.3-70b-versatile",  # Groq = fastest for command execution
            "provider": "Groq"
        },
        "Analyst": {
            "url": "https://integrate.api.nvidia.com/v1/chat/completions",
            "key": KEYS["nvidia"],
            "model": "minimaxai/minimax-m2.7",  # SWE-Bench 78%! Best for deep analysis
            "provider": "NVIDIA NIM"
        },
        "Reporter": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "key": KEYS["groq"],
            "model": "llama-3.3-70b-versatile",  # Fast report generation
            "provider": "Groq"
        },
        "CVEIntel": {
            "url": "https://integrate.api.nvidia.com/v1/chat/completions",
            "key": KEYS["nvidia"],
            "model": "nvidia/llama-3.3-nemotron-super-49b-v1.5",  # Smart CVE reasoning
            "provider": "NVIDIA NIM"
        },
        "ExploitGen": {
            "url": "https://integrate.api.nvidia.com/v1/chat/completions",
            "key": KEYS["nvidia"],
            "model": "minimaxai/minimax-m2.7",  # SWE-Bench 78%! Best free coder
            "provider": "NVIDIA NIM"
        },
    },

    # ══════════════════════════════════════════
    # MID TIER (~$20-50/month) - Claude + GPT + Gemini
    # Best value for money!
    # ══════════════════════════════════════════
    "mid": {
        "Planner": {
            "url": "https://api.anthropic.com/v1/messages",
            "key": KEYS["anthropic"],
            "model": "claude-sonnet-4-20260514",
            "provider": "Anthropic",
            "api_type": "anthropic"
        },
        "Hacker": {
            "url": "https://api.openai.com/v1/chat/completions",
            "key": KEYS["openai"],
            "model": "gpt-4.1-mini",
            "provider": "OpenAI"
        },
        "Analyst": {
            "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
            "key": KEYS["google"],
            "model": "gemini-2.5-pro",
            "provider": "Google AI"
        },
        "Reporter": {
            "url": "https://api.openai.com/v1/chat/completions",
            "key": KEYS["openai"],
            "model": "gpt-4.1-mini",
            "provider": "OpenAI"
        },
        "CVEIntel": {
            "url": "https://api.openai.com/v1/chat/completions",
            "key": KEYS["openai"],
            "model": "gpt-4.1-nano",
            "provider": "OpenAI"
        },
        "ExploitGen": {
            "url": "https://api.anthropic.com/v1/messages",
            "key": KEYS["anthropic"],
            "model": "claude-sonnet-4-20260514",
            "provider": "Anthropic",
            "api_type": "anthropic"
        },
    },

    # ══════════════════════════════════════════
    # PREMIUM TIER (~$100-200/month) - Full Claude Opus
    # Maximum intelligence, no compromises
    # ══════════════════════════════════════════
    "premium": {
        "Planner": {
            "url": "https://api.anthropic.com/v1/messages",
            "key": KEYS["anthropic"],
            "model": "claude-opus-4-20260416",
            "provider": "Anthropic",
            "api_type": "anthropic"
        },
        "Hacker": {
            "url": "https://api.anthropic.com/v1/messages",
            "key": KEYS["anthropic"],
            "model": "claude-sonnet-4-20260514",
            "provider": "Anthropic",
            "api_type": "anthropic"
        },
        "Analyst": {
            "url": "https://api.anthropic.com/v1/messages",
            "key": KEYS["anthropic"],
            "model": "claude-opus-4-20260416",
            "provider": "Anthropic",
            "api_type": "anthropic"
        },
        "Reporter": {
            "url": "https://api.anthropic.com/v1/messages",
            "key": KEYS["anthropic"],
            "model": "claude-sonnet-4-20260514",
            "provider": "Anthropic",
            "api_type": "anthropic"
        },
        "CVEIntel": {
            "url": "https://api.openai.com/v1/chat/completions",
            "key": KEYS["openai"],
            "model": "gpt-4.1",
            "provider": "OpenAI"
        },
        "ExploitGen": {
            "url": "https://api.anthropic.com/v1/messages",
            "key": KEYS["anthropic"],
            "model": "claude-opus-4-20260416",
            "provider": "Anthropic",
            "api_type": "anthropic"
        },
    },
}

# ─────────────────────────────────────────────
# ACTIVE CONFIG (auto-selected from tier)
# ─────────────────────────────────────────────
AGENT_CONFIG = TIERS[ACTIVE_TIER]
