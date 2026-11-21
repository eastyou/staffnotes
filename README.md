# staffnotes

[![CI](https://github.com/eastyou/staffnotes/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/staffnotes/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

五线谱识谱卡：随机抽取音名，画成 SVG 谱表，生成可打印的 A4 认谱练习与答案页。

## 特性

- 支持高音谱号与低音谱号，音域可自定义
- 按五线谱规则计算线、间、加线与音级位置
- 给出十二平均律频率，A4 = 440 Hz
- 同一页内音符不重复，随机种子可复现
- 卡片两栏排版，虚线方便裁剪
- 纯标准库，零依赖，跨平台

## 安装

```bash
python -m pip install -e .
```

## 用法

```bash
staffnotes sheet --count 8 --clef treble --seed 3 --answers -o sheet.html
staffnotes sheet --count 8 --clef bass --low G2 --high C4 -o bass.html
staffnotes list
staffnotes list --clef bass --html > reference.html
staffnotes note C4
```

| 命令 | 说明 |
| --- | --- |
| `sheet` | 生成识谱练习卡，`--answers` 追加答案页 |
| `list` | 列出五线四间的音名、位置与频率 |
| `note` | 查看单个音的音级距离、加线与频率 |

## 音名约定

- 中央 C 写作 `C4`，高音谱号最下面一条线是 `E4`，低音谱号最下面一条线是 `G2`
- 答案忽略大小写与空格，`c4`、`C 4` 都算正确
- 超出谱表的音会自动画出加线

## 示例

[examples/staffnotes.html](examples/staffnotes.html) 是 8 题高音谱号练习，带答案页。

## 测试

```bash
python -m unittest discover -s tests -v
```

## 协议

MIT © 2026 eastyou
