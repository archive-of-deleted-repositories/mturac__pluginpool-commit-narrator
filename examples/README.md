# commit-narrator — examples

Each scenario shows: the input (a real diff fixture), the exact command, the helper's raw output, and a sample of what Claude turns that output into.

---

## Scenario 1 — login-throttling feature

**Input fixture:** [`feat-auth-throttle.diff`](./feat-auth-throttle.diff) — a real unified diff adding a per-IP/email login throttle and its test.

**Command:**

```sh
cat examples/feat-auth-throttle.diff | python3 scripts/narrate.py --diff - --format text
```

**Helper output (verbatim):**

```text
test(src): add src coverage

Changed files:
- src/auth/login.py
- tests/test_login.py

WHY: Explain why this change is needed based on the diff.
```

The classifier picks `test` because more lines land in `tests/` than in `src/`. The `WHY` line is intentionally a placeholder — that's the slot for Claude to fill, grounded in the actual diff content.

**What Claude does next** (running `/commit-narrator`):

```text
feat(auth): throttle login after 5 attempts per (ip, email)

Changed files:
- src/auth/login.py
- tests/test_login.py

WHY: Prevent password-spray attacks on /login. The (ip, email)
tuple is the abuse key — single IPs hitting many accounts and
single accounts being targeted from many IPs are both common
patterns. Threshold of 5 matches the existing rate-limit
constant in src/security/limits.py; reusing it keeps the
ops dashboard alerts coherent.
```

Notice: Claude rewrote the type (`test` → `feat`), corrected the scope (`src` → `auth`), and produced rationale that the diff alone could not encode.

---

## Scenario 2 — JSON mode for tooling

If you want to wire the helper into your own scripts or CI, use `--format json`:

```sh
cat examples/feat-auth-throttle.diff | python3 scripts/narrate.py --diff - --format json
```

```json
{
  "body": "Changed files:\n- src/auth/login.py\n- tests/test_login.py\n\nWHY: Explain why this change is needed based on the diff.",
  "files": ["src/auth/login.py", "tests/test_login.py"],
  "scope": "src",
  "subject": "add src coverage",
  "type": "test"
}
```

This is the same content as the text mode but structured — good for piping into other tools.

---

## Scenario 3 — empty diff is safe

A common edge case: nothing staged. The helper produces nothing instead of a misleading commit message.

```sh
echo "" | python3 scripts/narrate.py --diff - --format text
# (no output, exit 0)
```

That's the right shape — the slash command can detect this and prompt the user to stage something.
