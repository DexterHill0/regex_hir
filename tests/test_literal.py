import unittest

from regex_hir import hir, Literal


class TestLiteral(unittest.TestCase):
    """Testing HIR of literals"""

    def test_literals(self):
        self.assertEqual(hir(r"a"), Literal.char("a"))
        self.assertEqual(hir(r"£"), Literal.char("£"))
        self.assertEqual(hir(r"4"), Literal.char("4"))
        self.assertEqual(hir(r"#"), Literal.char("#"))

    def test_escapes(self):
        self.assertEqual(hir(r"\n"), Literal.char("\n"))
        self.assertEqual(hir(r"\f"), Literal.char("\f"))
        self.assertEqual(hir(r"\a"), Literal.char("\a"))
        self.assertEqual(hir(r"\["), Literal.char("["))
        self.assertEqual(hir(r"\."), Literal.char("."))
        self.assertEqual(hir(r"\\"), Literal.char("\\"))
        self.assertEqual(hir(r"\^"), Literal.char("^"))

    def test_unicode(self):
        self.assertEqual(hir(r"🚗"), Literal.char("🚗"))
        self.assertEqual(hir(r"🔟"), Literal.char("🔟"))
        self.assertEqual(hir(r"🎅"), Literal.char("🎅"))


if __name__ == "__main__":
    unittest.main()