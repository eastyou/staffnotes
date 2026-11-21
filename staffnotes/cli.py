"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    CLEFS,
    NoteError,
    build_notes,
    check_clef,
    format_frequency,
    ledger_offsets,
    parse_note,
    position_label,
    reference_notes,
    staff_offset,
)
from .render import render_reference, render_sheet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="staffnotes",
        description="五线谱识谱卡：音名、频率与可打印 A4 练习",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sheet_parser = subparsers.add_parser("sheet", help="生成识谱练习卡")
    sheet_parser.add_argument("--clef", choices=("treble", "bass"), default="treble", help="谱号")
    sheet_parser.add_argument("--count", type=int, default=8, help="题目数量，默认 8")
    sheet_parser.add_argument("--low", default=None, help="最低音，例如 C4")
    sheet_parser.add_argument("--high", default=None, help="最高音，例如 F5")
    sheet_parser.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet_parser.add_argument("--title", default="", help="练习卡标题")
    sheet_parser.add_argument("--answers", action="store_true", help="追加答案页")
    sheet_parser.add_argument("-o", "--output", default=None, help="输出文件")

    note_parser = subparsers.add_parser("note", help="查看单个音的信息")
    note_parser.add_argument("name", help="例如 C4")
    note_parser.add_argument("--clef", choices=("treble", "bass"), default="treble", help="谱号")

    list_parser = subparsers.add_parser("list", help="列出五线四间的音名")
    list_parser.add_argument("--clef", choices=("treble", "bass"), default="treble", help="谱号")
    list_parser.add_argument("--html", action="store_true", help="输出 HTML 对照表")
    return parser


def _write_output(html_text: str, output: Optional[str]) -> None:
    if not output:
        print(html_text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")
    print("已写入 %s" % path)


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "sheet":
            notes = build_notes(args.count, args.clef, args.low, args.high, args.seed)
            html_text = render_sheet(notes, args.clef, args.title, include_answers=args.answers)
            _write_output(html_text, args.output)
            return 0
        if args.command == "list":
            if args.html:
                _write_output(render_reference(args.clef), None)
                return 0
            check_clef(args.clef)
            for note, position in reference_notes(args.clef):
                print("%-4s %-6s %s" % (note.label, position, format_frequency(note)))
            return 0
        note = parse_note(args.name)
        print("音名：%s" % note.label)
        print("谱号：%s" % CLEFS[args.clef]["label"])
        print("位置：%s" % position_label(note, args.clef))
        print("音级距离：%d" % staff_offset(note, args.clef))
        print("加线：%d 条" % len(ledger_offsets(note, args.clef)))
        print("频率：%s" % format_frequency(note))
        return 0
    except NoteError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
