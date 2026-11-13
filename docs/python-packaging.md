# Standard Python knihoven SYSNET-CZ

Jak založit sdílenou Python knihovnu a připojit ji k centrálnímu CI/CD v tomto repozitáři.

## 1. Založení nové knihovny

1. Repozitář `SYSNET-CZ/<jmeno>` s topics `library` a `python` (viz `docs/topic-guidelines.md` v `repo-catalog`).
2. Distribuční název s prefixem `sysnet-` (např. `sysnet-pyutils`). **Nikdy** nepoužívejte holý název
   (`pyutils`, `audit` už na PyPI patří cizím lidem). Import název se může lišit (`audit_lib`).
3. Před prvním vydáním ověřte, že název na PyPI není obsazen jiným subjektem
   (`curl -s -o /dev/null -w '%{http_code}' https://pypi.org/pypi/<nazev>/json`; 404 = volný).
   Obsazený název se **nepřejmenovává automaticky** - rozhodnutí patří správci.

## 2. Povinný obsah `pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]            # nebo setuptools>=68; stávající funkční backend neměňte
build-backend = "hatchling.build"

[project]
name = "sysnet-priklad"
version = "0.1.0"                   # PEP 440, jediný zdroj verze (žádný zvláštní soubor VERSION)
description = "..."
readme = "README.md"
requires-python = ">=3.11"
license = "AGPL-3.0-or-later"       # SPDX výraz (PEP 639); licenční soubor v repu
license-files = ["LICENSE*"]
authors = [{ name = "SYSNET s.r.o.", email = "info@sysnet.cz" }]
dependencies = ["..."]              # jen runtime, s rozumnou dolní mezí

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]    # pro python-ci výchozí install-command: pip install -e ".[dev]"

[project.urls]
Source = "https://github.com/SYSNET-CZ/<repo>"
Issues = "https://github.com/SYSNET-CZ/<repo>/issues"
Changelog = "https://github.com/SYSNET-CZ/<repo>/blob/main/CHANGELOG.md"
```

Pravidla: do balíčku nepatří secrets, `.env`, interní konfigurace ani testovací data s osobními údaji.
Obsah vzniklých archivů zkontrolujte: `python -m build && unzip -l dist/*.whl && tar tzf dist/*.tar.gz`.

## 3. Napojení na centrální CI/CD

`.github/workflows/ci.yml` v knihovně:

```yaml
name: CI
on:
  pull_request:
  push:
    branches: [main]
permissions: {}
jobs:
  ci:
    permissions:
      contents: read
    uses: SYSNET-CZ/.github/.github/workflows/python-ci.yml@v1.2.0
    with:
      python-versions: '["3.11", "3.12", "3.13"]'
```

`.github/workflows/publish.yml` - **název souboru musí být přesně `publish.yml`**, na něj se registruje Trusted Publisher.
Upload na PyPI musí být přímo v něm (PyPI oficiálně nepodporuje reusable workflow jako publishera, ověřeno
`invalid-publisher` při pokusu o upload z reusable workflow); ověření a build je centrální:

```yaml
name: Publish
on:
  push:
    tags: ["v[0-9]+.[0-9]+.[0-9]+"]
permissions: {}
concurrency:
  group: publish-${{ github.ref }}
  cancel-in-progress: false
jobs:
  build:
    permissions:
      contents: read
    uses: SYSNET-CZ/.github/.github/workflows/python-build.yml@v1.2.0
    with:
      package-name: sysnet-priklad
  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/download-artifact@9000827ccba6bdab643e8b6fd33ac0654aef8333 # v8.0.2
        with:
          name: python-dist
          path: dist/
      - uses: pypa/gh-action-pypi-publish@7245906fb61fa33a13554f9d5fb856fe61758086 # v1.14.3
        with:
          packages-dir: dist/
          attestations: false
  release:
    needs: publish
    permissions:
      contents: write
    uses: SYSNET-CZ/.github/.github/workflows/python-release.yml@v1.2.0
    with:
      package-name: sysnet-priklad
```

Volejte vždy přes přesný verzovaný tag (`@v1.2.0`), nikdy `@main`. Tagy se nepřepisují, každá změna reusable workflow je nový tag `v1.x.y`.

## 4. Runnery

CI (`python-ci.yml`) běží ve výchozím nastavení na `self-hosted`. Publikační job běží vždy na GitHub-hosted
`ubuntu-latest` - je krátký a nesmí používat sdílený dlouhodobý runner, který dostává OIDC identitu.
