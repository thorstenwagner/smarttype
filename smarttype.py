"""
SmartType - KI Textvervollständigung für beliebige Textfelder
=============================================================
Markiere unvollständigen Text mit ... am Anfang und Ende.
Drücke den Hotkey, und der Text wird automatisch vervollständigt.

Beispiel:
  Eingabe: "Hallo, ...ich mrgn zum arzt ghn... und danach gehe ich einkaufen."
  Ergebnis: "Hallo, ich muss morgen zum Arzt gehen und danach gehe ich einkaufen."
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

# ── Konfiguration ──────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
load_dotenv(SCRIPT_DIR / ".env")

API_KEY = os.getenv("CLAUDE_API_KEY")
HOTKEY = os.getenv("SMARTTYPE_HOTKEY", "ctrl+shift+j")
LANG_TOGGLE_HOTKEY = os.getenv("SMARTTYPE_LANG_HOTKEY", "ctrl+shift+g")
MODEL = os.getenv("SMARTTYPE_MODEL", "claude-sonnet-4-20250514")

# Spracheinstellungen (veränderbar zur Laufzeit)
current_language = os.getenv("SMARTTYPE_LANGUAGE", "de")
current_prompt = ""

LANG_NAMES = {"de": "Deutsch", "en": "English"}

if not API_KEY:
    print("[SmartType] FEHLER: CLAUDE_API_KEY nicht gesetzt!")
    print("  Bitte in .env Datei eintragen: CLAUDE_API_KEY=sk-ant-...")
    sys.exit(1)


def load_prompt(lang: str) -> str:
    """Lädt den System-Prompt für die angegebene Sprache."""
    prompt_file = SCRIPT_DIR / f"prompt_{lang}.txt"
    if not prompt_file.exists():
        print(f"[SmartType] FEHLER: Prompt-Datei nicht gefunden: {prompt_file}")
        sys.exit(1)
    return prompt_file.read_text(encoding="utf-8").strip()


current_prompt = load_prompt(current_language)

# Claude Client
client = anthropic.Anthropic(api_key=API_KEY)

# Pattern: ...text (ohne schließendes ..., endet am Cursor)
PATTERN = re.compile(r"\.\.\.([\s\S]+?)$")

# Verhindert gleichzeitige Verarbeitung
_processing = False


# ── KI-Vervollständigung ────────────────────────────────────────

def complete_with_ai(incomplete_text: str, context_before: str = "", context_after: str = "") -> str:
    """Sendet unvollständigen Text an Claude zur Vervollständigung."""
    user_msg = ""
    if context_before.strip():
        user_msg += f"Vorheriger Kontext: {context_before.strip()}\n\n"
    user_msg += incomplete_text.strip()
    if context_after.strip():
        user_msg += f"\n\nNachfolgender Kontext: {context_after.strip()}"

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=current_prompt,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text.strip()


# ── Textfeld-Verarbeitung ───────────────────────────────────────

def process_textfield():
    """Liest vom Cursor rückwärts bis zum ..., vervollständigt den Text."""
    global _processing

    if _processing:
        return
    _processing = True

    try:
        # Aktuelle Zwischenablage sichern
        try:
            old_clipboard = pyperclip.paste()
        except Exception:
            old_clipboard = ""

        # Zwischenablage leeren um frische Kopie zu erkennen
        pyperclip.copy("")
        time.sleep(0.05)

        # Alles vom Cursor bis Anfang markieren und kopieren
        keyboard.send("shift+home")
        time.sleep(0.1)
        keyboard.send("ctrl+c")
        time.sleep(0.15)
        text_before_cursor = pyperclip.paste()

        if not text_before_cursor or "..." not in text_before_cursor:
            # Selektion aufheben
            keyboard.send("right")
            print("[SmartType] Kein ... Marker gefunden.")
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            try:
                pyperclip.copy(old_clipboard)
            except Exception:
                pass
            return

        # Letztes ... finden
        marker_pos = text_before_cursor.rfind("...")
        incomplete = text_before_cursor[marker_pos + 3:]  # Text nach dem ...

        if not incomplete.strip():
            keyboard.send("right")
            print("[SmartType] Kein Text nach ... gefunden.")
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            try:
                pyperclip.copy(old_clipboard)
            except Exception:
                pass
            return

        # Selektion aufheben, dann nur ab ... bis Cursor selektieren
        keyboard.send("right")  # Cursor ans Ende (ursprüngliche Position)
        time.sleep(0.05)
        # Berechne Anzahl Zeichen ab ... bis Cursor (inkl. ...)
        chars_to_select = len(text_before_cursor) - marker_pos
        for _ in range(chars_to_select):
            keyboard.send("shift+left")
        time.sleep(0.1)

        print(f"[SmartType] Verarbeite: \"{incomplete.strip()[:60]}\"")

        # Feedback-Sound: Verarbeitung startet
        winsound.Beep(800, 150)

        completed = complete_with_ai(incomplete)

        print(f"  Ergebnis: \"{completed[:60]}\"")

        # Ergebnis einfügen (die Selektion ist noch aktiv — ersetzt ...text)
        pyperclip.copy(completed)
        time.sleep(0.05)
        keyboard.send("ctrl+v")
        time.sleep(0.2)

        # Feedback-Sound: Fertig
        winsound.Beep(1200, 150)
        time.sleep(0.1)
        winsound.Beep(1500, 150)

        print("[SmartType] Fertig!\n")

        # Zwischenablage nach kurzer Verzögerung wiederherstellen
        time.sleep(1.0)
        try:
            pyperclip.copy(old_clipboard)
        except Exception:
            pass

    except anthropic.APIError as e:
        print(f"[SmartType] API-Fehler: {e}")
        winsound.MessageBeep(winsound.MB_ICONHAND)
    except Exception as e:
        print(f"[SmartType] Fehler: {e}")
        winsound.MessageBeep(winsound.MB_ICONHAND)
    finally:
        _processing = False


def on_hotkey():
    """Wird beim Drücken des Hotkeys aufgerufen."""
    threading.Thread(target=process_textfield, daemon=True).start()


def show_toast(message: str, duration_ms: int = 1500):
    """Zeigt eine kurze Bildschirm-Meldung (Toast) oben und unten an."""
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
    """Wechselt zwischen Deutsch und Englisch."""
    global current_language, current_prompt
    current_language = "en" if current_language == "de" else "de"
    current_prompt = load_prompt(current_language)
    lang_name = LANG_NAMES.get(current_language, current_language)
    print(f"[SmartType] Sprache gewechselt: {lang_name}")
    show_toast(f"🌐 SmartType: {lang_name}")
    # Feedback: tief=de, hoch=en
    if current_language == "de":
        winsound.Beep(600, 150)
        time.sleep(0.05)
        winsound.Beep(800, 150)
    else:
        winsound.Beep(800, 150)
        time.sleep(0.05)
        winsound.Beep(1100, 150)


# ── Hauptprogramm ───────────────────────────────────────────────

def main():
    print()
    print("=" * 55)
    print("  SmartType - KI Textvervollständigung")
    print("=" * 55)
    print(f"  Vervollständigen:  {HOTKEY}")
    print(f"  Sprache wechseln:  {LANG_TOGGLE_HOTKEY}")
    print(f"  Sprache:           {LANG_NAMES.get(current_language, current_language)}")
    print(f"  Modell:            {MODEL}")
    print(f"  Markierung:        ...text")
    print("=" * 55)
    print()
    print("  Schreibe ... vor unvollständigem Text,")
    print("  setze den Cursor ans Ende und drücke den Hotkey.")
    print()
    print("  Beispiel:")
    print('    "Hallo, ...Katze schläft Sofa"  [Cursor hier]')
    print('    → "Hallo, Die Katze schläft auf dem Sofa."')
    print()
    print(f"  {HOTKEY} = Vervollständigen")
    print(f"  {LANG_TOGGLE_HOTKEY} = Sprache DE/EN umschalten")
    print("  Strg+C = Beenden")
    print()

    keyboard.add_hotkey(HOTKEY, on_hotkey, suppress=True)
    keyboard.add_hotkey(LANG_TOGGLE_HOTKEY, toggle_language, suppress=True)

    # Startup-Sound
    winsound.Beep(1000, 100)
    time.sleep(0.05)
    winsound.Beep(1200, 100)

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("\n[SmartType] Beendet.")


if __name__ == "__main__":
    main()
