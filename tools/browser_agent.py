# tools/browser_agent.py
# Browser Automation Agent - Uses Playwright for headless Chrome control
# Enables the swarm to interact with web applications (login, navigate, test XSS, etc.)

import sys
import json

def check_playwright():
    """Check if playwright is installed."""
    try:
        import playwright
        return True
    except ImportError:
        return False


def browse_url(url, actions=None, screenshot_path=None):
    """
    Navigate to a URL and optionally perform actions.
    
    Args:
        url: Target URL to visit
        actions: List of action dicts, e.g. [{"type":"click","selector":"#btn"}, {"type":"fill","selector":"#input","value":"test"}]
        screenshot_path: Optional path to save a screenshot
    
    Returns:
        dict with page title, content snippet, cookies, and any results
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"error": "playwright not installed. Run: pip install playwright && playwright install chromium"}
    
    result = {
        "url": url,
        "title": "",
        "status": 0,
        "content_snippet": "",
        "cookies": [],
        "console_logs": [],
        "actions_performed": [],
    }
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Capture console logs
            page.on("console", lambda msg: result["console_logs"].append(f"{msg.type}: {msg.text}"))
            
            # Navigate
            response = page.goto(url, wait_until="networkidle", timeout=30000)
            result["status"] = response.status if response else 0
            result["title"] = page.title()
            result["content_snippet"] = page.content()[:2000]
            
            # Perform actions if specified
            if actions:
                for action in actions:
                    action_type = action.get("type", "")
                    selector = action.get("selector", "")
                    value = action.get("value", "")
                    
                    try:
                        if action_type == "click":
                            page.click(selector, timeout=5000)
                            result["actions_performed"].append(f"clicked: {selector}")
                        elif action_type == "fill":
                            page.fill(selector, value, timeout=5000)
                            result["actions_performed"].append(f"filled: {selector} = {value}")
                        elif action_type == "type":
                            page.type(selector, value, timeout=5000)
                            result["actions_performed"].append(f"typed: {selector} = {value}")
                        elif action_type == "wait":
                            page.wait_for_timeout(int(value) if value else 1000)
                            result["actions_performed"].append(f"waited: {value}ms")
                        elif action_type == "screenshot":
                            path = value or "screenshot.png"
                            page.screenshot(path=path)
                            result["actions_performed"].append(f"screenshot: {path}")
                        elif action_type == "evaluate":
                            js_result = page.evaluate(value)
                            result["actions_performed"].append(f"js_result: {js_result}")
                    except Exception as e:
                        result["actions_performed"].append(f"FAILED {action_type} {selector}: {e}")
            
            # Save screenshot if requested
            if screenshot_path:
                page.screenshot(path=screenshot_path)
            
            # Get cookies
            result["cookies"] = [{"name": c["name"], "value": c["value"][:50], "domain": c.get("domain", "")} 
                                 for c in context.cookies()]
            
            browser.close()
    
    except Exception as e:
        result["error"] = str(e)
    
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/browser_agent.py <url> [screenshot_path]")
        sys.exit(1)
    
    url = sys.argv[1]
    screenshot = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not check_playwright():
        print(json.dumps({"error": "playwright not installed. Run: pip install playwright && playwright install chromium"}))
        sys.exit(1)
    
    result = browse_url(url, screenshot_path=screenshot)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
