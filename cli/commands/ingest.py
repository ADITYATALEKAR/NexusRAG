"""Document ingestion command for the CLI."""

from pathlib import Path
import time

import typer
from rich.console import Console

from cli.utils import get_config, parse_bool_option, resolve_cli_value

console = Console()


def ingest_command(
    path: str = typer.Argument(..., help="File or directory to ingest."),
    recursive: str = typer.Option(
        "false",
        "--recursive",
        help="Recursively ingest all files beneath a directory.",
    ),
    watch: str = typer.Option(
        "false",
        "--watch",
        help="Keep watching the target for new files.",
    ),
) -> None:
    """Ingest documents into the system."""
    from sdk.client import RAGClient

    path = str(resolve_cli_value(path))
    target = Path(path)
    if not target.exists():
        raise typer.BadParameter(f"Path does not exist: {path}")

    recursive_enabled = parse_bool_option(recursive, "recursive")
    watch_enabled = parse_bool_option(watch, "watch")
    seen: set[str] = set()
    with RAGClient(
        base_url=get_config("api_url"),
        api_key=get_config("api_key") or None,
        timeout=float(get_config("timeout", 30.0)),
    ) as client:
        while True:
            files = _resolve_files(target, recursive=recursive_enabled)
            pending = [file_path for file_path in files if str(file_path) not in seen]
            if not pending and not watch_enabled:
                break

            for file_path in pending:
                try:
                    result = client.ingest(str(file_path))
                    console.print(f"OK {file_path.name} ({result.chunks_indexed} chunks)")
                    seen.add(str(file_path))
                except Exception as error:  # noqa: BLE001
                    console.print(f"FAIL {file_path.name}: {error}", style="red")

            if not watch_enabled:
                break
            time.sleep(2)


def register(app: typer.Typer) -> None:
    """Register the ingest command on the root Typer app."""
    app.command(name="ingest")(ingest_command)


def _resolve_files(target: Path, recursive: bool) -> list[Path]:
    """Return files to ingest from a file or directory target."""
    if target.is_file():
        return [target]
    pattern = "**/*" if recursive else "*"
    return [path for path in target.glob(pattern) if path.is_file()]
