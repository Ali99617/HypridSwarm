# memory/workspace.py
# Handles loading and saving workspace memory (JSON-based persistence)

import os
import json

WORKSPACE_DIR = "workspaces"


def load_workspace(workspace_name, console):
    """Load a workspace's memory from a JSON file. Returns the planner_memory list or empty list."""
    if not os.path.exists(WORKSPACE_DIR):
        os.makedirs(WORKSPACE_DIR)
    
    workspace_file = os.path.join(WORKSPACE_DIR, f"{workspace_name}.json")
    if os.path.exists(workspace_file):
        with open(workspace_file, "r", encoding="utf-8") as f:
            memory = json.load(f)
        console.print(f"[bold green][LOADED] Workspace '{workspace_name}' restored successfully! ({len(memory)} messages in memory)[/bold green]")
        return memory
    
    return []


def save_workspace(workspace_name, planner_memory, console):
    """Save the planner's memory to a JSON workspace file."""
    if not os.path.exists(WORKSPACE_DIR):
        os.makedirs(WORKSPACE_DIR)
    
    workspace_file = os.path.join(WORKSPACE_DIR, f"{workspace_name}.json")
    with open(workspace_file, "w", encoding="utf-8") as f:
        json.dump(planner_memory, f, indent=4, ensure_ascii=False)
    console.print(f"[dim][SAVED] State saved to workspace: {workspace_name}[/dim]")
