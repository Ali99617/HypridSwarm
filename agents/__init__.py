# agents/__init__.py
from agents.prompts import (
    PROMPT_PLANNER, PROMPT_HACKER, PROMPT_ANALYST,
    PROMPT_REPORTER, PROMPT_CVE_INTEL, PROMPT_EXPLOIT_GEN
)
from agents.query import query_agent, extract_command
from agents.modes import ATTACK_MODES, get_mode_prompt, list_modes
