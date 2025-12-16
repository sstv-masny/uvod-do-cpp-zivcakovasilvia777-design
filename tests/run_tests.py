#!/usr/bin/env python3
"""
Autograder harness for uvod-do-cpp-xmasny-2.

- Discovers all task_* directories in the STUDENT repo.
- For each task, compiles main.cpp with g++ into b/<task>.exe
- Runs PUBLIC tests from <student_root>/task_*/tests/*.in/.out
- Optionally runs HIDDEN tests from $HIDDEN_TESTS_ROOT/task_*/tests/*.in/.out

Usage:
  python tests/run_tests.py          # default: run both if hidden root set
  python tests/run_tests.py public   # only public tests
  python tests/run_tests.py hidden   # only hidden tests (if available)

Exit:
  0 -> all selected tests passed
  1 -> some compilation or test failed
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
import argparse


STUDENT_ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = STUDENT_ROOT / "b"
TASK_PREFIX = "task_"


def run(cmd, *, input_text=None, cwd=None):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        input=input_text,
        text=True,
        capture_output=True,
        cwd=cwd,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result


def find_gpp() -> str | None:
    return shutil.which("g++") or shutil.which("g++.exe")


def normalize_output(s: str) -> str:
    lines = s.splitlines()
    lines = [line.rstrip() for line in lines]
    return "\n".join(lines).strip()


def compile_task(task_dir: Path, gpp: str) -> Path:
    task_name = task_dir.name
    main_cpp = task_dir / "main.cpp"
    if not main_cpp.exists():
        raise RuntimeError(f"{task_name}: main.cpp not found at {main_cpp}")

    exe_name = f"{task_name}.exe" if sys.platform.startswith("win") else task_name
    exe_path = BUILD_DIR / exe_name

    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        gpp,
        "-std=c++17",
        "-O2",
        "-Wall",
        "-Wextra",
        "-o",
        str(exe_path),
        str(main_cpp),
    ]
    print(f"\n=== Compiling {task_name} ===")
    proc = run(cmd)
    if proc.returncode != 0:
        raise RuntimeError(f"{task_name}: compilation failed")

    return exe_path


def run_tests_in_dir(
    task_name: str, exe_path: Path, tests_dir: Path, label: str
) -> tuple[int, int]:
    if not tests_dir.is_dir():
        print(f"{task_name} [{label}]: no tests/ dir at {tests_dir}, skipping.")
        return 0, 0

    in_files = sorted(tests_dir.glob("*.in"))
    if not in_files:
        print(f"{task_name} [{label}]: no *.in files, skipping.")
        return 0, 0

    print(f"\n=== Running {label} tests for {task_name} ===")
    passed = 0
    total = 0

    for in_path in in_files:
        total += 1
        test_id = in_path.stem
        out_path = tests_dir / f"{test_id}.out"

        input_text = in_path.read_text(encoding="utf-8")

        print(f"\n-- {task_name} [{label}] / test {test_id} --")
        proc = run([str(exe_path)], input_text=input_text, cwd=exe_path.parent)

        if proc.returncode != 0:
            print(
                f"FAIL: {task_name} [{label}] test {test_id}: "
                f"program exited with {proc.returncode}",
                file=sys.stderr,
            )
            continue

        if out_path.exists():
            expected = normalize_output(out_path.read_text(encoding="utf-8"))
            got = normalize_output(proc.stdout)

            if got == expected:
                print(f"PASS: {task_name} [{label}] test {test_id}")
                passed += 1
            else:
                print(
                    f"FAIL: {task_name} [{label}] test {test_id}: output mismatch",
                    file=sys.stderr,
                )
                print("Expected:")
                print(expected)
                print("Got:")
                print(got)
        else:
            print(f"PASS (no .out): {task_name} [{label}] test {test_id}")
            passed += 1

    print(f"\n{task_name} [{label}]: {passed}/{total} tests passed")
    return passed, total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["public", "hidden", "all"],
        default="all",
        help="Which tests to run",
    )
    parser.add_argument(
        "--task",
        help="Specific task dir name, e.g. task_01_even_or_odd. "
        "If omitted, run all tasks.",
    )
    args = parser.parse_args()

    mode = args.mode
    task_filter = args.task

    print("=== C++ assignment test runner ===")
    print(f"Student repo root: {STUDENT_ROOT}")
    print(f"Mode: {mode}")
    if task_filter:
        print(f"Task filter: {task_filter}")

    hidden_root_env = os.environ.get("HIDDEN_TESTS_ROOT")
    hidden_root = Path(hidden_root_env) if hidden_root_env else None
    if mode in ("hidden", "all") and hidden_root:
        print(f"Hidden tests root: {hidden_root}")
    elif mode in ("hidden", "all"):
        print(
            "No HIDDEN_TESTS_ROOT set; hidden tests will be skipped.", file=sys.stderr
        )
        hidden_root = None

    gpp = find_gpp()
    if not gpp:
        print("ERROR: g++ not found on PATH.", file=sys.stderr)
        return 1
    print("Using compiler:", gpp)

    # ↓↓↓ the important change ↓↓↓
    if task_filter:
        # single task
        task_dir = STUDENT_ROOT / task_filter
        if not task_dir.is_dir():
            print(f"ERROR: task dir {task_dir} does not exist", file=sys.stderr)
            return 1
        task_dirs = [task_dir]
    else:
        # all tasks
        task_dirs = sorted(
            d
            for d in STUDENT_ROOT.iterdir()
            if d.is_dir() and d.name.startswith(TASK_PREFIX)
        )

    if not task_dirs:
        print(
            f"ERROR: no '{TASK_PREFIX}*' task directories found in {STUDENT_ROOT}",
            file=sys.stderr,
        )
        return 1
    overall_passed = 0
    overall_total = 0
    had_error = False

    for task_dir in task_dirs:
        task_name = task_dir.name
        try:
            exe_path = compile_task(task_dir, gpp)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            had_error = True
            continue

        # PUBLIC tests
        if mode in ("public", "all"):
            pub_tests_dir = task_dir / "tests"
            p_passed, p_total = run_tests_in_dir(
                task_name, exe_path, pub_tests_dir, "PUBLIC"
            )
            overall_passed += p_passed
            overall_total += p_total
            if p_passed != p_total:
                had_error = True

        # HIDDEN tests
        if hidden_root and mode in ("hidden", "all"):
            hidden_task_dir = hidden_root / task_name / "tests"
            h_passed, h_total = run_tests_in_dir(
                task_name, exe_path, hidden_task_dir, "HIDDEN"
            )
            overall_passed += h_passed
            overall_total += h_total
            if h_passed != h_total:
                had_error = True

    print("\n=== Summary ===")
    print(f"Total: {overall_passed}/{overall_total} tests passed")

    if had_error:
        print("Some tests failed.", file=sys.stderr)
        return 1

    print("All tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
