# SYSNET-CZ GitHub Organization

Tento repozitář obsahuje:
- **Workflow šablony** — zobrazují se při vytváření nového Actions workflow v každém repos v org
- **Profil organizace** — `profile/README.md`

## Workflow šablony

| Šablona | Použití |
|---|---|
| `sysnet-docker-ci` | Docker build + push na Docker Hub (sysnetcz/) |
| `sysnet-python-ci` | Python testy + ruff lint + mypy |
| `sysnet-basic-ci` | Základní šablona pro ostatní projekty |

Všechny šablony jsou přednastaveny na **self-hosted runner** (`hermes-vm`).

## Přidání šablony do nového projektu

1. Jdi do repozitáře → **Actions** → **New workflow**
2. V sekci **SYSNET-CZ** vyber příslušnou šablonu
3. Upravit dle potřeby a commitni

## Reusable workflows - Python knihovny na PyPI

| Workflow | Účel |
|---|---|
| `python-ci.yml` | lint, testy v matici verzí, build a `twine check` |
| `python-publish.yml` | ověření tagu/verze, publikace na PyPI přes OIDC (Trusted Publishing) |
| `python-release.yml` | GitHub Release z `CHANGELOG.md` |

Volat přes `@v1`. Dokumentace: [`docs/python-packaging.md`](docs/python-packaging.md),
[`docs/python-release-process.md`](docs/python-release-process.md),
[`docs/pypi-trusted-publishing.md`](docs/pypi-trusted-publishing.md).
