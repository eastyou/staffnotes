"""五线谱识谱：音名、频率、谱表位置与题目生成。"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

STEP_NAMES = ("C", "D", "E", "F", "G", "A", "B")
SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

CLEFS: Dict[str, Dict[str, object]] = {
    "treble": {"label": "高音谱号", "bottom": ("E", 4), "symbol": "𝄞"},
    "bass": {"label": "低音谱号", "bottom": ("G", 2), "symbol": "𝄢"},
}

DEFAULT_RANGES = {
    "treble": ("C4", "F5"),
    "bass": ("G2", "C4"),
}

_PATTERN = re.compile(r"^([A-G])([0-8])$")


class NoteError(ValueError):
    """音名、音域或参数不合法。"""


@dataclass(frozen=True)
class Note:
    """一个自然音，例如 C4。"""

    name: str
    octave: int

    @property
    def step(self) -> int:
        """全音阶序号，C0 为 0，每上行一个音名加 1。"""
        return self.octave * 7 + STEP_NAMES.index(self.name)

    @property
    def midi(self) -> int:
        return 12 * (self.octave + 1) + SEMITONES[self.name]

    @property
    def frequency(self) -> float:
        return 440.0 * (2.0 ** ((self.midi - 69) / 12.0))

    @property
    def label(self) -> str:
        return "%s%d" % (self.name, self.octave)


def check_clef(clef: str) -> str:
    if clef not in CLEFS:
        raise NoteError("谱号必须是 treble 或 bass，收到 %r" % (clef,))
    return clef


def parse_note(text: str) -> Note:
    """解析 C4、c4、C 4 这样的音名。"""
    if not isinstance(text, str):
        raise NoteError("音名必须是字符串")
    cleaned = "".join(text.split()).upper()
    if not cleaned:
        raise NoteError("音名不能为空")
    match = _PATTERN.match(cleaned)
    if not match:
        raise NoteError("音名格式应为 C4 这样的形式，收到 %r" % text)
    return Note(match.group(1), int(match.group(2)))


def step_to_note(step: int) -> Note:
    """把全音阶序号还原成音名。"""
    if isinstance(step, bool) or not isinstance(step, int):
        raise NoteError("音阶序号必须是整数")
    if step < 0:
        raise NoteError("音阶序号不能为负数")
    octave, index = divmod(step, 7)
    return Note(STEP_NAMES[index], octave)


def staff_offset(note: Note, clef: str = "treble") -> int:
    """相对谱表最下面一条线的音级距离，线上为偶数。"""
    check_clef(clef)
    bottom_name, bottom_octave = CLEFS[clef]["bottom"]
    bottom = Note(str(bottom_name), int(bottom_octave))
    return note.step - bottom.step


def ledger_offsets(note: Note, clef: str = "treble") -> List[int]:
    """返回需要加线的位置，单位与 staff_offset 相同。"""
    offset = staff_offset(note, clef)
    if offset > 8:
        return list(range(10, offset + 1, 2))
    if offset < 0:
        return sorted(range(-2, offset - 1, -2))
    return []


def position_label(note: Note, clef: str = "treble") -> str:
    """用“第几线 / 第几间 / 谱表外”描述位置。"""
    offset = staff_offset(note, clef)
    if offset < 0:
        return "谱表下方"
    if offset > 8:
        return "谱表上方"
    if offset % 2 == 0:
        return "第 %d 线" % (offset // 2 + 1)
    return "第 %d 间" % ((offset - 1) // 2 + 1)


def reference_notes(clef: str = "treble") -> List[Tuple[Note, str]]:
    """返回五线四间共 9 个位置及说明，由低到高。"""
    check_clef(clef)
    bottom_name, bottom_octave = CLEFS[clef]["bottom"]
    bottom = Note(str(bottom_name), int(bottom_octave))
    result = []
    for offset in range(9):
        note = step_to_note(bottom.step + offset)
        result.append((note, position_label(note, clef)))
    return result


def build_notes(
    count: int,
    clef: str = "treble",
    low: Optional[str] = None,
    high: Optional[str] = None,
    seed: Optional[int] = None,
) -> List[Note]:
    """在音域内抽取互不重复的音，生成练习卡。"""
    check_clef(clef)
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise NoteError("题目数量必须是正整数")
    default_low, default_high = DEFAULT_RANGES[clef]
    low_note = parse_note(low if low is not None else default_low)
    high_note = parse_note(high if high is not None else default_high)
    if low_note.step > high_note.step:
        raise NoteError("最低音不能高于最高音")
    span = high_note.step - low_note.step + 1
    if count > span:
        raise NoteError("音域内只有 %d 个音，无法生成 %d 张卡片" % (span, count))
    rng = random.Random(seed)
    steps = rng.sample(range(low_note.step, high_note.step + 1), count)
    return [step_to_note(step) for step in steps]


def check_answer(note: Note, text: str) -> bool:
    """判断学生写的音名是否正确，忽略大小写和空格。"""
    try:
        return parse_note(text) == note
    except NoteError:
        return False


def format_frequency(note: Note) -> str:
    return "%.2f Hz" % note.frequency
