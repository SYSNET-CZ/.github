"""Tests of the version/name verification embedded in python-publish.yml.

Extracts the inline Python of the "Verify distribution" step, builds a tiny fixture
package and runs the step with valid and invalid tags/names.
Run: python -m pytest tests/   (needs: pytest, pyyaml, build, packaging)
"""
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

WORKFLOW = Path(__file__).parent.parent / ".github/workflows/python-publish.yml"


def _step_script() -> str:
    wf = yaml.safe_load(WORKFLOW.read_text())
    step = next(s for s in wf["jobs"]["verify"]["steps"] if s.get("id") == "dist")
    run = step["run"]
    start = run.index("<<'PY'\n") + len("<<'PY'\n")
    return textwrap.dedent(run[start:run.rindex("PY")])


@pytest.fixture(scope="module")
def dist_dir(tmp_path_factory):
    root = tmp_path_factory.mktemp("pkg")
    (root / "fixture_pkg").mkdir()
    (root / "fixture_pkg/__init__.py").write_text("")
    (root / "pyproject.toml").write_text(
        '[build-system]\nrequires=["setuptools>=68"]\nbuild-backend="setuptools.build_meta"\n'
        '[project]\nname="Fixture_Pkg"\nversion="1.2.3"\n'
    )
    subprocess.run([sys.executable, "-m", "build", "--outdir", "dist"], cwd=root, check=True, capture_output=True)
    return root


def _run(root: Path, tag: str, name: str):
    out = root / "gh_output"
    out.write_text("")
    env = {**os.environ, "TAG": tag, "PACKAGE_NAME": name, "GITHUB_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, "-c", _step_script()], cwd=root, env=env, capture_output=True, text=True)
    return r, out.read_text()


def test_matching_tag_and_name_passes(dist_dir):
    r, out = _run(dist_dir, "v1.2.3", "fixture-pkg")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "version=1.2.3" in out


def test_version_mismatch_fails(dist_dir):
    r, _ = _run(dist_dir, "v1.2.4", "fixture-pkg")
    assert r.returncode == 1 and "!= tag" in r.stdout


def test_name_mismatch_fails(dist_dir):
    r, _ = _run(dist_dir, "v1.2.3", "other-pkg")
    assert r.returncode == 1 and "název" in r.stdout


def test_tag_regex_in_workflow():
    wf = yaml.safe_load(WORKFLOW.read_text())
    script = wf["jobs"]["verify"]["steps"][0]["run"]
    for tag, ok in [("v1.2.3", True), ("1.2.3", False), ("v1.2", False), ("v1.2.3-rc1", False), ("main", False)]:
        env = {**os.environ, "REF_TYPE": "tag", "TAG": tag}
        r = subprocess.run(["bash", "-c", script], env=env, capture_output=True, text=True)
        assert (r.returncode == 0) == ok, tag
    r = subprocess.run(["bash", "-c", script], env={**os.environ, "REF_TYPE": "branch", "TAG": "v1.2.3"}, capture_output=True, text=True)
    assert r.returncode == 1
