"""五线谱练习卡的 SVG / HTML 渲染。"""

from __future__ import annotations

import html
from typing import Sequence

from .model import CLEFS, Note, check_clef, ledger_offsets, staff_offset

STYLE = """
@page { size: A4 portrait; margin: 14mm 13mm; }
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  color: #1b2430;
  font-size: 11pt;
  line-height: 1.5;
}
h1 { font-size: 20pt; margin: 0 0 2mm; }
.sub { color: #6b7280; font-size: 10pt; margin: 0 0 5mm; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm 8mm; }
.card {
  border: 0.6pt dashed #9aa5b1;
  border-radius: 2mm;
  padding: 3mm 4mm 3.5mm;
  page-break-inside: avoid;
}
.card .no { color: #7b8794; font-size: 9pt; }
.card svg { display: block; margin: 1mm auto 0; }
.answer-line {
  margin-top: 1.5mm;
  font-size: 10pt;
  color: #4b5563;
}
.blank {
  display: inline-block;
  width: 26mm;
  border-bottom: 0.8pt solid #1b2430;
  height: 1.05em;
}
.answers { page-break-before: always; }
.answers h2 { font-size: 15pt; margin: 0 0 4mm; }
.answers ol { columns: 3; column-gap: 10mm; padding-left: 8mm; }
.answers li { margin-bottom: 2mm; break-inside: avoid; font-family: "SFMono-Regular", Consolas, monospace; }
.note { color: #6b7280; font-size: 9.5pt; }
@media print { .card, .answers li { break-inside: avoid; } }
"""


def _escape(text: str) -> str:
    return html.escape(str(text), quote=True)


def staff_svg(note: Note, clef: str = "treble") -> str:
    """画一张 60mm × 34mm 的单音谱表。"""
    check_clef(clef)
    bottom_y = 24.0
    spacing = 3.0
    offset = staff_offset(note, clef)
    y = bottom_y - offset * (spacing / 2.0)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="60mm" height="34mm" '
        'viewBox="0 0 60 34" role="img" aria-label="%s的谱表位置">' % _escape(note.label)
    ]
    for index in range(5):
        line_y = 12.0 + index * spacing
        parts.append(
            '<line x1="14" y1="%.2f" x2="52" y2="%.2f" stroke="#334155" stroke-width="0.45"/>'
            % (line_y, line_y)
        )
    for ledger in ledger_offsets(note, clef):
        ledger_y = bottom_y - ledger * (spacing / 2.0)
        parts.append(
            '<line x1="24" y1="%.2f" x2="36" y2="%.2f" stroke="#334155" stroke-width="0.45"/>'
            % (ledger_y, ledger_y)
        )
    parts.append(
        '<text x="4" y="23" font-size="21" font-family="Bravura, Noto Music, serif" fill="#0f4c81">%s</text>'
        % CLEFS[clef]["symbol"]
    )
    stem_up = offset < 4
    stem_y = y - 12.0 if stem_up else y + 12.0
    parts.append(
        '<line x1="32.1" y1="%.2f" x2="32.1" y2="%.2f" stroke="#111827" stroke-width="0.55"/>'
        % (y, stem_y)
    )
    parts.append(
        '<ellipse cx="30" cy="%.2f" rx="2.4" ry="1.7" transform="rotate(-18 30 %.2f)" fill="#111827"/>'
        % (y, y)
    )
    parts.append("</svg>")
    return "".join(parts)


def render_sheet(
    notes: Sequence[Note],
    clef: str = "treble",
    title: str = "",
    include_answers: bool = False,
) -> str:
    """生成识谱练习卡；include_answers 为真时追加答案页。"""
    check_clef(clef)
    heading = title or "五线谱识谱练习（%s）" % CLEFS[clef]["label"]
    safe_title = _escape(heading)
    cards = []
    for index, note in enumerate(notes, start=1):
        cards.append(
            '<div class="card"><span class="no">第 %d 题</span>%s'
            '<div class="answer-line">音名：<span class="blank"></span></div></div>'
            % (index, staff_svg(note, clef))
        )
    body = "".join(cards) or '<p class="note">暂无题目。</p>'
    parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % safe_title,
        "<style>%s</style>" % STYLE,
        "</head>",
        "<body>",
        "<h1>%s</h1>" % safe_title,
        '<p class="sub">姓名：__________　班级：__________　日期：__________</p>',
        '<div class="grid">%s</div>' % body,
        '<p class="note">提示：音名用字母加数字表示，例如中央 C 写作 C4。</p>',
    ]
    if include_answers:
        answers = "".join(
            "<li>%d. %s</li>" % (index, _escape(note.label))
            for index, note in enumerate(notes, start=1)
        )
        parts.extend(
            [
                '<section class="answers">',
                "<h2>参考答案</h2>",
                "<ol>%s</ol>" % answers,
                "</section>",
            ]
        )
    parts.extend(["</body>", "</html>"])
    return "\n".join(parts)


def render_reference(clef: str = "treble", title: str = "") -> str:
    """生成五线四间的音名对照表。"""
    from .model import reference_notes

    check_clef(clef)
    heading = title or "%s音名对照" % CLEFS[clef]["label"]
    rows = "".join(
        "<tr><td>%s</td><td>%s</td><td class=\"num\" style=\"text-align:right\">%.2f Hz</td></tr>"
        % (_escape(note.label), _escape(position), note.frequency)
        for note, position in reference_notes(clef)
    )
    return "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="zh-CN"><head><meta charset="utf-8"><title>%s</title>'
            % _escape(heading),
            "<style>%s</style></head><body>" % STYLE,
            "<h1>%s</h1>" % _escape(heading),
            "<table><thead><tr><th>音名</th><th>位置</th><th>频率</th></tr></thead>"
            "<tbody>%s</tbody></table>" % rows,
            "</body></html>",
        ]
    )
