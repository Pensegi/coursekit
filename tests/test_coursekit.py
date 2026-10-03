# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Dennis Rudin - see LICENSE and NOTICE
"""Tests for the pure logic in coursekit.py: no models, no ffmpeg, no network."""

import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import coursekit


def test_version_flag():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    r = subprocess.run(
        [sys.executable, os.path.join(here, "coursekit.py"), "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0
    assert coursekit.__version__ in r.stdout


def test_parse_blocks(tmp_path):
    f = tmp_path / "01_Intro.md"
    f.write_text(
        "# Title\n\n[SLIDE 2]\n\nHello there.\nSecond line.\n\n[PAUSE 3]\n"
        "<!-- check: a note -->\n## Part\n\n[CLIP a.mp4]\n",
        encoding="utf-8",
    )
    assert coursekit.parse(str(f)) == [
        ("head", (1, "Title")),
        ("slide", 2),
        ("say", "Hello there. Second line."),
        ("pause", 3.0),
        ("head", (2, "Part")),
        ("clip", "a.mp4"),
    ]


def test_plain_strips_language_marks():
    assert coursekit.plain("Say {fr|bonjour} and {sv|tack}.") == "Say bonjour and tack."


@pytest.mark.parametrize(
    "seconds, expected", [(5, "0:05"), (65, "1:05"), (3661, "1:01:01")]
)
def test_hms(seconds, expected):
    assert coursekit.hms(seconds) == expected


def test_ts_srt_format():
    assert coursekit.ts(3661.5) == "01:01:01,500"


def test_chunks_respect_maximum_length():
    text = " ".join(
        ["This is a fairly long sentence with several words in it, and more."] * 4
    )
    parts = coursekit.chunks(text)
    assert parts
    assert all(len(p) <= coursekit.MAXCUE for p in parts)


def test_two_lines_splits_long_cue():
    cue = "one two three four five six seven eight nine ten eleven twelve thirteen"
    assert len(cue) > coursekit.MAXLINE
    assert coursekit.two_lines(cue).count("\n") == 1
    assert "\n" not in coursekit.two_lines("short cue")


def make_course(tmp_path, script):
    (tmp_path / "slides").mkdir()
    (tmp_path / "script").mkdir()
    (tmp_path / "source").mkdir()
    for n in (1, 2, 3):
        (tmp_path / "slides" / f"s-{n:03d}.png").write_bytes(b"")
    (tmp_path / "course.json").write_text("{}", encoding="utf-8")
    (tmp_path / "source" / "slides.json").write_text(
        json.dumps([{"slide": 1}, {"slide": 2}, {"slide": 3, "hidden": True}]),
        encoding="utf-8",
    )
    (tmp_path / "script" / "01_A.md").write_text(script, encoding="utf-8")
    return tmp_path


class Args:
    def __init__(self, course):
        self.course = str(course)


def test_check_all_good(tmp_path, capsys):
    course = make_course(tmp_path, "# A\n\n[SLIDE 1]\n\nHello.\n\n[SLIDE 2]\n\nMore.\n")
    coursekit.cmd_check(Args(course))
    assert "all good" in capsys.readouterr().out


def test_check_reports_problems(tmp_path, capsys):
    course = make_course(
        tmp_path, "# A\n\n[SLIDE 1]\n\nUse 50% of it.\n\n[SLIDE 9]\n\nMore.\n"
    )
    coursekit.cmd_check(Args(course))
    out = capsys.readouterr().out
    assert '"%"' in out
    assert "the deck has 3 slides" in out
    assert "slides never shown: [2]" in out


def test_read_tr_reports_missing_ids(tmp_path):
    course = make_course(tmp_path, "# A\n\n[SLIDE 1]\n")
    c = coursekit.load_course(str(course))
    src = [{"id": 0, "text": "a"}, {"id": 1, "text": "b"}]
    assert coursekit.read_tr(c, "sv", "X", src) == (None, "no translation yet")
    tr = tmp_path / "out" / "subtitles" / "tr" / "sv"
    tr.mkdir(parents=True, exist_ok=True)
    (tr / "X.txt").write_text("@@ 0\nett\n", encoding="utf-8")
    assert coursekit.read_tr(c, "sv", "X", src)[0] is None
    (tr / "X.txt").write_text("@@ 0\nett\n@@ 1\ntvå\n", encoding="utf-8")
    result, status = coursekit.read_tr(c, "sv", "X", src)
    assert status == "ok"
    assert [b["text"] for b in result] == ["ett", "två"]
