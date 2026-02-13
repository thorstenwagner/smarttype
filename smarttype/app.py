"""
SmartType - Core Application
==============================
AI text completion engine: hotkey listener, clipboard handling,
Claude API integration, and toast notifications.
"""

import re
import os
import sys
import time
import threading
import winsound

import tkinter as tk

import keyboard
import pyperclip
import anthropic
from pathlib import Path
from dotenv import load_dotenv

# ── Package-level paths ────────────────────────────────────────

# Support PyInstaller frozen mode
if getattr(sys, 'frozen', False):
    PACKAGE_DIR = Path(sys._MEIPASS) / "smarttype"
else:
    PACKAGE_DIR = Path(__file__).parent
PROMPTS_DIR = PACKAGE_DIR / "prompts"

# ── Configuration ──────────────────────────────────────────────

# Load .env from exe directory (frozen) or current working directory
if getattr(sys, 'frozen', False):
    _exe_dir = Path(sys.executable).parent
    _user_env = _exe_dir / ".env"
else:
    _user_env = Path.cwd() / ".env"
if _user_env.exists():
    load_dotenv(_user_env)
else:
    load_dotenv()

API_KEY = os.getenv("CLAUDE_API_KEY", "").strip()
HOTKEY = os.getenv("SMARTTYPE_HOTKEY", "ctrl+shift+j")
LANG_TOGGLE_HOTKEY = os.getenv("SMARTTYPE_LANG_HOTKEY", "ctrl+shift+g")
MARKER_TOGGLE_HOTKEY = os.getenv("SMARTTYPE_MARKER_HOTKEY", "ctrl+shift+h")
MODEL = os.getenv("SMARTTYPE_MODEL", "claude-sonnet-4-5-20250929")

# Language settings (changeable at runtime)
current_language = os.getenv("SMARTTYPE_LANGUAGE", "de")
current_prompt = ""

# Marker mode: when True, requires ... prefix; when False, completes entire line
marker_mode = False

LANG_NAMES = {"de": "Deutsch", "en": "English"}

# Claude Client (initialized in main after API key is available)
client = None

# Prevents concurrent processing
_processing = False


def load_prompt(lang: str) -> str:
    """Loads the system prompt for the given language."""
    # First check user's working directory
    user_prompt = Path.cwd() / f"prompt_{lang}.txt"
    if user_prompt.exists():
        return user_prompt.read_text(encoding="utf-8").strip()
    # Fall back to bundled prompts
    pkg_prompt = PROMPTS_DIR / f"prompt_{lang}.txt"
    if pkg_prompt.exists():
        return pkg_prompt.read_text(encoding="utf-8").strip()
    print(f"[SmartType] ERROR: Prompt file not found: prompt_{lang}.txt")
    sys.exit(1)


# ── AI Completion ────────────────────────────────────────────────

def complete_with_ai(incomplete_text: str, context_before: str = "", context_after: str = "") -> str:
    """Sends incomplete text to Claude for completion."""
    # Language-specific instruction prefix
    if current_language == "de":
        prefix = "Bitte vervollständige folgenden abgekürzten Text: "
    else:
        prefix = "Please complete the following abbreviated text: "

    user_msg = ""
    if context_before.strip():
        user_msg += f"Previous context: {context_before.strip()}\n\n"
    user_msg += prefix + incomplete_text.strip()
    if context_after.strip():
        user_msg += f"\n\nFollowing context: {context_after.strip()}"

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=current_prompt,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text.strip()


# ── Text Field Processing ───────────────────────────────────────

def process_textfield():
    """Reads backwards from cursor, completes the text."""
    global _processing

    if _processing:
        return
    _processing = True

    try:
        # Save current clipboard
        try:
            old_clipboard = pyperclip.paste()
        except Exception:
            old_clipboard = ""

        # Clear clipboard to detect fresh copy
        pyperclip.copy("")
        time.sleep(0.05)

        # Select everything from cursor to beginning of text field and copy
        keyboard.send("ctrl+shift+home")
        time.sleep(0.1)
        keyboard.send("ctrl+c")
        time.sleep(0.15)
        text_before_cursor = pyperclip.paste()

        if not text_before_cursor or not text_before_cursor.strip():
            keyboard.send("right")
            print("[SmartType] No text found.")
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            try:
                pyperclip.copy(old_clipboard)
            except Exception:
                pass
            return

        if marker_mode:
            # Marker mode: find ... and complete only the text after it
            if "..." not in text_before_cursor:
                keyboard.send("right")
                print("[SmartType] No ... marker found.")
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                try:
                    pyperclip.copy(old_clipboard)
                except Exception:
                    pass
                return

            marker_pos = text_before_cursor.rfind("...")
            incomplete = text_before_cursor[marker_pos + 3:]

            if not incomplete.strip():
                keyboard.send("right")
                print("[SmartType] No text after ... found.")
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                try:
                    pyperclip.copy(old_clipboard)
                except Exception:
                    pass
                return

            # Keep everything before the ... marker as prefix
            prefix = text_before_cursor[:marker_pos]
        else:
            # Full line mode: complete the entire selected text
            incomplete = text_before_cursor
            prefix = ""

        print(f"[SmartType] Processing: \"{incomplete.strip()[:60]}\"")

        # Feedback sound: processing started
        winsound.Beep(800, 150)

        completed = complete_with_ai(incomplete)

        print(f"  Result: \"{completed[:60]}\"")

        # Re-select everything from cursor to start (selection may have been lost during API call)
        keyboard.send("right")
        time.sleep(0.05)
        keyboard.send("ctrl+shift+home")
        time.sleep(0.1)

        # Replace entire selection with prefix + completed text
        pyperclip.copy(prefix + completed)
        time.sleep(0.05)
        keyboard.send("ctrl+v")
        time.sleep(0.2)

        # Feedback sound: done
        winsound.Beep(1200, 150)
        time.sleep(0.1)
        winsound.Beep(1500, 150)

        print("[SmartType] Done!\n")

        # Restore clipboard after short delay
        time.sleep(1.0)
        try:
            pyperclip.copy(old_clipboard)
        except Exception:
            pass

    except anthropic.APIError as e:
        print(f"[SmartType] API error: {e}")
        winsound.MessageBeep(winsound.MB_ICONHAND)
    except Exception as e:
        print(f"[SmartType] Error: {e}")
        winsound.MessageBeep(winsound.MB_ICONHAND)
    finally:
        _processing = False


def on_hotkey():
    """Called when the hotkey is pressed."""
    threading.Thread(target=process_textfield, daemon=True).start()


def show_toast(message: str, duration_ms: int = 1500):
    """Shows a brief on-screen notification (toast) at the top and bottom."""
    def _show():
        root = tk.Tk()
        root.withdraw()

        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()

        windows = []
        for position in ("top", "bottom"):
            win = tk.Toplevel(root)
            win.overrideredirect(True)
            win.attributes("-topmost", True)
            win.attributes("-alpha", 0.9)
            win.configure(bg="#1e1e2e")

            label = tk.Label(
                win, text=message, font=("Segoe UI", 18, "bold"),
                fg="#cdd6f4", bg="#1e1e2e", padx=30, pady=15,
            )
            label.pack()

            win.update_idletasks()
            w = win.winfo_reqwidth()
            h = win.winfo_reqheight()
            x = (screen_w - w) // 2

            if position == "top":
                y = 80
            else:
                y = screen_h - h - 80

            win.geometry(f"{w}x{h}+{x}+{y}")
            windows.append(win)

        def _close():
            for win in windows:
                win.destroy()
            root.destroy()

        root.after(duration_ms, _close)
        root.mainloop()

    threading.Thread(target=_show, daemon=True).start()


def toggle_language():
    """Toggles between German and English."""
    global current_language, current_prompt
    current_language = "en" if current_language == "de" else "de"
    current_prompt = load_prompt(current_language)
    lang_name = LANG_NAMES.get(current_language, current_language)
    print(f"[SmartType] Language switched: {lang_name}")
    show_toast(f"\U0001F310 SmartType: {lang_name}")
    if current_language == "de":
        winsound.Beep(600, 150)
        time.sleep(0.05)
        winsound.Beep(800, 150)
    else:
        winsound.Beep(800, 150)
        time.sleep(0.05)
        winsound.Beep(1100, 150)


def toggle_marker_mode():
    """Toggles between marker mode (...prefix) and full line mode."""
    global marker_mode
    marker_mode = not marker_mode
    mode_name = "...prefix" if marker_mode else "full line"
    print(f"[SmartType] Marker mode: {mode_name}")
    show_toast(f"SmartType: {mode_name}")
    if marker_mode:
        winsound.Beep(900, 100)
        time.sleep(0.05)
        winsound.Beep(1100, 100)
    else:
        winsound.Beep(1100, 100)
        time.sleep(0.05)
        winsound.Beep(900, 100)
