# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2020, Ansible Project

from __future__ import annotations

import re

import pytest

from antsibull_tool.collection import CollectionDetails, load_collection_details

LOAD_DATA_GOOD = [
    (
        r"""---
namespace: foo
name: bar
""",
        "galaxy.yml",
        CollectionDetails(namespace="foo", name="bar", dependencies={}),
    ),
    (
        r"""{
 "collection_info": {
  "description": null,
  "repository": "",
  "tags": [],
  "dependencies": {},
  "authors": [
   "Ansible (https://ansible.com)"
  ],
  "issues": "",
  "name": "testcol",
  "license": [
   "GPL-3.0-or-later"
  ],
  "documentation": "",
  "namespace": "testns",
  "version": "0.1.1231",
  "readme": "README.md",
  "license_file": "COPYING",
  "homepage": ""
 },
 "file_manifest_file": {
  "format": 1,
  "ftype": "file",
  "chksum_sha256": "4c15a867ceba8ba1eaf2f4a58844bb5dbb82fec00645fc7eb74a3d31964900f6",
  "name": "FILES.json",
  "chksum_type": "sha256"
 },
 "format": 1
}""",
        "MANIFEST.json",
        CollectionDetails(namespace="testns", name="testcol", dependencies={}),
    ),
]


@pytest.mark.parametrize("data, filename, expected", LOAD_DATA_GOOD)
def test_load_collection_details(data, filename, expected, tmp_path):
    (tmp_path / filename).write_text(data, encoding="utf-8")
    assert load_collection_details(tmp_path) == expected


LOAD_DATA_BAD = [
    (
        r"""
- namespace: foo
- name: bar
""",
        "galaxy.yml",
        "galaxy\\.yml is not a global mapping$",
    ),
    (
        r"""---
namespace: foo
""",
        "galaxy.yml",
        "1 validation error for CollectionDetails\nname\n  Field required.*",
    ),
    (
        r"""{"collection_info": []}""",
        "MANIFEST.json",
        "Cannot find collection_info in MANIFEST\\.json$",
    ),
]


@pytest.mark.parametrize("data, filename, expected", LOAD_DATA_BAD)
def test_load_collection_details_failure(data, filename, expected, tmp_path):
    (tmp_path / filename).write_text(data, encoding="utf-8")
    with pytest.raises(
        ValueError,
        match=f"^Error while loading collection details from .*: {expected}",
    ):
        load_collection_details(tmp_path)


def test_load_collection_details_failure_2(tmp_path):
    with pytest.raises(
        ValueError,
        match=f"^Cannot find galaxy.yml or MANIFEST.json in {re.escape(str(tmp_path))}$",
    ):
        load_collection_details(tmp_path)
