# Release proces Python knihoven

## Postup vydání

1. Změna kódu přes pull request, zelené CI (`python-ci.yml`), schválení.
2. Samostatný PR "release": zvýšit `version` v `pyproject.toml` (SemVer, PEP 440) a doplnit sekci
   `## [X.Y.Z]` do `CHANGELOG.md`. Sloučit do `main`.
3. Správce vytvoří tag na commitu z `main`: `git tag vX.Y.Z && git push origin vX.Y.Z`.
   Existující tagy se nepřepisují (žádný `git tag -f`, žádný force push).
4. Spustí se `publish.yml`:
   - `verify`: tag musí být `vX.Y.Z`, commit musí být na `main`, sestaví se wheel+sdist, `twine check --strict`,
     název a verze v obou archivech musí odpovídat parametru a tagu, verze nesmí na PyPI existovat.
   - `publish`: čeká na environment `pypi` (schválení, pokud je dostupné), publikuje přes OIDC.
   - `release`: vytvoří GitHub Release z `CHANGELOG.md` s odkazem na PyPI projekt.
5. Ověřte instalaci v čistém venv: `pip install sysnet-priklad==X.Y.Z && python -c "import ..."`.

## Opakované spuštění

- Selhal `verify` nebo `publish` před nahráním: opravte příčinu (mimo tag) a použijte *Re-run*; tag se nemění.
  Pokud je třeba změnit kód, vydejte novou verzi.
- Verze už na PyPI je: `verify` selže záměrně. Nahrazení neexistuje.
- Selhal jen `release`: *Re-run failed jobs*. Job je idempotentní (vytvoří nebo aktualizuje release).

## Nápravné vydání a rollback

Publikovanou verzi na PyPI **nelze přepsat ani znovu nahrát** (ani po smazání). Postup:

1. Vadnou verzi označte na PyPI jako **yanked** (Manage -> Release -> Yank, s důvodem). Instalace s přesným
   pinem funguje dál, běžné `pip install` ji přeskočí.
2. Opravu vydejte jako vyšší verzi (např. 1.2.4), nikdy ne přes opětovné použití čísla.
3. Do GitHub Release vadné verze doplňte upozornění; tag nemažte ani nepřepisujte.

## Kompromitace vydání

1. Okamžitě yank dotčených verzí; je-li to nutné, smazání verze/projektu provádí jen vlastník PyPI.
2. Odeberte Trusted Publisher (PyPI -> Publishing), případně dočasně zrušte oprávnění uživatelů projektu.
3. Zkontrolujte audit log PyPI, historii tagů a běhy workflow; zrušte všechny dlouhodobé tokeny (`PYPI_API_TOKEN`).
4. Vydejte čistou verzi z ověřeného commitu, nové přihlašovací údaje a Trusted Publisher nastavte až po analýze.
5. Informujte konzumenty (závislé repozitáře: `sysnet-auth` -> `sysnet-pyutils`, `sysnet-docversion` -> `sysnet-soft-delete`).
