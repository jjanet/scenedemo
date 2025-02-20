#!/usr/bin/env python
from argparse import ArgumentParser

from src.datasets.commands.convert import ConvertCommand
from src.datasets.commands.convert_to_parquet import ConvertToParquetCommand
from src.datasets.commands.delete_from_hub import DeleteFromHubCommand
from src.datasets.commands.env import EnvironmentCommand
from src.datasets.commands.test import TestCommand
from src.datasets.utils.logging import set_verbosity_info


def parse_unknown_args(unknown_args):
    return {key.lstrip("-"): value for key, value in zip(unknown_args[::2], unknown_args[1::2])}


def main():
    parser = ArgumentParser(
        "HuggingFace Datasets CLI tool", usage="datasets-cli <command> [<args>]", allow_abbrev=False
    )
    commands_parser = parser.add_subparsers(help="datasets-cli command helpers")
    set_verbosity_info()

    # Register commands
    ConvertCommand.register_subcommand(commands_parser)
    EnvironmentCommand.register_subcommand(commands_parser)
    TestCommand.register_subcommand(commands_parser)
    ConvertToParquetCommand.register_subcommand(commands_parser)
    DeleteFromHubCommand.register_subcommand(commands_parser)

    # Parse args
    args, unknown_args = parser.parse_known_args()
    if not hasattr(args, "func"):
        parser.print_help()
        exit(1)
    kwargs = parse_unknown_args(unknown_args)

    # Run
    service = args.func(args, **kwargs)
    service.run()


if __name__ == "__main__":
    main()
