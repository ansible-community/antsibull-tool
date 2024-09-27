<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# antsibull-tool -- Ansible Community Toolkit

[![Discuss on Matrix at #antsibull:ansible.com](https://img.shields.io/matrix/antsibull:ansible.com.svg?server_fqdn=ansible-accounts.ems.host&label=Discuss%20on%20Matrix%20at%20%23antsibull:ansible.com&logo=matrix)](https://matrix.to/#/#antsibull:ansible.com)

Toolkit for the Ansible community. This is mainly the `antsibull-tool` command. Please check out the [documentation](https://ansible.readthedocs.io/projects/antsibull-tool/) for more information.

antsibull-docs is covered by the [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html).

!!! note
    Need help or want to discuss the project? See our [Community guide](community.md) to learn how to join the conversation!

## `antsibull-tool` subcommands

The main CLI tool, `antsibull-tool`, has multiple subcommands:

* `run-local-collection`: allows to run commands in a local collection checkout that expects the collection to be on Ansible's `COLLECTIONS_PATH`, and to be in the right directory structure.

  Examples:

  1. Running `ansible-test` in a collection checkout requires the correct directory structure:
     ```shell
     $ antsibull-tool run-local-collection -- ansible-test sanity --docker -v
     ```

  2. Running `antsibull-docs collection --use-current` requires the collection checkout to be in Ansible's `COLLECTIONS_PATH`, which in turn requires the correct directory structure:
     ```shell
     $ antsibull-tool run-local-collection --template -- antsibull-docs collection --use-current --dest-dir "{cwd}/docs" {collection_name}
     ```

## License

Unless otherwise noted in the code, it is licensed under the terms of the GNU
General Public License v3 or, at your option, later. See
[LICENSES/GPL-3.0-or-later.txt](https://github.com/ansible-community/antsibull-tool/tree/main/LICENSE)
for a copy of the license.

The repository follows the [REUSE Specification](https://reuse.software/spec/) for declaring copyright and
licensing information. The only exception are changelog fragments in ``changelog/fragments/``.
