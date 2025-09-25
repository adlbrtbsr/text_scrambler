import random
from django.test import SimpleTestCase
from scrambler.utils import scramble_word, scramble_text


class UtilsTests(SimpleTestCase):
    def test_scramble_word_preserves_first_last(self):
        rng = random.Random(42)
        word = 'scramble'
        out = scramble_word(word, rng)
        self.assertEqual(out[0], 's')
        self.assertEqual(out[-1], 'e')

    def test_short_words_unchanged(self):
        rng = random.Random(42)
        for w in ['a', 'to', 'cat']:
            self.assertEqual(scramble_word(w, rng), w)

    def test_scramble_text_preserves_punctuation_and_whitespace(self):
        rng = random.Random(42)
        text = 'Hello, world!  New\nline.'
        out = scramble_text(text, rng)
        self.assertIn(',', out)
        self.assertIn('!', out)
        self.assertIn('  ', out)
        self.assertIn('\n', out)

    def test_scramble_text_words_changed_when_possible(self):
        rng = random.Random(42)
        text = 'Scrambling words internally.'
        out = scramble_text(text, rng)
        self.assertEqual(len(out), len(text))
        self.assertNotEqual(out, text)


