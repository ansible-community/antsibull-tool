# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024, Ansible Project

"""Collection details."""

from __future__ import annotations

import json
import typing as t
from dataclasses import dataclass
from pathlib import Path

from antsibull_fileutils.yaml import load_yaml_file


@dataclass
class CollectionDetails:
    namespace: str
    name: str
    dependencies: dict[str, str]

    @staticmethod
    def _parse_str(data: dict, key: t.Any) -> str:
        value = data.get(key)
        if not isinstance(value, str):
            raise ValueError(f"{key} is not a string, but {type(value)}")
        return value

    @classmethod
    def load(cls, data: dict) -> CollectionDetails:
        namespace = cls._parse_str(data, "namespace")
        name = cls._parse_str(data, "name")

        dependencies = {}
        deps = data.get("dependencies")
        if deps is not None:
            if not isinstance(deps, dict):
                raise ValueError(f"dependencies is not a mapping, but {type(deps)}")
            for k, v in deps.items():
                if not isinstance(k, str):
                    raise ValueError(f"dependencies key {k!r} is not a string")
                if not isinstance(v, str):
                    raise ValueError(f"dependencies.{k} value {v!r} is not a string")
                dependencies[k] = v

        return CollectionDetails(
            namespace=namespace, name=name, dependencies=dependencies
        )


def load_collection_details(path: Path) -> CollectionDetails:
    galaxy_yml_path = path / "galaxy.yml"
    if galaxy_yml_path.exists():
        try:
            data = load_yaml_file(galaxy_yml_path)
            if not isinstance(data, dict):
                raise ValueError("galaxy.yml is not a global mapping")
            return CollectionDetails.load(data)
        except Exception as exc:
            raise ValueError(
                f"Error while loading collection details from {galaxy_yml_path}: {exc}"
            ) from exc

    manifest_json_path = path / "MANIFEST.json"
    if manifest_json_path.exists():
        try:
            with manifest_json_path.open("rb") as f:
                data = json.load(f)
                if not isinstance(data, dict) or not isinstance(
                    data.get("collection_info"), dict
                ):
                    raise ValueError("Cannot find collection_info in MANIFEST.json")
                return CollectionDetails.load(data["collection_info"])
        except Exception as exc:
            raise ValueError(
                f"Error while loading collection details from {manifest_json_path}: {exc}"
            ) from exc

    raise ValueError(f"Cannot find galaxy.yml or MANIFEST.json in {path}")
