"""staffnotes：五线谱识谱卡。"""

from .model import (
    CLEFS,
    DEFAULT_RANGES,
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
from .render import render_reference, render_sheet, staff_svg

__all__ = [
    "CLEFS",
    "DEFAULT_RANGES",
    "Note",
    "NoteError",
    "build_notes",
    "check_answer",
    "check_clef",
    "format_frequency",
    "ledger_offsets",
    "parse_note",
    "position_label",
    "reference_notes",
    "render_reference",
    "render_sheet",
    "staff_offset",
    "staff_svg",
    "step_to_note",
]

__version__ = "0.1.0"
