"""Tests for the newsletter HTML lint script."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HOSTING_LINK = '<a href="https://dashboard.vercel.app/page">Dashboard</a>'


@pytest.fixture
def lint_repo(tmp_path):
    """Copy the script and checker so each case runs in its own repository."""
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copyfile(
        ROOT / "scripts/lint-newsletters.sh", scripts / "lint-newsletters.sh"
    )
    shutil.copytree(ROOT / "src", tmp_path / "src")
    return tmp_path


def run_lint(repo, files, env=None):
    for name, content in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("<!DOCTYPE html>\n" + content + "\n", encoding="utf-8")
    environment = os.environ.copy()
    environment.pop("GITHUB_ACTIONS", None)
    environment.update(env or {})
    return subprocess.run(
        ["/bin/bash", str(repo / "scripts/lint-newsletters.sh")],
        cwd=repo,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    "name",
    [
        "editions/2026-01-01.html",
        "editions/2026-10-29.html",
        "editions/2026-10-30.html",
        "editions/2027-01-01.html",
        "editions/welcome.html",
        "templates/axiom-newsletter-template.html",
    ],
)
def test_hosting_link_fails_for_every_edition_and_template(lint_repo, name):
    result = run_lint(lint_repo, {name: HOSTING_LINK})
    assert result.returncode == 1
    assert "hosting address" in result.stdout
    assert "axiom.org" in result.stdout
    assert "\n2:dashboard.vercel.app\n" in result.stdout


def test_encoded_hosting_link_fails(lint_repo):
    result = run_lint(
        lint_repo,
        {"editions/welcome.html": '<a href="https://x&#46;vercel%2Eapp/">Read</a>'},
    )
    assert result.returncode == 1
    assert "2:x.vercel.app" in result.stdout


def test_hosting_link_github_actions_annotations(lint_repo):
    result = run_lint(
        lint_repo,
        {
            "editions/welcome.html": (
                HOSTING_LINK
                + '\n<img src="https://theaxiomfoundation.github.io/a.png">'
            )
        },
        env={"GITHUB_ACTIONS": "true"},
    )
    assert result.returncode == 1
    assert "::error file=editions/welcome.html,line=2::Links dashboard.vercel.app" in (
        result.stdout
    )
    assert (
        "::error file=editions/welcome.html,line=3::Links theaxiomfoundation.github.io"
        in result.stdout
    )


def test_axiom_org_and_external_links_pass(lint_repo):
    html = (
        '<a href="https://axiom.org/research">Research</a>'
        '<a href="https://www.axiom.org/">Axiom</a>'
        '<a href="https://fhoces.github.io/">External site</a>'
    )
    result = run_lint(
        lint_repo,
        {
            "editions/welcome.html": html,
            "templates/axiom-newsletter-template.html": html,
        },
    )
    assert result.returncode == 0
    assert "All newsletter files passed" in result.stdout
    assert "hosting address" not in result.stdout


def test_missing_python_fails_the_lint(lint_repo):
    path_without_python = lint_repo / "bin"
    path_without_python.mkdir()
    (path_without_python / "dirname").symlink_to(shutil.which("dirname"))
    result = run_lint(
        lint_repo,
        {"editions/welcome.html": HOSTING_LINK},
        env={"PATH": str(path_without_python)},
    )
    assert result.returncode == 1
    assert "python3 is required to check for hosting addresses" in result.stdout


def test_checker_failure_fails_the_lint(lint_repo):
    (lint_repo / "src/newsletter_uploader/hosting_links.py").write_text(
        'raise RuntimeError("checker failed")\n', encoding="utf-8"
    )
    result = run_lint(
        lint_repo, {"editions/welcome.html": '<a href="https://axiom.org/">Axiom</a>'}
    )
    assert result.returncode == 1
    assert (
        "Could not check editions/welcome.html for hosting addresses" in result.stdout
    )


def test_no_html_files_passes(lint_repo):
    result = run_lint(lint_repo, {})
    assert result.returncode == 0
    assert "No newsletter HTML files found" in result.stdout
