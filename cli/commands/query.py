"""Query command for the CLI."""

import json

import typer
from rich.console import Console
from rich.table import Table

from cli.utils import get_config, parse_bool_option, resolve_cli_value

console = Console()


def query_command(
    text: str = typer.Argument(..., help="Question to ask the system."),
    top_k: int = typer.Option(5, "--top-k", help="Number of results to use."),
    show_evidence: str = typer.Option(
        "false",
        "--show-evidence",
        help="Include evidence and citations in the output.",
    ),
    output: str = typer.Option("text", "--output", help="Output format: text or json."),
) -> None:
    """Query the RAG system."""
    from sdk.client import RAGClient

    top_k = int(resolve_cli_value(top_k))
    output = str(resolve_cli_value(output))
    include_evidence = parse_bool_option(show_evidence, "show-evidence")
    with RAGClient(
        base_url=get_config("api_url"),
        api_key=get_config("api_key") or None,
        timeout=float(get_config("timeout", 30.0)),
    ) as client:
        with console.status("Querying..."):
            result = client.query(text, top_k=top_k, include_evidence=include_evidence)

    if output == "json":
        console.print_json(json=result.model_dump_json())
        return

    console.print(f"\n[bold]Answer:[/bold] {result.answer}\n")
    if include_evidence and result.citations:
        table = Table(title="Evidence")
        table.add_column("Citation")
        table.add_column("Chunk ID")
        table.add_column("Document")
        for citation in result.citations:
            table.add_row(citation.citation_key, citation.chunk_id, citation.document_id)
        console.print(table)


def register(app: typer.Typer) -> None:
    """Register the query command on the root Typer app."""
    app.command(name="query")(query_command)
