"""Regression tests for commit-narrator review findings."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import narrate  # noqa: E402


def test_quoted_path_with_space_is_extracted():
    diff = (
        'diff --git "a/folder with space/x.py" "b/folder with space/x.py"\n'
        '--- "a/folder with space/x.py"\n'
        '+++ "b/folder with space/x.py"\n'
        "@@ -0,0 +1 @@\n"
        "+hi\n"
    )
    files = narrate.changed_files(diff)
    assert "folder with space/x.py" in files


def test_quoted_binary_file_path_is_extracted():
    diff = (
        'diff --git "a/img/photo (1).png" "b/img/photo (1).png"\n'
        'Binary files "a/img/photo (1).png" and "b/img/photo (1).png" differ\n'
    )
    files = narrate.changed_files(diff)
    assert "img/photo (1).png" in files


def test_escaped_quote_in_path_is_unescaped():
    out = narrate._unescape_git_quoted(r'foo\"bar.py')
    assert out == 'foo"bar.py'


def test_plain_path_still_works():
    diff = (
        "diff --git a/src/a.py b/src/a.py\n"
        "--- a/src/a.py\n"
        "+++ b/src/a.py\n"
        "@@ -0,0 +1 @@\n"
        "+hi\n"
    )
    files = narrate.changed_files(diff)
    assert "src/a.py" in files
