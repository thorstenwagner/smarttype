"""
SmartType Unit Tests
====================
Tests AI text completion with real API calls in DE and EN.
Verifies that sentences are correctly and meaningfully completed.
"""

import os
import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from smarttype import complete_with_ai, load_prompt, client, MODEL

SCRIPT_DIR = Path(__file__).parent
PROMPT_DE = load_prompt("de")
PROMPT_EN = load_prompt("en")


def complete(text: str, lang: str = "de", context: str = "") -> str:
    """Helper: Completes text using the appropriate prompt."""
    import smarttype
    old_prompt = smarttype.current_prompt
    smarttype.current_prompt = PROMPT_DE if lang == "de" else PROMPT_EN
    try:
        result = complete_with_ai(text, context_before=context)
    finally:
        smarttype.current_prompt = old_prompt
    return result


def verify(result: str, expected_words: list[str], forbidden_words: list[str] = None,
           must_end_with: str = None, msg: str = "") -> None:
    """Verifies the result contains expected words and is correct."""
    result_lower = result.lower()
    for word in expected_words:
        assert word.lower() in result_lower, \
            f"{msg} Erwartet '{word}' in: '{result}'"
    if forbidden_words:
        for word in forbidden_words:
            assert word.lower() not in result_lower, \
                f"{msg} Unerwartetes '{word}' in: '{result}'"
    if must_end_with:
        assert result.rstrip().endswith(must_end_with), \
            f"{msg} Erwartet Ende mit '{must_end_with}': '{result}'"


class TestGermanCompletion(unittest.TestCase):
    """Tests for German text completion."""

    def test_articles_and_prepositions(self):
        """'Katze schläft Sofa' → 'Die Katze schläft auf dem Sofa.'"""
        result = complete("Katze schläft Sofa", lang="de")
        verify(result,
               expected_words=["die", "katze", "schläft", "auf", "dem", "sofa"],
               must_end_with=".", msg="Artikel+Präposition:")
        print(f"  OK: '{result}'")

    def test_auxiliary_verb(self):
        """'Ich morgen Arzt gehen' → Hilfsverb + Präposition nötig."""
        result = complete("Ich morgen Arzt gehen", lang="de")
        verify(result,
               expected_words=["ich", "morgen", "arzt", "gehen"],
               must_end_with=".", msg="Hilfsverb:")
        # Muss 'muss' oder 'werde' + 'zum' enthalten
        r = result.lower()
        self.assertTrue(
            ("muss" in r or "werde" in r or "will" in r) and "zum" in r,
            f"Erwartet Hilfsverb + 'zum': '{result}'"
        )
        print(f"  OK: '{result}'")

    def test_abbreviated_swimming(self):
        """'wln wr eign ma schw ghn' → 'Wollen wir eigentlich mal schwimmen gehen?'"""
        result = complete("wln wr eign ma schw ghn", lang="de")
        verify(result,
               expected_words=["wollen", "wir", "eigentlich", "mal", "schwimmen", "gehen"],
               must_end_with="?", msg="Abkürzungen:")
        print(f"  OK: '{result}'")

    def test_abbreviated_hobbies(self):
        """'ih hbe sps bei vln din abr bsors brtsple' → korrekter Satz über Brettspiele."""
        result = complete("ih hbe sps bei vln din abr bsors brtsple", lang="de")
        verify(result,
               expected_words=["ich", "habe", "spaß", "vielen", "dingen", "besonders", "brettspielen"],
               must_end_with=".", msg="Stark abgekürzt:")
        print(f"  OK: '{result}'")

    def test_two_sentences(self):
        """'mir geht gut. Keine schmerzen' → Zwei grammatisch korrekte Sätze."""
        result = complete("mir geht gut. Keine schmerzen", lang="de")
        verify(result,
               expected_words=["mir", "geht", "gut", "keine", "schmerzen"],
               msg="Zwei Sätze:")
        # Sollte 'es' ergänzen und 'Ich habe' oder ähnlich
        self.assertIn("es", result.lower(), f"Erwartet 'es' in: '{result}'")
        self.assertTrue(
            result.count(".") >= 2 or result.count("!") >= 1,
            f"Erwartet mindestens 2 Satzzeichen: '{result}'"
        )
        print(f"  OK: '{result}'")

    def test_context_grilling(self):
        """Mit Kontext 'Grillen' → sinnvolle Antwort zum Mitbringen."""
        result = complete("knn ich etws mtbrngn", lang="de",
                          context="Am Samstag grillen wir bei mir.")
        verify(result,
               expected_words=["kann", "ich", "etwas", "mitbringen"],
               must_end_with="?", msg="Kontext Grillen:")
        print(f"  OK: '{result}'")

    def test_question_time(self):
        """'Hst du hte Zt?' → 'Hast du heute Zeit?'"""
        result = complete("Hst du hte Zt?", lang="de")
        verify(result,
               expected_words=["hast", "du", "heute", "zeit"],
               must_end_with="?", msg="Frage Zeit:")
        print(f"  OK: '{result}'")

    def test_direction(self):
        """'Knnst du mr den wg zum bhnhf erkrn' → korrekter Satz."""
        result = complete("Knnst du mr den wg zum bhnhf erkrn", lang="de")
        verify(result,
               expected_words=["kannst", "du", "mir", "weg", "bahnhof", "erklären"],
               must_end_with="?", msg="Wegbeschreibung:")
        print(f"  OK: '{result}'")

    def test_weather(self):
        """'ds wttr ist hte shr schn' → korrekter Wettersatz."""
        result = complete("ds wttr ist hte shr schn", lang="de")
        verify(result,
               expected_words=["wetter", "ist", "heute", "sehr", "schön"],
               must_end_with=".", msg="Wetter:")
        print(f"  OK: '{result}'")


class TestEnglishCompletion(unittest.TestCase):
    """Tests for English text completion."""

    def test_articles_and_prepositions(self):
        """'cat sleeping sofa' → 'The cat is sleeping on the sofa.'"""
        result = complete("cat sleeping sofa", lang="en")
        verify(result,
               expected_words=["the", "cat", "sleeping", "on", "sofa"],
               must_end_with=".", msg="Articles:")
        print(f"  OK: '{result}'")

    def test_auxiliary_verb(self):
        """'I tomorrow doctor go' → need auxiliary + preposition."""
        result = complete("I tomorrow doctor go", lang="en")
        verify(result,
               expected_words=["i", "tomorrow", "doctor"],
               must_end_with=".", msg="Auxiliary:")
        r = result.lower()
        self.assertTrue(
            "to the" in r or "to a" in r,
            f"Expected 'to the/a doctor': '{result}'"
        )
        print(f"  OK: '{result}'")

    def test_abbreviated_swimming(self):
        """'wnt we actly go swmmng' → correct swimming question."""
        result = complete("wnt we actly go swmmng", lang="en")
        verify(result,
               expected_words=["want", "actually", "go", "swimming"],
               must_end_with="?", msg="Swimming:")
        print(f"  OK: '{result}'")

    def test_abbreviated_hobbies(self):
        """'i hve fun mny thngs but espcly bord gmes' → correct hobby sentence."""
        result = complete("i hve fun mny thngs but espcly bord gmes", lang="en")
        verify(result,
               expected_words=["have", "fun", "many", "things", "especially", "board", "games"],
               must_end_with=".", msg="Hobbies:")
        print(f"  OK: '{result}'")

    def test_two_sentences(self):
        """'me feeling good. no pain' → Two correct sentences."""
        result = complete("me feeling good. no pain", lang="en")
        verify(result,
               expected_words=["feeling", "good", "no", "pain"],
               msg="Two sentences:")
        self.assertTrue(
            result.count(".") >= 2 or result.count("!") >= 1,
            f"Expected at least 2 punctuation marks: '{result}'"
        )
        print(f"  OK: '{result}'")

    def test_context_barbecue(self):
        """With context 'barbecue' → meaningful offer to bring something."""
        result = complete("cn i brng smthng", lang="en",
                          context="We're having a barbecue on Saturday.")
        verify(result,
               expected_words=["can", "i", "bring", "something"],
               must_end_with="?", msg="Context BBQ:")
        print(f"  OK: '{result}'")

    def test_question_time(self):
        """'Do yu hve tme tdy?' → 'Do you have time today?'"""
        result = complete("Do yu hve tme tdy?", lang="en")
        verify(result,
               expected_words=["do", "you", "have", "time", "today"],
               must_end_with="?", msg="Question time:")
        print(f"  OK: '{result}'")

    def test_directions(self):
        """'cn yu tll me hw to gt to th sttio' → correct direction question."""
        result = complete("cn yu tll me hw to gt to th sttion", lang="en")
        verify(result,
               expected_words=["can", "you", "tell", "me", "how", "to", "get", "station"],
               must_end_with="?", msg="Directions:")
        print(f"  OK: '{result}'")

    def test_weather(self):
        """'th wthr is vry nce tdy' → correct weather sentence."""
        result = complete("th wthr is vry nce tdy", lang="en")
        verify(result,
               expected_words=["weather", "is", "very", "nice", "today"],
               must_end_with=".", msg="Weather:")
        print(f"  OK: '{result}'")


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  SmartType Unit Tests")
    print("=" * 55 + "\n")
    unittest.main(verbosity=2)
