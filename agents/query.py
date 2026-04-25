# agents/query.py
# Handles AI agent API communication and command extraction
# Supports: OpenAI-compatible (OpenAI, Groq, NVIDIA, Google, Cerebras) + Anthropic native

import re
import json
import requests
from rich.markdown import Markdown
from rich.live import Live
from config import AGENT_CONFIG


def query_agent(role_name, messages, console, color):
    """Send messages to an AI agent and stream the response.
    Auto-detects API type from config (OpenAI-compatible vs Anthropic native).
    """
    config = AGENT_CONFIG[role_name]
    api_type = config.get("api_type", "openai")  # default to OpenAI-compatible
    
    console.print(f"[{color}]>>> {role_name} (Using {config['provider']} | {config['model']}) is thinking...[/{color}]")
    
    if api_type == "anthropic":
        return _query_anthropic(role_name, messages, config, console)
    else:
        return _query_openai(role_name, messages, config, console)


def _query_openai(role_name, messages, config, console):
    """Query OpenAI-compatible APIs (OpenAI, Groq, NVIDIA NIM, Google, Cerebras)."""
    headers = {
        "Authorization": f"Bearer {config['key']}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    payload = {
        "model": config['model'],
        "messages": messages,
        "max_tokens": 2048,
        "stream": True
    }
    
    response_content = ""
    try:
        with requests.post(config['url'], headers=headers, json=payload, stream=True, timeout=120) as response:
            if response.status_code != 200:
                console.print(f"[bold red]   [!] Error from {config['provider']} API: {response.text[:300]}[/bold red]")
                return None
                
            with Live(console=console, refresh_per_second=20) as live:
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data_chunk = line_str[6:]
                            if data_chunk.strip() == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data_chunk)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        response_content += content
                                        live.update(Markdown(f"**{role_name}:** " + response_content))
                            except json.JSONDecodeError:
                                pass
        return response_content
    except Exception as e:
        console.print(f"\n[bold red][ERROR] Failed to connect to {config['provider']} API: {e}[/bold red]")
        return None


def _query_anthropic(role_name, messages, config, console):
    """Query Anthropic's native Messages API (Claude models)."""
    headers = {
        "x-api-key": config['key'],
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    
    # Anthropic requires system message separated from messages
    system_msg = ""
    api_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_msg = msg["content"]
        else:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
    
    payload = {
        "model": config['model'],
        "max_tokens": 2048,
        "system": system_msg,
        "messages": api_messages,
        "stream": True
    }
    
    response_content = ""
    try:
        with requests.post(config['url'], headers=headers, json=payload, stream=True, timeout=120) as response:
            if response.status_code != 200:
                console.print(f"[bold red]   [!] Error from Anthropic API: {response.text[:300]}[/bold red]")
                return None
            
            with Live(console=console, refresh_per_second=20) as live:
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data_chunk = line_str[6:]
                            if data_chunk.strip() == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data_chunk)
                                # Anthropic stream format
                                if chunk.get("type") == "content_block_delta":
                                    delta = chunk.get("delta", {})
                                    text = delta.get("text", "")
                                    if text:
                                        response_content += text
                                        live.update(Markdown(f"**{role_name}:** " + response_content))
                            except json.JSONDecodeError:
                                pass
        return response_content
    except Exception as e:
        console.print(f"\n[bold red][ERROR] Failed to connect to Anthropic API: {e}[/bold red]")
        return None


def extract_command(text):
    """Extract a bash command from the AI's Markdown code block."""
    pattern = r"```(?:bash|sh)\n([\s\S]*?)```"
    matches = re.finditer(pattern, text)
    commands = [match.group(1).strip() for match in matches]
    
    if not commands:
         pattern = r"```\n([\s\S]*?)```"
         matches = re.finditer(pattern, text)
         commands = [match.group(1).strip() for match in matches]
         
    return commands[0] if commands else None
