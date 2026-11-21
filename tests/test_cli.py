"""命令行测试。"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from staffnotes.cli import main


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class SheetCommandTest(unittest.TestCase):
    def test_writes_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "sheet.html")
            code, out, _ = run_cli(["sheet", "--count", "6", "--seed", "1", "-o", target])
            self.assertEqual(code, 0)
            self.assertIn("已写入", out)
            with open(target, encoding="utf-8") as handle:
                html = handle.read()
            self.assertEqual(html.count('class="card"'), 6)

    def test_stdout(self):
        code, out, _ = run_cli(["sheet", "--count", "3", "--seed", "2"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_answers_flag(self):
        code, out, _ = run_cli(["sheet", "--count", "2", "--seed", "3", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_bass_clef(self):
        code, out, _ = run_cli(["sheet", "--count", "2", "--clef", "bass", "--seed", "4"])
        self.assertEqual(code, 0)
        self.assertIn("低音谱号", out)

    def test_custom_range(self):
        code, out, _ = run_cli(
            ["sheet", "--count", "3", "--low", "C4", "--high", "G4", "--seed", "5"]
        )
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_too_many_returns_two(self):
        code, _, err = run_cli(["sheet", "--count", "12"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_invalid_note_returns_two(self):
        code, _, err = run_cli(["sheet", "--count", "2", "--low", "H4"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_nested_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "a", "b", "sheet.html")
            code, _, _ = run_cli(["sheet", "--count", "1", "-o", target])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(target))


class NoteCommandTest(unittest.TestCase):
    def test_c4_treble(self):
        code, out, _ = run_cli(["note", "C4"])
        self.assertEqual(code, 0)
        self.assertIn("C4", out)
        self.assertIn("261.63", out)
        self.assertIn("谱表下方", out)
        self.assertIn("1 条", out)

    def test_a4_frequency(self):
        code, out, _ = run_cli(["note", "A4"])
        self.assertEqual(code, 0)
        self.assertIn("440.00", out)

    def test_bass_position(self):
        code, out, _ = run_cli(["note", "C4", "--clef", "bass"])
        self.assertEqual(code, 0)
        self.assertIn("谱表上方", out)

    def test_invalid_note(self):
        code, _, err = run_cli(["note", "H4"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)


class ListCommandTest(unittest.TestCase):
    def test_nine_lines(self):
        code, out, _ = run_cli(["list"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out.strip().splitlines()), 9)

    def test_html(self):
        code, out, _ = run_cli(["list", "--html"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)
        self.assertIn("音名", out)

    def test_bass(self):
        code, out, _ = run_cli(["list", "--clef", "bass"])
        self.assertEqual(code, 0)
        self.assertIn("G2", out)


class HelpTest(unittest.TestCase):
    def test_help_exits_zero(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_sheet_help(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["sheet", "--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
