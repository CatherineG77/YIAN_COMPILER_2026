from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple
import os


def compile_all() -> int:
    script_path = Path(__file__).resolve()
    lab_root = script_path.parent
    ll_dir = lab_root / "ll"
    bin_dir = lab_root / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    ll_files = sorted(ll_dir.glob("*.ll"))
    if not ll_files:
        print(f"No .ll files found in {ll_dir}", file=sys.stderr)
        return 1

    for ll_file in ll_files:
        output_file = bin_dir / ll_file.stem
        # compile with optimization level -O3
        command = ["clang", "-O3", str(ll_file), "-o", str(output_file)]
        print(f"Compiling {ll_file.name} -> {output_file.name}")
        subprocess.run(command, check=True)

    # After compiling, run each executable and collect failures
    failures: List[Tuple[str, int, str, str]] = []
    for exe in sorted(bin_dir.iterdir()):
        if not exe.is_file():
            continue
        # skip non-executable files
        if not os.access(str(exe), os.X_OK):
            # try to make it executable (some files created may miss bits)
            try:
                exe.chmod(exe.stat().st_mode | 0o111)
            except Exception:
                continue

        print(f"Running {exe.name}...")
        proc = subprocess.run([str(exe)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            failures.append((exe.name, proc.returncode, proc.stdout, proc.stderr))

    if failures:
        print("\nFailures detected:")
        for name, code, out, err in failures:
            print(f"- {name}: exit {code}")
            if out:
                print(f"  stdout:\n{out.rstrip()}")
            if err:
                print(f"  stderr:\n{err.rstrip()}")
        return 2

    print("All executables returned 0.")
    return 0


def main() -> None:
    raise SystemExit(compile_all())


if __name__ == "__main__":
    main()
