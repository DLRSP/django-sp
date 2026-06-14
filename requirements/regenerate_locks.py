"""Regenerate django-sp requirement locks with target Python and Django pins."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQ_IN = ROOT / "requirements.in"

LOCKS: dict[str, tuple[str, str]] = {
    "py310-django32": ("3.10", "Django>=3.2a1,<3.3"),
    "py39-django42": ("3.9", "Django>=4.2,<4.3"),
    "py310-django42": ("3.10", "Django>=4.2,<4.3"),
    "py311-django42": ("3.11", "Django>=4.2,<4.3"),
    "py312-django42": ("3.12", "Django>=4.2,<4.3"),
    "py310-django52": ("3.10", "Django>=5.2,<5.3"),
    "py311-django52": ("3.11", "Django>=5.2,<5.3"),
    "py312-django52": ("3.12", "Django>=5.2,<5.3"),
    "py313-django52": ("3.13", "Django>=5.2,<5.3"),
    "py314-django52": ("3.14", "Django>=5.2,<5.3"),
}


def py_cmd(version: str) -> list[str]:
    return ["py", f"-{version}"]


def compile_lock(stem: str, py_version: str, django_pin: str) -> None:
    cmd = [
        *py_cmd(py_version),
        "-m",
        "piptools",
        "compile",
        "--generate-hashes",
        "--allow-unsafe",
        "-P",
        django_pin,
        "-o",
        f"{stem}.txt",
        REQ_IN.name,
    ]
    print(f"compiling {stem} with Python {py_version} ...")
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> None:
    for version in sorted({v for v, _ in LOCKS.values()}):
        subprocess.run(
            [*py_cmd(version), "-m", "pip", "install", "-q", "pip-tools"],
            check=True,
        )
    for stem, spec in LOCKS.items():
        compile_lock(stem, *spec)
    print("done")


if __name__ == "__main__":
    main()
