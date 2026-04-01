"""Evaluation command for the CLI."""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from cli.utils import get_config, parse_bool_option, resolve_cli_value

console = Console()


def evaluate_command(
    dataset: str = typer.Argument(..., help="Dataset identifier to evaluate."),
    baseline: Optional[str] = typer.Option(
        None,
        "--baseline",
        help="Baseline run identifier for regression comparison.",
    ),
    save_baseline: str = typer.Option(
        "false",
        "--save-baseline",
        help="Persist the current run as the new baseline.",
    ),
) -> None:
    """Run evaluation on a dataset."""
    from sdk.client import RAGClient

    dataset = str(resolve_cli_value(dataset))
    baseline = resolve_cli_value(baseline)
    should_save_baseline = parse_bool_option(save_baseline, "save-baseline")
    with RAGClient(
        base_url=get_config("api_url"),
        api_key=get_config("api_key") or None,
        timeout=float(get_config("timeout", 30.0)),
    ) as client:
        with console.status("Running evaluation..."):
            if baseline:
                result = client.regression_test(dataset, baseline)
                _print_regression(result)
            else:
                result = client.evaluate(dataset)
                _print_eval(result)
                if should_save_baseline:
                    client.save_baseline(result, dataset)
                    console.print(f"Baseline saved: {dataset}")


def register(app: typer.Typer) -> None:
    """Register the evaluation command on the root Typer app."""
    app.command(name="evaluate")(evaluate_command)


def _print_eval(result) -> None:
    """Render evaluation metrics as a compact table."""
    table = Table(title=f"Evaluation: {result.dataset_id}")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Run ID", result.run_id)
    table.add_row("Avg Latency", f"{result.avg_latency_ms:.2f}ms")
    table.add_row("P95 Latency", f"{result.p95_latency_ms:.2f}ms")
    table.add_row("Cost", f"${result.total_cost_usd:.4f}")
    console.print(table)


def _print_regression(result) -> None:
    """Render regression results."""
    table = Table(title="Regression Test")
    table.add_column("Status")
    table.add_column("Details")
    table.add_row("Passed", str(result.passed))
    table.add_row("Regressions", ", ".join(result.regressions) or "None")
    table.add_row("Improvements", ", ".join(result.improvements) or "None")
    console.print(table)
