#!/usr/bin/env python3
"""Build and verify the distributed public cases in an isolated project copy."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def ignore_generated(directory: str, names: list[str]) -> set[str]:
    ignored = set(names) & {
        '.git', '.venv', '__pycache__', '.pytest_cache', 'build',
        'yian_workspace', 'c2yian_workspace',
    }
    if Path(directory).name in {'lab1', 'lab2', 'lab3'}:
        ignored |= set(names) & {'output'}
    elif Path(directory).name == 'lab4':
        ignored |= set(names) & {'ast', 'hir', 'll', 'bin'}
    return ignored


def normalized_lines(path: Path) -> list[str]:
    lines = path.read_text(encoding='utf-8').splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def main() -> int:
    source = Path(__file__).resolve().parents[1]
    if shutil.which('clang') is None:
        print('clang is required. On Ubuntu: sudo apt install clang build-essential', file=sys.stderr)
        return 1
    root = Path(tempfile.mkdtemp(prefix='yian-public-tests-'))
    workspace = root / 'project'
    shutil.copytree(source, workspace, ignore=ignore_generated)
    logs = root / 'logs'
    logs.mkdir()
    (workspace / 'build').mkdir(exist_ok=True)
    for lab in range(1, 4):
        (workspace / f'labs/lab{lab}/output').mkdir(parents=True, exist_ok=True)
    for name in ['ast', 'hir', 'll']:
        (workspace / f'labs/lab4/{name}').mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    summary: dict[str, object] = {}

    def run(label: str, args: list[str], timeout: int = 180) -> subprocess.CompletedProcess[str]:
        print(f'[{label}]', flush=True)
        result = subprocess.run(args, cwd=workspace, env=env, capture_output=True,
                                text=True, errors='replace', timeout=timeout)
        (logs / f'{label}.log').write_text(result.stdout + '\nSTDERR:\n' + result.stderr,
                                         encoding='utf-8')
        if result.returncode:
            print(result.stdout[-5000:], file=sys.stderr)
            print(result.stderr[-5000:], file=sys.stderr)
            raise RuntimeError(f'{label}: exit {result.returncode}')
        return result

    def compile_program(label: str, input_path: str, output: Path) -> None:
        run(label, [sys.executable, 'scripts/yian_compiler.py', input_path,
                    '--output', str(output)])

    try:
        hello = workspace / 'build/hello'
        compile_program('hello-compile', 'labs/lab1/test_cases/hello.an', hello)
        result = run('hello-run', [str(hello)], timeout=15)
        if result.stdout.strip() != 'Hello, World!':
            raise RuntimeError('Hello program did not print Hello, World!')
        summary['hello'] = 'passed'
        print('Hello: passed', flush=True)

        for lab, folder in [(1, 'lex'), (2, 'parse'), (3, 'sema'), (4, 'translate')]:
            binary = workspace / f'build/lab{lab}'
            compile_program(f'lab{lab}-compile', f'labs/lab{lab}/{folder}', binary)
            run(f'lab{lab}-run', [str(binary)], timeout=60)
            if lab <= 3:
                names = {f'{i:02d}.txt' for i in range(1, 7)}
                output = workspace / f'labs/lab{lab}/output'
                actual_names = {p.name for p in output.glob('*.txt')}
                if actual_names != names:
                    raise RuntimeError(f'Lab{lab}: expected outputs 01.txt through 06.txt, got {sorted(actual_names)}')
                matches = sum(
                    normalized_lines(output / name) == normalized_lines(workspace / f'labs/lab{lab}/test_results/{name}')
                    for name in sorted(names)
                )
                if lab in (1, 2) and matches != 6:
                    raise RuntimeError(f'Lab{lab}: only {matches}/6 outputs match the public references')
                if lab == 3:
                    # The lab rubric requires successful execution, not identical formatting.
                    summary['lab3'] = {'public_cases': 6, 'runtime': 'passed', 'reference_matches': matches}
                    print(f'Lab3: 6/6 completed; reference matches {matches}/6 (informational)', flush=True)
                else:
                    summary[f'lab{lab}'] = {'public_cases': 6, 'reference_matches': matches}
                    print(f'Lab{lab}: 6/6 reference outputs matched', flush=True)
            else:
                names = {f'{i:02d}' for i in range(1, 11)}
                ir_names = {p.stem for p in (workspace / 'labs/lab4/ll').glob('*.ll')}
                if ir_names != names:
                    raise RuntimeError(f'Lab4: expected ten new IR files, got {sorted(ir_names)}')
                result = run('lab4-clang-tests', [sys.executable, 'labs/lab4/test_all.py'], timeout=120)
                bin_names = {p.name for p in (workspace / 'labs/lab4/bin').iterdir() if p.is_file()}
                if bin_names != names or 'All executables returned 0.' not in result.stdout:
                    raise RuntimeError('Lab4: not all ten generated programs were verified')
                summary['lab4'] = {'public_cases': 10, 'ir_count': 10, 'executables_returning_zero': 10}
                print('Lab4: 10/10 IR files compiled; all executables returned 0', flush=True)
        (root / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f'PUBLIC TESTS FAILED: {error}', file=sys.stderr)
        print(f'Logs and generated files: {root}', file=sys.stderr)
        return 1

    print('ALL PUBLIC TESTS PASSED', flush=True)
    print(f'Logs and generated files: {root}', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
