# PyPI Trusted Publishing (OIDC)

Publikace nepoužívá žádný dlouhodobý PyPI token ani heslo v GitHub Secrets. Job `publish` dostane
krátkodobý OIDC token od GitHubu a PyPI jej vymění za jednorázový upload token.

## Registrace Trusted Publisheru (manuálně, správce PyPI)

PyPI nenabízí podporované API pro správu Trusted Publisherů; registrace se dělá ve webovém UI. Automatizace UI
není součástí řešení.

Existující projekt: PyPI -> projekt -> **Manage** -> **Publishing** -> *Add a new publisher* -> GitHub:

| Pole | Hodnota |
|---|---|
| PyPI project name | např. `sysnet-pyutils` |
| Owner | `SYSNET-CZ` |
| Repository name | např. `pyutils` |
| Workflow name | `publish.yml` (**volající workflow s krokem uploadu**) |
| Environment name | `pypi` |

Nový projekt: stejná tabulka v **Your account -> Publishing** jako *Pending Publisher*; projekt vznikne prvním
publikováním. Projekt, jehož název vlastní jiný subjekt, nelze registrovat - rozhodnutí o názvu je na správci.

Pro TestPyPI se registruje samostatně na https://test.pypi.org (jiný účet i publisher), environment `testpypi`,
`repository-url: https://test.pypi.org/legacy/`.

## Ověření shody identity

OIDC claim `repository` je volající repozitář a `workflow_ref` volající workflow, proto publisher musí
odpovídat repozitáři a souboru `publish.yml` knihovny. Nesoulad se projeví chybou `invalid-publisher`
při publikaci. Pro privátní repozitáře se attestations nevytvářejí (`attestations: false`).

## Doporučená ochrana (GitHub)

- Environment `pypi`: omezit na deployment tags `v*`; požadovaní reviewers jen pokud to plán dovoluje
  (u privátních repozitářů je to dostupné až v plánu Enterprise, ověřte).
- Alternativa: ruleset `v*` tagů (create/update/delete jen správci) a branch protection / ruleset na `main`
  (PR + povinné CI).
- Workflow pinují všechny actions na SHA; org doporučená práva `GITHUB_TOKEN`: read.

## Správa oprávnění

- PyPI: role *Owner* jen pro nezbytné osoby, ostatní *Maintainer*; vyžadujte 2FA.
- Po zprovoznění Trusted Publishingu smazat secret `PYPI_API_TOKEN` (repo i org) a token na PyPI zneplatnit.
- Odchod člena týmu: odebrat z PyPI projektů a z GitHub týmů s právem push na tagy.

## Upload musí být ve volajícím workflow

Pokus o upload z reusable workflow (`v1.1.0`) selhal na `invalid-publisher`, ačkoli publisher odpovídal volajícímu
workflow. PyPI reusable workflow jako publishera oficiálně nepodporuje (warehouse#11096). Proto `python-build.yml`
(od `v1.2.0`) jen ověřuje a sestavuje a krok `pypa/gh-action-pypi-publish` je přímo v `publish.yml` knihovny.
Ověřeno úspěšným uploadem dev verze na TestPyPI.

## TestPyPI

`python-build.yml` s `repository-url: https://test.pypi.org/legacy/` běží v testovacím režimu: nevyžaduje tag ani
větev `main`, ale **přijme jen dev verze** (`X.Y.Z.devN`), takže produkční číslo verze nelze touto cestou spálit.
Doporučené spouštění: `workflow_dispatch` ve vlastním `publish-test.yml` s environmentem `testpypi`.

## Verze reusable workflows

Odkazujte přesným tagem (`@v1.2.0`); existující tagy se nepřepisují, ani pohyblivý `v1` (zůstává na `v1.0.0`); `v1.0.0` a `v1.1.0` obsahují nepoužitelný `python-publish.yml`.
