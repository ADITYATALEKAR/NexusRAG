"""Typer CLI entrypoint."""

import typer
import typer.core as typer_core

from cli.commands import config as config_command
from cli.commands import eval as eval_command
from cli.commands import index as index_command
from cli.commands import ingest as ingest_command
from cli.commands import query as query_command

# Typer 0.12.x and Click 8.3.x disagree on Rich help rendering internals.
# Disable Typer's Rich-formatted help while keeping Rich available for command output.
typer_core.rich = None

app = typer.Typer(name="rag-cli", help="RAG System CLI", no_args_is_help=True)

query_command.register(app)
ingest_command.register(app)
index_command.register(app)
eval_command.register(app)
config_command.register(app)


def main() -> None:
    """Run the CLI application."""
    app()


if __name__ == "__main__":
    main()
