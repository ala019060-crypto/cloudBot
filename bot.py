import os
import time
import json
import re
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import google.generativeai as genai
from PIL import Image

target_url = "https://example.com"

PRIVATE_KEY = os.environ.get("PRIVATE_KEY_1")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

def clean_json_response(text):
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

def run_bot():
    with sync_playwright() as p:
        print("System: Initializing stealth browser environment...")
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        stealth_sync(page)

        print(f"System: Navigating to target URL: {target_url}")
        page.goto(target_url, wait_until="networkidle")
        time.sleep(5)

        screenshot_path = "screen.png"
        page.screenshot(path=screenshot_path)
        print("System: Captured screen state. Forwarding to AI model...")

        prompt = (
            "Analyze this screenshot of a Web3 interface. "
            "Identify the primary action button (e.g., 'Connect Wallet', 'Claim', 'Start', 'Login', 'Harvest'). "
            "Calculate its center X and Y coordinates for a 1280x720 screen. "
            "Return ONLY a raw JSON object formatted exactly like this, with no markdown formatting: "
            '{"x": 100, "y": 200, "found": true}. If no button is found, return {"x": 0, "y": 0, "found": false}.'
        )

        try:
            raw_image = Image.open(screenshot_path)
            response = model.generate_content([prompt, raw_image])
            cleaned_response = clean_json_response(response.text.strip())
            print(f"System: AI Response parsed: {cleaned_response}")

            decision = json.loads(cleaned_response)
            if decision.get("found") and decision["x"] > 0:
                target_x = int(decision["x"])
                target_y = int(decision["y"])
                print(f"System: Target acquired at X:{target_x}, Y:{target_y}. Executing human-like click...")
                
                page.mouse.move(target_x, target_y)
                time.sleep(1)
                page.mouse.click(target_x, target_y)
                
                time.sleep(5)
                page.screenshot(path="after_click.png")
                print("System: Execution successful. Post-action state captured.")
            else:
                print("System: No actionable target identified on screen.")
                
        except Exception as e:
            print(f"System: Critical failure in parsing AI decision. Error: {e}")

        browser.close()

if __name__ == "__main__":
    print("System: Automation sequence initiated.")
    run_bot()
    print("System: Automation sequence terminated.")
