"""
SmartType - CLI Entry Point
==============================
Handles startup, API key prompt, and hotkey registration.
"""

import sys
import time
import winsound

import keyboard
import anthropic

from smarttype import __version__
from smarttype.app import (
    API_KEY, HOTKEY, LANG_TOGGLE_HOTKEY, MARKER_TOGGLE_HOTKEY, MODEL,
    LANG_NAMES, current_language, marker_mode,
    load_prompt, on_hotkey, toggle_language, toggle_marker_mode,
)
from pathlib import Path
from dotenv import load_dotenv, set_key
import smarttype.app as app


def prompt_for_api_key():
    """Prompts user for API key and saves it to .env."""
    print()
    print("=" * 55)
    print("  SmartType - API Key Setup")
    print("=" * 55)
    print()
    print("  No Claude API key found.")
    print("  Get your key at: https://console.anthropic.com/")
    print()
    key = input("  Enter your Claude API key: ").strip()
    if not key:
        print("  No key entered. Exiting.")
        sys.exit(1)
    app.API_KEY = key
    # Save to .env file in current working directory
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        content = env_path.read_text(encoding="utf-8")
        import re
        if "CLAUDE_API_KEY=" in content:
            content = re.sub(
                r"CLAUDE_API_KEY=.*",
                f"CLAUDE_API_KEY={key}",
                content,
            )
        else:
            content += f"\nCLAUDE_API_KEY={key}\n"
        env_path.write_text(content, encoding="utf-8")
    else:
        env_path.write_text(f"CLAUDE_API_KEY={key}\n", encoding="utf-8")
    print()
    print(f"  API key saved to {env_path}")
    print()


def main():
    """Main entry point for SmartType."""
    if not app.API_KEY:
        prompt_for_api_key()

    # Initialize prompt and Claude client
    app.current_prompt = load_prompt(app.current_language)
    app.client = anthropic.Anthropic(api_key=app.API_KEY)

    print()
    print("=" * 55)
    print(f"  SmartType v{__version__} - AI Text Completion")
    print("=" * 55)
    print(f"  Complete:          {HOTKEY}")
    print(f"  Toggle language:   {LANG_TOGGLE_HOTKEY}")
    print(f"  Toggle ...marker:  {MARKER_TOGGLE_HOTKEY}")
    print(f"  Language:          {LANG_NAMES.get(app.current_language, app.current_language)}")
    print(f"  Model:             {MODEL}")
    print(f"  Marker mode:       {'ON (...prefix)' if app.marker_mode else 'OFF (full line)'}")
    print("=" * 55)
    print()
    print("  Write ... before incomplete text (marker mode),")
    print("  or complete entire line (full line mode).")
    print()
    print("  Examples:")
    print('    "...ih mss mrgn zm arzt ghn"')
    print('    \u2192 "Ich muss morgen zum Arzt gehen."')
    print()
    print('    "Hi, ...cn yu tll me hw to gt to th sttion"')
    print('    \u2192 "Hi, Can you tell me how to get to the station?"')
    print()
    print(f"  {HOTKEY} = Complete")
    print(f"  {LANG_TOGGLE_HOTKEY} = Toggle language DE/EN")
    print(f"  {MARKER_TOGGLE_HOTKEY} = Toggle ...marker mode")
    print("  Ctrl+C = Exit")
    print()

    keyboard.add_hotkey(HOTKEY, on_hotkey, suppress=True)
    keyboard.add_hotkey(LANG_TOGGLE_HOTKEY, toggle_language, suppress=True)
    keyboard.add_hotkey(MARKER_TOGGLE_HOTKEY, toggle_marker_mode, suppress=True)

    # Startup sound
    winsound.Beep(1000, 100)
    time.sleep(0.05)
    winsound.Beep(1200, 100)

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("\n[SmartType] Stopped.")


if __name__ == "__main__":
    main()
