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
MODEL = os.getenv("SMARTTYPE_MODEL", "claude-sonnet-4-20250514")
LANGUAGE = os.getenv("SMARTTYPE_LANGUAGE", "de")

if not API_KEY:
    print("[SmartType] FEHLER: CLAUDE_API_KEY nicht gesetzt!")
    print("  Bitte in .env Datei eintragen: CLAUDE_API_KEY=sk-ant-...")
    sys.exit(1)

# Prompt laden
prompt_file = SCRIPT_DIR / f"prompt_{LANGUAGE}.txt"
if not prompt_file.exists():
    print(f"[SmartType] FEHLER: Prompt-Datei nicht gefunden: {prompt_file}")
    sys.exit(1)
SYSTEM_PROMPT = prompt_file.read_text(encoding="utf-8").strip()

# Claude Client
client = anthropic.Anthropic(api_key=API_KEY)

# Pattern: ...text...
PATTERN = re.compile(r"\.\.\.([\s\S]+?)\.\.\.")

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
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text.strip()


# ── Textfeld-Verarbeitung ───────────────────────────────────────

def process_textfield():
    """Liest das aktuelle Textfeld, vervollständigt ...Text... Bereiche, fügt Ergebnis ein."""
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

        # Alles auswählen und kopieren
        keyboard.send("ctrl+a")
        time.sleep(0.15)
        keyboard.send("ctrl+c")
        time.sleep(0.2)

        # Text aus Zwischenablage lesen
        text = pyperclip.paste()

        if not text or not PATTERN.search(text):
            print("[SmartType] Keine ...Markierungen... gefunden.")
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            try:
                pyperclip.copy(old_clipboard)
            except Exception:
                pass
            return

        print(f"[SmartType] Verarbeite Text ({len(text)} Zeichen)...")

        # Feedback-Sound: Verarbeitung startet
        winsound.Beep(800, 150)

        # Alle ...text... Bereiche von hinten nach vorne ersetzen
        # (damit Positionen stabil bleiben)
        matches = list(PATTERN.finditer(text))
        matches.reverse()

        for match in matches:
            incomplete = match.group(1)

            # Kontext extrahieren (bis zu 300 Zeichen vor/nach)
            ctx_start = max(0, match.start() - 300)
            ctx_end = min(len(text), match.end() + 300)
            context_before = text[ctx_start:match.start()]
            context_after = text[match.end():ctx_end]

            print(f"  Vervollständige: \"{incomplete.strip()[:60]}...\"")

            completed = complete_with_ai(incomplete, context_before, context_after)

            print(f"  Ergebnis: \"{completed[:60]}...\"")

            # Ersetzen (inklusive der ... Marker)
            text = text[:match.start()] + completed + text[match.end():]

        # Ergebnis einfügen
        pyperclip.copy(text)
        time.sleep(0.05)
        keyboard.send("ctrl+a")
        time.sleep(0.1)
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


# ── Hauptprogramm ───────────────────────────────────────────────

def main():
    print()
    print("=" * 55)
    print("  SmartType - KI Textvervollständigung")
    print("=" * 55)
    print(f"  Hotkey:      {HOTKEY}")
    print(f"  Sprache:     {LANGUAGE}")
    print(f"  Modell:      {MODEL}")
    print(f"  Markierung:  ...text...")
    print("=" * 55)
    print()
    print("  Markiere unvollständigen Text mit ... am Anfang")
    print("  und Ende, dann drücke den Hotkey.")
    print()
    print("  Beispiel:")
    print('    "...Katze schläft Sofa..."')
    print('    → "Die Katze schläft auf dem Sofa."')
    print()
    print('    "Hallo, ...ich mrgn arzt ghn... und danach"')
    print('    → "Hallo, ich muss morgen zum Arzt gehen und danach"')
    print()
    print(f"  Drücke {HOTKEY} zum Vervollständigen.")
    print("  Drücke Strg+C zum Beenden.")
    print()

    keyboard.add_hotkey(HOTKEY, on_hotkey, suppress=True)

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
