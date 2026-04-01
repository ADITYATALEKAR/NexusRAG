"""Index management command for the CLI."""

import json

import typer
from rich.console import Console

from cli.utils import get_config, resolve_cli_value

console = Console()


def index_command(
    output: str = typer.Option("text", "--output", help="Output format: text or json."),
) -> None:
    """Inspect basic index and system readiness state."""
    from sdk.client import RAGClient

    output = str(resolve_cli_value(output))
    with RAGClient(
        base_url=get_config("api_url"),
        api_key=get_config("api_key") or None,
        timeout=float(get_config("timeout", 30.0)),
    ) as client:
        result = client.health()

    if output == "json":
        console.print_json(json=json.dumps(result))
        return
    console.print(f"System status: {result.get('status', 'unknown')}")


def register(app: typer.Typer) -> None:
    """Register the index command on the root Typer app."""
    app.command(name="index")(index_command)
