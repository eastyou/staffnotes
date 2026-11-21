"""模型层测试。"""

import unittest

from staffnotes.model import (
    Note,
    NoteError,
    build_notes,
    check_answer,
    check_clef,
    format_frequency,
    ledger_offsets,
    parse_note,
    position_label,
    reference_notes,
    staff_offset,
    step_to_note,
)


class ParseNoteTest(unittest.TestCase):
    def test_standard(self):
        note = parse_note("C4")
        self.assertEqual((note.name, note.octave), ("C", 4))

    def test_lowercase(self):
        self.assertEqual(parse_note("f5").name, "F")

    def test_spaces_removed(self):
        self.assertEqual(parse_note(" a 4 ").label, "A4")

    def test_all_names(self):
        for name in "CDEFGAB":
            self.assertEqual(parse_note(name + "3").name, name)

    def test_octave_range(self):
        self.assertEqual(parse_note("C0").octave, 0)
        self.assertEqual(parse_note("C8").octave, 8)

    def test_empty_rejected(self):
        with self.assertRaises(NoteError):
            parse_note("  ")

    def test_bad_letter(self):
        with self.assertRaises(NoteError):
            parse_note("H4")

    def test_bad_octave(self):
        with self.assertRaises(NoteError):
            parse_note("C9")

    def test_missing_octave(self):
        with self.assertRaises(NoteError):
            parse_note("C")

    def test_non_string(self):
        with self.assertRaises(NoteError):
            parse_note(4)


class StepTest(unittest.TestCase):
    def test_c0_is_zero(self):
        self.assertEqual(Note("C", 0).step, 0)

    def test_b4(self):
        self.assertEqual(Note("B", 4).step, 34)

    def test_c5(self):
        self.assertEqual(Note("C", 5).step, 35)

    def test_roundtrip(self):
        for step in range(0, 60):
            self.assertEqual(step_to_note(step).step, step)

    def test_step_to_note(self):
        self.assertEqual(step_to_note(28).label, "C4")

    def test_negative_step_rejected(self):
        with self.assertRaises(NoteError):
            step_to_note(-1)

    def test_non_integer_step(self):
        with self.assertRaises(NoteError):
            step_to_note("28")


class FrequencyTest(unittest.TestCase):
    def test_a4(self):
        self.assertAlmostEqual(Note("A", 4).frequency, 440.0, places=6)

    def test_a5(self):
        self.assertAlmostEqual(Note("A", 5).frequency, 880.0, places=6)

    def test_a3(self):
        self.assertAlmostEqual(Note("A", 3).frequency, 220.0, places=6)

    def test_c4(self):
        self.assertAlmostEqual(Note("C", 4).frequency, 261.625565, places=5)

    def test_e4(self):
        self.assertAlmostEqual(Note("E", 4).frequency, 329.627557, places=5)

    def test_midi_numbers(self):
        self.assertEqual(Note("A", 4).midi, 69)
        self.assertEqual(Note("C", 4).midi, 60)

    def test_format(self):
        self.assertEqual(format_frequency(Note("A", 4)), "440.00 Hz")


class StaffPositionTest(unittest.TestCase):
    def test_treble_bottom_line(self):
        self.assertEqual(staff_offset(Note("E", 4), "treble"), 0)

    def test_treble_first_space(self):
        self.assertEqual(staff_offset(Note("F", 4), "treble"), 1)

    def test_treble_top_line(self):
        self.assertEqual(staff_offset(Note("F", 5), "treble"), 8)

    def test_bass_bottom_line(self):
        self.assertEqual(staff_offset(Note("G", 2), "bass"), 0)

    def test_invalid_clef(self):
        with self.assertRaises(NoteError):
            check_clef("alto")

    def test_no_ledger_inside(self):
        self.assertEqual(ledger_offsets(Note("B", 4), "treble"), [])

    def test_ledger_below_once(self):
        self.assertEqual(ledger_offsets(Note("C", 4), "treble"), [-2])

    def test_ledger_below_twice(self):
        self.assertEqual(ledger_offsets(Note("A", 3), "treble"), [-4, -2])

    def test_ledger_space_above(self):
        self.assertEqual(ledger_offsets(Note("G", 5), "treble"), [])

    def test_ledger_above_once(self):
        self.assertEqual(ledger_offsets(Note("A", 5), "treble"), [10])

    def test_position_line(self):
        self.assertEqual(position_label(Note("E", 4), "treble"), "第 1 线")
        self.assertEqual(position_label(Note("F", 5), "treble"), "第 5 线")

    def test_position_space(self):
        self.assertEqual(position_label(Note("F", 4), "treble"), "第 1 间")
        self.assertEqual(position_label(Note("E", 5), "treble"), "第 4 间")

    def test_position_outside(self):
        self.assertEqual(position_label(Note("C", 4), "treble"), "谱表下方")
        self.assertEqual(position_label(Note("A", 5), "treble"), "谱表上方")

    def test_reference_nine_positions(self):
        notes = reference_notes("treble")
        self.assertEqual(len(notes), 9)
        self.assertEqual(notes[0][0].label, "E4")
        self.assertEqual(notes[-1][0].label, "F5")

    def test_reference_bass(self):
        notes = reference_notes("bass")
        self.assertEqual(notes[0][0].label, "G2")
        self.assertEqual(notes[-1][0].label, "A3")


class BuildNotesTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(build_notes(6, seed=1)), 6)

    def test_unique(self):
        notes = build_notes(8, seed=2)
        self.assertEqual(len(set(notes)), 8)

    def test_in_range(self):
        notes = build_notes(5, low="C4", high="G4", seed=3)
        for note in notes:
            self.assertGreaterEqual(note.step, Note("C", 4).step)
            self.assertLessEqual(note.step, Note("G", 4).step)

    def test_deterministic(self):
        first = [note.label for note in build_notes(6, seed=4)]
        second = [note.label for note in build_notes(6, seed=4)]
        self.assertEqual(first, second)

    def test_different_seeds(self):
        first = [note.label for note in build_notes(6, seed=4)]
        second = [note.label for note in build_notes(6, seed=5)]
        self.assertNotEqual(first, second)

    def test_bass_default(self):
        notes = build_notes(6, clef="bass", seed=6)
        for note in notes:
            self.assertGreaterEqual(note.step, Note("G", 2).step)
            self.assertLessEqual(note.step, Note("C", 4).step)

    def test_too_many(self):
        with self.assertRaises(NoteError):
            build_notes(12)

    def test_zero(self):
        with self.assertRaises(NoteError):
            build_notes(0)

    def test_reversed_range(self):
        with self.assertRaises(NoteError):
            build_notes(3, low="F5", high="C4")

    def test_invalid_clef(self):
        with self.assertRaises(NoteError):
            build_notes(3, clef="alto")


class CheckAnswerTest(unittest.TestCase):
    def test_correct(self):
        self.assertTrue(check_answer(Note("C", 4), "C4"))

    def test_lowercase(self):
        self.assertTrue(check_answer(Note("C", 4), "c4"))

    def test_with_spaces(self):
        self.assertTrue(check_answer(Note("G", 5), " g 5 "))

    def test_wrong_note(self):
        self.assertFalse(check_answer(Note("C", 4), "D4"))

    def test_wrong_octave(self):
        self.assertFalse(check_answer(Note("C", 4), "C5"))

    def test_invalid_text(self):
        self.assertFalse(check_answer(Note("C", 4), "H4"))

    def test_empty(self):
        self.assertFalse(check_answer(Note("C", 4), ""))


if __name__ == "__main__":
    unittest.main()
