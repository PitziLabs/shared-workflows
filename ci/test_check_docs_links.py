#!/usr/bin/env python3
"""Tests for check_docs_links.py — proves the checker goes red on a genuinely
broken link and stays green on the link classes it is designed to skip.

Self-contained: builds throwaway git repos in a tempdir, no pytest dependency.
Run locally exactly as CI does:  python3 ci/test_check_docs_links.py
Exit status is 0 only when every case passes.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(HERE, "check_docs_links.py")

RESULTS = []


def make_repo(files):
    """Create a git repo in a fresh tempdir, write+track `files`, return path."""
    tmp = tempfile.mkdtemp(prefix="docs-check-test-")
    subprocess.run(["git", "-C", tmp, "init", "-q"], check=True)
    for rel, content in files.items():
        path = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
    subprocess.run(["git", "-C", tmp, "add", "-A"], check=True)
    return tmp


def run_checker(root, *extra):
    proc = subprocess.run(
        [sys.executable, CHECKER, "--root", root, *extra],
        capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def case(name, expect_rc, files, extra=(), needle=None):
    root = make_repo(files)
    rc, out = run_checker(root, *extra)
    ok = rc == expect_rc and (needle is None or needle in out)
    RESULTS.append((name, ok))
    status = "ok  " if ok else "FAIL"
    print(f"  {status}  {name}  (rc={rc}, want {expect_rc})")
    if not ok:
        print("        --- output ---")
        for line in out.splitlines():
            print(f"        {line}")


def main():
    # The headline guarantee: a deliberately broken link reds the check.
    case("broken link fails", 1,
         {"README.md": "See [the guide](./docs/missing.md).\n"},
         needle="no such path")

    # A link that resolves is fine.
    case("valid link passes", 0,
         {"README.md": "See [the guide](./docs/guide.md).\n",
          "docs/guide.md": "# Guide\n"})

    # False-positive class 1: site-absolute router routes are skipped by rule.
    case("site-absolute route skipped", 0,
         {"README.md": "Browse the [library](/library/) and [guides](/guides/x/).\n"})

    # False-positive class 2: GitHub repo-relative nav escapes root, skipped.
    case("github ../../issues nav skipped", 0,
         {"README.md": "Filed as [#5](../../issues/5).\n"})

    # A broken link survives even when a good and a skipped link share the file.
    case("mixed: one broken among skips still fails", 1,
         {"docs/x.md": ("[home](/) [issue](../../issues/9) "
                        "[dead](./nope.md) [ok](./y.md)\n"),
          "docs/y.md": "y\n"},
         needle="nope.md")

    # Anchors, query strings, and external schemes are not path checks.
    case("anchors/queries/schemes skipped", 0,
         {"README.md": ("[a](#section) [b](https://example.com) "
                        "[c](mailto:x@y.z) [d](./guide.md?v=1#top)\n"),
          "guide.md": "# g\n"})

    # Links inside fenced or inline code are examples, not real links.
    case("fenced and inline code skipped", 0,
         {"README.md": "Inline `[x](./nope.md)` and:\n\n```\n[y](./gone.md)\n```\n"})

    # Reference-style definitions are resolved; a broken one fails.
    case("broken reference definition fails", 1,
         {"README.md": "See [the guide][g].\n\n[g]: ./docs/missing.md\n"},
         needle="missing.md")

    # Images use the same resolver.
    case("broken image fails", 1,
         {"README.md": "![diagram](./assets/nope.png)\n"},
         needle="nope.png")

    # The explicit ignore input silences a chosen false positive.
    case("--ignore silences a target", 0,
         {"README.md": "[gen](./generated/out.html)\n"},
         extra=("--ignore", "*/generated/*"))

    # A checked-in .docs-check-ignore does the same, per-repo.
    case(".docs-check-ignore file honored", 0,
         {"README.md": "[gen](./build/out.html)\n",
          ".docs-check-ignore": "# repo-local ignores\n*/build/*\n"})

    failed = [n for n, ok in RESULTS if not ok]
    print()
    if failed:
        print(f"{len(failed)} of {len(RESULTS)} case(s) FAILED: {', '.join(failed)}")
        return 1
    print(f"all {len(RESULTS)} cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
