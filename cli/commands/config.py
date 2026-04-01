"""Config management command for the CLI."""

from typing import Optional

import typer
from rich.console import Console

from cli.utils import CONFIG_PATH, load_config, parse_bool_option, resolve_cli_value, set_config

console = Console()


def config_command(
    key: Optional[str] = typer.Option(None, "--key", help="Configuration key to set."),
    value: Optional[str] = typer.Option(None, "--value", help="Configuration value to set."),
    list_all: str = typer.Option(
        "false",
        "--list",
        help="Print the current CLI configuration.",
    ),
) -> None:
    """Manage CLI configuration."""
    key = resolve_cli_value(key)
    value = resolve_cli_value(value)
    if parse_bool_option(list_all, "list"):
        if CONFIG_PATH.exists():
            console.print(CONFIG_PATH.read_text(encoding="utf-8"))
        else:
            console.print(load_config())
        return

    if key and value is not None:
        set_config(key, value)
        console.print(f"Saved {key}")
        return

    console.print("Use `rag-cli config --list` or `rag-cli config --key <key> --value <value>`.")


def register(app: typer.Typer) -> None:
    """Register the config command on the root Typer app."""
    app.command(name="config")(config_command)
