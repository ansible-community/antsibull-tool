<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# antsibull-tool -- Ansible Community Toolkit
[![Documentation](https://img.shields.io/badge/docs-brightgreen.svg)](https://ansible.readthedocs.io/projects/antsibull-tool/changelog/)
[![Discuss on Matrix at #antsibull:ansible.com](https://img.shields.io/matrix/antsibull:ansible.com.svg?server_fqdn=ansible-accounts.ems.host&label=Discuss%20on%20Matrix%20at%20%23antsibull:ansible.com&logo=matrix)](https://matrix.to/#/#antsibull:ansible.com)
[![Nox badge](https://github.com/ansible-community/antsibull-tool/actions/workflows/nox.yml/badge.svg)](https://github.com/ansible-community/antsibull-tool/actions/workflows/nox.yml)
[![Codecov badge](https://img.shields.io/codecov/c/github/ansible-community/antsibull-tool)](https://codecov.io/gh/ansible-community/antsibull-tool)
[![REUSE status](https://api.reuse.software/badge/github.com/ansible-community/antsibull-tool)](https://api.reuse.software/info/github.com/ansible-community/antsibull-tool)

Toolkit for the Ansible community. This is mainly the `antsibull-tool` command. Please check out the [documentation](https://ansible.readthedocs.io/projects/antsibull-tool/) for more information.

You can find a list of changes in [the antsibull-tool changelog](https://ansible.readthedocs.io/projects/antsibull-tool/changelog/).

antsibull-tool is covered by the [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html).

## Community

Need help or want to discuss the project? See our [Community guide](https://ansible.readthedocs.io/projects/antsibull-tool/community/) to learn how to join the conversation!

## Versioning and compatibility

From version 1.0.0 on, antsibull-tool sticks to semantic versioning and aims at providing no backwards compatibility breaking changes **to the command line API (antsibull-tool)** during a major release cycle. We might make exceptions from this in case of security fixes for vulnerabilities that are severe enough.

We explicitly exclude code compatibility. **antsibull-tool is not supposed to be used as a library.** If you want to use a certain part of antsibull-tool as a library, please create an issue so we can discuss whether we add a stable interface for **parts** of the Python code. We do not promise that this will actually happen though.

## Development

Install and run `nox` to run all tests. That's it for simple contributions!
`nox` will create virtual environments in `.nox` inside the checked out project
and install the requirements needed to run the tests there.

---

antsibull-tool depends on the sister antsibull-core and antsibull-fileutils projects.
By default, `nox` will install a development version of these projects from Github.
If you're hacking on antsibull-core and/or antsibull-fileutils alongside antsibull-tool,
nox will automatically install the projects from  `../antsibull-core`
and `../antsibull-fileutils` when running tests if those paths exist.
You can change this behavior through the `OTHER_ANTSIBULL_MODE` env var:

- `OTHER_ANTSIBULL_MODE=auto` — the default behavior described above
- `OTHER_ANTSIBULL_MODE=local` — install the projects from `../antsibull-core`
  and `../antsibull-fileutils`.
  Fail if those paths don't exist.
- `OTHER_ANTSIBULL_MODE=git` — install the projects from the Github main branch
- `OTHER_ANTSIBULL_MODE=pypi` — install the latest versions from PyPI

---

To run specific tests:

1. `nox -e test` to only run unit tests;
2. `nox -e lint` to run all linters and formatter;
3. `nox -e codeqa` to run `flake8`, `pylint`, `reuse lint`, and `antsibull-changelog lint`;
4. `nox -e formatters` to run `isort` and `black`;
5. `nox -e typing` to run `mypy`.

To create a more complete local development env:

```console
git clone https://github.com/ansible-community/antsibull-core.git
git clone https://github.com/ansible-community/antsibull-fileutils.git
cd antsibull-tool
python3 -m venv venv
. ./venv/bin/activate
pip install -e '.[dev]' -e ../antsibull-core -e ../antsibull-fileutils
[...]
nox
```

## Creating a new release:

1. Run `nox -e bump -- <version> <release_summary_message>`. This:
   * Bumps the package version in `src/antsibull_tool/__init__.py`.
   * Creates `changelogs/fragments/<version>.yml` with a `release_summary` section.
   * Runs `antsibull-changelog release --version <version>` and adds the changed files to git.
   * Commits with message `Release <version>.` and runs `git tag -a -m 'antsibull-tool <version>' <version>`.
   * Runs `hatch build --clean`.
2. Run `git push` to the appropriate remotes.
3. Once CI passes on GitHub, run `nox -e publish`. This:
   * Runs `hatch publish`;
   * Bumps the version to `<version>.post0`;
   * Adds the changed file to git and run `git commit -m 'Post-release version bump.'`;
4. Run `git push --follow-tags` to the appropriate remotes and create a GitHub release.

## License

Unless otherwise noted in the code, it is licensed under the terms of the GNU
General Public License v3 or, at your option, later. See
[LICENSES/GPL-3.0-or-later.txt](https://github.com/ansible-community/antsibull-tool/tree/main/LICENSE)
for a copy of the license.

The repository follows the [REUSE Specification](https://reuse.software/spec/) for declaring copyright and
licensing information. The only exception are changelog fragments in ``changelog/fragments/``.
