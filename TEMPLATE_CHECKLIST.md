# Template checklist — de-templating a fresh copy

Work through this file **top to bottom in every repository created from
`forkrul/project-template-mvp-basic`**. When you finish, no evidence remains
that the project started from a template: step 9 proves it with a grep, and
step 10 deletes this file.

Pick your names first and use them everywhere below:

- `NEW-REPO` — the GitHub repository name (e.g. `forkrul-widgets`)
- `new-dist` — the Python distribution name in `pyproject.toml` (often the same)
- `new_pkg` — the Python import package (e.g. `forkrul_widgets`)

## 1. Rename the code and project identity

```sh
git mv src/mvp_template "src/new_pkg"
git grep -lz 'mvp_template' | xargs -0 sed -i 's/mvp_template/new_pkg/g'
git grep -lz 'forkrul-mvp-template' | xargs -0 sed -i 's/forkrul-mvp-template/new-dist/g'
git grep -lz 'project-template-mvp-basic' | xargs -0 sed -i 's/project-template-mvp-basic/NEW-REPO/g'
uv lock && make check   # regenerate the lockfile under the new name; stay green
```

## 2. Rewrite the identity prose (sed cannot do this part)

- [ ] `README.md` — real title, real one-liner, rewrite **What's inside** for this
      project, and **delete the "Using this template" section entirely**.
- [ ] `AGENTS.md` — replace the `## Project` sentence (and drop its
      "TEMPLATE_CHECKLIST" remark); prune any rule that does not apply.
- [ ] `pyproject.toml` — real `description`.
- [ ] `src/new_pkg/` — replace the placeholder docstrings in `__init__.py` and
      `core.py` (they name the template), or replace the module with real code and
      update `tests/` + `docs/api.md` to match.
- [ ] `docs/index.md` — real title and pitch.
- [ ] `docs/conf.py` — set `author`/`copyright` if "forkrul" is not right.

## 3. Reset the history-facing files

- [ ] `CHANGELOG.md` — one entry: `## 0.1.0 - <today>` with `_First release._`
      (Common Changelog; add real groups when 0.1.0 actually ships something).
- [ ] `LICENSE` — correct year and owner; swap the proprietary stub for MIT/Apache-2.0
      if this project will ever be public.
- [ ] `SECURITY.md` — confirm the reporting route (private GitHub advisory) is enabled
      on the new repo.

## 4. Choose shared packages

- [ ] Pick what this project needs from `PACKAGES.md` and `uv add` it (auth notes are
      in that file).
- [ ] Delete the rows you did not adopt — or delete `PACKAGES.md` entirely and rely on
      the estate copy in the template repo.

## 5. Wire up CI

- [ ] Replace `woodpecker.example.com` in `README.md` with the real Woodpecker host,
      and enable the repo in the Woodpecker UI (it reads `.woodpecker/` as-is).
- [ ] Onboard the local pre-commit engine: `wp-local init --template python-uv`
      (it keeps the committed `.woodpecker/` pipelines and writes `.wp-local.yml` +
      hooks; commit `.wp-local.yml`).
- [ ] Push a branch and confirm the GitHub Actions **CI** workflow runs green.
- [ ] Confirm both badges at the top of `README.md` render.
- [ ] `make ci-local` passes on a machine with Docker (see `docs/ci.md` caveats).

## 6. Repository settings (GitHub)

- [ ] Repo is **private** (estate rule) with a real description and topics.
- [ ] "Template repository" is **unchecked** (only the template keeps it).
- [ ] Branch protection on the default branch; squash merges; delete-branch-on-merge.
- [ ] Dependabot alerts/updates enabled (`.github/dependabot.yml` is already there).

## 7. Docs stay warning-free

- [ ] `make docs` — must exit green: the build runs `sphinx-build -W --keep-going`,
      so one warning fails it. Fix warnings, never relax the flag.

## 8. Full verification

```sh
make check      # lint + test + docs, all green
```

## 9. Prove no template residue remains

The following must print **nothing** (it excludes only this checklist, which the
next step removes):

```sh
git grep -nIE 'mvp[_-]template|project-template-mvp-basic|Use this template|woodpecker\.example\.com' -- ':!TEMPLATE_CHECKLIST.md'
```

## 10. Remove the evidence, commit, tag

```sh
git rm TEMPLATE_CHECKLIST.md
git add -A && git commit -m "chore: de-template repository"
git tag v0.1.0    # matches the CHANGELOG entry; push tags with the branch
```

Done: the repository now stands on its own.
