"""渲染层测试。"""

import unittest

from staffnotes.model import Note, build_notes
from staffnotes.render import render_reference, render_sheet, staff_svg


class StaffSvgTest(unittest.TestCase):
    def test_svg_size(self):
        svg = staff_svg(Note("E", 4))
        self.assertIn('width="60mm"', svg)
        self.assertIn('height="34mm"', svg)

    def test_five_staff_lines(self):
        svg = staff_svg(Note("E", 4))
        self.assertEqual(svg.count('stroke="#334155"'), 5)

    def test_ledger_line_added(self):
        svg = staff_svg(Note("C", 4))
        self.assertEqual(svg.count('stroke="#334155"'), 6)

    def test_treble_symbol(self):
        self.assertIn("𝄞", staff_svg(Note("E", 4), "treble"))

    def test_bass_symbol(self):
        self.assertIn("𝄢", staff_svg(Note("G", 2), "bass"))

    def test_note_head(self):
        self.assertIn("<ellipse", staff_svg(Note("E", 4)))

    def test_stem(self):
        self.assertIn("<line", staff_svg(Note("E", 4)))

    def test_invalid_clef(self):
        with self.assertRaises(Exception):
            staff_svg(Note("E", 4), "alto")


class SheetTest(unittest.TestCase):
    def test_card_count(self):
        html = render_sheet(build_notes(6, seed=1))
        self.assertEqual(html.count('class="card"'), 6)

    def test_skeleton(self):
        html = render_sheet(build_notes(2, seed=1))
        self.assertTrue(html.startswith("<!DOCTYPE html>"))
        self.assertIn('<meta charset="utf-8">', html)

    def test_default_title_treble(self):
        html = render_sheet(build_notes(2, seed=1), "treble")
        self.assertIn("高音谱号", html)

    def test_default_title_bass(self):
        html = render_sheet(build_notes(2, clef="bass", seed=1), "bass")
        self.assertIn("低音谱号", html)

    def test_custom_title_escaped(self):
        html = render_sheet(build_notes(1, seed=1), title="<识谱> & 练习")
        self.assertIn("&lt;识谱&gt; &amp; 练习", html)

    def test_answers_hidden(self):
        html = render_sheet(build_notes(3, seed=1))
        self.assertNotIn("参考答案", html)

    def test_answers_included(self):
        notes = build_notes(3, seed=1)
        html = render_sheet(notes, include_answers=True)
        self.assertIn("参考答案", html)
        for note in notes:
            self.assertIn(note.label, html)

    def test_empty(self):
        html = render_sheet([])
        self.assertIn("暂无题目", html)

    def test_a4_style(self):
        html = render_sheet(build_notes(1, seed=1))
        self.assertIn("size: A4", html)
        self.assertIn("@media print", html)

    def test_blank_line(self):
        self.assertIn("音名：", render_sheet(build_notes(1, seed=1)))


class ReferenceTest(unittest.TestCase):
    def test_nine_rows(self):
        html = render_reference("treble")
        self.assertEqual(html.count("<tr><td>"), 9)

    def test_first_and_last(self):
        html = render_reference("treble")
        self.assertIn("E4", html)
        self.assertIn("F5", html)

    def test_bass(self):
        html = render_reference("bass")
        self.assertIn("G2", html)
        self.assertIn("A3", html)

    def test_frequency_present(self):
        self.assertIn("440.00", render_reference("treble"))

    def test_title_escaped(self):
        html = render_reference("treble", title="<对照>")
        self.assertIn("&lt;对照&gt;", html)


if __name__ == "__main__":
    unittest.main()
