from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _resolve_python_executable(project_root: Path) -> Path:
    override = os.getenv("BBMS_BACKEND_PYTHON")
    if override:
        return Path(override)

    if os.name == "nt":
        candidate = project_root / ".venv" / "Scripts" / "python.exe"
    else:
        candidate = project_root / ".venv" / "bin" / "python"

    if candidate.exists():
        return candidate

    return Path(sys.executable)


def _run_command(command: list[str], cwd: Path) -> None:
    completed = subprocess.run(command, cwd=cwd, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    python_executable = _resolve_python_executable(project_root)

    _run_command([str(python_executable), "-m", "compileall", "app"], project_root)
    _run_command([str(python_executable), "-m", "pytest", "-q"], project_root)


if __name__ == "__main__":
    main()
