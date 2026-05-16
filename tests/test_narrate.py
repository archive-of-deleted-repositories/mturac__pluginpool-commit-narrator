import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "narrate.py"


def run_script(diff, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--diff", "-", *args],
        input=diff,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def test_json_output_shape():
    diff = "diff --git a/src/app.py b/src/app.py\n+print('x')\n"
    data = json.loads(run_script(diff, "--format", "json").stdout)
    assert set(data) == {"type", "scope", "subject", "body", "files"}
    assert data["files"] == ["src/app.py"]


def test_docs_classification():
    diff = "diff --git a/README.md b/README.md\n+Usage\n"
    assert json.loads(run_script(diff, "--format", "json").stdout)["type"] == "docs"


def test_test_classification():
    diff = "diff --git a/tests/test_app.py b/tests/test_app.py\n+def test_x(): pass\n"
    assert json.loads(run_script(diff, "--format", "json").stdout)["type"] == "test"


def test_fix_classification_from_hunk():
    diff = "diff --git a/src/app.py b/src/app.py\n+fix regression in parser\n"
    assert json.loads(run_script(diff, "--format", "json").stdout)["type"] == "fix"


def test_empty_diff_is_graceful_text():
    assert run_script("").stdout == ""


def test_binary_file_is_listed_and_safe():
    diff = "diff --git a/assets/logo.png b/assets/logo.png\nBinary files a/assets/logo.png and b/assets/logo.png differ\n"
    data = json.loads(run_script(diff, "--format", "json").stdout)
    assert data["files"] == ["assets/logo.png"]
    assert data["type"] == "chore"


def test_changed_files_handles_spaces_via_plusplus():
    """A real git diff with a space-containing path: parse via `+++ b/...` line."""
    diff = (
        "diff --git \"a/folder with space/file.py\" \"b/folder with space/file.py\"\n"
        "index abc..def 100644\n"
        "--- \"a/folder with space/file.py\"\n"
        "+++ \"b/folder with space/file.py\"\n"
        "@@ -1 +1 @@\n"
        "-old\n"
        "+new\n"
    )
    # Even though the +++ line is quoted, this is the second variant.
    # Re-test the more common form:
    diff2 = (
        "diff --git a/path/with space/file.py b/path/with space/file.py\n"
        "--- a/path/with space/file.py\n"
        "+++ b/path/with space/file.py\n"
        "@@ -1 +1 @@\n"
        "+new\n"
    )
    import scripts.narrate as narrate  # type: ignore
    files = narrate.changed_files(diff2)
    assert files == ["path/with space/file.py"]


def test_changed_files_handles_spaces_via_diff_git_quoted():
    """Compact diff fixture (no +++ line) with quoted, space-containing path."""
    import scripts.narrate as narrate  # type: ignore
    diff = 'diff --git "a/some path/x.py" "b/some path/x.py"\n+new\n'
    files = narrate.changed_files(diff)
    assert files == ["some path/x.py"]
