# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2024, Ansible Project

# PYTHON_ARGCOMPLETE_OK

"""Entrypoint to the antsibull-tool script."""

from __future__ import annotations

import argparse
import os
import os.path
import sys
from collections.abc import Callable
from importlib import import_module

try:
    import argcomplete

    HAS_ARGCOMPLETE = True
except ImportError:
    HAS_ARGCOMPLETE = False

import twiggy  # type: ignore[import]
from antsibull_core.logging import initialize_app_logging, log

initialize_app_logging()

# We have to call initialize_app_logging() before these imports so that the log object is configured
# correctly before other antisbull modules make copies of it.
# pylint: disable=wrong-import-position
from antsibull_core import app_context  # noqa: E402
from antsibull_core.args import (  # noqa: E402
    InvalidArgumentError,
    get_toplevel_parser,
    normalize_toplevel_options,
)
from antsibull_core.compat import BooleanOptionalAction  # noqa: E402
from antsibull_core.config import ConfigError, load_config  # noqa: E402

import antsibull_tool  # noqa: E402

from .schemas.app_context import ToolAppContext  # noqa: E402

# pylint: enable=wrong-import-position


mlog = log.fields(mod=__name__)


def _create_loader(module: str, function: str) -> Callable[[], Callable[[], int]]:
    def load():
        module_obj = import_module(f"antsibull_tool.{module}")
        return getattr(module_obj, function)

    return load


#: Mapping from command line subcommand names to functions which implement those
#: The functions need to take a single argument, the processed list of args.
ARGS_MAP: dict[str, Callable[[], Callable[[], int]]] = {
    "run-local-collection": _create_loader("run", "run_local_collection"),
}


def parse_args(program_name: str, args: list[str]) -> argparse.Namespace:
    """
    Parse and coerce the command line arguments.

    :arg program_name: The name of the program
    :arg args: A list of the command line arguments
    :returns: A :python:obj:`argparse.Namespace`
    :raises InvalidArgumentError: Whenever there's something wrong with the arguments.
    """
    flog = mlog.fields(func="parse_args")
    flog.fields(program_name=program_name, raw_args=args).info("Enter")

    parser = get_toplevel_parser(
        prog=program_name,
        package="antsibull_tool",
        package_version=antsibull_tool.__version__,
        program_name="antsibull-tool",
        description="Ansible Community Toolkit",
    )
    subparsers = parser.add_subparsers(
        title="Subcommands", dest="command", help="for help use: `SUBCOMMANDS -h`"
    )
    subparsers.required = True

    run_local_collection_parser = subparsers.add_parser(
        "run-local-collection",
        description="Run command in the local collection checkout."
        " The command's return code is returned without modification.",
    )

    run_local_collection_parser.add_argument(
        "argv", metavar="command", nargs="+", help="The command to run."
    )

    run_local_collection_parser.add_argument(
        "--vcs",
        choices=["auto", "none", "git"],
        default="auto",
        help="The VCS to use to determine which files to copy.",
    )

    run_local_collection_parser.add_argument(
        "--template",
        action=BooleanOptionalAction,
        default=False,
        help="Use Python string templating for commands."
        " Variables: {cwd}, {root_path}, {collection_path}, {namespace},"
        " {name}, {collection_name}",
    )

    # This must come after all parser setup
    if HAS_ARGCOMPLETE:
        argcomplete.autocomplete(parser)

    flog.debug("Argument parser setup")

    parsed_args: argparse.Namespace = parser.parse_args(args)
    flog.fields(args=parsed_args).debug("Arguments parsed")

    # Validation and coercion
    normalize_toplevel_options(parsed_args)
    flog.fields(args=parsed_args).debug("Arguments normalized")

    return parsed_args


def run(args: list[str]) -> int:
    """
    Run the program.

    :arg args: A list of command line arguments.  Typically :python:`sys.argv`.
    :returns: A program return code.  0 for success, integers for any errors.  These are documented
        in :func:`main`.
    """
    flog = mlog.fields(func="run")
    flog.fields(raw_args=args).info("Enter")

    program_name = os.path.basename(args[0])
    try:
        parsed_args: argparse.Namespace = parse_args(program_name, args[1:])
    except InvalidArgumentError as e:
        print(e)
        return 2
    flog.fields(args=parsed_args).info("Arguments parsed")

    try:
        cfg = load_config(parsed_args.config_file, app_context_model=ToolAppContext)
        flog.fields(config=cfg).info("Config loaded")
    except ConfigError as e:
        print(e)
        return 2

    context_data = app_context.create_contexts(
        args=parsed_args, cfg=cfg, app_context_model=ToolAppContext
    )
    with app_context.app_and_lib_context(context_data) as (app_ctx, dummy_):
        twiggy.dict_config(app_ctx.logging_cfg.model_dump())
        flog.debug("Set logging config")

        flog.fields(command=parsed_args.command).info("Action")
        return ARGS_MAP[parsed_args.command]()()


def main() -> int:
    """
    Entrypoint called from the script.

    console_scripts call functions which take no parameters.  However, it's hard to test a function
    which takes no parameters so this function lightly wraps :func:`run`, which actually does the
    heavy lifting.

    :returns: A program return code.

    Return codes:
        :0: Success
        :1: Unhandled error.  See the Traceback for more information.
        :2: There was a problem with the command line arguments
        :3: Unexpected problem downloading ansible-core
    """
    return run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
