# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024, Ansible Project

"""Run things in local collection checkout."""

from __future__ import annotations

import os
import subprocess
import typing as t
from collections.abc import Sequence
from pathlib import Path

from antsibull_core.logging import log
from antsibull_fileutils.copier import CollectionCopier, Copier, CopierError, GitCopier
from antsibull_fileutils.vcs import detect_vcs

from . import app_context
from .collection import CollectionDetails, load_collection_details

mlog = log.fields(mod=__name__)


_ANSIBLE_COLLECTIONS_PATHS = ("ANSIBLE_COLLECTIONS_PATH", "ANSIBLE_COLLECTIONS_PATHS")


def _template_argv(
    argv: Sequence[str],
    *,
    root_dir: str,
    collection_dir: str,
    path: Path,
    details: CollectionDetails,
) -> list[str]:
    subs = {
        "root_path": root_dir,
        "collection_path": collection_dir,
        "cwd": str(path),
        "namespace": details.namespace,
        "name": details.name,
        "collection_name": f"{details.namespace}.{details.name}",
    }
    argv = list(argv)
    for i, arg in enumerate(argv):
        try:
            argv[i] = arg.format(**subs)
        except Exception as exc:
            raise ValueError(
                f"Error while templating argument {arg!r} (#{i + 1}): {exc}"
            ) from exc
    return argv


def _prepare_environment(root_dir: str) -> dict[str, str]:
    env = dict(os.environ)
    existing_path = None
    for env_var in _ANSIBLE_COLLECTIONS_PATHS:
        if env_var in env:
            if existing_path is None:
                existing_path = env[env_var]
            del env[env_var]
    modified_path = root_dir
    if existing_path is not None:
        modified_path = f"{modified_path}:{existing_path}"
    for env_var in _ANSIBLE_COLLECTIONS_PATHS:
        env[env_var] = modified_path
    return env


def run_local_collection() -> int:
    flog = mlog.fields(func="generate_docs")
    flog.debug("Begin processing docs")

    app_ctx = app_context.app_ctx.get()

    argv: Sequence[str] = app_ctx.extra["argv"]
    vcs: t.Literal["auto", "none", "git"] = app_ctx.extra["vcs"]
    template: bool = app_ctx.extra["template"]

    path = Path.cwd()

    try:
        if vcs == "auto":
            vcs = detect_vcs(path, log_debug=flog.debug, log_info=flog.info)

        copier = {
            "none": Copier,
            "git": GitCopier,
        }[vcs]()

        details = load_collection_details(path)

        with CollectionCopier(
            source_directory=str(path),
            namespace=details.namespace,
            name=details.name,
            copier=copier,
            log_debug=log.debug,
        ) as (root_dir, collection_dir):
            if template:
                argv = _template_argv(
                    argv,
                    root_dir=root_dir,
                    collection_dir=collection_dir,
                    path=path,
                    details=details,
                )
            env = _prepare_environment(root_dir)
            p = subprocess.run(argv, check=False, cwd=collection_dir, env=env)
            return p.returncode
    except (ValueError, CopierError) as e:
        flog.error(str(e))
        return 5
