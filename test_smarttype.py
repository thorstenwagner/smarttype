"""
SmartType Unit Tests
====================
Testet die KI-Vervollständigung mit echten API-Aufrufen in DE und EN.
"""

import os
import sys
import unittest
from pathlib import Path

# Projekt-Root zum Path hinzufügen
sys.path.insert(0, str(Path(__file__).parent))

from smarttype import complete_with_ai, load_prompt, client, MODEL

SCRIPT_DIR = Path(__file__).parent
PROMPT_DE = load_prompt("de")
PROMPT_EN = load_prompt("en")


def complete(text: str, lang: str = "de", context: str = "") -> str:
    """Hilfsfunktion: Vervollständigt Text mit dem passenden Prompt."""
    import smarttype
    old_prompt = smarttype.current_prompt
    smarttype.current_prompt = PROMPT_DE if lang == "de" else PROMPT_EN
    try:
        result = complete_with_ai(text, context_before=context)
    finally:
        smarttype.current_prompt = old_prompt
    return result


class TestGermanCompletion(unittest.TestCase):
    """Tests für deutsche Textvervollständigung."""

    def test_missing_articles(self):
        """Fehlende Artikel ergänzen."""
        result = complete("Katze schläft Sofa", lang="de")
        self.assertIn("Katze", result)
        self.assertIn("Sofa", result)
        # Sollte Artikel enthalten
        self.assertTrue(
            "Die" in result or "die" in result,
            f"Erwartet Artikel 'Die/die' in: {result}"
        )
        print(f"  DE Artikel: '{result}'")

    def test_missing_prepositions(self):
        """Fehlende Präpositionen ergänzen."""
        result = complete("Ich morgen Arzt gehen", lang="de")
        self.assertIn("Arzt", result)
        # Sollte 'zum' oder 'zum Arzt' enthalten
        self.assertTrue(
            "zum" in result.lower() or "arzt" in result.lower(),
            f"Erwartet Präposition in: {result}"
        )
        print(f"  DE Präposition: '{result}'")

    def test_abbreviated_words(self):
        """Abgekürzte Wörter vervollständigen."""
        result = complete("wln wr eign ma schw ghn", lang="de")
        self.assertTrue(
            "wollen" in result.lower() or "schwimmen" in result.lower(),
            f"Erwartet vervollständigte Wörter in: {result}"
        )
        print(f"  DE Abkürzungen: '{result}'")

    def test_heavily_abbreviated(self):
        """Stark abgekürzte Wörter."""
        result = complete("ih hbe sps bei vln din", lang="de")
        self.assertTrue(
            "habe" in result.lower() or "spaß" in result.lower() or "vielen" in result.lower(),
            f"Erwartet korrekte Wörter in: {result}"
        )
        print(f"  DE Stark abgekürzt: '{result}'")

    def test_multiple_sentences(self):
        """Mehrere Sätze vervollständigen."""
        result = complete("mir geht gut. Keine schmerzen", lang="de")
        self.assertTrue(
            "geht" in result.lower() and "schmerzen" in result.lower(),
            f"Erwartet beide Sätze in: {result}"
        )
        print(f"  DE Mehrere Sätze: '{result}'")

    def test_with_context(self):
        """Vervollständigung mit Kontext."""
        result = complete(
            "knn ich mtbrngn",
            lang="de",
            context="Am Samstag grillen wir bei mir."
        )
        self.assertTrue(
            len(result) > len("knn ich mtbrngn"),
            f"Erwartet längeren Text als Eingabe: {result}"
        )
        print(f"  DE Mit Kontext: '{result}'")

    def test_question(self):
        """Frage vervollständigen."""
        result = complete("Hst du hte Zt?", lang="de")
        self.assertTrue(
            "?" in result,
            f"Erwartet Fragezeichen in: {result}"
        )
        print(f"  DE Frage: '{result}'")


class TestEnglishCompletion(unittest.TestCase):
    """Tests für englische Textvervollständigung."""

    def test_missing_articles(self):
        """Missing articles."""
        result = complete("cat sleeping sofa", lang="en")
        self.assertIn("cat", result.lower())
        self.assertIn("sofa", result.lower())
        self.assertTrue(
            "the" in result.lower() or "a" in result.lower(),
            f"Expected article in: {result}"
        )
        print(f"  EN Articles: '{result}'")

    def test_missing_prepositions(self):
        """Missing prepositions."""
        result = complete("I tomorrow doctor go", lang="en")
        self.assertTrue(
            "doctor" in result.lower() and "go" in result.lower(),
            f"Expected preposition in: {result}"
        )
        print(f"  EN Preposition: '{result}'")

    def test_abbreviated_words(self):
        """Abbreviated words."""
        result = complete("wnt we actly go swmmng", lang="en")
        self.assertTrue(
            "want" in result.lower() or "swimming" in result.lower(),
            f"Expected completed words in: {result}"
        )
        print(f"  EN Abbreviated: '{result}'")

    def test_heavily_abbreviated(self):
        """Heavily abbreviated words."""
        result = complete("i hve fun mny thngs but espcly bord gmes", lang="en")
        self.assertTrue(
            "have" in result.lower() or "fun" in result.lower(),
            f"Expected correct words in: {result}"
        )
        print(f"  EN Heavily abbrev: '{result}'")

    def test_multiple_sentences(self):
        """Multiple sentences."""
        result = complete("me feeling good. no pain", lang="en")
        self.assertTrue(
            "feeling" in result.lower() or "good" in result.lower(),
            f"Expected both sentences in: {result}"
        )
        print(f"  EN Multiple sentences: '{result}'")

    def test_with_context(self):
        """Completion with context."""
        result = complete(
            "cn i brng smthng",
            lang="en",
            context="We're having a barbecue on Saturday."
        )
        self.assertTrue(
            len(result) > len("cn i brng smthng"),
            f"Expected longer text than input: {result}"
        )
        print(f"  EN With context: '{result}'")

    def test_question(self):
        """Question completion."""
        result = complete("Do yu hve tme tdy?", lang="en")
        self.assertTrue(
            "?" in result,
            f"Expected question mark in: {result}"
        )
        print(f"  EN Question: '{result}'")


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  SmartType Unit Tests")
    print("=" * 55 + "\n")
    unittest.main(verbosity=2)
